"""Prepare data-only TSMOM expansion files and QC report.

This task intentionally performs no backtest, signal generation, or
statistical test. It only downloads Binance official archives, writes new
CSV files, and validates the resulting data files.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from urllib.parse import urlencode
from zipfile import ZipFile

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FUTURES_DIR = PROJECT_ROOT / "06_RESEARCH/DATA/FUTURES"
REPORT_PATH = PROJECT_ROOT / "04_AI_TEAM/CODEX_TASKS/REPORT_TSMOM_EXPANSION_DATA.md"
OLD_HASH_PATH = PROJECT_ROOT / "06_RESEARCH/DATA/DATA_HASHES_20260610.txt"
NEW_HASH_PATH = PROJECT_ROOT / "06_RESEARCH/DATA/DATA_HASHES_20260611.txt"

BASE_URL = "https://data.binance.vision/data/futures/um"
FUNDING_API_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
NEW_SYMBOLS = ["BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "LTCUSDT"]
EXISTING_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
MONTH_SCAN_START = "2019-09"
MONTH_SCAN_END = "2026-05"
DAILY_START = date(2026, 6, 1)
DAILY_END = date(2026, 6, 5)

MARK_COLUMNS = ["datetime", "open", "high", "low", "close", "volume"]
FUNDING_COLUMNS = ["datetime", "funding_interval_hours", "last_funding_rate"]


@dataclass(frozen=True)
class ArchiveJob:
    symbol: str
    dataset: str
    timeframe: str
    period: str
    frequency: str
    required: bool


@dataclass(frozen=True)
class FileSpec:
    path: Path
    dataset: str
    timeframe: str
    expected_hours: int
    reference_path: Path


def archive_url(job: ArchiveJob) -> str:
    if job.dataset == "mark":
        return (
            f"{BASE_URL}/{job.frequency}/markPriceKlines/{job.symbol}/"
            f"{job.timeframe}/{job.symbol}-{job.timeframe}-{job.period}.zip"
        )
    return (
        f"{BASE_URL}/{job.frequency}/fundingRate/{job.symbol}/"
        f"{job.symbol}-fundingRate-{job.period}.zip"
    )


def download_archive(job: ArchiveJob, retries: int = 3) -> tuple[ArchiveJob, bytes | None]:
    url = archive_url(job)
    for attempt in range(1, retries + 1):
        try:
            with urlopen(url, timeout=40) as response:
                return job, response.read()
        except HTTPError as exc:
            if exc.code == 404 and not job.required:
                return job, None
            if attempt == retries:
                raise RuntimeError(f"HTTP {exc.code}: {url}") from exc
        except (TimeoutError, URLError, http.client.RemoteDisconnected, OSError) as exc:
            if attempt == retries:
                raise RuntimeError(f"download failed: {url}") from exc
        time.sleep(1.5 * attempt)
    raise AssertionError("unreachable")


def parse_archive(payload: bytes, dataset: str) -> pd.DataFrame:
    with ZipFile(BytesIO(payload)) as archive:
        member = archive.namelist()[0]
        raw_bytes = archive.read(member)

    frame = pd.read_csv(BytesIO(raw_bytes))
    if dataset == "mark":
        if "open_time" not in frame.columns:
            frame = pd.read_csv(
                BytesIO(raw_bytes),
                header=None,
                names=[
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
                ],
            )
        return frame[["open_time", "open", "high", "low", "close", "volume"]]

    if "calc_time" not in frame.columns:
        frame = pd.read_csv(
            BytesIO(raw_bytes),
            header=None,
            names=["calc_time", "funding_interval_hours", "last_funding_rate"],
        )
    return frame[["calc_time", "funding_interval_hours", "last_funding_rate"]]


def parse_mixed_epoch(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="raise")
    milliseconds = numeric < 10**15
    parsed = pd.Series(pd.NaT, index=numeric.index, dtype="datetime64[ns]")
    parsed.loc[milliseconds] = pd.to_datetime(
        numeric.loc[milliseconds], unit="ms", utc=True
    ).dt.tz_localize(None)
    parsed.loc[~milliseconds] = pd.to_datetime(
        numeric.loc[~milliseconds], unit="us", utc=True
    ).dt.tz_localize(None)
    return parsed


def month_periods() -> list[str]:
    return [str(period) for period in pd.period_range(MONTH_SCAN_START, MONTH_SCAN_END, freq="M")]


def day_periods() -> list[str]:
    return [
        day.strftime("%Y-%m-%d")
        for day in pd.date_range(DAILY_START, DAILY_END, freq="D").date
    ]


def download_jobs(jobs: Iterable[ArchiveJob]) -> dict[tuple[str, str, str], list[pd.DataFrame]]:
    jobs = list(jobs)
    collected: dict[tuple[str, str, str], list[pd.DataFrame]] = {}
    seen_periods: dict[tuple[str, str, str, str], list[str]] = {}
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(download_archive, job): job for job in jobs}
        for count, future in enumerate(as_completed(futures), start=1):
            job, payload = future.result()
            if payload is not None:
                key = (job.symbol, job.dataset, job.timeframe)
                collected.setdefault(key, []).append(parse_archive(payload, job.dataset))
                seen_key = (job.symbol, job.dataset, job.timeframe, job.frequency)
                seen_periods.setdefault(seen_key, []).append(job.period)
            if count % 25 == 0 or count == len(jobs):
                print(f"Downloaded/checked {count}/{len(jobs)} archives", flush=True)

    missing_after_start = []
    for symbol in NEW_SYMBOLS:
        for dataset in ["mark", "funding"]:
            key = (symbol, dataset, "4h", "monthly")
            seen = set(seen_periods.get(key, []))
            ordered = month_periods()
            first_index = next((idx for idx, month in enumerate(ordered) if month in seen), None)
            if first_index is None:
                missing_after_start.append(f"{symbol} {dataset} monthly: no archives found")
                continue
            missing = [month for month in ordered[first_index:] if month not in seen]
            if missing:
                missing_after_start.append(
                    f"{symbol} {dataset} monthly missing after first archive: {', '.join(missing)}"
                )
    if missing_after_start:
        raise RuntimeError("; ".join(missing_after_start))
    return collected


def utc_ms(day: date, end_of_day: bool = False) -> int:
    if end_of_day:
        stamp = datetime(day.year, day.month, day.day, 23, 59, 59, 999000, tzinfo=timezone.utc)
    else:
        stamp = datetime(day.year, day.month, day.day, 0, 0, 0, tzinfo=timezone.utc)
    return int(stamp.timestamp() * 1000)


def fetch_funding_api(symbol: str, retries: int = 3) -> pd.DataFrame:
    params = urlencode(
        {
            "symbol": symbol,
            "startTime": utc_ms(DAILY_START),
            "endTime": utc_ms(DAILY_END, end_of_day=True),
            "limit": 1000,
        }
    )
    url = f"{FUNDING_API_URL}?{params}"
    for attempt in range(1, retries + 1):
        try:
            with urlopen(url, timeout=40) as response:
                payload = response.read()
            rows = json.loads(payload.decode("utf-8"))
            frame = pd.DataFrame(rows)
            if frame.empty:
                return pd.DataFrame(columns=FUNDING_COLUMNS)
            frame["calc_time"] = pd.to_numeric(frame["fundingTime"], errors="raise")
            frame["funding_interval_hours"] = 8
            frame["last_funding_rate"] = pd.to_numeric(frame["fundingRate"], errors="raise")
            return frame[["calc_time", "funding_interval_hours", "last_funding_rate"]]
        except (HTTPError, TimeoutError, URLError, http.client.RemoteDisconnected, OSError) as exc:
            if attempt == retries:
                raise RuntimeError(f"funding API failed: {url}") from exc
            time.sleep(1.5 * attempt)
    raise AssertionError("unreachable")


def normalize_mark(frames: list[pd.DataFrame]) -> pd.DataFrame:
    frame = pd.concat(frames, ignore_index=True)
    frame["datetime"] = parse_mixed_epoch(frame["open_time"])
    return (
        frame[MARK_COLUMNS]
        .sort_values("datetime")
        .drop_duplicates("datetime")
        .reset_index(drop=True)
    )


def normalize_funding(frames: list[pd.DataFrame]) -> pd.DataFrame:
    frame = pd.concat(frames, ignore_index=True)
    frame["datetime"] = parse_mixed_epoch(frame["calc_time"]).dt.floor("s")
    return (
        frame[FUNDING_COLUMNS]
        .sort_values("datetime")
        .drop_duplicates("datetime")
        .reset_index(drop=True)
    )


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, date_format="%Y-%m-%d %H:%M:%S")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_hash_file(path: Path) -> dict[str, str]:
    hashes = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        digest, rel_path = line.split(maxsplit=1)
        hashes[rel_path.strip()] = digest
    return hashes


def old_files_to_verify() -> list[Path]:
    paths = []
    for symbol in EXISTING_SYMBOLS:
        paths.extend(
            [
                FUTURES_DIR / f"{symbol}_MARK_4H.csv",
                FUTURES_DIR / f"{symbol}_MARK_1H.csv",
                FUTURES_DIR / f"{symbol}_FUNDING_8H.csv",
            ]
        )
    return paths


def verify_old_hashes() -> list[dict[str, str]]:
    expected = load_hash_file(OLD_HASH_PATH)
    rows = []
    for path in old_files_to_verify():
        rel_path = path.relative_to(PROJECT_ROOT).as_posix()
        actual = sha256_file(path)
        rows.append(
            {
                "file": rel_path,
                "expected_sha256": expected.get(rel_path, "MISSING_EXPECTED"),
                "actual_sha256": actual,
                "status": "OK" if expected.get(rel_path) == actual else "MISMATCH",
            }
        )
    return rows


def gap_details(datetimes: pd.Series, expected_hours: int) -> tuple[int, float, list[dict[str, str]]]:
    if datetimes.empty:
        return 0, 0.0, []
    expected = pd.Timedelta(hours=expected_hours)
    diffs = datetimes.diff()
    gaps = diffs > expected
    details = []
    missing_intervals = 0
    for idx in datetimes.index[gaps.fillna(False)]:
        delta = datetimes.loc[idx] - datetimes.loc[idx - 1]
        missing = int(delta / expected) - 1
        missing_intervals += max(0, missing)
        details.append(
            {
                "prev": str(datetimes.loc[idx - 1]),
                "next": str(datetimes.loc[idx]),
                "delta": str(delta),
                "missing_intervals": str(missing),
            }
        )
    span_intervals = int((datetimes.iloc[-1] - datetimes.iloc[0]) / expected)
    gap_rate = missing_intervals / span_intervals if span_intervals > 0 else 0.0
    return missing_intervals, gap_rate, details


def qc_file(spec: FileSpec) -> dict[str, object]:
    frame = pd.read_csv(spec.path, parse_dates=["datetime"])
    reference_cols = list(pd.read_csv(spec.reference_path, nrows=0).columns)
    actual_cols = list(frame.columns)
    missing, gap_rate, gaps = gap_details(frame["datetime"], spec.expected_hours)
    utc_aligned = bool(
        frame["datetime"].dt.minute.eq(0).all()
        and frame["datetime"].dt.second.eq(0).all()
        and frame["datetime"].dt.microsecond.eq(0).all()
    )
    return {
        "file": spec.path.relative_to(PROJECT_ROOT).as_posix(),
        "rows": len(frame),
        "start": str(frame["datetime"].iloc[0]) if len(frame) else "EMPTY",
        "end": str(frame["datetime"].iloc[-1]) if len(frame) else "EMPTY",
        "columns": actual_cols,
        "schema_match": actual_cols == reference_cols,
        "utc_aligned": utc_aligned,
        "missing_intervals": missing,
        "gap_rate": gap_rate,
        "gaps": gaps,
        "sha256": sha256_file(spec.path),
    }


def build_jobs() -> list[ArchiveJob]:
    jobs: list[ArchiveJob] = []
    for symbol in NEW_SYMBOLS:
        for month in month_periods():
            jobs.append(ArchiveJob(symbol, "mark", "4h", month, "monthly", False))
            jobs.append(ArchiveJob(symbol, "funding", "4h", month, "monthly", False))
        for day in day_periods():
            jobs.append(ArchiveJob(symbol, "mark", "4h", day, "daily", True))

    for symbol in EXISTING_SYMBOLS:
        for day in day_periods():
            jobs.append(ArchiveJob(symbol, "mark", "4h", day, "daily", True))
            jobs.append(ArchiveJob(symbol, "mark", "1h", day, "daily", True))
    return jobs


def render_report(qc_rows: list[dict[str, object]], old_hash_rows: list[dict[str, str]]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# REPORT_TSMOM_EXPANSION_DATA",
        "",
        f"Generated: {generated_at}",
        "",
        "Script scope: data download and QC only. No backtest, signal generation, "
        "statistical test, preregistration edit, HOLDOUT path access, or git commit "
        "is performed by this script.",
        "",
        "Execution note: during preflight, Codex ran a repository filename search that "
        "returned HOLDOUT path names. No HOLDOUT file contents were opened or parsed.",
        "",
        "Source note: MARK files and funding history through 2026-05 use data.binance.vision "
        "official archives. data.binance.vision daily fundingRate archives for 2026-06-01 "
        "through 2026-06-05 returned 404 during execution, so funding rows for that window "
        "were filled from Binance official futures funding API and are explicitly disclosed here.",
        "",
        "## Old sealed-file hash check",
        "",
        "| file | status | expected sha256 | actual sha256 |",
        "|---|---:|---|---|",
    ]
    for row in old_hash_rows:
        lines.append(
            f"| {row['file']} | {row['status']} | {row['expected_sha256']} | {row['actual_sha256']} |"
        )

    lines.extend(
        [
            "",
            "## New file QC",
            "",
            "| file | rows | start UTC | end UTC | schema | utc | missing intervals | gap rate | sha256 |",
            "|---|---:|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in qc_rows:
        lines.append(
            "| {file} | {rows} | {start} | {end} | {schema} | {utc} | {missing} | {gap_rate:.6%} | {sha} |".format(
                file=row["file"],
                rows=row["rows"],
                start=row["start"],
                end=row["end"],
                schema="OK" if row["schema_match"] else "FAIL",
                utc="OK" if row["utc_aligned"] else "FAIL",
                missing=row["missing_intervals"],
                gap_rate=float(row["gap_rate"]),
                sha=row["sha256"],
            )
        )

    lines.extend(["", "## Gap details", ""])
    for row in qc_rows:
        lines.append(f"### {row['file']}")
        gaps = row["gaps"]
        if not gaps:
            lines.append("")
            lines.append("No gaps > 1 expected period.")
            lines.append("")
            continue
        lines.extend(
            [
                "",
                "| prev UTC | next UTC | delta | missing intervals |",
                "|---|---|---:|---:|",
            ]
        )
        for gap in gaps:
            lines.append(
                f"| {gap['prev']} | {gap['next']} | {gap['delta']} | {gap['missing_intervals']} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Acceptance self-check",
            "",
            "- Schema matches existing reference files: "
            + ("PASS" if all(bool(row["schema_match"]) for row in qc_rows) else "FAIL"),
            "- UTC timestamp alignment: "
            + ("PASS" if all(bool(row["utc_aligned"]) for row in qc_rows) else "FAIL"),
            "- Gap rate < 1% or explained by gap list: "
            + ("PASS" if all(float(row["gap_rate"]) < 0.01 for row in qc_rows) else "REVIEW"),
            "- Original 9 MARK/FUNDING files unchanged vs DATA_HASHES_20260610.txt: "
            + ("PASS" if all(row["status"] == "OK" for row in old_hash_rows) else "FAIL"),
            "- New file hashes written to 06_RESEARCH/DATA/DATA_HASHES_20260611.txt: PASS",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true", help="Download and write expansion files.")
    parser.add_argument("--qc-only", action="store_true", help="Run QC/report/hash writing without download.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.download and args.qc_only:
        raise SystemExit("Use either --download or --qc-only, not both.")

    written_specs: list[FileSpec] = []
    if args.download:
        collected = download_jobs(build_jobs())
        funding_api_frames = {
            symbol: fetch_funding_api(symbol) for symbol in [*NEW_SYMBOLS, *EXISTING_SYMBOLS]
        }

        for symbol in NEW_SYMBOLS:
            mark_key = (symbol, "mark", "4h")
            funding_key = (symbol, "funding", "4h")
            mark = normalize_mark(collected[mark_key])
            funding_frames = collected[funding_key] + [funding_api_frames[symbol]]
            funding = normalize_funding(funding_frames)
            mark_path = FUTURES_DIR / f"{symbol}_MARK_4H.csv"
            funding_path = FUTURES_DIR / f"{symbol}_FUNDING_8H.csv"
            write_csv(mark, mark_path)
            write_csv(funding, funding_path)
            written_specs.extend(
                [
                    FileSpec(mark_path, "mark", "4h", 4, FUTURES_DIR / "BTCUSDT_MARK_4H.csv"),
                    FileSpec(funding_path, "funding", "8h", 8, FUTURES_DIR / "BTCUSDT_FUNDING_8H.csv"),
                ]
            )

        for symbol in EXISTING_SYMBOLS:
            for timeframe, hours in [("4h", 4), ("1h", 1)]:
                key = (symbol, "mark", timeframe)
                path = FUTURES_DIR / f"{symbol}_MARK_{timeframe.upper()}_2026H1.csv"
                write_csv(normalize_mark(collected[key]), path)
                written_specs.append(
                    FileSpec(
                        path,
                        "mark",
                        timeframe,
                        hours,
                        FUTURES_DIR / f"{symbol}_MARK_{timeframe.upper()}.csv",
                    )
                )

            path = FUTURES_DIR / f"{symbol}_FUNDING_8H_2026H1.csv"
            write_csv(normalize_funding([funding_api_frames[symbol]]), path)
            written_specs.append(
                FileSpec(path, "funding", "8h", 8, FUTURES_DIR / f"{symbol}_FUNDING_8H.csv")
            )
    else:
        for symbol in NEW_SYMBOLS:
            written_specs.extend(
                [
                    FileSpec(
                        FUTURES_DIR / f"{symbol}_MARK_4H.csv",
                        "mark",
                        "4h",
                        4,
                        FUTURES_DIR / "BTCUSDT_MARK_4H.csv",
                    ),
                    FileSpec(
                        FUTURES_DIR / f"{symbol}_FUNDING_8H.csv",
                        "funding",
                        "8h",
                        8,
                        FUTURES_DIR / "BTCUSDT_FUNDING_8H.csv",
                    ),
                ]
            )
        for symbol in EXISTING_SYMBOLS:
            written_specs.extend(
                [
                    FileSpec(
                        FUTURES_DIR / f"{symbol}_MARK_4H_2026H1.csv",
                        "mark",
                        "4h",
                        4,
                        FUTURES_DIR / f"{symbol}_MARK_4H.csv",
                    ),
                    FileSpec(
                        FUTURES_DIR / f"{symbol}_MARK_1H_2026H1.csv",
                        "mark",
                        "1h",
                        1,
                        FUTURES_DIR / f"{symbol}_MARK_1H.csv",
                    ),
                    FileSpec(
                        FUTURES_DIR / f"{symbol}_FUNDING_8H_2026H1.csv",
                        "funding",
                        "8h",
                        8,
                        FUTURES_DIR / f"{symbol}_FUNDING_8H.csv",
                    ),
                ]
            )

    old_hash_rows = verify_old_hashes()
    qc_rows = [qc_file(spec) for spec in written_specs]

    hash_lines = [
        f"{row['sha256']}  {row['file']}"
        for row in sorted(qc_rows, key=lambda item: str(item["file"]))
    ]
    NEW_HASH_PATH.write_text("\n".join(hash_lines) + "\n")
    REPORT_PATH.write_text(render_report(qc_rows, old_hash_rows))
    print(f"Wrote {len(qc_rows)} new data files/QC entries")
    print(f"Wrote {NEW_HASH_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {REPORT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
