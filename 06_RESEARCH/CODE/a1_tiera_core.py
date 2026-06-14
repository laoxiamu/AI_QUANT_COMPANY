#!/usr/bin/env python3
"""Auditable primitives for the preregistered A-1 Tier A screen."""

from __future__ import annotations

import bisect
import gc
import hashlib
import math
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import NormalDist
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


SEED = 20260615
BOOTSTRAP_REPLICATIONS = 10_000
BLOCK_WIDTH_HOURS = 144
CUTOFF_EXCLUSIVE = pd.Timestamp("2024-12-10T00:00:00Z")
WINDOW_DAYS = 365
MIN_HISTORY_DAYS = 180
MIN_HISTORY_OBSERVATIONS = 720
REFRACTORY_HOURS = 24
HORIZONS = (24, 48, 72)
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")


def assert_not_restricted_path(path: str | Path) -> None:
    """Reject all sealed/HOLDOUT inputs in executor-facing code."""
    resolved = Path(path)
    upper_parts = {part.upper() for part in resolved.parts}
    upper_name = resolved.name.upper()
    assert "HOLDOUT" not in upper_parts, f"forbidden HOLDOUT path: {resolved}"
    assert "SEALED" not in upper_name, f"forbidden sealed path: {resolved}"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def empirical_midrank_percentile(sorted_prior: Sequence[float], value: float) -> float:
    """Return (# prior below + 0.5 * # tied) / N."""
    if not sorted_prior:
        return math.nan
    lower = bisect.bisect_left(sorted_prior, value)
    upper = bisect.bisect_right(sorted_prior, value)
    return float((lower + 0.5 * (upper - lower)) / len(sorted_prior))


def rolling_midrank_percentile(
    times: pd.Series,
    values: pd.Series,
    *,
    window_days: int = WINDOW_DAYS,
    min_history_days: int = MIN_HISTORY_DAYS,
    min_observations: int = MIN_HISTORY_OBSERVATIONS,
) -> pd.Series:
    """Compute strict-prior rolling percentiles with the frozen validity gate."""
    utc_times = pd.to_datetime(times, utc=True)
    numeric_values = pd.to_numeric(values, errors="coerce")
    result = np.full(len(utc_times), np.nan, dtype=float)
    sorted_prior: list[float] = []
    day_counts: Counter[date] = Counter()
    left = 0

    for idx, current_time in enumerate(utc_times):
        if idx:
            prior_value = float(numeric_values.iloc[idx - 1])
            if not math.isnan(prior_value):
                bisect.insort(sorted_prior, prior_value)
                prior_day = utc_times.iloc[idx - 1].date()
                day_counts[prior_day] += 1

        cutoff = current_time - pd.Timedelta(days=window_days)
        while left < idx and utc_times.iloc[left] < cutoff:
            expired_value = float(numeric_values.iloc[left])
            if not math.isnan(expired_value):
                remove_at = bisect.bisect_left(sorted_prior, expired_value)
                if remove_at >= len(sorted_prior) or sorted_prior[remove_at] != expired_value:
                    raise AssertionError("rolling percentile state lost an observation")
                sorted_prior.pop(remove_at)
                expired_day = utc_times.iloc[left].date()
                day_counts[expired_day] -= 1
                if day_counts[expired_day] == 0:
                    del day_counts[expired_day]
            left += 1

        current_value = float(numeric_values.iloc[idx])
        if (
            not math.isnan(current_value)
            and len(sorted_prior) >= min_observations
            and len(day_counts) >= min_history_days
        ):
            result[idx] = empirical_midrank_percentile(sorted_prior, current_value)

    return pd.Series(result, index=values.index, dtype="float64")


