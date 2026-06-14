"""Pre-holdout CSV loaders with UTC normalization and row auditing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


DEFAULT_CUTOFF = pd.Timestamp("2024-12-10T00:00:00Z")
TIME_ALIASES = ("timestamp", "datetime", "time", "fundingTime", "open_time")
FUNDING_ALIASES = (
    "funding_rate",
    "last_funding_rate",
    "fundingRate",
)
MARK_ALIASES = ("mark_price", "close", "price", "markPrice")
SPOT_ALIASES = ("spot_price", "spot_close")


@dataclass(frozen=True)
class SymbolData:
    symbol: str
    funding: pd.DataFrame
    mark: pd.DataFrame
    audit: dict[str, dict[str, int | str]]


def assert_preholdout_path(path: str | Path) -> Path:
    candidate = Path(path)
    inspected_parts = list(candidate.parts)
    inspected_parts.extend(candidate.resolve(strict=False).parts)
    if any("HOLDOUT" in part.upper() for part in inspected_parts):
        raise ValueError("Holdout paths are forbidden")
    return candidate


def normalize_cutoff(cutoff: str | pd.Timestamp) -> pd.Timestamp:
    cutoff_ts = pd.Timestamp(cutoff)
    if cutoff_ts.tzinfo is None:
        cutoff_ts = cutoff_ts.tz_localize("UTC")
    else:
        cutoff_ts = cutoff_ts.tz_convert("UTC")
    if cutoff_ts > DEFAULT_CUTOFF:
        raise ValueError(
            f"cutoff {cutoff_ts} is later than frozen {DEFAULT_CUTOFF}"
        )
    return cutoff_ts


def _nonempty_data_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return max(sum(1 for line in handle if line.strip()) - 1, 0)


def _pick_column(columns: pd.Index, aliases: tuple[str, ...], label: str) -> str:
    for alias in aliases:
        if alias in columns:
            return alias
    raise ValueError(f"missing {label}; accepted columns: {aliases}")


def _read_and_normalize(
    path: Path,
    *,
    value_aliases: tuple[str, ...],
    value_name: str,
    cutoff: pd.Timestamp,
) -> tuple[pd.DataFrame, dict[str, int | str]]:
    raw_rows = _nonempty_data_rows(path)
    raw = pd.read_csv(path, on_bad_lines="skip")
    parsed_rows = len(raw)
    time_col = _pick_column(raw.columns, TIME_ALIASES, "timestamp")
    value_col = _pick_column(raw.columns, value_aliases, value_name)

    normalized = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                raw[time_col],
                utc=True,
                errors="coerce",
            ),
            value_name: pd.to_numeric(raw[value_col], errors="coerce"),
        }
    )
    valid_mask = normalized["timestamp"].notna() & normalized[value_name].notna()
    invalid_rows = raw_rows - int(valid_mask.sum())
    normalized = normalized.loc[valid_mask].copy()
    cutoff_rows = int((normalized["timestamp"] >= cutoff).sum())
    normalized = normalized.loc[normalized["timestamp"] < cutoff]
    duplicate_rows = int(normalized["timestamp"].duplicated(keep="last").sum())
    normalized = (
        normalized.drop_duplicates("timestamp", keep="last")
        .sort_values("timestamp")
        .reset_index(drop=True)
    )
    audit: dict[str, int | str] = {
        "path": str(path),
        "raw_rows": raw_rows,
        "parsed_rows": parsed_rows,
        "invalid_rows": invalid_rows,
        "cutoff_rows": cutoff_rows,
        "duplicate_rows": duplicate_rows,
        "output_rows": len(normalized),
    }
    return normalized, audit


def load_symbol_data(
    data_dir: str | Path,
    symbol: str,
    *,
    cutoff: str | pd.Timestamp = DEFAULT_CUTOFF,
) -> SymbolData:
    """Load one symbol and return only rows before the strict UTC cutoff."""
    normalized_symbol = symbol.upper()
    if not normalized_symbol.isalnum():
        raise ValueError("symbol must be alphanumeric")
    directory = assert_preholdout_path(data_dir)
    cutoff_ts = normalize_cutoff(cutoff)

    funding, funding_audit = _read_and_normalize(
        directory / f"{normalized_symbol}_FUNDING_8H.csv",
        value_aliases=FUNDING_ALIASES,
        value_name="funding_rate",
        cutoff=cutoff_ts,
    )
    mark, mark_audit = _read_and_normalize(
        directory / f"{normalized_symbol}_MARK_1H.csv",
        value_aliases=MARK_ALIASES,
        value_name="mark_price",
        cutoff=cutoff_ts,
    )

    mark["spot_price"] = mark["mark_price"]
    raw_mark = pd.read_csv(
        directory / f"{normalized_symbol}_MARK_1H.csv",
        on_bad_lines="skip",
    )
    spot_col = next(
        (name for name in SPOT_ALIASES if name in raw_mark.columns),
        None,
    )
    if spot_col is not None:
        time_col = _pick_column(raw_mark.columns, TIME_ALIASES, "timestamp")
        spot = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    raw_mark[time_col],
                    utc=True,
                    errors="coerce",
                ),
                "spot_price": pd.to_numeric(
                    raw_mark[spot_col],
                    errors="coerce",
                ),
            }
        ).dropna()
        spot = spot.loc[spot["timestamp"] < cutoff_ts]
        spot = spot.drop_duplicates("timestamp", keep="last")
        mark = mark.drop(columns="spot_price").merge(
            spot,
            on="timestamp",
            how="left",
        )
        mark["spot_price"] = mark["spot_price"].fillna(mark["mark_price"])

    return SymbolData(
        symbol=normalized_symbol,
        funding=funding,
        mark=mark,
        audit={"funding": funding_audit, "mark": mark_audit},
    )
