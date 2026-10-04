from __future__ import annotations

import numpy as np
import pandas as pd

from .base import Strategy


def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)
    return rsi.where(loss != 0, 100.0).where(gain.notna())


class RSIMeanReversion(Strategy):
    """Go long when RSI < oversold; go flat when RSI > overbought."""

    name = "rsi"

    def __init__(self, period: int = 14, oversold: float = 30, overbought: float = 70):
        if oversold >= overbought:
            raise ValueError("oversold must be below overbought")
        self.period, self.oversold, self.overbought = period, oversold, overbought

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        rsi = compute_rsi(data["close"], self.period)
        state = pd.Series(np.nan, index=data.index)
        state[rsi < self.oversold] = 1
        state[rsi > self.overbought] = 0
        return self._finalize(state.ffill(), data.index)
