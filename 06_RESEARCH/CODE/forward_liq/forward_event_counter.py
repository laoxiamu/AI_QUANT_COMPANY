#!/usr/bin/env python3
"""Count forward liquidation pulse candidates without computing returns."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Literal

import pandas as pd

try:
    from .liq_parser import OUTPUT_COLUMNS, ParseReport, empty_liquidation_frame, parse_jsonl
except ImportError:  # Direct script execution.
    from liq_parser import OUTPUT_COLUMNS, ParseReport, empty_liquidation_frame, parse_jsonl


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REPORT_PATH = PROJECT_ROOT / "06_RESEARCH/RESULTS/A1_FORWARD_EVENT_COUNT.md"
TARGET_SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
CountMode = Literal["episode_start", "all_hits"]


@dataclass(frozen=True)
class CounterConfig:
    """Placeholder readiness-counter parameters, not preregistered values."""

    window: str = "1h"
    quantile: float = 0.99
    min_history: int = 24
    n_min: int = 120
    count_mode: CountMode = "episode_start"

    def validate(self) -> None:
        window_delta = pd.Timedelta(self.window)
        if window_delta <= pd.Timedelta(0):
            raise ValueError("window must be positive")
        if not 0.0 <= self.quantile <= 1.0:
            raise ValueError("quantile must be in [0, 1]")
        if self.min_history < 1:
            raise ValueError("min_history must be >= 1")
        if self.n_min < 1:
            raise ValueError("n_min must be >= 1")
        if self.count_mode not in {"episode_start", "all_hits"}:
            raise ValueError(f"unsupported count_mode: {self.count_mode}")


@dataclass
class CounterResult:
    signals: pd.DataFrame
    events: pd.DataFrame
    monthly_counts: pd.DataFrame
    symbol_summary: pd.DataFrame
    overall_summary: dict[str, object]


def discover_jsonl_files(inputs: Iterable[str | Path], pattern: str = "*.jsonl") -> list[Path]:
    """Resolve files and recursively scan directories in deterministic order."""
    discovered: set[Path] = set()
    for raw_path in inputs:
        path = Path(raw_path)
        if path.is_file():
            discovered.add(path.resolve())
        elif path.is_dir():
            discovered.update(candidate.resolve() for candidate in path.rglob(pattern) if candidate.is_file())
        else:
            raise FileNotFoundError(f"input path not found: {path}")
    return sorted(discovered)


def parse_files(paths: Iterable[Path]) -> tuple[pd.DataFrame, list[ParseReport], int]:
    """Parse files and remove exact payload duplicates spanning file boundaries."""
    frames: list[pd.DataFrame] = []
    reports: list[ParseReport] = []
    for path in paths:
        frame, report = parse_jsonl(path)
        with_hash = frame.copy()
        with_hash["_payload_sha256"] = frame.attrs.get("payload_sha256", [])
        frames.append(with_hash)
        reports.append(report)

    if not frames:
        return empty_liquidation_frame(), reports, 0

    combined = pd.concat(frames, ignore_index=True)
    before = len(combined)
    combined = combined.drop_duplicates(subset=["_payload_sha256"], keep="first")
    cross_file_duplicates = before - len(combined)
    combined = combined.drop(columns="_payload_sha256")
    combined = combined.sort_values(["ts_utc", "symbol", "side"], kind="stable").reset_index(drop=True)
    return combined, reports, cross_file_duplicates


def _validate_frame(frame: pd.DataFrame) -> pd.DataFrame:
    missing = set(OUTPUT_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"liquidation frame missing columns: {sorted(missing)}")

    normalized = frame.loc[:, OUTPUT_COLUMNS].copy()
    normalized["ts_utc"] = pd.to_datetime(normalized["ts_utc"], utc=True, errors="raise")
    normalized["symbol"] = normalized["symbol"].astype("string").str.upper()
    normalized["side"] = normalized["side"].astype("string").str.upper()
    normalized["notional_usdt"] = pd.to_numeric(normalized["notional_usdt"], errors="raise")
    if (~normalized["side"].isin(["SELL", "BUY"])).any():
        raise ValueError("side must be SELL or BUY")
    if (~normalized["notional_usdt"].map(math.isfinite)).any() or (normalized["notional_usdt"] <= 0).any():
        raise ValueError("notional_usdt must be finite and positive")
    return normalized.sort_values(["symbol", "ts_utc"], kind="stable").reset_index(drop=True)


def compute_candidate_events(frame: pd.DataFrame, config: CounterConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute no-lookahead SELL pulse candidates for target symbols."""
    config.validate()
    normalized = _validate_frame(frame)
    sell = normalized.loc[
        normalized["symbol"].isin(TARGET_SYMBOLS) & normalized["side"].eq("SELL")
    ].copy()

    signal_columns = [
        *OUTPUT_COLUMNS,
        "rolling_sell_notional",
        "historical_quantile",
        "qualifies",
        "is_candidate",
    ]
    if sell.empty:
        empty = pd.DataFrame(columns=signal_columns)
        return empty, empty.copy()

    window_delta = pd.Timedelta(config.window)
    symbol_frames: list[pd.DataFrame] = []
    for symbol, group in sell.groupby("symbol", sort=True):
        group = group.sort_values("ts_utc", kind="stable").reset_index(drop=True)
        indexed_notional = group.set_index("ts_utc")["notional_usdt"]
        rolling_sum = indexed_notional.rolling(config.window, closed="right").sum().to_numpy()
        rolling_series = pd.Series(rolling_sum, index=group.index, dtype="float64")

        # Shift first: the threshold at t is estimated only from rolling sums before t.
        historical_quantile = (
            rolling_series.shift(1)
            .expanding(min_periods=config.min_history)
            .quantile(config.quantile)
        )
        qualifies = historical_quantile.notna() & rolling_series.ge(historical_quantile)

        if config.count_mode == "all_hits":
            is_candidate = qualifies
        else:
            prior_qualifies = qualifies.shift(1, fill_value=False)
            gap_resets_pulse = group["ts_utc"].diff().ge(window_delta).fillna(True)
            is_candidate = qualifies & (~prior_qualifies | gap_resets_pulse)

        group["rolling_sell_notional"] = rolling_series
        group["historical_quantile"] = historical_quantile
        group["qualifies"] = qualifies.astype(bool)
        group["is_candidate"] = is_candidate.astype(bool)
        symbol_frames.append(group)

    signals = pd.concat(symbol_frames, ignore_index=True)
    signals = signals.loc[:, signal_columns].sort_values(["ts_utc", "symbol"], kind="stable")
    signals = signals.reset_index(drop=True)
    events = signals.loc[signals["is_candidate"]].copy().reset_index(drop=True)
    return signals, events


