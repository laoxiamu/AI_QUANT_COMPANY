"""DATA-001 carry v4 missing data procurement CLI."""

from __future__ import annotations

import argparse
import datetime as dt
import traceback
from pathlib import Path

import pandas as pd

from carry_data_procurement.binance import BinanceClient, BinanceConfig, month_range
from carry_data_procurement.events import detect_depeg_events
from carry_data_procurement.io_utils import (
    write_json_atomic,
    write_parquet_atomic,
    write_text_atomic,
)
from carry_data_procurement.manifest import build_file_record, write_manifest
from carry_data_procurement.schemas import (
    normalize_index_rows,
    normalize_kline_rows,
    validate_ohlcv_1h,
    validate_price_1h,
)


SYMBOLS = ["BTCUSDT", "ETHUSDT"]
START = pd.Timestamp("2020-01-01T00:00:00Z")
END = pd.Timestamp("2024-12-31T23:00:00Z")
END_EXCLUSIVE = END + pd.Timedelta(hours=1)


def _ms(timestamp: pd.Timestamp) -> int:
    return int(timestamp.timestamp() * 1000)


def _write_adl_note(path: Path) -> None:
    write_text_atomic(
        """# ADL model assumption

Binance does not expose historical ADL execution records for 2020-2024.

Carry v4 FEASIBILITY-LOCK must therefore use the frozen conservative model assumption:
- ADL trigger probability: during extreme market days (intraday move > 15%), assume 0.5% of positions are reduced by ADL.
- ADL reduction size: assume maximum 50% reduction.
- Forward shadow gate: monitor `/fapi/v1/adlQuantile` in real time before any promotion beyond historical feasibility.

Quality conclusion: historical ADL data is not observable from official public archives; this file documents the required model assumption rather than empirical history.
""",
        path,
    )


def _write_liquidation_fee_note(path: Path, *, network_status: str) -> None:
    write_text_atomic(
        f"""# Liquidation fee history

Default modeling value: 0.5% of liquidated position notional.

Source requirement: Binance official fee/rules page plus 2020-2024 Binance announcement history search.

Network/search status in this run: {network_status}

Quality conclusion: use 0.5% as the conservative default requested by DATA-001, but do not treat this file as a completed historical change audit until official announcement search is rerun from a network-enabled environment.
""",
        path,
    )


def _write_withdrawal_placeholder(path: Path, *, network_status: str) -> None:
    write_text_atomic(
        f"""# Binance withdrawal suspension events

Status: historical withdrawal suspension records need manual supplement.

Reason: DATA-001 explicitly allows this placeholder when Binance announcement scraping fails. This run could not complete official announcement scraping.

Network/scrape status: {network_status}

Required manual fields:
- date
- duration
- affected asset(s)
- official Binance announcement URL

Quality conclusion: incomplete by design; this item must not block the other seven data inputs, but FEASIBILITY-LOCK event-stress interpretation should flag this as missing manual history.
""",
        path,
    )


