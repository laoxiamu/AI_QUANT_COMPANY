#!/usr/bin/env python3
"""Download Tier 1 Binance USD-M 4H kline archives for TSMOM expansion.

This is a data acquisition script only. It selects Tier 1 assets from the C1
candidate table, downloads public Binance monthly kline ZIPs sequentially, and
writes one pre-cutoff OHLCV CSV per symbol plus a JSON manifest.
"""

from __future__ import annotations

import argparse
import io
import json
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANDIDATES_PATH = PROJECT_ROOT / "06_RESEARCH/DATA/c1_candidates.csv"
OUT_DIR = PROJECT_ROOT / "06_RESEARCH/DATA/FUTURES_EXPANDED"
MANIFEST_PATH = OUT_DIR / "DOWNLOAD_MANIFEST.json"

BASE_URL = "https://data.binance.vision/data/futures/um/monthly/klines"
INTERVAL = "4h"
CUTOFF = pd.Timestamp("2024-12-09 23:59:59", tz="UTC")
MIN_SUCCESS_ROWS = 5000
MAX_TIER1_ASSETS = 35
ZIP_SLEEP_SECONDS = 0.1

BLACKLIST = {
    "REEFUSDT",
    "OGNUSDT",
    "COTIUSDT",
    "BLZUSDT",
    "SFPUSDT",
    "STMXUSDT",
    "LINAUSDT",
    "NKNUSDT",
    "DENTUSDT",
    "BTCDOMUSDT",
    "IOTAUSDT",
    "IOSTUSDT",
    "QTUMUSDT",
    "ONTUSDT",
    "BATUSDT",
    "VETUSDT",
    "NEOUSDT",
    "ZILUSDT",
    "RSRUSDT",
    "BELUSDT",
    "CHRUSDT",
    "ALICEUSDT",
    "ONEUSDT",
    "HOTUSDT",
    "MTLUSDT",
    "BAKEUSDT",
    "ANKRUSDT",
    "RLCUSDT",
    "BANDUSDT",
    "ALPHAUSDT",
    "KAVAUSDT",
    "FLMUSDT",
    "ZENUSDT",
    "TRBUSDT",
    "SKLUSDT",
    "DEFIUSDT",
    "BALUSDT",
    "STORJUSDT",
    "UNFIUSDT",
    "XEMUSDT",
    "GTCUSDT",
    "HBARUSDT",
    "CELRUSDT",
}


class NetworkPermissionDenied(RuntimeError):
    """Raised when the local sandbox blocks outbound network sockets."""


@dataclass(frozen=True)
class SymbolResult:
    symbol: str
    rows: int
    start: str | None
    end: str | None
    ok: bool
    error: str | None = None

    def as_manifest_row(self) -> dict[str, object]:
        row: dict[str, object] = {
            "rows": self.rows,
            "start": self.start,
            "end": self.end,
            "ok": self.ok,
        }
        if self.error:
            row["error"] = self.error
        return row