def _month_grid(observed: pd.DataFrame) -> pd.DataFrame:
    if observed.empty:
        return pd.DataFrame(columns=["symbol", "month_utc"])
    start = observed["ts_utc"].min().strftime("%Y-%m")
    end = observed["ts_utc"].max().strftime("%Y-%m")
    months = [str(period) for period in pd.period_range(start, end, freq="M")]
    return pd.MultiIndex.from_product(
        [TARGET_SYMBOLS, months],
        names=["symbol", "month_utc"],
    ).to_frame(index=False)


def _project_target_date(
    events: pd.DataFrame,
    observed: pd.DataFrame,
    n_min: int,
) -> tuple[float | None, str | None]:
    total = len(events)
    if total >= n_min:
        reached_at = events.sort_values("ts_utc").iloc[n_min - 1]["ts_utc"]
        return None, reached_at.strftime("%Y-%m-%d")
    if total == 0 or observed.empty:
        return None, None

    start = observed["ts_utc"].min()
    end = observed["ts_utc"].max()
    elapsed_days = (end - start).total_seconds() / 86_400
    if elapsed_days <= 0:
        return None, None

    rate = total / elapsed_days
    days_needed = math.ceil((n_min - total) / rate)
    projected = end + pd.Timedelta(days=days_needed)
    return rate, projected.strftime("%Y-%m-%d")