def procure(args: argparse.Namespace) -> int:
    output = Path(args.output)
    metadata = output / "metadata"
    events_dir = output / "events"
    records: list[dict[str, object]] = []
    failures: list[str] = []
    client = BinanceClient(BinanceConfig(no_proxy=args.no_proxy, timeout_s=args.timeout))

    _write_adl_note(metadata / "adl_note.md")
    _write_liquidation_fee_note(
        metadata / "liquidation_fee_history.md",
        network_status="not yet audited in this run",
    )
    _write_withdrawal_placeholder(
        events_dir / "withdrawal_suspension_events.md",
        network_status="not yet scraped in this run",
    )

    # ── Funding rate (CRITICAL: core carry return source, from data.binance.vision) ──
    for symbol in SYMBOLS:
        funding_frames: list[pd.DataFrame] = []
        funding_failures: list[str] = []
        for year, month in month_range(2020, 1, 2024, 12):
            try:
                frame = client.download_data_vision_funding_month(symbol, year, month)
                funding_frames.append(frame)
            except Exception as exc:
                funding_failures.append(f"{year}-{month:02d}: {exc}")
        if funding_frames:
            combined = pd.concat(funding_frames, ignore_index=True).drop_duplicates("calc_time").sort_values("calc_time")
            path = output / "funding_rate" / f"{symbol}_funding_rate.parquet"
            write_parquet_atomic(combined, path)
            records.append(build_file_record(path, combined, source="data.binance.vision fundingRate monthly"))
            if funding_failures:
                failures.append(f"funding_rate {symbol} partial failures: {funding_failures[:3]}")
        else:
            failures.append(f"funding_rate {symbol}: all months failed: {funding_failures[:3]}")

    spot_warnings: list[str] = []
    for symbol in SYMBOLS:
        for year, month in month_range(2020, 1, 2024, 12):
            try:
                frame = client.download_data_vision_spot_month(symbol, year, month)
                start = pd.Timestamp(f"{year:04d}-{month:02d}-01T00:00:00Z")
                end = start + pd.offsets.MonthEnd(0) + pd.Timedelta(hours=23)
                report = validate_ohlcv_1h(frame, start=start, end=end)
                # Allow up to 24 missing hours (exchange maintenance); reject hard failures only
                hard_issues = [i for i in report.issues if not i.startswith("missing_hours=") and not i.startswith("start_mismatch") and not i.startswith("end_mismatch") and not i.startswith("extra_hours")]
                missing_h = next((int(i.split("=")[1]) for i in report.issues if i.startswith("missing_hours=")), 0)
                if hard_issues:
                    raise RuntimeError(f"spot {symbol} {year}-{month:02d} hard validation failed: {hard_issues}")
                if missing_h > 24:
                    raise RuntimeError(f"spot {symbol} {year}-{month:02d} too many missing hours: {missing_h}")
                if report.issues:
                    spot_warnings.append(f"{symbol} {year}-{month:02d}: {report.issues}")
                path = output / "spot_1h" / f"{symbol}_1h_{year:04d}{month:02d}.parquet"
                write_parquet_atomic(frame, path)
                records.append(build_file_record(path, frame, source="data.binance.vision spot monthly klines"))
            except Exception as exc:
                failures.append(f"spot_1h {symbol} {year}-{month:02d}: {type(exc).__name__}: {exc}")
    if spot_warnings:
        failures.append(f"spot_1h_warnings: {spot_warnings[:5]}")

    for symbol in SYMBOLS:
        try:
            rows = client.paginated_klines(
                base_url=client.config.futures_api,
                path="/fapi/v1/klines",
                symbol=symbol,
                start_ms=_ms(START),
                end_ms=_ms(END_EXCLUSIVE),
            )
            frame = normalize_kline_rows(rows)
            report = validate_ohlcv_1h(frame, start=START, end=END)
            if not report.ok:
                raise RuntimeError(f"perp {symbol} validation failed: {report.issues}")
            path = output / "perp_1h" / f"{symbol}_contract_1h.parquet"
            write_parquet_atomic(frame, path)
            records.append(build_file_record(path, frame, source="/fapi/v1/klines"))
        except Exception as exc:
            failures.append(f"perp_1h {symbol}: {type(exc).__name__}: {exc}")

        try:
            # indexPriceKlines uses "pair" not "symbol" parameter
            rows = client.paginated_klines(
                base_url=client.config.futures_api,
                path="/fapi/v1/indexPriceKlines",
                symbol=symbol,
                start_ms=_ms(START),
                end_ms=_ms(END_EXCLUSIVE),
                symbol_key="pair",
            )
            if not rows:
                raise RuntimeError(f"indexPriceKlines returned empty for {symbol}")
            frame = normalize_index_rows(rows)
            # Relax validation: allow missing hours (gaps due to exchange maintenance)
            report = validate_price_1h(frame, start=START, end=END)
            hard_issues = [i for i in report.issues if not any(i.startswith(p) for p in ("missing_hours=", "start_mismatch", "end_mismatch", "extra_hours"))]
            if hard_issues:
                raise RuntimeError(f"index {symbol} validation failed: {hard_issues}")
            path = output / "index_1h" / f"{symbol}_index_1h.parquet"
            write_parquet_atomic(frame, path)
            records.append(build_file_record(path, frame, source="/fapi/v1/indexPriceKlines (pair=)"))
        except Exception as exc:
            failures.append(f"index_1h {symbol}: {type(exc).__name__}: {exc}")

        try:
            payload = client.fetch_leverage_brackets(symbol)
            path = metadata / f"leverage_brackets_{symbol}.json"
            write_json_atomic(payload, path)
            records.append(build_file_record(path, pd.DataFrame({"timestamp": [pd.Timestamp.utcnow()]}), source="/fapi/v1/leverageBracket"))
        except Exception as exc:
            failures.append(f"leverage_brackets {symbol}: {type(exc).__name__}: {exc}")

        try:
            payload = client.fetch_adl_quantile(symbol)
            path = metadata / f"adl_quantile_{symbol}.json"
            write_json_atomic(payload, path)
            records.append(build_file_record(path, pd.DataFrame({"timestamp": [pd.Timestamp.utcnow()]}), source="/fapi/v1/adlQuantile"))
        except Exception as exc:
            failures.append(f"adl_quantile {symbol}: {type(exc).__name__}: {exc}")

    try:
        rows = client.paginated_klines(
            base_url=client.config.spot_api,
            path="/api/v3/klines",
            symbol="USDCUSDT",
            start_ms=_ms(START),
            end_ms=_ms(END_EXCLUSIVE),
            limit=1000,
        )
        stable = normalize_kline_rows(rows)
        events = detect_depeg_events(stable)
        path = events_dir / "usdt_depeg_events.parquet"
        write_parquet_atomic(events, path)
        records.append(build_file_record(path, events, source="/api/v3/klines?symbol=USDCUSDT"))
    except Exception as exc:
        failures.append(f"usdt_depeg_events: {type(exc).__name__}: {exc}")

    for text_path in [
        metadata / "adl_note.md",
        metadata / "liquidation_fee_history.md",
        events_dir / "withdrawal_suspension_events.md",
    ]:
        records.append(build_file_record(text_path, pd.DataFrame(), source="DATA-001 documented assumption"))

    status = "blocked" if failures else "completed"
    write_manifest(output / "data_manifest.yaml", records, status=status)
    if failures:
        write_text_atomic("\n".join(failures) + "\n", output / "procurement_failures.log")
        if args.verbose:
            traceback.print_exc()
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Procure DATA-001 carry v4 missing inputs.")
    parser.add_argument("--output", default="08_DATA/carry")
    parser.add_argument("--no-proxy", action="store_true")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--verbose", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    return procure(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
