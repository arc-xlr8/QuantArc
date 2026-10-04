from __future__ import annotations

import pandas as pd

from ..analytics.performance import summarize
from ..models.results import BacktestResult
from ..strategies.base import Strategy
from .execution import ExecutionHandler
from .portfolio import Portfolio
from .risk import RiskManager


class Backtester:
    """Event-style daily-bar backtester.

    Per bar t: (1) act on the signal from bar t-1 at the open, (2) check
    protective exits inside the bar, (3) mark to market at the close.
    """

    def __init__(self, strategy: Strategy, initial_cash: float = 100_000.0,
                 execution: ExecutionHandler | None = None, risk: RiskManager | None = None,
                 periods_per_year: int = 252):
        self.strategy = strategy
        self.initial_cash = initial_cash
        self.execution = execution or ExecutionHandler()
        self.risk = risk or RiskManager()
        self.periods_per_year = periods_per_year

    def run(self, data: pd.DataFrame) -> BacktestResult:
        if data.empty:
            raise ValueError("Cannot backtest on empty data")
        signals = self.strategy.generate_signals(data)
        pf = Portfolio(self.initial_cash)
        blocked = False  # after a protective exit, wait for the signal to reset

        prev_signal = 0
        for ts, bar in data.iterrows():
            target = prev_signal
            if target == 0:
                blocked = False

            # 1) signal-driven trades at the open
            if target == 1 and not pf.in_position and not blocked:
                qty = self.risk.position_size(self.execution.max_affordable(pf.cash, bar.open))
                if qty > 0:
                    pf.open(ts, self.execution.fill("buy", bar.open, qty))
            elif target == 0 and pf.in_position:
                pf.close(ts, self.execution.fill("sell", bar.open, pf.quantity))

            # 2) protective exits during the bar
            if pf.in_position:
                hit = self.risk.check_exit(pf.entry_price, bar.open, bar.high, bar.low)
                if hit:
                    price, reason = hit
                    pf.close(ts, self.execution.fill("sell", price, pf.quantity), reason)
                    blocked = True

            # 3) mark to market
            pf.mark(ts, bar.close)
            prev_signal = int(signals.loc[ts])

        if pf.in_position:  # liquidate so the last trade is counted
            ts, last = data.index[-1], data.iloc[-1]
            pf.close(ts, self.execution.fill("sell", last.close, pf.quantity), "end_of_data")
            pf.mark(ts, last.close)

        result = BacktestResult(
            strategy=repr(self.strategy),
            equity_curve=pf.equity_curve,
            signals=signals,
            trades=pf.trades,
            initial_cash=self.initial_cash,
        )
        result.metrics = summarize(result, data["close"], self.periods_per_year)
        return result
