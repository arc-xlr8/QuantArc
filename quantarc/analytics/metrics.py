from __future__ import annotations

import numpy as np
import pandas as pd

from .drawdown import max_drawdown


def returns(equity: pd.Series) -> pd.Series:
    return equity.pct_change().dropna()


def total_return(equity: pd.Series) -> float:
    return float(equity.iloc[-1] / equity.iloc[0] - 1) if len(equity) > 1 else 0.0


def cagr(equity: pd.Series) -> float:
    if len(equity) < 2:
        return 0.0
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    if years <= 0 or equity.iloc[0] <= 0 or equity.iloc[-1] <= 0:
        return 0.0
    return float((equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1)


def annual_volatility(rets: pd.Series, periods_per_year: int = 252) -> float:
    return float(rets.std(ddof=1) * np.sqrt(periods_per_year)) if len(rets) > 1 else 0.0


def sharpe_ratio(rets: pd.Series, risk_free: float = 0.0, periods_per_year: int = 252) -> float:
    if len(rets) < 2:
        return 0.0
    excess = rets - risk_free / periods_per_year
    sd = excess.std(ddof=1)
    return float(excess.mean() / sd * np.sqrt(periods_per_year)) if sd > 0 else 0.0


def sortino_ratio(rets: pd.Series, risk_free: float = 0.0, periods_per_year: int = 252) -> float:
    if len(rets) < 2:
        return 0.0
    excess = rets - risk_free / periods_per_year
    downside = np.sqrt((np.minimum(excess, 0) ** 2).mean())
    return float(excess.mean() / downside * np.sqrt(periods_per_year)) if downside > 0 else 0.0


def calmar_ratio(equity: pd.Series) -> float:
    mdd = abs(max_drawdown(equity))
    return float(cagr(equity) / mdd) if mdd > 0 else 0.0
