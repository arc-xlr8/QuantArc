from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd


@dataclass(frozen=True)
class Trade:
    """A completed round trip (entry -> exit), long-only."""

    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_price: float
    exit_price: float
    quantity: float
    fees: float
    exit_reason: str = "signal"  # signal | stop_loss | take_profit | end_of_data

    @property
    def pnl(self) -> float:
        return (self.exit_price - self.entry_price) * self.quantity - self.fees

    @property
    def return_pct(self) -> float:
        cost = self.entry_price * self.quantity
        return self.pnl / cost if cost else 0.0

    @property
    def days_held(self) -> int:
        return (self.exit_time - self.entry_time).days

    def to_dict(self) -> dict:
        d = asdict(self)
        d["entry_time"] = str(self.entry_time)
        d["exit_time"] = str(self.exit_time)
        d["pnl"] = self.pnl
        d["return_pct"] = self.return_pct
        d["days_held"] = self.days_held
        return d