def summarize_counts(
    frame: pd.DataFrame,
    signals: pd.DataFrame,
    events: pd.DataFrame,
    config: CounterConfig,
) -> CounterResult:
    """Build monthly, symbol, and pooled readiness summaries."""
    observed = _validate_frame(frame)
    observed = observed.loc[observed["symbol"].isin(TARGET_SYMBOLS)].copy()

    month_grid = _month_grid(observed)
    if events.empty:
        event_monthly = pd.DataFrame(columns=["symbol", "month_utc", "candidate_events"])
    else:
        event_monthly = events.assign(month_utc=events["ts_utc"].dt.strftime("%Y-%m"))
        event_monthly = (
            event_monthly.groupby(["symbol", "month_utc"], as_index=False)
            .size()
            .rename(columns={"size": "candidate_events"})
        )
    monthly = month_grid.merge(event_monthly, on=["symbol", "month_utc"], how="left")
    if not monthly.empty:
        monthly["candidate_events"] = monthly["candidate_events"].fillna(0).astype(int)
        monthly = monthly.sort_values(["month_utc", "symbol"]).reset_index(drop=True)

    summary_rows: list[dict[str, object]] = []
    for symbol in TARGET_SYMBOLS:
        symbol_events = events.loc[events["symbol"].eq(symbol)].sort_values("ts_utc")
        summary_rows.append(
            {
                "symbol": symbol,
                "cumulative_n": len(symbol_events),
                "first_candidate_utc": (
                    symbol_events["ts_utc"].min().strftime("%Y-%m-%d %H:%M:%S")
                    if not symbol_events.empty
                    else None
                ),
                "last_candidate_utc": (
                    symbol_events["ts_utc"].max().strftime("%Y-%m-%d %H:%M:%S")
                    if not symbol_events.empty
                    else None
                ),
            }
        )
    symbol_summary = pd.DataFrame(summary_rows)

    event_rate, projected_date = _project_target_date(events, observed, config.n_min)
    overall = {
        "cumulative_n": len(events),
        "n_min": config.n_min,
        "remaining_n": max(config.n_min - len(events), 0),
        "first_candidate_utc": (
            events["ts_utc"].min().strftime("%Y-%m-%d %H:%M:%S") if not events.empty else None
        ),
        "last_candidate_utc": (
            events["ts_utc"].max().strftime("%Y-%m-%d %H:%M:%S") if not events.empty else None
        ),
        "observed_start_utc": (
            observed["ts_utc"].min().strftime("%Y-%m-%d %H:%M:%S") if not observed.empty else None
        ),
        "observed_end_utc": (
            observed["ts_utc"].max().strftime("%Y-%m-%d %H:%M:%S") if not observed.empty else None
        ),
        "event_rate_per_elapsed_day": event_rate,
        "projected_target_date": projected_date,
        "gate_status": "READY" if len(events) >= config.n_min else "NOT_READY",
    }
    return CounterResult(signals, events, monthly, symbol_summary, overall)


def run_counter(frame: pd.DataFrame, config: CounterConfig) -> CounterResult:
    signals, events = compute_candidate_events(frame, config)
    return summarize_counts(frame, signals, events, config)


def _display(value: object) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "N/A"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    columns = list(frame.columns)
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    rows = [
        "| " + " | ".join(_display(value) for value in row) + " |"
        for row in frame.itertuples(index=False, name=None)
    ]
    return "\n".join([header, separator, *rows])


