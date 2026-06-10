"""Event study for bullish Liquidity Sweep forward returns."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "06_RESEARCH/CODE/output"
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
SWEEP_LOOKBACK = 20
HORIZONS = (6, 12, 24)
HOLDOUT_FRACTION = 0.2


def load_pre_holdout(
    path: Path,
    expected_holdout_start: pd.Timestamp,
    registered_total_rows: int,
) -> tuple[pd.DataFrame, pd.Timestamp]:
    """Load only the first 80%; the remaining rows never enter analysis."""
    holdout_index = int(registered_total_rows * (1 - HOLDOUT_FRACTION))
    research = pd.read_csv(
        path, parse_dates=["datetime"], nrows=holdout_index
    )
    required = {"datetime", "open", "high", "low", "close", "volume"}
    missing = required.difference(research.columns)
    if missing:
        raise ValueError(f"{path.name} missing columns: {sorted(missing)}")
    if not research["datetime"].is_monotonic_increasing:
        raise ValueError(f"{path.name} datetime must be ascending")
    if (
        research["datetime"].duplicated().any()
        or research[list(required)].isna().any().any()
    ):
        raise ValueError(f"{path.name} contains duplicates or nulls")
    expected_rows = {
        "BTC_USDT_4H.csv": 13013,
        "ETH_USDT_4H.csv": 13013,
        "SOL_USDT_4H.csv": 10194,
    }
    if len(research) != expected_rows[path.name]:
        raise ValueError(
            f"{path.name} snapshot changed; re-register holdout before analysis"
        )
    return research.reset_index(drop=True), expected_holdout_start


def add_regime(bars: pd.DataFrame) -> pd.DataFrame:
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
    result = bars.copy()
    result["day"] = result["datetime"].dt.floor("D")
    return result.join(daily["bull_regime"], on="day")


def detect_events(
    symbol: str, bars: pd.DataFrame
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Apply SPEC-0A6 section 1 and calculate future log returns."""
    data = add_regime(bars)
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
    regime_events = data[
        data["bullish_sweep"] & data["bull_regime"].eq(True)
    ].copy()
    regime_count = len(regime_events)
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
        "regime_sweeps": regime_count,
        "complete_events": len(complete),
    }


def period_label(timestamp: pd.Timestamp) -> str:
    year = timestamp.year
    if year <= 2020:
        return "2019-2020"
    if year == 2021:
        return "2021"
    if year == 2022:
        return "2022"
    if year <= 2024:
        return "2023-2024"
    return "2025-2026"


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
        t_stat = None
        p_one = None
        p_two = None
    else:
        greater = ttest_1samp(clean, popmean=0, alternative="greater")
        two_sided = ttest_1samp(clean, popmean=0, alternative="two-sided")
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
    result: dict[str, object] = {"by_symbol": {}, "combined": {}}
    for symbol, group in events.groupby("symbol", sort=True):
        result["by_symbol"][symbol] = {
            str(h): summarize(group[f"future_ret_{h}"]) for h in HORIZONS
        }
    result["combined"] = {
        str(h): summarize(events[f"future_ret_{h}"]) for h in HORIZONS
    }
    return result


def period_statistics(events: pd.DataFrame) -> dict[str, object]:
    labels = ("2019-2020", "2021", "2022", "2023-2024", "2025-2026")
    result: dict[str, object] = {}
    for label in labels:
        period_events = events[events["period"] == label]
        result[label] = {
            "combined": {
                str(h): summarize(period_events[f"future_ret_{h}"])
                for h in HORIZONS
            },
            "by_symbol": {
                symbol: {
                    str(h): summarize(
                        period_events.loc[
                            period_events["symbol"] == symbol,
                            f"future_ret_{h}",
                        ]
                    )
                    for h in HORIZONS
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
            mask = (events["datetime"] >= start) & (events["datetime"] < end)
        else:
            mask = (events["datetime"] >= start) & (events["datetime"] <= end)
        values = events.loc[mask, "future_ret_12"]
        windows.append(
            {
                "window": index + 1,
                "start": str(start),
                "end": str(end),
                **summarize(values),
            }
        )
    return windows


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    event_frames = []
    counts = {}
    research_ranges = {}
    for symbol, (
        path,
        expected_holdout_start,
        registered_total_rows,
    ) in SYMBOL_CONFIG.items():
        bars, holdout_start = load_pre_holdout(
            path, expected_holdout_start, registered_total_rows
        )
        events, symbol_counts = detect_events(symbol, bars)
        event_frames.append(events)
        counts[symbol] = symbol_counts
        research_ranges[symbol] = {
            "research_start": str(bars["datetime"].iloc[0]),
            "research_end": str(bars["datetime"].iloc[-1]),
            "holdout_start": str(holdout_start),
            "research_rows": len(bars),
        }

    events = pd.concat(event_frames, ignore_index=True).sort_values(
        ["datetime", "symbol"]
    )
    common_start = max(
        pd.Timestamp(values["research_start"])
        for values in research_ranges.values()
    )
    common_end = min(
        pd.Timestamp(values["research_end"])
        for values in research_ranges.values()
    )
    common_events = events[
        (events["datetime"] >= common_start)
        & (events["datetime"] <= common_end)
    ]
    output = {
        "experiment": "v5_sweep_only_bull_v3",
        "holdout_accessed": False,
        "parameters": {
            "sweep_lookback": SWEEP_LOOKBACK,
            "horizons": list(HORIZONS),
            "regime": "previous completed UTC daily close > Daily EMA200",
        },
        "research_ranges": research_ranges,
        "event_counts": counts,
        "overall": grouped_statistics(events),
        "periods": period_statistics(events),
        "walk_forward_t12": walk_forward_statistics(
            common_events, common_start, common_end
        ),
        "common_walk_forward_range": {
            "start": str(common_start),
            "end": str(common_end),
            "events": len(common_events),
        },
    }
    main_pass = all(
        output["overall"]["combined"][str(h)]["mean"] > 0
        and output["overall"]["combined"][str(h)][
            "p_one_sided_greater"
        ] < 0.05
        for h in HORIZONS
    )
    output["main_hypothesis_passed"] = main_pass

    events.to_csv(
        OUTPUT_DIR / "events_v5_sweep_only_bull_v3.csv",
        index=False,
        date_format="%Y-%m-%d %H:%M:%S",
    )
    with open(
        OUTPUT_DIR / "stats_v5_sweep_only_bull_v3.json",
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)

    print("=== Sweep Event Study ===")
    for symbol in SYMBOL_CONFIG:
        print(symbol, counts[symbol])
    print("Combined:")
    for horizon in HORIZONS:
        print(f"t+{horizon}", output["overall"]["combined"][str(horizon)])
    print("Walk-forward t+12:")
    for window in output["walk_forward_t12"]:
        print(window)
    print("Main hypothesis passed:", main_pass)


if __name__ == "__main__":
    main()
