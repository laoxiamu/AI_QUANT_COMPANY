#!/usr/bin/env python3
"""P1-05 two-axis market-regime attribution for existing signals."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp

from p1_04_tsmom_regime_long import (
    ADX_ENTRY,
    ADX_EXIT,
    ADX_PERIOD,
    calculate_adx,
    hysteresis_regime,
)
from v4_strategy_backtest import INITIAL_CAPITAL, SYMBOL_CONFIG, SYMBOL_ORDER


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "06_RESEARCH" / "CODE" / "output"
RESULT_PATH = OUTPUT / "p1_05_regime_attribution.json"
ER_PERIOD = 60
ER_THRESHOLD = 0.50
BULL_MA_DAYS = 200
ALMOST_ALL_THRESHOLD = 0.80

TRADE_FILES = {
    "TSMOM_v1": OUTPUT / "p1_01_tsmom_trades.csv",
    "TSMOM_v2": OUTPUT / "p1_02_tsmom_voltarget_trades.csv",
    "P1_04_regime_long": OUTPUT / "p1_04_tsmom_regime_long_trades.csv",
}
SWEEP_FILES = {
    "Sweep_v3_unfiltered": OUTPUT / "events_v5_sweep_only_bull_v3.csv",
    "Sweep_v4_bull_regime": OUTPUT / "events_v5_sweep_regime_bull_v4.csv",
}


def efficiency_ratio(close: pd.Series, period: int = ER_PERIOD) -> pd.Series:
    direction = (close - close.shift(period)).abs()
    volatility = close.diff().abs().rolling(period).sum()
    return direction / volatility.replace(0, np.nan)


def prior_daily_bull_state(
    datetimes: pd.Series,
    close: pd.Series,
    ma_days: int = BULL_MA_DAYS,
) -> pd.Series:
    intraday = pd.Series(close.to_numpy(), index=pd.DatetimeIndex(datetimes))
    daily_close = intraday.resample("1D").last()
    daily_ma = daily_close.rolling(ma_days, min_periods=ma_days).mean()
    completed = pd.DataFrame({
        "daily_close": daily_close,
        "daily_ma": daily_ma,
    }).shift(1)
    day_index = pd.DatetimeIndex(datetimes).normalize()
    mapped = completed.reindex(day_index)
    valid = mapped["daily_close"].notna() & mapped["daily_ma"].notna()
    bull = pd.Series(
        pd.array(
            np.where(
                valid,
                mapped["daily_close"] > mapped["daily_ma"],
                pd.NA,
            ),
            dtype="boolean",
        ),
        index=close.index,
    )
    return bull


def directional_indicators(
    bars: pd.DataFrame,
    period: int = ADX_PERIOD,
) -> tuple[pd.Series, pd.Series]:
    high = bars["high"].astype(float)
    low = bars["low"].astype(float)
    close = bars["close"].astype(float)
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(
        np.where((up_move > down_move) & (up_move > 0), up_move, 0.0),
        index=bars.index,
    )
    minus_dm = pd.Series(
        np.where((down_move > up_move) & (down_move > 0), down_move, 0.0),
        index=bars.index,
    )
    true_range = pd.concat(
        [
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = true_range.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()
    plus_di = (
        100
        * plus_dm.ewm(
            alpha=1 / period,
            adjust=False,
            min_periods=period,
        ).mean()
        / atr
    )
    minus_di = (
        100
        * minus_dm.ewm(
            alpha=1 / period,
            adjust=False,
            min_periods=period,
        ).mean()
        / atr
    )
    return plus_di, minus_di


def classify_grid(
    trend_state: bool,
    plus_di: float,
    minus_di: float,
    bull: bool,
) -> str:
    if pd.isna(bull):
        return "unknown"
    macro = "bull" if bull else "bear"
    if not trend_state:
        return f"range_{macro}"
    direction = "trend_up" if plus_di >= minus_di else "trend_down"
    return f"{direction}_{macro}"


def sample_grade(count: int) -> str:
    if count >= 500:
        return "CONFIRMATORY"
    if count >= 300:
        return "EXPLORATORY"
    return "INSUFFICIENT"


def one_sample_p_value(values: pd.Series) -> float | None:
    clean = values.dropna()
    if len(clean) < 2:
        return None
    return float(ttest_1samp(clean, 0.0, nan_policy="omit").pvalue)


def load_states() -> dict[str, pd.DataFrame]:
    states = {}
    for symbol, config in SYMBOL_CONFIG.items():
        bars = pd.read_csv(
            config["bars"],
            parse_dates=["datetime"],
            nrows=config["expected_research_rows"],
        )
        if bars["datetime"].max() >= config["holdout_start"]:
            raise ValueError(f"{symbol} Holdout boundary crossed")
        bars["adx"] = calculate_adx(bars)
        bars["adx_trend"] = hysteresis_regime(bars["adx"])
        bars["er60"] = efficiency_ratio(bars["close"])
        bars["er_trend"] = bars["er60"] > ER_THRESHOLD
        bars["plus_di"], bars["minus_di"] = directional_indicators(bars)
        bars["bull"] = prior_daily_bull_state(
            bars["datetime"],
            bars["close"],
        )
        bars["grid"] = [
            classify_grid(trend, plus, minus, bull)
            for trend, plus, minus, bull in zip(
                bars["adx_trend"],
                bars["plus_di"],
                bars["minus_di"],
                bars["bull"],
                strict=True,
            )
        ]
        states[symbol] = bars.set_index("datetime", drop=False)
    return states


def state_duration_summary(frame: pd.DataFrame) -> dict[str, object]:
    changed = frame["grid"].ne(frame["grid"].shift())
    runs = frame.groupby(changed.cumsum().to_numpy()).agg(
        grid=("grid", "first"),
        bars=("grid", "size"),
    )
    output = {}
    for grid, group in runs.groupby("grid"):
        output[grid] = {
            "run_count": int(len(group)),
            "median_duration_days": float(group["bars"].median() / 6),
            "mean_duration_days": float(group["bars"].mean() / 6),
        }
    return output


def state_coverage(states: dict[str, pd.DataFrame]) -> dict[str, object]:
    output = {}
    all_frames = []
    for symbol, frame in states.items():
        valid = frame[frame["adx"].notna() & frame["plus_di"].notna()]
        agreement_sample = valid[valid["er60"].notna()]
        output[symbol] = {
            "bars": int(len(valid)),
            "grid_share": {
                key: float(value)
                for key, value in valid["grid"].value_counts(
                    normalize=True
                ).sort_index().items()
            },
            "adx_er_trend_agreement": float(
                (
                    agreement_sample["adx_trend"]
                    == agreement_sample["er_trend"]
                ).mean()
            ),
            "adx_trend_share": float(valid["adx_trend"].mean()),
            "er_trend_share": float(agreement_sample["er_trend"].mean()),
            "durations": state_duration_summary(valid),
        }
        all_frames.append(valid.assign(symbol=symbol))
    combined = pd.concat(all_frames)
    output["combined"] = {
        "grid_share": {
            key: float(value)
            for key, value in combined["grid"].value_counts(
                normalize=True
            ).sort_index().items()
        },
        "adx_er_trend_agreement": float(
            (
                combined.loc[combined["er60"].notna(), "adx_trend"]
                == combined.loc[combined["er60"].notna(), "er_trend"]
            ).mean()
        ),
    }
    return output


def attach_state(
    frame: pd.DataFrame,
    states: dict[str, pd.DataFrame],
    time_column: str,
) -> pd.DataFrame:
    parts = []
    for symbol, group in frame.groupby("symbol"):
        labels = states[symbol][
            ["grid", "adx_trend", "er_trend", "bull", "adx", "er60"]
        ]
        merged = group.merge(
            labels,
            left_on=time_column,
            right_index=True,
            how="left",
            validate="many_to_one",
        )
        if merged["grid"].isna().any():
            raise ValueError(f"{symbol}: state labels missing for {time_column}")
        parts.append(merged)
    return pd.concat(parts, ignore_index=True)


def trade_max_drawdown(group: pd.DataFrame) -> float:
    ordered = group.sort_values("exit_time")
    equity = INITIAL_CAPITAL + ordered["net_pnl"].cumsum()
    path = pd.concat(
        [pd.Series([INITIAL_CAPITAL]), equity.reset_index(drop=True)],
        ignore_index=True,
    )
    return float((path / path.cummax() - 1).min())


def trade_attribution(
    name: str,
    path: Path,
    states: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, dict[str, object]]:
    trades = pd.read_csv(
        path,
        parse_dates=["entry_time", "exit_time", "signal_time"],
    )
    attributed = attach_state(trades, states, "entry_time")
    rows = []
    for grid, group in attributed.groupby("grid"):
        rows.append({
            "signal": name,
            "grid": grid,
            "count": int(len(group)),
            "sample_grade": sample_grade(len(group)),
            "net_pnl": float(group["net_pnl"].sum()),
            "win_rate": float((group["net_pnl"] > 0).mean()),
            "mean_r": float(group["expectancy_r"].mean()),
            "max_drawdown": trade_max_drawdown(group),
        })
    return attributed, {"rows": rows, "total_count": int(len(attributed))}


def sweep_attribution(
    name: str,
    path: Path,
    states: dict[str, pd.DataFrame],
) -> dict[str, object]:
    events = pd.read_csv(path, parse_dates=["datetime"])
    attributed = attach_state(events, states, "datetime")
    rows = []
    for grid, group in attributed.groupby("grid"):
        row: dict[str, object] = {
            "signal": name,
            "grid": grid,
            "count": int(len(group)),
            "sample_grade": sample_grade(len(group)),
        }
        stable_positive = True
        for horizon in (6, 12, 24):
            values = group[f"future_ret_{horizon}"].dropna()
            mean = float(values.mean())
            row[f"mean_ret_{horizon}"] = mean
            row[f"median_ret_{horizon}"] = float(values.median())
            row[f"positive_rate_{horizon}"] = float((values > 0).mean())
            row[f"p_value_{horizon}"] = one_sample_p_value(values)
            stable_positive = stable_positive and mean > 0
        row["stable_positive_all_horizons"] = stable_positive
        row["t24_significant_positive"] = bool(
            row["count"] >= 30
            and row["mean_ret_24"] > 0
            and row["p_value_24"] is not None
            and row["p_value_24"] < 0.05
        )
        rows.append(row)
    range_events = attributed[attributed["grid"].str.startswith("range_")]
    trend_events = attributed[attributed["grid"].str.startswith("trend_")]
    comparison = {}
    for label, group in {"range": range_events, "trend": trend_events}.items():
        comparison[label] = {
            "count": int(len(group)),
            "mean_ret_6": float(group["future_ret_6"].mean()),
            "mean_ret_12": float(group["future_ret_12"].mean()),
            "mean_ret_24": float(group["future_ret_24"].mean()),
            "p_value_24": one_sample_p_value(group["future_ret_24"]),
        }
    return {
        "rows": rows,
        "total_count": int(len(attributed)),
        "strength_comparison": comparison,
    }


def p104_2022_trap_test(
    attributed: pd.DataFrame,
) -> dict[str, object]:
    cohort = attributed[
        (attributed["entry_time"] >= pd.Timestamp("2022-01-01"))
        & (attributed["entry_time"] < pd.Timestamp("2023-01-01"))
    ]
    by_grid = cohort.groupby("grid")["net_pnl"].agg(["count", "sum"])
    negative_cells = by_grid.loc[by_grid["sum"] < 0, "sum"].abs()
    trap_loss = abs(
        min(float(by_grid["sum"].get("trend_up_bear", 0.0)), 0.0)
    )
    macro_bear_loss = sum(
        abs(min(float(by_grid["sum"].get(grid, 0.0)), 0.0))
        for grid in ("trend_up_bear", "trend_down_bear", "range_bear")
    )
    total_negative = float(negative_cells.sum())
    concentration = trap_loss / total_negative if total_negative else 0.0
    macro_bear_concentration = (
        macro_bear_loss / total_negative if total_negative else 0.0
    )
    return {
        "definition": (
            "P1-04 trades entering during 2022, attributed by entry state; "
            "not identical to calendar-period equity P&L"
        ),
        "calendar_2022_equity_net_profit_reference": -190787.9471022765,
        "cohort_net_pnl": float(cohort["net_pnl"].sum()),
        "cohort_trade_count": int(len(cohort)),
        "by_grid": {
            grid: {
                "count": int(row["count"]),
                "net_pnl": float(row["sum"]),
            }
            for grid, row in by_grid.iterrows()
        },
        "trend_up_bear_share_of_negative_cell_pnl": concentration,
        "macro_bear_share_of_negative_cell_pnl": macro_bear_concentration,
        "almost_all_threshold": ALMOST_ALL_THRESHOLD,
        "almost_all_confirmed": bool(concentration >= ALMOST_ALL_THRESHOLD),
    }


def main() -> None:
    states = load_states()
    trade_results = {}
    attributed_trades = {}
    for name, path in TRADE_FILES.items():
        attributed, summary = trade_attribution(name, path, states)
        attributed_trades[name] = attributed
        trade_results[name] = summary

    sweep_results = {
        name: sweep_attribution(name, path, states)
        for name, path in SWEEP_FILES.items()
    }
    payload = {
        "task": "P1-05 two-axis regime attribution",
        "holdout_accessed": False,
        "definitions": {
            "strength": (
                "ADX(14) Wilder hysteresis >25 trend, <20 range; "
                "+DI/-DI supplies trend direction"
            ),
            "strength_cross_check": "Kaufman ER(60) > 0.50",
            "macro_direction": (
                "previous completed daily close > previous completed "
                "daily SMA200 = bull; otherwise bear"
            ),
            "grid": [
                "trend_up_bull",
                "trend_up_bear",
                "trend_down_bull",
                "trend_down_bear",
                "range_bull",
                "range_bear",
            ],
            "almost_all": "at least 80% of negative grid-cell P&L",
        },
        "state_coverage": state_coverage(states),
        "trade_attribution": trade_results,
        "sweep_attribution": sweep_results,
        "p1_04_2022_trap_test": p104_2022_trap_test(
            attributed_trades["P1_04_regime_long"]
        ),
    }
    RESULT_PATH.write_text(json.dumps(payload, indent=2, default=str))
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
