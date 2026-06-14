"""Explicitly gated future runner for approved pre-holdout real data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from carry.config import EngineConfig
from carry.costs import CostModel
from carry.data import (
    DEFAULT_CUTOFF,
    assert_preholdout_path,
    load_symbol_data,
    normalize_cutoff,
)
from carry.metrics import (
    compute_metrics,
    moving_block_bootstrap_pvalue,
    three_way_walk_forward,
)
from carry.portfolio import DEFAULT_WEIGHTS, run_portfolio_comparison


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = (
    ROOT / "06_RESEARCH" / "CODE" / "output" / "carry_backtest_summary.json"
)


def authorization_errors(args: argparse.Namespace) -> list[str]:
    required = (
        ("confirm_prereg_approved", "blind review approval is not confirmed"),
        ("confirm_holdout_sealed", "custodian Holdout seal is not confirmed"),
        ("confirm_preholdout_only", "pre-holdout-only execution is not confirmed"),
    )
    return [
        message for attribute, message in required if not getattr(args, attribute)
    ]


def _load_oi_percentile(
    path: Path,
    *,
    cutoff: pd.Timestamp,
) -> pd.Series:
    path = assert_preholdout_path(path)
    frame = pd.read_csv(path, on_bad_lines="skip")
    time_col = next(
        (
            name
            for name in ("timestamp", "datetime", "ts", "time")
            if name in frame.columns
        ),
        None,
    )
    value_col = next(
        (
            name
            for name in (
                "d6h_rolling_pctl",
                "oi_percentile",
                "percentile",
            )
            if name in frame.columns
        ),
        None,
    )
    if time_col is None or value_col is None:
        raise ValueError(f"{path} missing OI timestamp/percentile columns")
    timestamp = pd.to_datetime(frame[time_col], utc=True, errors="coerce")
    value = pd.to_numeric(frame[value_col], errors="coerce")
    valid = timestamp.notna() & value.notna() & (timestamp < cutoff)
    series = pd.Series(
        value.loc[valid].to_numpy(dtype=float),
        index=pd.DatetimeIndex(timestamp.loc[valid]),
        name="oi_percentile",
    )
    return series[~series.index.duplicated(keep="last")].sort_index()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the approved pre-holdout carry comparison."
    )
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--btc-oi", type=Path, required=True)
    parser.add_argument("--eth-oi", type=Path, required=True)
    parser.add_argument("--cutoff", default=str(DEFAULT_CUTOFF))
    parser.add_argument("--base-notional", type=float, default=100_000.0)
    parser.add_argument("--leverage", type=float, default=2.0)
    parser.add_argument("--minimum-maintenance-rate", type=float, default=0.005)
    parser.add_argument("--event-slippage-rate", type=float, default=0.003)
    parser.add_argument("--bootstrap-block-size", type=int, default=9)
    parser.add_argument("--bootstrap-iterations", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260615)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--confirm-prereg-approved", action="store_true")
    parser.add_argument("--confirm-holdout-sealed", action="store_true")
    parser.add_argument("--confirm-preholdout-only", action="store_true")
    return parser


def _variant_payload(
    result,
    *,
    block_size: int,
    iterations: int,
    seed: int,
) -> dict[str, object]:
    equity = result.timeline.set_index("timestamp")["equity"]
    returns = equity.pct_change().dropna()
    payload: dict[str, object] = {
        "summary": result.summary,
        "metrics": compute_metrics(returns) if not returns.empty else None,
        "walk_forward": (
            three_way_walk_forward(returns) if len(returns) >= 3 else None
        ),
        "events": result.events.to_dict(orient="records"),
    }
    if len(returns) >= 2:
        payload["block_bootstrap"] = moving_block_bootstrap_pvalue(
            returns.to_numpy(),
            block_size=min(block_size, len(returns)),
            iterations=iterations,
            seed=seed,
        )
    else:
        payload["block_bootstrap"] = None
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    errors = authorization_errors(args)
    if errors:
        parser.error("; ".join(errors))

    cutoff = normalize_cutoff(args.cutoff)
    oi_paths = {"BTCUSDT": args.btc_oi, "ETHUSDT": args.eth_oi}
    loaded = {
        symbol: load_symbol_data(args.data_dir, symbol, cutoff=cutoff)
        for symbol in DEFAULT_WEIGHTS
    }
    inputs = {
        symbol: (
            loaded[symbol].mark,
            loaded[symbol].funding,
            _load_oi_percentile(oi_paths[symbol], cutoff=cutoff),
        )
        for symbol in DEFAULT_WEIGHTS
    }
    config = EngineConfig(
        base_notional=args.base_notional,
        leverage=args.leverage,
        minimum_maintenance_margin_rate=args.minimum_maintenance_rate,
        costs=CostModel(event_slippage_rate=args.event_slippage_rate),
    )
    comparison = run_portfolio_comparison(inputs, config=config)
    payload = {
        "cutoff_exclusive_utc": cutoff.isoformat(),
        "weights": DEFAULT_WEIGHTS,
        "data_audit": {
            symbol: item.audit for symbol, item in loaded.items()
        },
        "variants": {
            name: _variant_payload(
                result,
                block_size=args.bootstrap_block_size,
                iterations=args.bootstrap_iterations,
                seed=args.seed,
            )
            for name, result in comparison.items()
        },
        "acceptance_judgment": None,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
