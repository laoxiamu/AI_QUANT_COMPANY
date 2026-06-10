"""Small, deterministic rule primitives shared by backtest tests."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Iterable


class BarAction(str, Enum):
    NONE = "NONE"
    STOP = "STOP"
    TAKE_PROFIT_1 = "TAKE_PROFIT_1"


@dataclass(frozen=True)
class BarDecision:
    action: BarAction
    exit_price: float | None
    position_fraction: float


def evaluate_long_bar(
    *,
    high: float,
    low: float,
    stop_price: float,
    take_profit_1: float,
) -> BarDecision:
    """Resolve a long-position bar, conservatively checking the stop first."""
    if low <= stop_price:
        return BarDecision(BarAction.STOP, stop_price, 1.0)
    if high >= take_profit_1:
        return BarDecision(BarAction.TAKE_PROFIT_1, take_profit_1, 0.5)
    return BarDecision(BarAction.NONE, None, 0.0)


class PositionRegistry:
    """Track active symbol/direction pairs and reject duplicate exposure."""

    def __init__(self) -> None:
        self._active: set[tuple[str, str]] = set()

    def try_open(self, symbol: str, direction: str) -> bool:
        key = (symbol, direction)
        if key in self._active:
            return False
        self._active.add(key)
        return True

    def close(self, symbol: str, direction: str) -> None:
        self._active.remove((symbol, direction))

    @property
    def count(self) -> int:
        return len(self._active)


@dataclass(frozen=True)
class FundingSettlement:
    timestamp: datetime
    rate: float
    notional: float


def long_funding_cost(
    settlements: Iterable[FundingSettlement],
    *,
    entry_time: datetime,
    exit_time: datetime | None = None,
) -> float:
    """Return funding paid by a long at settlements while it is open.

    Entry is exclusive because a position opened at a settlement timestamp
    did not exist before that settlement. Exit is inclusive because funding
    is applied before an exit occurring at the same timestamp.
    """
    return sum(
        event.notional * event.rate
        for event in settlements
        if entry_time < event.timestamp
        and (exit_time is None or event.timestamp <= exit_time)
    )
