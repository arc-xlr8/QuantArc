from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Strategy(ABC):
    """Maps price data to a *target position* per bar: 1 = long, 0 = flat.
    The engine executes a signal from bar t at the open of bar t+1 (no look-ahead)."""

    name: str = "strategy"

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        ...

    @property
    def params(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith("_")}

    def __repr__(self) -> str:
        args = ", ".join(f"{k}={v}" for k, v in self.params.items())
        return f"{type(self).__name__}({args})"

    @staticmethod
    def _finalize(signal: pd.Series, index: pd.Index) -> pd.Series:
        return signal.reindex(index).fillna(0).astype(int).rename("signal")