def utc_now_text() -> str:
    """Return an ISO-like UTC timestamp for audit manifests."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def month_range(start_month: str, end_month: str) -> list[str]:
    """Return inclusive YYYY-MM month labels."""
    return [str(period) for period in pd.period_range(start_month, end_month, freq="M")]


def monthly_kline_url(symbol: str, month: str) -> str:
    """Build one Binance USD-M monthly kline ZIP URL."""
    quoted = quote(symbol, safe="")
    return f"{BASE_URL}/{quoted}/{INTERVAL}/{quoted}-{INTERVAL}-{month}.zip"


def select_tier1_assets(candidates_path: Path = CANDIDATES_PATH) -> pd.DataFrame:
    """Select Tier 1 symbols using the D1 task rules."""
    frame = pd.read_csv(candidates_path)
    required = {"symbol", "onboard", "head_first_ok", "head_recent_ok", "est_bars"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{candidates_path} missing columns: {sorted(missing)}")

    mask = (
        (frame["head_first_ok"] == True)  # noqa: E712
        & (frame["head_recent_ok"] == True)  # noqa: E712
        & (pd.to_numeric(frame["est_bars"], errors="coerce") >= 7000)
        & (~frame["symbol"].isin(BLACKLIST))
    )
    selected = frame.loc[mask].copy()
    selected["est_bars"] = pd.to_numeric(selected["est_bars"], errors="raise").astype(int)
    selected["onboard_ts"] = pd.to_datetime(selected["onboard"], utc=True, errors="raise")
    selected = selected.sort_values(["est_bars", "symbol"], ascending=[False, True]).head(MAX_TIER1_ASSETS)
    return selected.loc[:, ["symbol", "onboard", "est_bars", "onboard_ts"]].reset_index(drop=True)


def fetch_zip_bytes(url: str, retries: int = 3, timeout: int = 30) -> bytes:
    """Download one ZIP archive with bounded retries."""
    request = Request(url, headers={"User-Agent": "codex-d1-tier1-download/1.0"})
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}: {url}")
                return response.read()
        except HTTPError as exc:
            if exc.code == 404:
                raise RuntimeError(f"HTTP 404: {url}") from exc
            last_error = exc
        except URLError as exc:
            if isinstance(exc.reason, PermissionError):
                raise NetworkPermissionDenied(str(exc.reason)) from exc
            last_error = exc
        except (TimeoutError, OSError, RuntimeError) as exc:
            if isinstance(exc, PermissionError):
                raise NetworkPermissionDenied(str(exc)) from exc
            last_error = exc

        if attempt < retries:
            time.sleep(0.7 * attempt)

    raise RuntimeError(f"{type(last_error).__name__}: {last_error}") from last_error


def parse_kline_zip(payload: bytes) -> pd.DataFrame:
    """Parse one Binance kline ZIP into normalized OHLCV rows."""
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        csv_names = [name for name in archive.namelist() if name.endswith(".csv")]
        if len(csv_names) != 1:
            raise ValueError(f"expected one CSV member, found {csv_names}")
        raw_bytes = archive.read(csv_names[0])

    columns = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_volume",
        "count",
        "taker_buy_volume",
        "taker_buy_quote_volume",
        "ignore",
    ]
    frame = pd.read_csv(io.BytesIO(raw_bytes), header=None, names=columns)
    keep = ["open_time", "open", "high", "low", "close", "volume"]
    for column in keep:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=keep).copy()
    if frame.empty:
        return pd.DataFrame(columns=["datetime", "open", "high", "low", "close", "volume"])

    open_time = frame["open_time"].astype("int64")
    unit = "us" if open_time.median() >= 10**15 else "ms"
    frame["datetime"] = pd.to_datetime(open_time, unit=unit, utc=True)
    frame = frame.loc[frame["datetime"] <= CUTOFF, ["datetime", "open", "high", "low", "close", "volume"]]
    return frame


def read_existing_symbol(path: Path) -> SymbolResult:
    """Validate an already-written symbol CSV for resumable runs."""
    try:
        frame = pd.read_csv(path, usecols=["datetime", "open", "high", "low", "close", "volume"])
        rows = len(frame)
        if rows == 0:
            return SymbolResult(path.stem.removesuffix("_4H"), 0, None, None, False, "existing CSV is empty")
        dates = pd.to_datetime(frame["datetime"], utc=True, errors="coerce")
        if dates.isna().any():
            return SymbolResult(path.stem.removesuffix("_4H"), rows, None, None, False, "existing CSV has invalid datetime")
        if dates.max() > CUTOFF:
            return SymbolResult(
                path.stem.removesuffix("_4H"),
                rows,
                dates.min().strftime("%Y-%m-%d %H:%M:%S"),
                dates.max().strftime("%Y-%m-%d %H:%M:%S"),
                False,
                "existing CSV exceeds cutoff",
            )
        return SymbolResult(
            path.stem.removesuffix("_4H"),
            rows,
            dates.min().strftime("%Y-%m-%d %H:%M:%S"),
            dates.max().strftime("%Y-%m-%d %H:%M:%S"),
            rows >= MIN_SUCCESS_ROWS,
            None if rows >= MIN_SUCCESS_ROWS else f"rows < {MIN_SUCCESS_ROWS}",
        )
    except Exception as exc:  # noqa: BLE001 - manifest should capture exact file issue
        return SymbolResult(path.stem.removesuffix("_4H"), 0, None, None, False, f"{type(exc).__name__}: {exc}")


def download_symbol(symbol: str, onboard: str, force: bool) -> SymbolResult:
    """Download and merge all monthly ZIPs for one symbol."""
    out_path = OUT_DIR / f"{symbol}_4H.csv"
    if out_path.exists() and not force:
        result = read_existing_symbol(out_path)
        if result.ok:
            print(f"{symbol}: {result.rows} rows, {result.start} ~ {result.end} (existing)", flush=True)
            return result

    start_month = pd.Timestamp(onboard).strftime("%Y-%m")
    months = month_range(start_month, CUTOFF.strftime("%Y-%m"))
    frames: list[pd.DataFrame] = []
    for month in months:
        payload = fetch_zip_bytes(monthly_kline_url(symbol, month))
        parsed = parse_kline_zip(payload)
        if not parsed.empty:
            frames.append(parsed)
        time.sleep(ZIP_SLEEP_SECONDS)

    if not frames:
        return SymbolResult(symbol, 0, None, None, False, "no rows parsed")

    merged = (
        pd.concat(frames, ignore_index=True)
        .sort_values("datetime")
        .drop_duplicates("datetime")
        .reset_index(drop=True)
    )
    merged["datetime"] = pd.to_datetime(merged["datetime"], utc=True)
    merged = merged[merged["datetime"] <= CUTOFF].copy()
    rows = len(merged)
    start = merged["datetime"].min().strftime("%Y-%m-%d %H:%M:%S") if rows else None
    end = merged["datetime"].max().strftime("%Y-%m-%d %H:%M:%S") if rows else None
    ok = rows >= MIN_SUCCESS_ROWS
    if rows:
        output = merged.copy()
        output["datetime"] = output["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
        temp_path = out_path.with_suffix(".tmp")
        output.to_csv(temp_path, index=False)
        temp_path.replace(out_path)
    print(f"{symbol}: {rows} rows, {start} ~ {end}", flush=True)
    return SymbolResult(symbol, rows, start, end, ok, None if ok else f"rows < {MIN_SUCCESS_ROWS}")


def write_manifest(tier1: pd.DataFrame, results: dict[str, SymbolResult]) -> None:
    """Write the D1 download manifest."""
    failed = [symbol for symbol, result in results.items() if not result.ok]
    success = [symbol for symbol, result in results.items() if result.ok]
    manifest = {
        "generated": utc_now_text(),
        "base_url": BASE_URL,
        "interval": INTERVAL,
        "cutoff": CUTOFF.strftime("%Y-%m-%d %H:%M:%S%z"),
        "candidate_source": str(CANDIDATES_PATH.relative_to(PROJECT_ROOT)),
        "selection": {
            "head_first_ok": True,
            "head_recent_ok": True,
            "min_est_bars": 7000,
            "max_assets": MAX_TIER1_ASSETS,
            "blacklist_size": len(BLACKLIST),
        },
        "tier1_assets": tier1["symbol"].tolist(),
        "downloads": {symbol: result.as_manifest_row() for symbol, result in results.items()},
        "failed": failed,
        "summary": {"total": len(tier1), "success": len(success), "failed": len(failed)},
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Re-download symbols even when valid CSVs already exist.")
    parser.add_argument(
        "--select-only",
        action="store_true",
        help="Print the Tier 1 selection and write a manifest without network downloads.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tier1 = select_tier1_assets()
    print("Tier 1 assets:", ", ".join(tier1["symbol"].tolist()), flush=True)

    results: dict[str, SymbolResult] = {}
    if args.select_only:
        for row in tier1.itertuples(index=False):
            results[row.symbol] = SymbolResult(row.symbol, 0, None, None, False, "select-only; not downloaded")
        write_manifest(tier1, results)
        return

    network_denied_error: str | None = None
    for row in tier1.itertuples(index=False):
        symbol = row.symbol
        if network_denied_error:
            results[symbol] = SymbolResult(symbol, 0, None, None, False, network_denied_error)
            continue
        try:
            results[symbol] = download_symbol(symbol, row.onboard, force=args.force)
        except NetworkPermissionDenied as exc:
            network_denied_error = f"network permission denied: {exc}"
            results[symbol] = SymbolResult(symbol, 0, None, None, False, network_denied_error)
            print(f"{symbol}: FAILED {network_denied_error}", flush=True)
        except Exception as exc:  # noqa: BLE001 - keep going and audit every symbol
            error = f"{type(exc).__name__}: {exc}"
            results[symbol] = SymbolResult(symbol, 0, None, None, False, error)
            print(f"{symbol}: FAILED {error}", flush=True)

    write_manifest(tier1, results)
    summary = {"total": len(tier1), "success": sum(result.ok for result in results.values())}
    print(f"Manifest written: {MANIFEST_PATH.relative_to(PROJECT_ROOT)} {summary}", flush=True)


if __name__ == "__main__":
    main()
