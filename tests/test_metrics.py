import numpy as np
import pandas as pd
import pytest

from quantarc.analytics import metrics as m
from quantarc.analytics.drawdown import drawdown_series, longest_drawdown_days, max_drawdown


def _eq(values):
    return pd.Series(values, index=pd.bdate_range("2021-01-01", periods=len(values)), dtype=float)


def test_max_drawdown():
    assert max_drawdown(_eq([100, 120, 90, 110])) == pytest.approx(-0.25)


def test_drawdown_never_positive():
    assert (drawdown_series(_eq([100, 105, 95, 110])) <= 0).all()


def test_longest_drawdown():
    eq = _eq([100, 90, 95, 100, 101])  # underwater from bar 1 until bar 3 recovers
    assert longest_drawdown_days(eq) >= 2


def test_total_return_and_cagr_positive():
    eq = _eq(np.linspace(100, 150, 300))
    assert m.total_return(eq) == pytest.approx(0.5)
    assert m.cagr(eq) > 0


def test_sharpe_zero_for_flat_returns():
    assert m.sharpe_ratio(pd.Series([0.0] * 10)) == 0.0


def test_sharpe_sign():
    rng = np.random.default_rng(0)
    assert m.sharpe_ratio(pd.Series(rng.normal(0.002, 0.01, 500))) > 0
    assert m.sharpe_ratio(pd.Series(rng.normal(-0.002, 0.01, 500))) < 0
