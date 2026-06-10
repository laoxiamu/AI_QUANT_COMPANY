"""Detect bullish Sweep -> FVG -> CHoCH -> retracement sequences."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


SWEEP_LOOKBACK = 20
SWING_LOOKBACK = 10
SWING_N = 2
SEQUENCE_WINDOW = 20

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_INPUT_PATH = PROJECT_ROOT / "BTC_USDT_4H.csv"
OUTPUT_DIR = PROJECT_ROOT / "06_RESEARCH/CODE/output"
OUTPUT_COLUMNS = [
    "signal_time",
    "sweep_time",
    "choch_time",
    "fvg_low",
    "fvg_high",
    "entry_price",
    "stop_loss",
    "risk_pct",
]


def load_data(path: Path) -> pd.DataFrame:
    """Load and validate the OHLCV input used by the detector."""
    data = pd.read_csv(path, parse_dates=["datetime"])
    required = {"datetime", "open", "high", "low", "close", "volume"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if data.empty:
        raise ValueError("Input data is empty")
    if data["datetime"].isna().any():
        raise ValueError("Input contains invalid datetime values")
    if not data["datetime"].is_monotonic_increasing:
        raise ValueError("Input datetime column must be sorted ascending")
    if data["datetime"].duplicated().any():
        raise ValueError("Input contains duplicate datetime values")
    if data[["open", "high", "low", "close", "volume"]].isna().any().any():
        raise ValueError("Input contains missing OHLCV values")
    return data.reset_index(drop=True)


def detect_base_signals(data: pd.DataFrame) -> pd.DataFrame:
    """Implement SPEC-0A6 sections 1-3 using pandas vector operations."""
    signals = data.copy()
    row_index = np.arange(len(signals))

    # SPEC section 1: prior 20-bar low, excluding the current bar.
    signals["sweep_ref_low"] = (
        signals["low"]
        .shift(1)
        .rolling(SWEEP_LOOKBACK, min_periods=SWEEP_LOOKBACK)
        .min()
    )
    signals["bullish_sweep"] = (
        (signals["low"] < signals["sweep_ref_low"])
        & (signals["close"] > signals["sweep_ref_low"])
    )

    # SPEC section 2: strict two-sided swing high with two confirming bars.
    swing_high = pd.Series(True, index=signals.index)
    for offset in range(1, SWING_N + 1):
        swing_high &= signals["high"] > signals["high"].shift(offset)
        swing_high &= signals["high"] > signals["high"].shift(-offset)
    signals["swing_high"] = swing_high.fillna(False)

    swing_value = signals["high"].where(signals["swing_high"])
    swing_index = pd.Series(
        np.where(signals["swing_high"], row_index, np.nan),
        index=signals.index,
    )
    known_swing_value = swing_value.shift(SWING_N).ffill()
    known_swing_index = swing_index.shift(SWING_N).ffill()
    recent_swing = (
        known_swing_index.notna()
        & ((row_index - known_swing_index) <= SWING_LOOKBACK)
    )
    fallback_high = (
        signals["high"]
        .shift(1)
        .rolling(SWING_LOOKBACK, min_periods=SWING_LOOKBACK)
        .max()
    )
    signals["ref_swing_high"] = known_swing_value.where(
        recent_swing, fallback_high
    )
    enough_choch_history = row_index >= SWING_LOOKBACK + SWING_N
    signals["bullish_choch"] = (
        enough_choch_history
        & (signals["close"] > signals["ref_swing_high"])
    )

    # SPEC section 3: gap is detected on bar i and timestamped at bar i-1.
    fvg_detected = signals["high"].shift(2) < signals["low"]
    signals["bullish_fvg_at_middle"] = fvg_detected.shift(-1).fillna(False)
    signals["fvg_low"] = signals["high"].shift(1).where(
        signals["bullish_fvg_at_middle"]
    )
    signals["fvg_high"] = signals["low"].shift(-1).where(
        signals["bullish_fvg_at_middle"]
    )
    return signals


def detect_triple_signals(signals: pd.DataFrame) -> pd.DataFrame:
    """Implement the ordered sequence in SPEC-0A6 section 4."""
    sweep_indices = np.flatnonzero(signals["bullish_sweep"].to_numpy())
    choch_indices = np.flatnonzero(signals["bullish_choch"].to_numpy())
    fvg_indices = np.flatnonzero(
        signals["bullish_fvg_at_middle"].to_numpy()
    )
    lows = signals["low"].to_numpy()
    closes = signals["close"].to_numpy()
    datetimes = signals["datetime"].to_numpy()
    fvg_lows = signals["fvg_low"].to_numpy()
    fvg_highs = signals["fvg_high"].to_numpy()
    sweep_ref_lows = signals["sweep_ref_low"].to_numpy()

    records: list[dict[str, object]] = []
    for sweep_idx in sweep_indices:
        candidate_chochs = choch_indices[
            (choch_indices > sweep_idx)
            & (choch_indices <= sweep_idx + SEQUENCE_WINDOW)
        ]
        for choch_idx in candidate_chochs:
            candidate_fvgs = fvg_indices[
                (fvg_indices > sweep_idx) & (fvg_indices <= choch_idx)
            ]
            if candidate_fvgs.size == 0:
                continue

            fvg_idx = int(candidate_fvgs[-1])
            fvg_low = float(fvg_lows[fvg_idx])
            fvg_high = float(fvg_highs[fvg_idx])
            entry_end = min(choch_idx + SEQUENCE_WINDOW, len(signals) - 1)
            entry_indices = np.arange(choch_idx + 1, entry_end + 1)
            enters_zone = (
                (lows[entry_indices] <= fvg_high)
                & (closes[entry_indices] >= fvg_low)
            )
            if not enters_zone.any():
                continue

            entry_idx = int(entry_indices[np.flatnonzero(enters_zone)[0]])
            stop_loss = float(sweep_ref_lows[sweep_idx])
            risk_pct = (fvg_high - stop_loss) / fvg_high * 100.0
            records.append(
                {
                    "signal_time": datetimes[entry_idx],
                    "sweep_time": datetimes[sweep_idx],
                    "choch_time": datetimes[choch_idx],
                    "fvg_low": fvg_low,
                    "fvg_high": fvg_high,
                    "entry_price": fvg_high,
                    "stop_loss": stop_loss,
                    "risk_pct": risk_pct,
                }
            )
            break

    return pd.DataFrame.from_records(records, columns=OUTPUT_COLUMNS)


def print_summary(
    data: pd.DataFrame, signals: pd.DataFrame, triples: pd.DataFrame
) -> None:
    """Print SPEC-0A6 section 5 format 2."""
    elapsed_years = (
        data["datetime"].iloc[-1] - data["datetime"].iloc[0]
    ).total_seconds() / (365.2425 * 24 * 60 * 60)
    per_year = len(triples) / elapsed_years if elapsed_years > 0 else 0.0
    print("=== 信号统计摘要 ===")
    print(
        f"数据范围：{data['datetime'].iloc[0]} ~ "
        f"{data['datetime'].iloc[-1]}"
    )
    print(f"总K线数：{len(data)}")
    print(f"Bullish Sweep 次数：{int(signals['bullish_sweep'].sum())}")
    print(f"Bullish CHoCH 次数：{int(signals['bullish_choch'].sum())}")
    print(
        "Bullish FVG 次数："
        f"{int(signals['bullish_fvg_at_middle'].sum())}"
    )
    print(f"三重确认信号次数：{len(triples)}")
    print(
        f"信号触发频率：{len(triples)}次 / {elapsed_years:.2f}年 "
        f"= 平均每年{per_year:.2f}次"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect SPEC-0A6 bullish triple-confirmation signals."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="OHLCV CSV path (default: BTC_USDT_4H.csv)",
    )
    parser.add_argument(
        "--symbol",
        default=DEFAULT_SYMBOL,
        help="Output symbol label (default: BTCUSDT)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input if args.input.is_absolute() else PROJECT_ROOT / args.input
    symbol = args.symbol.upper().replace("/", "").replace("_", "")
    output_path = OUTPUT_DIR / f"triple_signals_{symbol}_4H.csv"

    data = load_data(input_path)
    signals = detect_base_signals(data)
    triples = detect_triple_signals(signals)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    triples.to_csv(output_path, index=False, date_format="%Y-%m-%d %H:%M:%S")
    print_summary(data, signals, triples)


if __name__ == "__main__":
    main()
