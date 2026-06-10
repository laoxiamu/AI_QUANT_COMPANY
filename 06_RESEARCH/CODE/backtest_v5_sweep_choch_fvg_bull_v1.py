"""Backtest a pre-registered Sweep/CHoCH/FVG hypothesis."""

import argparse
from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "06_RESEARCH/DATA/FUTURES"
OUTPUT_DIR = PROJECT_ROOT / "06_RESEARCH/CODE/output"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
FEE_RATE = 0.001
SLIPPAGE_RATE = 0.001
TP1_FRACTION = 0.5
INITIAL_EQUITY = 1.0
HOLDOUT_FRACTION = 0.2
TIMEFRAME = "4H"
TIMEFRAME_HOURS = 4
EXPERIMENT = "v5_sweep_choch_fvg_bull_v1"


@dataclass
class SimulationResult:
    trades: pd.DataFrame
    equity: pd.Series
    candidate_count: int
    rejected_conflicts: int


def load_signal_module():
    path = PROJECT_ROOT / "06_RESEARCH/CODE/signal_detector.py"
    spec = importlib.util.spec_from_file_location("signal_detector", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_symbol(symbol: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    bars = pd.read_csv(
        DATA_DIR / f"{symbol}_MARK_{TIMEFRAME}.csv",
        parse_dates=["datetime"],
    )
    funding = pd.read_csv(
        DATA_DIR / f"{symbol}_FUNDING_8H.csv", parse_dates=["datetime"]
    )
    funding["datetime"] = funding["datetime"].dt.floor("s")
    funding["last_funding_rate"] = pd.to_numeric(
        funding["last_funding_rate"]
    )
    return bars, funding


def build_candidates(
    bars: pd.DataFrame, parameters: dict[str, int] | None = None
) -> pd.DataFrame:
    detector = load_signal_module()
    if parameters:
        detector.SWEEP_LOOKBACK = parameters.get(
            "sweep_lookback", detector.SWEEP_LOOKBACK
        )
        detector.SWING_LOOKBACK = parameters.get(
            "swing_lookback", detector.SWING_LOOKBACK
        )
        detector.SEQUENCE_WINDOW = parameters.get(
            "sequence_window", detector.SEQUENCE_WINDOW
        )
    base = detector.detect_base_signals(bars)
    signals = detector.detect_triple_signals(base)
    low_by_time = bars.set_index("datetime")["low"]
    signals["stop_loss"] = signals["sweep_time"].map(low_by_time)
    signals["risk"] = signals["entry_price"] - signals["stop_loss"]
    signals = signals[signals["risk"] > 0].copy()
    signals = (
        signals.sort_values(
            ["signal_time", "sweep_time"], ascending=[True, False]
        )
        .drop_duplicates("signal_time", keep="first")
        .reset_index(drop=True)
    )

    daily = (
        bars.set_index("datetime")["close"]
        .resample("1D")
        .last()
        .to_frame("daily_close")
    )
    daily["ema200"] = daily["daily_close"].ewm(
        span=200, adjust=False, min_periods=200
    ).mean()
    daily["bull_regime"] = (
        daily["daily_close"] > daily["ema200"]
    ).shift(1)
    signals["day"] = signals["signal_time"].dt.floor("D")
    signals = signals.join(daily["bull_regime"], on="day")
    return signals[signals["bull_regime"].eq(True)].reset_index(drop=True)


def funding_by_bar(
    bars: pd.DataFrame, funding: pd.DataFrame
) -> dict[pd.Timestamp, float]:
    valid_times = set(bars["datetime"])
    return {
        row.datetime: float(row.last_funding_rate)
        for row in funding.itertuples(index=False)
        if row.datetime in valid_times
    }


def simulate(
    bars: pd.DataFrame,
    funding: pd.DataFrame,
    candidates: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
    symbol: str,
) -> SimulationResult:
    period_bars = bars[
        (bars["datetime"] >= start) & (bars["datetime"] <= end)
    ].reset_index(drop=True)
    period_candidates = candidates[
        (candidates["signal_time"] >= start)
        & (candidates["signal_time"] <= end)
    ].copy()
    candidate_map = {
        row.signal_time: row for row in period_candidates.itertuples()
    }
    funding_map = funding_by_bar(period_bars, funding)

    balance = INITIAL_EQUITY
    units = 0.0
    entry_price = stop = tp1 = tp2 = 0.0
    entry_time = sweep_time = pd.NaT
    original_units = remaining_units = 0.0
    tp1_done = False
    funding_paid = 0.0
    entry_fee = 0.0
    exit_fees_paid = 0.0
    records: list[dict[str, object]] = []
    equity_points: list[tuple[pd.Timestamp, float]] = []
    rejected_conflicts = 0

    def close_units(
        quantity: float, reference_price: float
    ) -> tuple[float, float]:
        nonlocal balance, remaining_units
        execution_price = reference_price * (1 - SLIPPAGE_RATE)
        fee = quantity * execution_price * FEE_RATE
        pnl = quantity * (execution_price - entry_price)
        balance += pnl - fee
        remaining_units -= quantity
        return execution_price, fee

    for row in period_bars.itertuples(index=False):
        now = row.datetime
        had_position_at_bar_start = remaining_units > 0

        if remaining_units > 0 and now in funding_map and now > entry_time:
            payment = remaining_units * row.open * funding_map[now]
            balance -= payment
            funding_paid += payment

        exit_reason = None
        exit_price = np.nan
        exit_fee_total = 0.0
        if remaining_units > 0 and now > entry_time:
            if row.low <= stop:
                exit_price, fee = close_units(remaining_units, stop)
                exit_fee_total += fee
                exit_fees_paid += fee
                exit_reason = "STOP"
            else:
                if not tp1_done and row.high >= tp1:
                    exit_price, fee = close_units(
                        original_units * TP1_FRACTION, tp1
                    )
                    exit_fee_total += fee
                    exit_fees_paid += fee
                    tp1_done = True
                if remaining_units > 1e-15 and row.high >= tp2:
                    exit_price, fee = close_units(remaining_units, tp2)
                    exit_fee_total += fee
                    exit_fees_paid += fee
                    exit_reason = "TP2"

        if exit_reason is not None:
            start_equity = original_units * entry_price
            net_pnl = balance - trade_start_equity
            records.append(
                {
                    "symbol": symbol,
                    "entry_time": entry_time,
                    "exit_time": now,
                    "sweep_time": sweep_time,
                    "entry_price": entry_price,
                    "stop_loss": stop,
                    "tp1": tp1,
                    "tp2": tp2,
                    "exit_price": exit_price,
                    "exit_reason": exit_reason,
                    "tp1_hit": tp1_done,
                    "entry_fee": entry_fee,
                    "exit_fees": exit_fees_paid,
                    "funding_paid": funding_paid,
                    "net_pnl": net_pnl,
                    "net_return": net_pnl / trade_start_equity,
                    "initial_risk_pct": (entry_price - stop) / entry_price,
                    "net_r": (
                        (net_pnl / trade_start_equity)
                        / ((entry_price - stop) / entry_price)
                    ),
                    "holding_hours": (now - entry_time).total_seconds()
                    / 3600,
                }
            )
            units = original_units = remaining_units = 0.0

        candidate = candidate_map.get(now)
        if candidate is not None:
            if had_position_at_bar_start or remaining_units > 0:
                rejected_conflicts += 1
            else:
                trade_start_equity = balance
                raw_entry = float(candidate.entry_price)
                entry_price = raw_entry * (1 + SLIPPAGE_RATE)
                stop = float(candidate.stop_loss)
                risk = raw_entry - stop
                tp1 = raw_entry + risk
                tp2 = raw_entry + 2 * risk
                original_units = trade_start_equity / entry_price
                units = remaining_units = original_units
                entry_fee = original_units * entry_price * FEE_RATE
                balance -= entry_fee
                entry_time = now
                sweep_time = candidate.sweep_time
                tp1_done = False
                funding_paid = 0.0
                exit_fees_paid = 0.0

        marked_equity = balance
        if remaining_units > 0:
            marked_equity += remaining_units * (row.close - entry_price)
        equity_points.append((now, marked_equity))

    if remaining_units > 0:
        last = period_bars.iloc[-1]
        exit_price, exit_fee_total = close_units(
            remaining_units, float(last["close"])
        )
        exit_fees_paid += exit_fee_total
        net_pnl = balance - trade_start_equity
        records.append(
            {
                "symbol": symbol,
                "entry_time": entry_time,
                "exit_time": last["datetime"],
                "sweep_time": sweep_time,
                "entry_price": entry_price,
                "stop_loss": stop,
                "tp1": tp1,
                "tp2": tp2,
                "exit_price": exit_price,
                "exit_reason": "WINDOW_END",
                "tp1_hit": tp1_done,
                "entry_fee": entry_fee,
                "exit_fees": exit_fees_paid,
                "funding_paid": funding_paid,
                "net_pnl": net_pnl,
                "net_return": net_pnl / trade_start_equity,
                "initial_risk_pct": (entry_price - stop) / entry_price,
                "net_r": (
                    (net_pnl / trade_start_equity)
                    / ((entry_price - stop) / entry_price)
                ),
                "holding_hours": (
                    last["datetime"] - entry_time
                ).total_seconds()
                / 3600,
            }
        )
        equity_points[-1] = (last["datetime"], balance)

    trades = pd.DataFrame.from_records(records)
    equity = pd.Series(
        [value for _, value in equity_points],
        index=pd.DatetimeIndex([time for time, _ in equity_points]),
        name=symbol,
    )
    return SimulationResult(
        trades=trades,
        equity=equity,
        candidate_count=len(period_candidates),
        rejected_conflicts=rejected_conflicts,
    )


def metrics(equity: pd.Series, trades: pd.DataFrame) -> dict[str, float]:
    returns = equity.pct_change().replace([np.inf, -np.inf], np.nan).fillna(0)
    periods_per_year = 365.2425 * 24 / TIMEFRAME_HOURS
    std = returns.std(ddof=1)
    sharpe = (
        returns.mean() / std * np.sqrt(periods_per_year) if std > 0 else 0.0
    )
    drawdown = equity / equity.cummax() - 1
    expectancy = (
        trades["net_r"].mean() if not trades.empty else float("nan")
    )
    return {
        "final_equity": float(equity.iloc[-1]),
        "total_return": float(equity.iloc[-1] / equity.iloc[0] - 1),
        "sharpe": float(sharpe),
        "max_drawdown": float(drawdown.min()),
        "trade_count": int(len(trades)),
        "win_rate": float((trades["net_return"] > 0).mean())
        if not trades.empty
        else float("nan"),
        "expectancy_r": float(expectancy),
        "funding_paid": float(trades["funding_paid"].sum())
        if not trades.empty
        else 0.0,
    }


def combine_equity(curves: dict[str, pd.Series]) -> pd.Series:
    frame = pd.concat(curves.values(), axis=1, sort=False).sort_index().ffill()
    for column in frame:
        frame[column] = frame[column].fillna(INITIAL_EQUITY)
    return frame.mean(axis=1).rename("PORTFOLIO")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeframe", default="4H", choices=["1H", "4H"])
    parser.add_argument(
        "--experiment", default="v5_sweep_choch_fvg_bull_v1"
    )
    return parser.parse_args()


def main() -> None:
    global TIMEFRAME, TIMEFRAME_HOURS, EXPERIMENT
    args = parse_args()
    TIMEFRAME = args.timeframe.upper()
    TIMEFRAME_HOURS = int(TIMEFRAME.removesuffix("H"))
    EXPERIMENT = args.experiment
    bar_delta = pd.Timedelta(hours=TIMEFRAME_HOURS)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    datasets = {}
    holdout_starts = {}
    for symbol in SYMBOLS:
        full_bars, full_funding = load_symbol(symbol)
        holdout_index = int(len(full_bars) * (1 - HOLDOUT_FRACTION))
        holdout_start = full_bars["datetime"].iloc[holdout_index]
        holdout_starts[symbol] = holdout_start
        bars = full_bars[full_bars["datetime"] < holdout_start].copy()
        funding = full_funding[
            full_funding["datetime"] < holdout_start
        ].copy()
        candidates = build_candidates(bars)
        datasets[symbol] = (bars, funding, candidates)

    global_end = min(holdout_starts.values()) - bar_delta
    global_start = max(
        data[0]["datetime"].iloc[0] for data in datasets.values()
    )
    common_bars = datasets["SOLUSDT"][0]
    common_bars = common_bars[
        (common_bars["datetime"] >= global_start)
        & (common_bars["datetime"] <= global_end)
    ]
    split_times = [
        common_bars["datetime"].iloc[int(len(common_bars) * fraction)]
        for fraction in (0.625, 0.75, 0.875)
    ]
    split_times.append(global_end + bar_delta)

    full_results = {}
    all_trades = []
    curves = {}
    for symbol, (bars, funding, candidates) in datasets.items():
        result = simulate(
            bars, funding, candidates, global_start, global_end, symbol
        )
        local_bars = bars[
            (bars["datetime"] >= global_start)
            & (bars["datetime"] <= global_end)
        ]
        local_split_index = int(len(local_bars) * 0.75)
        local_validation_start = local_bars["datetime"].iloc[
            local_split_index
        ]
        local_train_end = local_validation_start - bar_delta
        train_result = simulate(
            bars,
            funding,
            candidates,
            global_start,
            local_train_end,
            symbol,
        )
        validation_result = simulate(
            bars,
            funding,
            candidates,
            local_validation_start,
            global_end,
            symbol,
        )
        full_results[symbol] = {
            "candidate_count": result.candidate_count,
            "rejected_conflicts": result.rejected_conflicts,
            **metrics(result.equity, result.trades),
            "train": {
                "start": str(global_start),
                "end": str(local_train_end),
                "candidate_count": train_result.candidate_count,
                **metrics(train_result.equity, train_result.trades),
            },
            "validation": {
                "start": str(local_validation_start),
                "end": str(global_end),
                "candidate_count": validation_result.candidate_count,
                **metrics(
                    validation_result.equity, validation_result.trades
                ),
            },
        }
        all_trades.append(result.trades)
        curves[symbol] = result.equity
        result.trades.to_csv(
            OUTPUT_DIR / f"trades_{symbol}_{EXPERIMENT}.csv",
            index=False,
        )

    portfolio_equity = combine_equity(curves)
    combined_trades = pd.concat(all_trades, ignore_index=True)
    portfolio_metrics = metrics(portfolio_equity, combined_trades)
    portfolio_equity.to_csv(
        OUTPUT_DIR / f"equity_{EXPERIMENT}.csv",
        header=True,
    )

    common_validation_start = common_bars["datetime"].iloc[
        int(len(common_bars) * 0.75)
    ]
    common_train_end = common_validation_start - bar_delta
    portfolio_split_metrics = {}
    for period_name, period_start, period_end in (
        ("train", global_start, common_train_end),
        ("validation", common_validation_start, global_end),
    ):
        period_curves = {}
        period_trades = []
        period_candidates = 0
        for symbol, (bars, funding, candidates) in datasets.items():
            result = simulate(
                bars,
                funding,
                candidates,
                period_start,
                period_end,
                symbol,
            )
            period_curves[symbol] = result.equity
            period_trades.append(result.trades)
            period_candidates += result.candidate_count
        period_equity = combine_equity(period_curves)
        period_trade_frame = pd.concat(period_trades, ignore_index=True)
        portfolio_split_metrics[period_name] = {
            "start": str(period_start),
            "end": str(period_end),
            "candidate_count": period_candidates,
            **metrics(period_equity, period_trade_frame),
        }

    walk_forward = []
    for window_number in range(3):
        start = split_times[window_number]
        end = split_times[window_number + 1] - bar_delta
        window_curves = {}
        window_trades = []
        candidate_count = 0
        for symbol, (bars, funding, candidates) in datasets.items():
            result = simulate(bars, funding, candidates, start, end, symbol)
            window_curves[symbol] = result.equity
            window_trades.append(result.trades)
            candidate_count += result.candidate_count
        window_equity = combine_equity(window_curves)
        window_trade_frame = pd.concat(window_trades, ignore_index=True)
        walk_forward.append(
            {
                "window": window_number + 1,
                "train_start": str(global_start),
                "train_end": str(start - pd.Timedelta(hours=4)),
                "validation_start": str(start),
                "validation_end": str(end),
                "candidate_count": candidate_count,
                **metrics(window_equity, window_trade_frame),
            }
        )

    sensitivity_definitions = {
        "sweep_lookback_16": {"sweep_lookback": 16},
        "sweep_lookback_24": {"sweep_lookback": 24},
        "swing_lookback_8": {"swing_lookback": 8},
        "swing_lookback_12": {"swing_lookback": 12},
        "sequence_window_16": {"sequence_window": 16},
        "sequence_window_24": {"sequence_window": 24},
    }
    sensitivity = {}
    for name, parameters in sensitivity_definitions.items():
        variant_curves = {}
        variant_trades = []
        variant_candidates = 0
        for symbol, (bars, funding, _) in datasets.items():
            candidates = build_candidates(bars, parameters)
            result = simulate(
                bars,
                funding,
                candidates,
                global_start,
                global_end,
                symbol,
            )
            variant_curves[symbol] = result.equity
            variant_trades.append(result.trades)
            variant_candidates += result.candidate_count
        variant_equity = combine_equity(variant_curves)
        variant_trade_frame = pd.concat(variant_trades, ignore_index=True)
        sensitivity[name] = {
            "parameters": parameters,
            "candidate_count": variant_candidates,
            **metrics(variant_equity, variant_trade_frame),
        }

    output = {
        "experiment": EXPERIMENT,
        "timeframe": TIMEFRAME,
        "holdout_returns_accessed": False,
        "formal_signal_generation_truncated_before_holdout": True,
        "data_start": str(global_start),
        "analysis_end": str(global_end),
        "holdout_starts": {
            key: str(value) for key, value in holdout_starts.items()
        },
        "symbol_metrics": full_results,
        "portfolio_metrics": portfolio_metrics,
        "portfolio_train_validation": portfolio_split_metrics,
        "walk_forward": walk_forward,
        "sensitivity": sensitivity,
    }
    with open(
        OUTPUT_DIR / f"metrics_{EXPERIMENT}.json",
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
