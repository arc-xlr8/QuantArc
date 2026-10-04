from __future__ import annotations

import pandas as pd

from . import metrics as m
from .drawdown import longest_drawdown_days, max_drawdown


def trade_stats(trades) -> dict:
    if not trades:
        return {"num_trades": 0, "win_rate": 0.0, "profit_factor": 0.0,
                "avg_win": 0.0, "avg_loss": 0.0, "avg_trade_return": 0.0,
                "total_fees": 0.0}
    pnls = pd.Series([t.pnl for t in trades])
    wins, losses = pnls[pnls > 0], pnls[pnls <= 0]
    gross_loss = abs(losses.sum())
    return {
        "num_trades": len(trades),
        "win_rate": float(len(wins) / len(trades)),
        "profit_factor": float(wins.sum() / gross_loss) if gross_loss > 0 else float("inf") if len(wins) else 0.0,
        "avg_win": float(wins.mean()) if len(wins) else 0.0,
        "avg_loss": float(losses.mean()) if len(losses) else 0.0,
        "avg_trade_return": float(pd.Series([t.return_pct for t in trades]).mean()),
        "total_fees": float(sum(t.fees for t in trades)),
    }


def summarize(result, close: pd.Series, periods_per_year: int = 252) -> dict:
    """Headline metrics for a backtest, plus a buy & hold benchmark."""
    eq = result.equity_curve
    rets = m.returns(eq)
    bh = close.loc[eq.index] / close.loc[eq.index].iloc[0] * result.initial_cash
    out = {
        "total_return": m.total_return(eq),
        "cagr": m.cagr(eq),
        "volatility": m.annual_volatility(rets, periods_per_year),
        "sharpe": m.sharpe_ratio(rets, periods_per_year=periods_per_year),
        "sortino": m.sortino_ratio(rets, periods_per_year=periods_per_year),
        "max_drawdown": max_drawdown(eq),
        "calmar": m.calmar_ratio(eq),
        "longest_drawdown_days": longest_drawdown_days(eq),
        "buy_hold_return": m.total_return(bh),
        "buy_hold_max_drawdown": max_drawdown(bh),
    }
    out.update(trade_stats(result.trades))
    return out