def add_nominal_oi_features(hourly: pd.DataFrame) -> pd.DataFrame:
    """Add the v5 6h nominal-OI change and strict-prior percentile."""
    required = {"ts", "oi_notional"}
    missing = required - set(hourly.columns)
    if missing:
        raise ValueError(f"hourly OI missing columns: {sorted(missing)}")

    frame = hourly.sort_values("ts").reset_index(drop=True).copy()
    frame["ts"] = pd.to_datetime(frame["ts"], utc=True)
    frame["oi_notional"] = pd.to_numeric(frame["oi_notional"], errors="coerce")
    lagged = frame["oi_notional"].shift(6)
    frame["d6h_pct"] = frame["oi_notional"] / lagged - 1.0
    endpoints_valid = frame["oi_notional"].notna() & lagged.notna()
    frame.loc[~endpoints_valid, "d6h_pct"] = np.nan
    frame["d6h_rolling_pctl"] = rolling_midrank_percentile(
        frame["ts"], frame["d6h_pct"]
    )
    return frame


def add_mark_direction(hourly: pd.DataFrame, mark: pd.DataFrame) -> pd.DataFrame:
    """Attach same-window 6h MARK log return without filling price gaps."""
    prices = mark.loc[:, ["ts", "mark_close"]].copy()
    prices["ts"] = pd.to_datetime(prices["ts"], utc=True)
    prices["mark_close"] = pd.to_numeric(prices["mark_close"], errors="coerce")
    price_map = prices.set_index("ts")["mark_close"]
    frame = hourly.copy()
    frame["mark_close"] = frame["ts"].map(price_map)
    frame["mark_close_lag6"] = (frame["ts"] - pd.Timedelta(hours=6)).map(price_map)
    valid = (
        frame["mark_close"].notna()
        & frame["mark_close_lag6"].notna()
        & (frame["mark_close"] > 0)
        & (frame["mark_close_lag6"] > 0)
    )
    frame["r6h_mark"] = np.nan
    frame.loc[valid, "r6h_mark"] = np.log(
        frame.loc[valid, "mark_close"] / frame.loc[valid, "mark_close_lag6"]
    )
    return frame.drop(columns=["mark_close_lag6"])


def trigger_rows(features: pd.DataFrame) -> pd.DataFrame:
    """Select the frozen P1 nominal-OI drop and negative-MARK condition."""
    required = {"ts", "d6h_rolling_pctl", "r6h_mark"}
    missing = required - set(features.columns)
    if missing:
        raise ValueError(f"trigger features missing columns: {sorted(missing)}")
    mask = (
        features["d6h_rolling_pctl"].notna()
        & (features["d6h_rolling_pctl"] <= 0.01)
        & features["r6h_mark"].notna()
        & (features["r6h_mark"] < 0)
    )
    return features.loc[mask].sort_values("ts").reset_index(drop=True)


def apply_refractory(
    triggers: pd.DataFrame,
    *,
    hours: int = REFRACTORY_HOURS,
) -> pd.DataFrame:
    """Keep the first trigger, then ignore triggers through event+24h inclusive."""
    if triggers.empty:
        return triggers.copy()
    frame = triggers.sort_values("ts").reset_index(drop=True)
    keep: list[int] = []
    last_event: pd.Timestamp | None = None
    refractory = pd.Timedelta(hours=hours)
    for idx, raw_time in enumerate(frame["ts"]):
        current = pd.Timestamp(raw_time)
        if last_event is None or current - last_event > refractory:
            keep.append(idx)
            last_event = current
    return frame.iloc[keep].reset_index(drop=True)


def severity_label(percentile: float) -> tuple[str, int]:
    if 0.0 <= percentile <= 0.0033:
        return "Severe", 2
    if 0.0033 < percentile <= 0.0067:
        return "Medium", 1
    if 0.0067 < percentile <= 0.01:
        return "Mild", 0
    raise ValueError(f"percentile outside frozen severity bins: {percentile}")


