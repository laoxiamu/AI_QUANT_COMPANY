import pandas as pd

from carry.config import EngineConfig
from carry.costs import CostModel
from carry.portfolio import DEFAULT_WEIGHTS, run_portfolio_comparison


def _symbol_input(rate: float) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    timestamps = pd.to_datetime(
        ["2024-01-01T00:00:00Z", "2024-01-01T08:00:00Z"],
        utc=True,
    )
    marks = pd.DataFrame(
        {
            "timestamp": timestamps,
            "mark_price": [100.0, 100.0],
            "spot_price": [100.0, 100.0],
        }
    )
    funding = pd.DataFrame(
        {
            "timestamp": [timestamps[-1]],
            "funding_rate": [rate],
        }
    )
    oi = pd.Series([0.5, 0.5], index=timestamps)
    return marks, funding, oi


def test_portfolio_uses_frozen_btc_eth_weights_and_two_variants() -> None:
    inputs = {
        "BTCUSDT": _symbol_input(0.001),
        "ETHUSDT": _symbol_input(0.002),
    }
    config = EngineConfig(
        base_notional=10_000.0,
        costs=CostModel(fee_rate=0.0, slippage_rate=0.0),
    )

    result = run_portfolio_comparison(inputs, config=config)

    assert DEFAULT_WEIGHTS == {"BTCUSDT": 0.7, "ETHUSDT": 0.3}
    assert set(result) == {"without_trigger", "with_trigger"}
    expected_funding = 7_000.0 * 0.001 + 3_000.0 * 0.002
    assert result["without_trigger"].summary["funding_pnl"] == expected_funding
