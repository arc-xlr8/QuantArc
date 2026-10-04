from __future__ import annotations

import pandas as pd

from .base import Strategy


class SMACrossover(Strategy):
    name = "sma"

    def __init__(self, fast: int = 20, slow: int = 50):
        if fast >= slow:
            raise ValueError("fast must be smaller than slow")
        self.fast, self.slow = fast, slow

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["close"]
        fast = close.rolling(self.fast).mean()
        slow = close.rolling(self.slow).mean()
        sig = (fast > slow) & slow.notna()
        return self._finalize(sig.astype(int), data.index)
