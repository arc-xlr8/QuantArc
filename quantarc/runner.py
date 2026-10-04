"""Glue shared by the API and dashboard: load data, build strategy, run."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .data.repository import DataRepository
from .engine.backtest import Backtester
from .engine.execution import ExecutionHandler
from .engine.risk import RiskManager
from .models.results import BacktestResult
from .strategies import get_strategy

SAMPLE_CSV = Path(__file__).parent / "data" / "data_test" / "AAPL_6years.csv"


def load_data(source: str = "csv", symbol: str = "AAPL", csv_path: str | None = None,
              start: str | None = None, end: str | None = None) -> pd.DataFrame:
    repo = DataRepository()
    if source == "csv":
        df = repo.load_csv(csv_path or SAMPLE_CSV)
        return repo.slice(df, start, end)
    if source == "yfinance":
        return repo.get(symbol, start, end)
    raise ValueError(f"Unknown source {source!r}")


def run_backtest(data: pd.DataFrame, strategy: str = "sma", params: dict | None = None,
                 initial_cash: float = 100_000.0, commission: float = 0.001,
                 slippage: float = 0.0005, stop_loss: float | None = None,
                 take_profit: float | None = None, position_fraction: float = 1.0,
                 allow_fractional: bool = False) -> BacktestResult:
    bt = Backtester(
        get_strategy(strategy, **(params or {})),
        initial_cash=initial_cash,
        execution=ExecutionHandler(commission, slippage),
        risk=RiskManager(position_fraction, stop_loss, take_profit, allow_fractional),
    )
    return bt.run(data)
