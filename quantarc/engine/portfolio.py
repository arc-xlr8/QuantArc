from __future__ import annotations

import pandas as pd

from ..models.trade import Trade
from .execution import Fill


class Portfolio:
    """Tracks cash, a single long position, closed trades and the equity curve."""

    def __init__(self, initial_cash: float = 100_000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.quantity = 0.0
        self.entry_price = 0.0
        self.entry_time: pd.Timestamp | None = None
        self._entry_fees = 0.0
        self.trades: list[Trade] = []
        self._equity: dict[pd.Timestamp, float] = {}

    @property
    def in_position(self) -> bool:
        return self.quantity > 0

    def open(self, ts: pd.Timestamp, fill: Fill) -> None:
        self.cash -= fill.price * fill.quantity + fill.commission
        self.quantity = fill.quantity
        self.entry_price = fill.price
        self.entry_time = ts
        self._entry_fees = fill.commission

    def close(self, ts: pd.Timestamp, fill: Fill, reason: str = "signal") -> Trade:
        self.cash += fill.price * fill.quantity - fill.commission
        trade = Trade(self.entry_time, ts, self.entry_price, fill.price, self.quantity,
                      self._entry_fees + fill.commission, reason)
        self.trades.append(trade)
        self.quantity, self.entry_price, self.entry_time, self._entry_fees = 0.0, 0.0, None, 0.0
        return trade

    def mark(self, ts: pd.Timestamp, price: float) -> None:
        self._equity[ts] = self.cash + self.quantity * price

    @property
    def equity_curve(self) -> pd.Series:
        return pd.Series(self._equity, name="equity", dtype=float)
