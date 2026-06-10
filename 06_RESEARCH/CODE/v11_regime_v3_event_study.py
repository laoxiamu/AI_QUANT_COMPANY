"""Bullish Sweep event study with a third BTC drawdown regime filter."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

import sweep_dual_regime as v4


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "06_RESEARCH/CODE/output"
EVENTS_PATH = OUTPUT_DIR / "events_v5_sweep_regime_bull_v7.csv"
STATS_PATH = OUTPUT_DIR / "stats_v5_sweep_regime_bull_v7.json"
V3_STATS_PATH = OUTPUT_DIR / "stats_v5_sweep_only_bull_v3.json"
V4_STATS_PATH = OUTPUT_DIR / "stats_v5_sweep_regime_bull_v4.json"
EXPECTED_RESEARCH_END = {
    "BTC_USDT_4H.csv": pd.Timestamp("2024-12-09 12:00:00"),
    "ETH_USDT_4H.csv": pd.Timestamp("2024-12-09 12:00:00"),
    "SOL_USDT_4H.csv": pd.Timestamp("2025-04-06 00:00:00"),
}
BTC_DRAWDOWN_DAYS = 90
BTC_DRAWDOWN_LIMIT = 0.20
NONOVERLAP_BARS = 24


def load_registered_pre_holdout(
    path: Path,
    expected_holdout_start: pd.Timestamp,
    registered_total_rows: int,
) -> tuple[pd.DataFrame, pd.Timestamp]:
    """Use v4's fixed-nrows loader and verify the registered final row."""
    bars, holdout_start = v4.load_pre_holdout(
        path,
        expected_holdout_start,
        registered_total_rows,
    )
    if bars["datetime"].iloc[-1] != EXPECTED_RESEARCH_END[path.name]:
        raise ValueError(f"{path.name} pre-Holdout boundary changed")
    return bars, holdout_start


def btc_regime_series(
    btc_bars: pd.DataFrame,
) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    """Return unchanged v4 momentum plus the preregistered drawdown filter."""
    momentum = v4.btc_momentum_regime(btc_bars)
    daily = v4.daily_close(btc_bars, "btc_daily_close")
    daily["rolling_high_90"] = daily["btc_daily_close"].rolling(
        BTC_DRAWDOWN_DAYS,
        min_periods=BTC_DRAWDOWN_DAYS,
    ).max().shift(1)
    daily["previous_close"] = daily["btc_daily_close"].shift(1)
    daily["drawdown_from_high"] = (
        daily["rolling_high_90"] - daily["previous_close"]
    ) / daily["rolling_high_90"]
    daily["btc_drawdown_bull"] = daily["drawdown_from_high"].lt(
        BTC_DRAWDOWN_LIMIT
    )
    return momentum, daily["btc_drawdown_bull"], daily


def add_triple_regime(
    bars: pd.DataFrame,
    btc_momentum_bull: pd.Series,
    btc_drawdown_bull: pd.Series,
) -> pd.DataFrame:
    """Preserve v4 conditions 1/2 and append only condition 3."""
    result = v4.add_dual_regime(bars, btc_momentum_bull)
    result["bar_index"] = np.arange(len(result))
    result = result.join(btc_drawdown_bull, on="day")
    result["triple_regime"] = (
        result["dual_regime"].eq(True)
        & result["btc_drawdown_bull"].eq(True)
    )
    return result


def detect_events(
    symbol: str,
    bars: pd.DataFrame,
    btc_momentum_bull: pd.Series,
    btc_drawdown_bull: pd.Series,
) -> tuple[pd.DataFrame, dict[str, int]]:
    data = add_triple_regime(
        bars,
        btc_momentum_bull,
        btc_drawdown_bull,
    )
    data["ref_low"] = (
        data["low"]
        .shift(1)
        .rolling(v4.SWEEP_LOOKBACK, min_periods=v4.SWEEP_LOOKBACK)
        .min()
    )
    data["bullish_sweep"] = (
        (data["low"] < data["ref_low"])
        & (data["close"] > data["ref_low"])
    )
    for horizon in v4.HORIZONS:
        data[f"future_ret_{horizon}"] = np.log(
            data["close"].shift(-horizon) / data["close"]
        )

    raw_count = int(data["bullish_sweep"].sum())
    ema_count = int(
        (data["bullish_sweep"] & data["ema_bull"].eq(True)).sum()
    )
    dual_count = int(
        (data["bullish_sweep"] & data["dual_regime"]).sum()
    )
    regime_events = data[
        data["bullish_sweep"] & data["triple_regime"]
    ].copy()
    return_columns = [f"future_ret_{h}" for h in v4.HORIZONS]
    complete = regime_events.dropna(subset=return_columns).copy()
    complete["symbol"] = symbol
    complete["period"] = complete["datetime"].map(v4.period_label)
    columns = [
        "symbol",
        "datetime",
        "bar_index",
        "period",
        "close",
        "ref_low",
        *return_columns,
    ]
    return complete[columns], {
        "raw_sweeps": raw_count,
        "ema_regime_sweeps": ema_count,
        "dual_regime_sweeps": dual_count,
        "triple_regime_sweeps": len(regime_events),
        "complete_events": len(complete),
    }