def split_work_sealed(episodes: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sort deterministically and reserve every fifth row for sealed holdout."""
    frame = episodes.sort_values(
        ["event_time_utc", "symbol"], kind="mergesort"
    ).reset_index(drop=True)
    sealed_mask = np.arange(len(frame)) % 5 == 4
    work = frame.loc[~sealed_mask].reset_index(drop=True)
    sealed = frame.loc[sealed_mask].reset_index(drop=True)
    return work, sealed


def encrypt_aes256_gcm(plaintext: bytes, key: bytes, nonce: bytes) -> bytes:
    """Return the frozen 12B nonce || ciphertext || 16B GCM tag layout."""
    if len(key) != 32:
        raise ValueError("AES-256-GCM requires a 32-byte key")
    if len(nonce) != 12:
        raise ValueError("AES-GCM nonce must be 12 bytes")
    ciphertext_and_tag = AESGCM(key).encrypt(nonce, plaintext, None)
    return nonce + ciphertext_and_tag


def decrypt_aes256_gcm(payload: bytes, key: bytes) -> bytes:
    if len(payload) < 12 + 16:
        raise ValueError("encrypted payload is too short")
    return AESGCM(key).decrypt(payload[:12], payload[12:], None)


def release_plaintext(*objects: object) -> None:
    """Drop custodian plaintext references before the process exits."""
    for obj in objects:
        if isinstance(obj, bytearray):
            obj[:] = b"\x00" * len(obj)
    del objects
    gc.collect()


def circular_block_indices(
    event_times: Sequence[pd.Timestamp],
    *,
    start_offset_hours: int,
    width_hours: int = BLOCK_WIDTH_HOURS,
) -> np.ndarray:
    """Return one circular block ordered by offset from its sampled start."""
    times = pd.DatetimeIndex(pd.to_datetime(event_times, utc=True))
    if len(times) == 0:
        return np.array([], dtype=int)
    span_hours = int((times[-1] - times[0]) / pd.Timedelta(hours=1)) + 1
    if not 0 <= start_offset_hours < span_hours:
        raise ValueError("start offset is outside the circular grid")
    hour_offsets = (
        (times - times[0]) / pd.Timedelta(hours=1)
    ).to_numpy(dtype=np.int64)
    circular_offsets = (hour_offsets - start_offset_hours) % span_hours
    members = np.flatnonzero(circular_offsets < width_hours)
    order = np.argsort(circular_offsets[members], kind="stable")
    return members[order]


def bootstrap_sample_indices(
    event_times: Sequence[pd.Timestamp],
    rng: np.random.Generator,
    *,
    width_hours: int = BLOCK_WIDTH_HOURS,
) -> np.ndarray:
    """Draw circular blocks until exactly n episode indices are accumulated."""
    times = pd.DatetimeIndex(pd.to_datetime(event_times, utc=True))
    n = len(times)
    if n == 0:
        return np.array([], dtype=int)
    span_hours = int((times[-1] - times[0]) / pd.Timedelta(hours=1)) + 1
    sampled: list[int] = []
    while len(sampled) < n:
        start = int(rng.integers(0, span_hours))
        block = circular_block_indices(
            times,
            start_offset_hours=start,
            width_hours=width_hours,
        )
        if len(block) == 0:
            continue
        remaining = n - len(sampled)
        sampled.extend(int(item) for item in block[:remaining])
    return np.asarray(sampled, dtype=int)


@dataclass(frozen=True)
class BootstrapResult:
    n: int
    estimate: float
    p_value: float
    ci_low: float
    ci_high: float
    replications: int
    seed: int


def moving_block_mean_test(
    event_times: Sequence[pd.Timestamp],
    values: Sequence[float],
    *,
    replications: int = BOOTSTRAP_REPLICATIONS,
    seed: int = SEED,
) -> BootstrapResult | None:
    """Frozen one-sided centered test and basic 95% CI for a mean."""
    numeric = np.asarray(values, dtype=float)
    times = pd.DatetimeIndex(pd.to_datetime(event_times, utc=True))
    valid = np.isfinite(numeric)
    numeric = numeric[valid]
    times = times[valid]
    if len(numeric) == 0:
        return None
    order = np.argsort(times.asi8, kind="stable")
    times = times[order]
    numeric = numeric[order]
    observed = float(numeric.mean())
    rng = np.random.default_rng(seed)
    bootstrap_means = np.empty(replications, dtype=float)
    for replication in range(replications):
        indices = bootstrap_sample_indices(times, rng)
        bootstrap_means[replication] = float(numeric[indices].mean())
    centered = bootstrap_means - observed
    p_value = float((np.sum(centered >= observed) + 1) / (replications + 1))
    q025, q975 = np.quantile(bootstrap_means, [0.025, 0.975])
    return BootstrapResult(
        n=len(numeric),
        estimate=observed,
        p_value=p_value,
        ci_low=float(2 * observed - q975),
        ci_high=float(2 * observed - q025),
        replications=replications,
        seed=seed,
    )


def spearman_rho(x_values: Sequence[float], y_values: Sequence[float]) -> float:
    x = pd.Series(x_values, dtype="float64")
    y = pd.Series(y_values, dtype="float64")
    valid = x.notna() & y.notna()
    x_rank = x.loc[valid].rank(method="average").to_numpy()
    y_rank = y.loc[valid].rank(method="average").to_numpy()
    if len(x_rank) < 2 or np.std(x_rank) == 0 or np.std(y_rank) == 0:
        return math.nan
    return float(np.corrcoef(x_rank, y_rank)[0, 1])


def moving_block_spearman_test(
    event_times: Sequence[pd.Timestamp],
    severity: Sequence[float],
    values: Sequence[float],
    *,
    replications: int = BOOTSTRAP_REPLICATIONS,
    seed: int = SEED,
) -> BootstrapResult | None:
    """Paired moving-block bootstrap centered at observed Spearman rho."""
    times = pd.DatetimeIndex(pd.to_datetime(event_times, utc=True))
    x = np.asarray(severity, dtype=float)
    y = np.asarray(values, dtype=float)
    valid = np.isfinite(x) & np.isfinite(y)
    times = times[valid]
    x = x[valid]
    y = y[valid]
    if len(x) < 2:
        return None
    order = np.argsort(times.asi8, kind="stable")
    times = times[order]
    x = x[order]
    y = y[order]
    observed = spearman_rho(x, y)
    if not math.isfinite(observed):
        return None

    rng = np.random.default_rng(seed)
    bootstrap_rhos = np.empty(replications, dtype=float)
    for replication in range(replications):
        indices = bootstrap_sample_indices(times, rng)
        bootstrap_rhos[replication] = spearman_rho(x[indices], y[indices])
    if not np.isfinite(bootstrap_rhos).all():
        return None
    centered = bootstrap_rhos - observed
    p_value = float((np.sum(centered >= observed) + 1) / (replications + 1))
    q025, q975 = np.quantile(bootstrap_rhos, [0.025, 0.975])
    return BootstrapResult(
        n=len(x),
        estimate=observed,
        p_value=p_value,
        ci_low=float(2 * observed - q975),
        ci_high=float(2 * observed - q025),
        replications=replications,
        seed=seed,
    )


def holm_adjust(
    raw_p_values: Mapping[str, float | None],
) -> dict[str, float | None]:
    """Holm-adjust a fixed family, treating unavailable members as p=1."""
    items = list(raw_p_values.items())
    sortable = [
        (name, 1.0 if value is None or not math.isfinite(value) else float(value))
        for name, value in items
    ]
    sortable.sort(key=lambda item: item[1])
    adjusted_numeric: dict[str, float] = {}
    running = 0.0
    family_size = len(sortable)
    for rank, (name, value) in enumerate(sortable):
        candidate = min(1.0, (family_size - rank) * value)
        running = max(running, candidate)
        adjusted_numeric[name] = running
    return {
        name: (
            None
            if raw_p_values[name] is None
            or not math.isfinite(float(raw_p_values[name]))
            else adjusted_numeric[name]
        )
        for name, _ in items
    }


def wf_segment_lengths(n: int) -> tuple[int, int, int]:
    first = math.ceil(n / 3)
    second = math.ceil((n - first) / 2)
    return first, second, n - first - second


def wf_stability(episodes: pd.DataFrame) -> dict[str, object]:
    """Apply the frozen split, midpoint cuts, footprint purge, and bare means."""
    required = {"event_time", "align_time", "car_48h"}
    missing = required - set(episodes.columns)
    if missing:
        raise ValueError(f"WF input missing columns: {sorted(missing)}")
    frame = episodes.sort_values(["event_time", "symbol"], kind="mergesort").reset_index(
        drop=True
    )
    lengths = wf_segment_lengths(len(frame))
    boundaries = (lengths[0], lengths[0] + lengths[1])
    if len(frame) < 3 or any(index <= 0 or index >= len(frame) for index in boundaries):
        return {
            "status": "N.A.",
            "lengths_before_purge": list(lengths),
            "cutpoints": [],
            "segments": [],
            "positive_segments": 0,
        }

    event_times = pd.to_datetime(frame["event_time"], utc=True)
    cutpoints = [
        event_times.iloc[index - 1]
        + (event_times.iloc[index] - event_times.iloc[index - 1]) / 2
        for index in boundaries
    ]
    segment_ids = np.repeat(np.arange(3), lengths)
    frame["segment"] = segment_ids
    frame["footprint_start"] = event_times - pd.Timedelta(hours=72)
    frame["footprint_end"] = pd.to_datetime(frame["align_time"], utc=True) + pd.Timedelta(
        hours=48
    )
    crosses = np.zeros(len(frame), dtype=bool)
    for cutpoint in cutpoints:
        crosses |= (
            (frame["footprint_start"] < cutpoint)
            & (frame["footprint_end"] > cutpoint)
        ).to_numpy()
    frame["purged"] = crosses

    segment_rows: list[dict[str, object]] = []
    positive = 0
    any_na = False
    for segment in range(3):
        original = frame.loc[frame["segment"] == segment]
        retained = original.loc[~original["purged"]]
        values = pd.to_numeric(retained["car_48h"], errors="coerce").dropna()
        mean = float(values.mean()) if len(values) else None
        if mean is None:
            any_na = True
        elif mean > 0:
            positive += 1
        segment_rows.append(
            {
                "segment": segment + 1,
                "n_before_purge": int(len(original)),
                "n_purged": int(original["purged"].sum()),
                "n_car": int(len(values)),
                "mean_car_48h": mean,
            }
        )
    return {
        "status": "N.A." if any_na else ("PASS" if positive >= 2 else "FAIL"),
        "lengths_before_purge": list(lengths),
        "cutpoints": [item.strftime("%Y-%m-%dT%H:%M:%SZ") for item in cutpoints],
        "segments": segment_rows,
        "positive_segments": positive,
    }


def power_diagnostic(
    episodes: pd.DataFrame,
    *,
    horizon: int,
    iccs: Iterable[float] = (0.0, 0.2, 0.5),
) -> list[dict[str, float | int]]:
    """Return the preregistered event-pre variance and clustered MDE diagnostic."""
    car_col = f"car_{horizon}h"
    required = {"event_time", "baseline_variance", car_col}
    missing = required - set(episodes.columns)
    if missing:
        raise ValueError(f"power input missing columns: {sorted(missing)}")
    valid = episodes[car_col].notna() & episodes["baseline_variance"].notna()
    frame = episodes.loc[valid].copy()
    n = len(frame)
    if n == 0:
        return []
    event_days = pd.to_datetime(frame["event_time"], utc=True).dt.date.nunique()
    median_variance = float(frame["baseline_variance"].median())
    sigma_pre = math.sqrt(horizon * median_variance)
    m_bar = n / event_days
    z_sum = NormalDist().inv_cdf(0.95) + NormalDist().inv_cdf(0.80)
    rows: list[dict[str, float | int]] = []
    for icc in iccs:
        n_eff = n / (1.0 + (m_bar - 1.0) * icc)
        rows.append(
            {
                "horizon_hours": horizon,
                "n": n,
                "event_days": int(event_days),
                "m_bar": float(m_bar),
                "icc": float(icc),
                "n_eff": float(n_eff),
                "sigma_pre_h": float(sigma_pre),
                "mde_80": float(z_sum * sigma_pre / math.sqrt(n_eff)),
            }
        )
    return rows
