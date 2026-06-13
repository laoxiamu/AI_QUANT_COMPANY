"""Focused tests for the D2 extended-universe fail-closed entrypoint."""

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import d2_tsmom_extended_backtest as d2  # noqa: E402
from d2_tsmom_extended_backtest import (  # noqa: E402
    BASE_FULL_SYMBOLS,
    DEC_070_REQUIRED_FILTERS,
    HARD_CUTOFF,
    assert_pre_holdout_frame,
    audit_expanded_inputs,
    select_expanded_symbols,
)


def _manifest(base_url: str = "https://example/monthly/klines") -> dict:
    downloads = {
        f"COIN{index:02d}USDT": {
            "rows": 10_000 - index,
            "ok": True,
        }
        for index in range(35)
    }
    downloads[BASE_FULL_SYMBOLS[0]] = {"rows": 99_999, "ok": True}
    return {
        "base_url": base_url,
        "downloads": downloads,
        "summary": {"success": len(downloads)},
    }


def test_selection_is_rows_descending_and_excludes_base_assets() -> None:
    selected = select_expanded_symbols(_manifest(), 20)
    assert len(selected) == 20
    assert selected[0] == "COIN00USDT"
    assert selected[-1] == "COIN19USDT"
    assert not set(selected).intersection(BASE_FULL_SYMBOLS)


def test_cutoff_assert_accepts_boundary_and_rejects_later_data() -> None:
    valid = pd.DataFrame({"datetime": [HARD_CUTOFF]})
    assert_pre_holdout_frame(valid, "valid")

    invalid = pd.DataFrame(
        {"datetime": [HARD_CUTOFF + pd.Timedelta(seconds=1)]}
    )
    try:
        assert_pre_holdout_frame(invalid, "invalid")
    except AssertionError as exc:
        assert "crossed cutoff" in str(exc)
    else:
        raise AssertionError("post-cutoff frame was not rejected")


def test_expanded_audit_fails_closed_on_current_d1_shape() -> None:
    manifest = _manifest()
    selected = select_expanded_symbols(manifest, 30)
    blockers = audit_expanded_inputs(manifest, selected)
    codes = {blocker.code for blocker in blockers}
    assert "PRICE_SOURCE_MISMATCH" in codes
    assert "MISSING_REAL_FUNDING" in codes
    assert "DEC_070_FILTERS_NOT_AUDITABLE" in codes


def test_expanded_audit_accepts_corrected_input_contract(
    tmp_path: Path,
    monkeypatch,
) -> None:
    manifest = _manifest(
        "https://example/monthly/markPriceKlines"
    )
    manifest["dec_070_quality_audit"] = {
        key: True for key in DEC_070_REQUIRED_FILTERS
    }
    selected = select_expanded_symbols(manifest, 30)
    for symbol in selected:
        (tmp_path / f"{symbol}_FUNDING_8H.csv").touch()
    monkeypatch.setattr(d2, "EXPANDED", tmp_path)
    assert audit_expanded_inputs(manifest, selected) == []