def nonoverlapping_subset(events: pd.DataFrame) -> pd.DataFrame:
    kept = []
    for _, group in events.groupby("symbol", sort=True):
        group = group.sort_values("bar_index")
        last_bar = None
        indices = []
        for row in group.itertuples():
            if last_bar is None or row.bar_index - last_bar > NONOVERLAP_BARS:
                indices.append(row.Index)
                last_bar = row.bar_index
        kept.append(group.loc[indices])
    return pd.concat(kept, ignore_index=True).sort_values(
        ["datetime", "symbol"]
    )


def baseline_snapshot(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        stats = json.load(handle)
    return {
        "experiment": stats["experiment"],
        "event_counts": stats["event_counts"],
        "overall": stats["overall"],
        "periods": stats["periods"],
        "walk_forward_t12": stats["walk_forward_t12"],
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    loaded = {}
    ranges = {}
    for symbol, (path, holdout_start, total_rows) in v4.SYMBOL_CONFIG.items():
        bars, registered_holdout = load_registered_pre_holdout(
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

    momentum, drawdown_filter, drawdown_daily = btc_regime_series(
        loaded["BTC"]
    )
    frames = []
    counts = {}
    for symbol, bars in loaded.items():
        events, symbol_counts = detect_events(
            symbol,
            bars,
            momentum,
            drawdown_filter,
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
    common_events = events[
        events["datetime"].between(common_start, common_end)
    ]
    overall = v4.grouped_statistics(events)
    nonoverlap_stats = v4.grouped_statistics(nonoverlap)

    output = {
        "experiment": "v5_sweep_regime_bull_v7",
        "baseline_experiments": [
            "v5_sweep_only_bull_v3",
            "v5_sweep_regime_bull_v4",
        ],
        "holdout_accessed": False,
        "physical_holdout_truncation": True,
        "parameters": {
            "sweep_lookback": v4.SWEEP_LOOKBACK,
            "horizons": list(v4.HORIZONS),
            "ema_regime": (
                "unchanged v4: previous completed UTC daily close "
                "> own Daily EMA200"
            ),
            "momentum_regime": (
                "unchanged v4: previous completed UTC day BTC "
                "30-day log return > 0"
            ),
            "drawdown_regime": (
                "previous completed UTC day BTC close drawdown from "
                "90-day rolling highest close < 20%"
            ),
            "drawdown_window_days": BTC_DRAWDOWN_DAYS,
            "drawdown_min_periods": BTC_DRAWDOWN_DAYS,
            "drawdown_limit": BTC_DRAWDOWN_LIMIT,
            "rolling_high_shift": 1,
            "previous_close_shift": 1,
            "test_alternative": "greater",
            "nonoverlap_rule": (
                "within symbol, retained bar-index distance > 24"
            ),
        },
        "research_ranges": ranges,
        "drawdown_diagnostics": {
            "first_valid_rolling_high_day": str(
                drawdown_daily["rolling_high_90"].first_valid_index()
            ),
            "valid_days": int(
                drawdown_daily["rolling_high_90"].notna().sum()
            ),
        },
        "event_counts": counts,
        "overall": overall,
        "periods": v4.period_statistics(events),
        "walk_forward_t12": v4.walk_forward_statistics(
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
            "statistics": nonoverlap_stats,
        },
        "v3_baseline": baseline_snapshot(V3_STATS_PATH),
        "v4_baseline": baseline_snapshot(V4_STATS_PATH),
    }
    output["main_hypothesis_passed"] = all(
        overall["combined"][str(horizon)]["mean"] > 0
        and overall["combined"][str(horizon)][
            "p_one_sided_greater"
        ] < 0.05
        for horizon in v4.HORIZONS
    )
    output["nonoverlap_all_windows_passed"] = all(
        nonoverlap_stats["combined"][str(horizon)]["mean"] > 0
        and nonoverlap_stats["combined"][str(horizon)][
            "p_one_sided_greater"
        ] < 0.05
        for horizon in v4.HORIZONS
    )
    output["exploratory_sample_threshold_met"] = len(events) >= 300

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
        "exploratory_sample_threshold_met": (
            output["exploratory_sample_threshold_met"]
        ),
        "nonoverlap_events": len(nonoverlap),
        "nonoverlap_all_windows_passed": (
            output["nonoverlap_all_windows_passed"]
        ),
        "event_counts": counts,
        "combined": overall["combined"],
        "periods": output["periods"],
        "walk_forward_t12": output["walk_forward_t12"],
        "nonoverlap_combined": nonoverlap_stats["combined"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
