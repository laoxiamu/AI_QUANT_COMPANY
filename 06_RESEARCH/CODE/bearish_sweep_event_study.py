"""Bearish Liquidity Sweep event study under a dual bear regime."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "06_RESEARCH/CODE/output"
V4_STATS_PATH = OUTPUT_DIR / "stats_v5_sweep_regime_bull_v4.json"
EVENTS_PATH = OUTPUT_DIR / "events_v5_sweep_regime_bear_v5.csv"
STATS_PATH = OUTPUT_DIR / "stats_v5_sweep_regime_bear_v5.json"
SYMBOL_CONFIG = {
    "BTC": (
        PROJECT_ROOT / "BTC_USDT_4H.csv",
        pd.Timestamp("2024-12-09 16:00:00"),
        16267,
    ),
    "ETH": (
        PROJECT_ROOT / "ETH_USDT_4H.csv",
        pd.Timestamp("2024-12-09 16:00:00"),
        16267,
    ),
    "SOL": (
        PROJECT_ROOT / "SOL_USDT_4H.csv",
        pd.Timestamp("2025-04-06 04:00:00"),
        12743,
    ),
}
EXPECTED_RESEARCH_ROWS = {
    "BTC_USDT_4H.csv": 13013,
    "ETH_USDT_4H.csv": 13013,
    "SOL_USDT_4H.csv": 10194,
}
EXPECTED_RESEARCH_END = {
    "BTC_USDT_4H.csv": pd.Timestamp("2024-12-09 12:00:00"),
    "ETH_USDT_4H.csv": pd.Timestamp("2024-12-09 12:00:00"),
    "SOL_USDT_4H.csv": pd.Timestamp("2025-04-06 00:00:00"),
}
SWEEP_LOOKBACK = 20
BTC_MOMENTUM_DAYS = 30
HORIZONS = (6, 12, 24)
HOLDOUT_FRACTION = 0.2
NONOVERLAP_BARS = 24
PERIOD_LABELS = (
    "2019-2020",
    "2021",
    "2022",
    "2023-2024",
    "2025",
)


def load_pre_holdout(
    path: Path,
    expected_holdout_start: pd.Timestamp,
    registered_total_rows: int,
) -> tuple[pd.DataFrame, pd.Timestamp]:
    """Parse only the registered first 80%; Holdout rows stay unread."""
    research_rows = int(registered_total_rows * (1 - HOLDOUT_FRACTION))
    bars = pd.read_csv(path, parse_dates=["datetime"], nrows=research_rows)
    required = {"datetime", "open", "high", "low", "close", "volume"}
    missing = required.difference(bars.columns)
    if missing:
        raise ValueError(f"{path.name} missing columns: {sorted(missing)}")
    if len(bars) != EXPECTED_RESEARCH_ROWS[path.name]:
        raise ValueError(
            f"{path.name} snapshot changed; re-register before analysis"
        )
    if bars["datetime"].iloc[-1] != EXPECTED_RESEARCH_END[path.name]:
        raise ValueError(f"{path.name} pre-Holdout boundary changed")
    if not bars["datetime"].is_monotonic_increasing:
        raise ValueError(f"{path.name} datetime must be ascending")
    if bars["datetime"].duplicated().any():
        raise ValueError(f"{path.name} contains duplicate timestamps")
    if bars[list(required)].isna().any().any():
        raise ValueError(f"{path.name} contains null values")
    return bars.reset_index(drop=True), expected_holdout_start


def daily_close(bars: pd.DataFrame, column: str) -> pd.DataFrame:
    daily = (
        bars.set_index("datetime")["close"]
        .resample("1D")
        .last()
        .to_frame(column)
    )
    if daily[column].isna().any():
        raise ValueError("Daily close contains gaps")
    return daily


def btc_bear_momentum(btc_bars: pd.DataFrame) -> pd.Series:
    daily = daily_close(btc_bars, "btc_daily_close")
    daily["btc_return_30"] = np.log(
        daily["btc_daily_close"]
        / daily["btc_daily_close"].shift(BTC_MOMENTUM_DAYS)
    )
    daily["btc_momentum_bear"] = daily["btc_return_30"].lt(0).shift(1)
    return daily["btc_momentum_bear"]


def add_dual_bear_regime(
    bars: pd.DataFrame,
    btc_momentum_bear: pd.Series,
) -> pd.DataFrame:
    own_daily = daily_close(bars, "daily_close")
    own_daily["ema200"] = own_daily["daily_close"].ewm(
        span=200,
        adjust=False,
        min_periods=200,
    ).mean()
    own_daily["ema_bear"] = (
        own_daily["daily_close"] < own_daily["ema200"]
    ).shift(1)

    result = bars.copy()
    result["bar_index"] = np.arange(len(result))
    result["day"] = result["datetime"].dt.floor("D")
    result = result.join(own_daily["ema_bear"], on="day")
    result = result.join(btc_momentum_bear, on="day")
    result["dual_bear_regime"] = (
        result["ema_bear"].eq(True)
        & result["btc_momentum_bear"].eq(True)
    )
    return result


def period_label(timestamp: pd.Timestamp) -> str:
    if timestamp.year <= 2020:
        return "2019-2020"
    if timestamp.year == 2021:
        return "2021"
    if timestamp.year == 2022:
        return "2022"
    if timestamp.year <= 2024:
        return "2023-2024"
    return "2025"


def detect_events(
    symbol: str,
    bars: pd.DataFrame,
    momentum_bear: pd.Series,
) -> tuple[pd.DataFrame, dict[str, int]]:
    data = add_dual_bear_regime(bars, momentum_bear)
    data["ref_high"] = (
        data["high"]
        .shift(1)
        .rolling(SWEEP_LOOKBACK, min_periods=SWEEP_LOOKBACK)
        .max()
    )
    data["bearish_sweep"] = (
        (data["high"] > data["ref_high"])
        & (data["close"] < data["ref_high"])
    )
    for horizon in HORIZONS:
        data[f"future_ret_{horizon}"] = np.log(
            data["close"].shift(-horizon) / data["close"]
        )

    raw_count = int(data["bearish_sweep"].sum())
    ema_count = int(
        (data["bearish_sweep"] & data["ema_bear"].eq(True)).sum()
    )
    regime_events = data[
        data["bearish_sweep"] & data["dual_bear_regime"]
    ].copy()
    return_columns = [f"future_ret_{h}" for h in HORIZONS]
    complete = regime_events.dropna(subset=return_columns).copy()
    complete["symbol"] = symbol
    complete["period"] = complete["datetime"].map(period_label)
    columns = [
        "symbol",
        "datetime",
        "bar_index",
        "period",
        "close",
        "ref_high",
        *return_columns,
    ]
    return complete[columns], {
        "regime_before": raw_count,
        "ema_bear_sweeps": ema_count,
        "regime_after": len(regime_events),
        "complete_events": len(complete),
    }


def summarize(values: pd.Series) -> dict[str, float | int | None]:
    clean = values.dropna().astype(float)
    empty = {
        "n": 0,
        "mean": None,
        "std": None,
        "median": None,
        "short_hit_rate": None,
        "t_stat": None,
        "p_one_sided_less": None,
        "p_two_sided": None,
    }
    if clean.empty:
        return empty
    if len(clean) < 2 or clean.std(ddof=1) == 0:
        t_stat = p_less = p_two = None
    else:
        less = ttest_1samp(clean, popmean=0, alternative="less")
        two_sided = ttest_1samp(clean, popmean=0, alternative="two-sided")
        t_stat = float(less.statistic)
        p_less = float(less.pvalue)
        p_two = float(two_sided.pvalue)
    return {
        "n": int(len(clean)),
        "mean": float(clean.mean()),
        "std": float(clean.std(ddof=1)) if len(clean) > 1 else None,
        "median": float(clean.median()),
        "short_hit_rate": float((clean < 0).mean()),
        "t_stat": t_stat,
        "p_one_sided_less": p_less,
        "p_two_sided": p_two,
    }


def grouped_statistics(events: pd.DataFrame) -> dict[str, object]:
    return {
        "by_symbol": {
            symbol: {
                str(horizon): summarize(group[f"future_ret_{horizon}"])
                for horizon in HORIZONS
            }
            for symbol, group in events.groupby("symbol", sort=True)
        },
        "combined": {
            str(horizon): summarize(events[f"future_ret_{horizon}"])
            for horizon in HORIZONS
        },
    }


def period_statistics(events: pd.DataFrame) -> dict[str, object]:
    result = {}
    for label in PERIOD_LABELS:
        period_events = events[events["period"] == label]
        result[label] = {
            "combined": {
                str(horizon): summarize(
                    period_events[f"future_ret_{horizon}"]
                )
                for horizon in HORIZONS
            },
            "by_symbol": {
                symbol: {
                    str(horizon): summarize(
                        period_events.loc[
                            period_events["symbol"] == symbol,
                            f"future_ret_{horizon}",
                        ]
                    )
                    for horizon in HORIZONS
                }
                for symbol in SYMBOL_CONFIG
            },
        }
    return result


def walk_forward_statistics(
    events: pd.DataFrame,
    common_start: pd.Timestamp,
    common_end: pd.Timestamp,
) -> list[dict[str, object]]:
    span = common_end - common_start
    boundaries = [
        common_start,
        (common_start + span / 3).floor("4h"),
        (common_start + span * 2 / 3).floor("4h"),
        common_end,
    ]
    windows = []
    for index in range(3):
        start = boundaries[index]
        end = boundaries[index + 1]
        if index < 2:
            mask = (events["datetime"] >= start) & (
                events["datetime"] < end
            )
        else:
            mask = events["datetime"].between(start, end)
        windows.append({
            "window": index + 1,
            "start": str(start),
            "end": str(end),
            **summarize(events.loc[mask, "future_ret_12"]),
        })
    return windows


def nonoverlapping_subset(events: pd.DataFrame) -> pd.DataFrame:
    kept_groups = []
    for _, group in events.groupby("symbol", sort=True):
        group = group.sort_values("bar_index")
        keep = []
        last_kept = None
        for row in group.itertuples():
            if (
                last_kept is None
                or row.bar_index - last_kept > NONOVERLAP_BARS
            ):
                keep.append(row.Index)
                last_kept = row.bar_index
        kept_groups.append(group.loc[keep])
    return pd.concat(kept_groups, ignore_index=True).sort_values(
        ["datetime", "symbol"]
    )


def v4_baseline() -> dict[str, object]:
    with V4_STATS_PATH.open(encoding="utf-8") as handle:
        v4 = json.load(handle)
    return {
        "experiment": v4["experiment"],
        "event_counts": v4["event_counts"],
        "overall": v4["overall"],
        "periods": v4["periods"],
        "walk_forward_t12": v4["walk_forward_t12"],
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    loaded = {}
    ranges = {}
    for symbol, (path, holdout_start, total_rows) in SYMBOL_CONFIG.items():
        bars, registered_holdout = load_pre_holdout(
            path,
            holdout_start,
            total_rows,
        )
        loaded[symbol] = bars
        ranges[symbol] = {
            "research_start": str(bars["datetime"].iloc[0]),
            "research_end": str(bars["datetime"].iloc[-1]),
            "holdout_start": str(registered_holdout),
            "research_rows": len(bars),
        }

    momentum_bear = btc_bear_momentum(loaded["BTC"])
    frames = []
    counts = {}
    for symbol, bars in loaded.items():
        events, symbol_counts = detect_events(
            symbol,
            bars,
            momentum_bear,
        )
        frames.append(events)
        counts[symbol] = symbol_counts

    events = pd.concat(frames, ignore_index=True).sort_values(
        ["datetime", "symbol"]
    )
    nonoverlap = nonoverlapping_subset(events)
    common_start = max(
        pd.Timestamp(values["research_start"])
        for values in ranges.values()
    )
    common_end = min(
        pd.Timestamp(values["research_end"])
        for values in ranges.values()
    )
    common_events = events[events["datetime"].between(
        common_start,
        common_end,
    )]

    overall = grouped_statistics(events)
    output = {
        "experiment": "v5_sweep_regime_bear_v5",
        "baseline_experiment": "v5_sweep_regime_bull_v4",
        "holdout_accessed": False,
        "physical_holdout_truncation": True,
        "parameters": {
            "sweep_lookback": SWEEP_LOOKBACK,
            "horizons": list(HORIZONS),
            "ema_regime": (
                "previous completed UTC daily close < own Daily EMA200"
            ),
            "momentum_regime": (
                "previous completed UTC day BTC 30-day log return < 0"
            ),
            "test_alternative": "less",
            "nonoverlap_rule": (
                "within symbol, retained bar-index distance > 24"
            ),
        },
        "research_ranges": ranges,
        "event_counts": counts,
        "overall": overall,
        "periods": period_statistics(events),
        "walk_forward_t12": walk_forward_statistics(
            common_events,
            common_start,
            common_end,
        ),
        "common_walk_forward_range": {
            "start": str(common_start),
            "end": str(common_end),
            "events": len(common_events),
        },
        "nonoverlap": {
            "event_count": len(nonoverlap),
            "counts_by_symbol": {
                key: int(value)
                for key, value in nonoverlap["symbol"].value_counts().items()
            },
            "statistics": grouped_statistics(nonoverlap),
        },
        "v4_baseline": v4_baseline(),
    }
    output["main_hypothesis_passed"] = all(
        overall["combined"][str(horizon)]["mean"] < 0
        and overall["combined"][str(horizon)]["p_one_sided_less"] < 0.05
        for horizon in HORIZONS
    )
    output["nonoverlap_all_windows_passed"] = all(
        output["nonoverlap"]["statistics"]["combined"][str(horizon)][
            "mean"
        ] < 0
        and output["nonoverlap"]["statistics"]["combined"][str(horizon)][
            "p_one_sided_less"
        ] < 0.05
        for horizon in HORIZONS
    )

    events.to_csv(
        EVENTS_PATH,
        index=False,
        date_format="%Y-%m-%d %H:%M:%S",
    )
    with STATS_PATH.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)

    print(json.dumps({
        "events": len(events),
        "main_hypothesis_passed": output["main_hypothesis_passed"],
        "nonoverlap_events": len(nonoverlap),
        "nonoverlap_all_windows_passed": (
            output["nonoverlap_all_windows_passed"]
        ),
        "event_counts": counts,
        "combined": overall["combined"],
        "walk_forward_t12": output["walk_forward_t12"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
