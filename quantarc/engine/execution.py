from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Fill:
    side: str  # "buy" | "sell"
    price: float  # after slippage
    quantity: float
    commission: float


class ExecutionHandler:
    """Simulates fills with proportional commission and adverse slippage."""

    def __init__(self, commission_pct: float = 0.001, slippage_pct: float = 0.0005):
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct

    def fill(self, side: str, price: float, quantity: float) -> Fill:
        sign = 1 if side == "buy" else -1
        px = price * (1 + sign * self.slippage_pct)
        return Fill(side, px, quantity, px * quantity * self.commission_pct)

    def max_affordable(self, cash: float, price: float) -> float:
        """Largest quantity whose cost + commission fits in `cash`."""
        px = price * (1 + self.slippage_pct)
        return max(cash / (px * (1 + self.commission_pct)), 0.0)
