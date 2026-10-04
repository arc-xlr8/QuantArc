from __future__ import annotations

import math
from dataclasses import dataclass, field

import pandas as pd

from .trade import Trade


@dataclass
class BacktestResult:
    strategy: str
    equity_curve: pd.Series
    signals: pd.Series
    trades: list[Trade] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    initial_cash: float = 0.0

    @property
    def final_equity(self) -> float:
        return float(self.equity_curve.iloc[-1])

    def trades_frame(self) -> pd.DataFrame:
        return pd.DataFrame([t.to_dict() for t in self.trades])

    def to_dict(self) -> dict:
        return {
            "strategy": self.strategy,
            "initial_cash": self.initial_cash,
            "final_equity": self.final_equity,
            "metrics": {k: (None if isinstance(v, float) and not math.isfinite(v) else v)
                        for k, v in self.metrics.items()},
            "equity_curve": [{"t": str(t), "v": float(v)} for t, v in self.equity_curve.items()],
            "trades": [t.to_dict() for t in self.trades],
        }
