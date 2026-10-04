from __future__ import annotations

import pandas as pd

from .base import Strategy


class MACDStrategy(Strategy):
    name = "macd"

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        if fast >= slow:
            raise ValueError("fast must be smaller than slow")
        self.fast, self.slow, self.signal = fast, slow, signal

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["close"]
        macd = close.ewm(span=self.fast, adjust=False).mean() - close.ewm(span=self.slow, adjust=False).mean()
        signal_line = macd.ewm(span=self.signal, adjust=False).mean()
        sig = (macd > signal_line).astype(int)
        sig.iloc[: self.slow] = 0  # warm-up
        return self._finalize(sig, data.index)