def render_report(
    result: CounterResult,
    config: CounterConfig,
    input_files: list[Path],
    parse_reports: list[ParseReport],
    cross_file_duplicates: int,
) -> str:
    """Render the readiness monitor; it intentionally contains no returns."""
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    parser_totals = {
        "files": len(parse_reports),
        "total_lines": sum(report.total_lines for report in parse_reports),
        "parsed_rows": sum(report.parsed_rows for report in parse_reports),
        "bad_lines": sum(report.bad_lines for report in parse_reports),
        "duplicate_lines": sum(report.duplicate_lines for report in parse_reports),
        "cross_file_duplicates": cross_file_duplicates,
    }
    parser_totals["bad_line_ratio"] = (
        parser_totals["bad_lines"] / parser_totals["total_lines"]
        if parser_totals["total_lines"]
        else 0.0
    )

    overall = result.overall_summary
    real_data_status = "NO INPUT JSONL FOUND" if not input_files else "INPUT JSONL PROCESSED"
    return f"""# A1 Forward Liquidation Event Count

**Generated UTC:** {generated_at}  
**Data status:** {real_data_status}  
**Readiness gate:** {overall["gate_status"]}

## Governance

This is a count-only monitoring artifact. It computes no event-forward returns,
performance metrics, or edge conclusion. All trigger parameters below are
placeholders and must be frozen only by the formal Path B preregistration.

## Placeholder Parameters

| parameter | value |
| --- | --- |
| symbols | {", ".join(TARGET_SYMBOLS)} |
| rolling SELL window | {config.window} |
| historical quantile | {config.quantile} |
| minimum prior rolling observations | {config.min_history} |
| count mode | {config.count_mode} |
| readiness target n_min | {config.n_min} |

The historical quantile at time `t` uses only rolling sums strictly before `t`.
`episode_start` counts the first exceedance in a continuous pulse; a gap of at
least one rolling window resets the pulse.

## Pooled Readiness

| metric | value |
| --- | --- |
| cumulative n | {_display(overall["cumulative_n"])} |
| target n_min | {_display(overall["n_min"])} |
| remaining n | {_display(overall["remaining_n"])} |
| first candidate UTC | {_display(overall["first_candidate_utc"])} |
| last candidate UTC | {_display(overall["last_candidate_utc"])} |
| observed start UTC | {_display(overall["observed_start_utc"])} |
| observed end UTC | {_display(overall["observed_end_utc"])} |
| event rate / elapsed day | {_display(overall["event_rate_per_elapsed_day"])} |
| projected target date | {_display(overall["projected_target_date"])} |

Projection is a linear extrapolation from elapsed calendar coverage and is
unavailable until at least one candidate exists across a positive time span.
It does not adjust for collector downtime or changing market regimes.

## By Symbol

{_markdown_table(result.symbol_summary)}

## By Symbol And UTC Month

{_markdown_table(result.monthly_counts)}

## Parser Audit

```json
{json.dumps(parser_totals, ensure_ascii=False, indent=2)}
```
"""


def write_report(
    result: CounterResult,
    config: CounterConfig,
    input_files: list[Path],
    parse_reports: list[ParseReport],
    cross_file_duplicates: int,
    output_path: str | Path = DEFAULT_REPORT_PATH,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_report(result, config, input_files, parse_reports, cross_file_duplicates),
        encoding="utf-8",
    )
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="JSONL files or directories.")
    parser.add_argument("--pattern", default="*.jsonl", help="Recursive directory glob.")
    parser.add_argument("--window", default="1h")
    parser.add_argument("--quantile", type=float, default=0.99)
    parser.add_argument("--min-history", type=int, default=24)
    parser.add_argument("--n-min", type=int, default=120)
    parser.add_argument(
        "--count-mode",
        choices=["episode_start", "all_hits"],
        default="episode_start",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = CounterConfig(
        window=args.window,
        quantile=args.quantile,
        min_history=args.min_history,
        n_min=args.n_min,
        count_mode=args.count_mode,
    )
    config.validate()
    input_files = discover_jsonl_files(args.inputs, pattern=args.pattern)
    frame, parse_reports, cross_file_duplicates = parse_files(input_files)
    result = run_counter(frame, config)
    output_path = write_report(
        result,
        config,
        input_files,
        parse_reports,
        cross_file_duplicates,
        args.output,
    )
    print(
        json.dumps(
            {
                "input_files": len(input_files),
                "parsed_rows": len(frame),
                "candidate_events": len(result.events),
                "gate_status": result.overall_summary["gate_status"],
                "output": str(output_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
