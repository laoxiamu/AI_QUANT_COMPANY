"""Event study for bullish Liquidity Sweep under a dual market regime."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "06_RESEARCH/CODE/output"
V3_STATS_PATH = OUTPUT_DIR / "stats_v5_sweep_only_bull_v3.json"
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
SWEEP_LOOKBACK = 20
BTC_MOMENTUM_DAYS = 30
HORIZONS = (6, 12, 24)
HOLDOUT_FRACTION = 0.2
PERIOD_LABELS = (
    "2019-2020",
    "2021",
    "2022",
    "2023-2024",
    "2025-2026",
)


def load_pre_holdout(
    path: Path,
    expected_holdout_start: pd.Timestamp,
    registered_total_rows: int,
) -> tuple[pd.DataFrame, pd.Timestamp]:
    """Read only the registered first 80%; Holdout bytes are not parsed."""
    research_rows = int(registered_total_rows * (1 - HOLDOUT_FRACTION))
    bars = pd.read_csv(
        path,
        parse_dates=["datetime"],
        nrows=research_rows,
    )
    required = {"datetime", "open", "high", "low", "close", "volume"}
    missing = required.difference(bars.columns)
    if missing:
        raise ValueError(f"{path.name} missing columns: {sorted(missing)}")
    if len(bars) != EXPECTED_RESEARCH_ROWS[path.name]:
        raise ValueError(
            f"{path.name} snapshot changed; re-register before analysis"
        )
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


def btc_momentum_regime(btc_bars: pd.DataFrame) -> pd.Series:
    daily = daily_close(btc_bars, "btc_daily_close")
    daily["btc_return_30"] = np.log(
        daily["btc_daily_close"]
        / daily["btc_daily_close"].shift(BTC_MOMENTUM_DAYS)
    )
    # The value joined to a Sweep day must be known after the prior UTC day.
    daily["btc_momentum_bull"] = daily["btc_return_30"].gt(0).shift(1)
    return daily["btc_momentum_bull"]


def add_dual_regime(
    bars: pd.DataFrame,
    btc_momentum_bull: pd.Series,
) -> pd.DataFrame:
    own_daily = daily_close(bars, "daily_close")
    own_daily["ema200"] = own_daily["daily_close"].ewm(
        span=200,
        adjust=False,
        min_periods=200,
    ).mean()
    own_daily["ema_bull"] = (
        own_daily["daily_close"] > own_daily["ema200"]
    ).shift(1)

    result = bars.copy()
    result["day"] = result["datetime"].dt.floor("D")
    result = result.join(own_daily["ema_bull"], on="day")
    result = result.join(btc_momentum_bull, on="day")
    result["dual_regime"] = (
        result["ema_bull"].eq(True)
        & result["btc_momentum_bull"].eq(True)
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
    return "2025-2026"


def detect_events(
    symbol: str,
    bars: pd.DataFrame,
    btc_momentum_bull: pd.Series,
) -> tuple[pd.DataFrame, dict[str, int]]:
    data = add_dual_regime(bars, btc_momentum_bull)
    data["ref_low"] = (
        data["low"]
        .shift(1)
        .rolling(SWEEP_LOOKBACK, min_periods=SWEEP_LOOKBACK)
        .min()
    )
    data["bullish_sweep"] = (
        (data["low"] < data["ref_low"])
        & (data["close"] > data["ref_low"])
    )
    for horizon in HORIZONS:
        data[f"future_ret_{horizon}"] = np.log(
            data["close"].shift(-horizon) / data["close"]
        )

    raw_count = int(data["bullish_sweep"].sum())
    ema_count = int(
        (data["bullish_sweep"] & data["ema_bull"].eq(True)).sum()
    )
    regime_events = data[
        data["bullish_sweep"] & data["dual_regime"]
    ].copy()
    return_columns = [f"future_ret_{h}" for h in HORIZONS]
    complete = regime_events.dropna(subset=return_columns).copy()
    complete["symbol"] = symbol
    complete["period"] = complete["datetime"].map(period_label)
    columns = [
        "symbol",
        "datetime",
        "period",
        "close",
        "ref_low",
        *return_columns,
    ]
    return complete[columns], {
        "raw_sweeps": raw_count,
        "ema_regime_sweeps": ema_count,
        "dual_regime_sweeps": len(regime_events),
        "complete_events": len(complete),
    }


def summarize(values: pd.Series) -> dict[str, float | int | None]:
    clean = values.dropna().astype(float)
    if clean.empty:
        return {
            "n": 0,
            "mean": None,
            "std": None,
            "median": None,
            "hit_rate": None,
            "t_stat": None,
            "p_one_sided_greater": None,
            "p_two_sided": None,
        }
    if len(clean) < 2 or clean.std(ddof=1) == 0:
        t_stat = p_one = p_two = None
    else:
        greater = ttest_1samp(clean, popmean=0, alternative="greater")
        two_sided = ttest_1samp(
            clean,
            popmean=0,
            alternative="two-sided",
        )
        t_stat = float(greater.statistic)
        p_one = float(greater.pvalue)
        p_two = float(two_sided.pvalue)
    return {
        "n": int(len(clean)),
        "mean": float(clean.mean()),
        "std": float(clean.std(ddof=1)) if len(clean) > 1 else None,
        "median": float(clean.median()),
        "hit_rate": float((clean > 0).mean()),
        "t_stat": t_stat,
        "p_one_sided_greater": p_one,
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
            mask = (events["datetime"] >= start) & (
                events["datetime"] <= end
            )
        windows.append(
            {
                "window": index + 1,
                "start": str(start),
                "end": str(end),
                **summarize(events.loc[mask, "future_ret_12"]),
            }
        )
    return windows


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    loaded = {}
    ranges = {}
    for symbol, (
        path,
        holdout_start,
        total_rows,
    ) in SYMBOL_CONFIG.items():
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

    momentum = btc_momentum_regime(loaded["BTC"])
    frames = []
    counts = {}
    for symbol, bars in loaded.items():
        events, symbol_counts = detect_events(symbol, bars, momentum)
        frames.append(events)
        counts[symbol] = symbol_counts

    events = pd.concat(frames, ignore_index=True).sort_values(
        ["datetime", "symbol"]
    )
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
    with V3_STATS_PATH.open(encoding="utf-8") as handle:
        v3 = json.load(handle)

    output = {
        "experiment": "v5_sweep_regime_bull_v4",
        "baseline_experiment": "v5_sweep_only_bull_v3",
        "holdout_accessed": False,
        "parameters": {
            "sweep_lookback": SWEEP_LOOKBACK,
            "horizons": list(HORIZONS),
            "ema_regime": (
                "previous completed UTC daily close > own Daily EMA200"
            ),
            "momentum_regime": (
                "previous completed UTC day BTC 30-day log return > 0"
            ),
        },
        "research_ranges": ranges,
        "event_counts": counts,
        "overall": grouped_statistics(events),
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
        "v3_baseline": {
            "event_counts": v3["event_counts"],
            "overall": v3["overall"],
            "periods": v3["periods"],
            "walk_forward_t12": v3["walk_forward_t12"],
        },
    }
    output["main_hypothesis_passed"] = all(
        output["overall"]["combined"][str(horizon)]["mean"] > 0
        and output["overall"]["combined"][str(horizon)][
            "p_one_sided_greater"
        ] < 0.05
        for horizon in HORIZONS
    )
    output["sample_reliable"] = len(events) >= 100

    events.to_csv(
        OUTPUT_DIR / "events_v5_sweep_regime_bull_v4.csv",
        index=False,
        date_format="%Y-%m-%d %H:%M:%S",
    )
    with (
        OUTPUT_DIR / "stats_v5_sweep_regime_bull_v4.json"
    ).open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)

    print(json.dumps({
        "events": len(events),
        "main_hypothesis_passed": output["main_hypothesis_passed"],
        "sample_reliable": output["sample_reliable"],
        "event_counts": counts,
        "combined": output["overall"]["combined"],
        "walk_forward_t12": output["walk_forward_t12"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
