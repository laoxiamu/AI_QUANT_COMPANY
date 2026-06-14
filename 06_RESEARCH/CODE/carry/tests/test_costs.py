import pytest

from carry.costs import CostModel


def test_spot_and_perp_each_pay_fee_and_slippage_per_side() -> None:
    model = CostModel(fee_rate=0.001, slippage_rate=0.001)

    cost = model.trade_cost(spot_turnover=1_000.0, perp_turnover=1_000.0)

    assert cost.fee == pytest.approx(2.0)
    assert cost.slippage == pytest.approx(2.0)
    assert cost.total == pytest.approx(4.0)


def test_event_slippage_and_basis_entry_exit_are_separate() -> None:
    model = CostModel(
        fee_rate=0.001,
        slippage_rate=0.001,
        event_slippage_rate=0.003,
    )

    event = model.trade_cost(
        spot_turnover=0.0,
        perp_turnover=1_000.0,
        event=True,
    )
    basis = model.basis_cost(
        notional=1_000.0,
        entry_basis_rate=0.002,
        exit_basis_rate=-0.001,
    )

    assert event.total == pytest.approx(4.0)
    assert basis == pytest.approx(3.0)
