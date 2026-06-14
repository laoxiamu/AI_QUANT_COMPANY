"""Configuration with conservative frozen defaults."""

from __future__ import annotations

from dataclasses import dataclass, field

from carry.costs import CostModel


@dataclass(frozen=True)
class EngineConfig:
    base_notional: float = 100_000.0
    leverage: float = 2.0
    delta_rebalance_threshold: float = 0.05
    minimum_maintenance_margin_rate: float = 0.005
    maintenance_buffer_multiple: float = 3.0
    close_at_end: bool = True
    entry_basis_rate: float = 0.0
    exit_basis_rate: float = 0.0
    costs: CostModel = field(default_factory=CostModel)

    def __post_init__(self) -> None:
        if self.base_notional <= 0:
            raise ValueError("base_notional must be positive")
        if not 0 < self.leverage <= 2.0:
            raise ValueError("leverage must be in (0, 2]")
        if self.delta_rebalance_threshold < 0:
            raise ValueError("delta_rebalance_threshold must be non-negative")
        if not 0 < self.minimum_maintenance_margin_rate < 1:
            raise ValueError(
                "minimum_maintenance_margin_rate must be in (0, 1)"
            )
        if self.maintenance_buffer_multiple < 1:
            raise ValueError("maintenance_buffer_multiple must be >= 1")
