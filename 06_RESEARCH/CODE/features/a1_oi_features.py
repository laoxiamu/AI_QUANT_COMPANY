#!/usr/bin/env python3
"""Build A-1 open-interest feature tables with no lookahead."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
CODE_DIR = ROOT / "06_RESEARCH" / "CODE"
DATA_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES"
OUTPUT_DIR = CODE_DIR / "output"

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from features.a2_funding_features import add_rolling_percentiles  # noqa: E402


SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
OI_COLUMN = "sum_open_interest"
TIME_COLUMN = "create_time"
OUTPUT_COLUMNS = [
    "ts",
    "oi",
    "d6h_pct",
    "d24h_pct",
    "d6h_rolling_pctl",
    "d24h_rolling_pctl",
    "warmup",
]


def read_metrics(path: Path) -> pd.DataFrame:
    """Read only the columns needed for the A-1 OI feature layer."""
    df = pd.read_csv(path, usecols=[TIME_COLUMN, OI_COLUMN])
    df[TIME_COLUMN] = pd.to_datetime(df[TIME_COLUMN], utc=True)
    df[OI_COLUMN] = pd.to_numeric(df[OI_COLUMN], errors="coerce")
    return df


def resample_oi_1h(metrics: pd.DataFrame) -> pd.DataFrame:
    """Resample 5-minute OI to a UTC 1H grid using each hour's last row."""
    df = metrics.loc[:, [TIME_COLUMN, OI_COLUMN]].copy()
    df[TIME_COLUMN] = pd.to_datetime(df[TIME_COLUMN], utc=True)
    df = df.sort_values(TIME_COLUMN).set_index(TIME_COLUMN)

    hourly = df[OI_COLUMN].resample("1h").agg(
        lambda values: values.iloc[-1] if len(values) else pd.NA
    )
    return hourly.rename("oi").reset_index().rename(columns={TIME_COLUMN: "ts"})


def add_pct_changes(hourly: pd.DataFrame) -> pd.DataFrame:
    """Add 6h and 24h OI percentage changes without filling gaps."""
    df = hourly.copy()
    df["d6h_pct"] = df["oi"].pct_change(periods=6, fill_method=None)
    df["d24h_pct"] = df["oi"].pct_change(periods=24, fill_method=None)
    return df


def _rolling_percentile_feature(
    features: pd.DataFrame,
    *,
    value_col: str,
    out_col: str,
    warmup_col: str,
) -> tuple[pd.DataFrame, pd.Timestamp | None]:
    """Return no-lookahead rolling percentile for a single feature column."""
    valid = features.loc[features[value_col].notna(), ["ts", value_col]].copy()
    if valid.empty:
        out = features.loc[:, ["ts"]].copy()
        out[out_col] = pd.NA
        out[warmup_col] = True
        return out, None

    rolled = add_rolling_percentiles(valid, time_col="ts", value_col=value_col)
    pctls = rolled.loc[:, ["ts", "rolling_pctl", "warmup"]].rename(
        columns={"rolling_pctl": out_col, "warmup": warmup_col}
    )
    out = features.loc[:, ["ts"]].merge(pctls, on="ts", how="left")

    ready = pctls.loc[~pctls[warmup_col], "ts"]
    first_ready = ready.min() if not ready.empty else None
    if first_ready is None or pd.isna(first_ready):
        out[warmup_col] = True
    else:
        missing_warmup = out[warmup_col].isna()
        out.loc[missing_warmup, warmup_col] = out.loc[missing_warmup, "ts"] < first_ready
        out[warmup_col] = out[warmup_col].astype(bool)

    return out, first_ready


def add_rolling_oi_percentiles(features: pd.DataFrame) -> pd.DataFrame:
    """Add A-1 no-lookahead rolling percentiles for 6h and 24h OI changes."""
    d6, d6_ready = _rolling_percentile_feature(
        features,
        value_col="d6h_pct",
        out_col="d6h_rolling_pctl",
        warmup_col="_d6h_warmup",
    )
    d24, d24_ready = _rolling_percentile_feature(
        features,
        value_col="d24h_pct",
        out_col="d24h_rolling_pctl",
        warmup_col="_d24h_warmup",
    )

    df = features.merge(d6, on="ts", how="left").merge(d24, on="ts", how="left")
    df["warmup"] = df["_d6h_warmup"] | df["_d24h_warmup"]
    if d6_ready is None or d24_ready is None:
        df["warmup"] = True
    return df.drop(columns=["_d6h_warmup", "_d24h_warmup"])


def build_symbol_features(symbol: str, data_dir: Path = DATA_DIR) -> pd.DataFrame:
    path = data_dir / f"{symbol}_METRICS_5M.csv"
    metrics = read_metrics(path)
    features = add_pct_changes(resample_oi_1h(metrics))
    features = add_rolling_oi_percentiles(features)
    out = features.loc[:, OUTPUT_COLUMNS].copy()
    out["ts"] = pd.to_datetime(out["ts"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def summarize_features(symbol: str, features: pd.DataFrame) -> dict[str, object]:
    ts = pd.to_datetime(features["ts"], utc=True)
    expected_rows = int(((ts.max() - ts.min()) / pd.Timedelta(hours=1)) + 1)
    gap_hours = int(features["oi"].isna().sum())
    return {
        "symbol": symbol,
        "start_utc": ts.min().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_utc": ts.max().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rows": int(len(features)),
        "expected_1h_grid_rows": expected_rows,
        "warmup_rows": int(features["warmup"].sum()),
        "oi_gap_hours": gap_hours,
        "oi_gap_rate": float(gap_hours / len(features)) if len(features) else None,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, object]] = []

    for symbol in SYMBOLS:
        features = build_symbol_features(symbol, DATA_DIR)
        out_path = OUTPUT_DIR / f"a1_oi_features_{symbol}.csv"
        features.to_csv(out_path, index=False)
        summary = summarize_features(symbol, features)
        summary["output"] = str(out_path.relative_to(ROOT))
        summaries.append(summary)

    payload = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "symbols": list(SYMBOLS),
        "outputs": summaries,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
