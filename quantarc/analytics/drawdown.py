from __future__ import annotations

import pandas as pd


def drawdown_series(equity: pd.Series) -> pd.Series:
    """Fractional drawdown from the running peak (<= 0)."""
    return equity / equity.cummax() - 1.0


def max_drawdown(equity: pd.Series) -> float:
    return float(drawdown_series(equity).min()) if len(equity) else 0.0


def longest_drawdown_days(equity: pd.Series) -> int:
    """Longest calendar-day stretch spent below a previous equity peak."""
    underwater = drawdown_series(equity) < 0
    longest, start = 0, None
    for ts, under in underwater.items():
        if under and start is None:
            start = ts
        elif not under and start is not None:
            longest, start = max(longest, (ts - start).days), None
    if start is not None:
        longest = max(longest, (equity.index[-1] - start).days)
    return longest
