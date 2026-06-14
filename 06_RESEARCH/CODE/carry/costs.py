"""Explicit per-leg execution and basis costs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostBreakdown:
    fee: float
    slippage: float

    @property
    def total(self) -> float:
        return self.fee + self.slippage


@dataclass(frozen=True)
class CostModel:
    """Frozen fee/slippage rates applied to absolute traded notional."""

    fee_rate: float = 0.001
    slippage_rate: float = 0.001
    event_slippage_rate: float = 0.003

    def __post_init__(self) -> None:
        for name, value in (
            ("fee_rate", self.fee_rate),
            ("slippage_rate", self.slippage_rate),
            ("event_slippage_rate", self.event_slippage_rate),
        ):
            if value < 0:
                raise ValueError(f"{name} must be non-negative")

    def trade_cost(
        self,
        *,
        spot_turnover: float,
        perp_turnover: float,
        event: bool = False,
    ) -> CostBreakdown:
        if spot_turnover < 0 or perp_turnover < 0:
            raise ValueError("turnover must be non-negative")
        total_turnover = spot_turnover + perp_turnover
        slippage_rate = (
            self.event_slippage_rate if event else self.slippage_rate
        )
        return CostBreakdown(
            fee=total_turnover * self.fee_rate,
            slippage=total_turnover * slippage_rate,
        )

    @staticmethod
    def basis_cost(
        *,
        notional: float,
        entry_basis_rate: float = 0.0,
        exit_basis_rate: float = 0.0,
    ) -> float:
        if notional < 0:
            raise ValueError("notional must be non-negative")
        return notional * (
            abs(float(entry_basis_rate)) + abs(float(exit_basis_rate))
        )
