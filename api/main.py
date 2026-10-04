"""Run:  uvicorn api.main:app --reload"""
from __future__ import annotations

from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from quantarc.runner import load_data, run_backtest
from quantarc.strategies import REGISTRY

app = FastAPI(title="QuantArc API", version="0.1.0")


class BacktestRequest(BaseModel):
    symbol: str = "AAPL"
    source: Literal["csv", "yfinance"] = "csv"
    csv_path: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    strategy: str = "sma"
    params: dict = Field(default_factory=dict)
    initial_cash: float = 100_000.0
    commission: float = 0.001
    slippage: float = 0.0005
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_fraction: float = 1.0
    allow_fractional: bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/strategies")
def strategies():
    import inspect
    return {
        name: {k: v.default for k, v in inspect.signature(cls.__init__).parameters.items()
               if k != "self"}
        for name, cls in REGISTRY.items()
    }


@app.post("/backtest")
def backtest(req: BacktestRequest):
    try:
        data = load_data(req.source, req.symbol, req.csv_path, req.start, req.end)
        result = run_backtest(
            data, req.strategy, req.params, req.initial_cash, req.commission, req.slippage,
            req.stop_loss, req.take_profit, req.position_fraction, req.allow_fractional,
        )
    except (ValueError, FileNotFoundError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return result.to_dict()
