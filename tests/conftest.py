import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def ohlcv() -> pd.DataFrame:
    """Deterministic synthetic daily bars with a trend and cycles."""
    n = 600
    idx = pd.bdate_range("2020-01-01", periods=n)
    rng = np.random.default_rng(42)
    close = 100 + np.cumsum(rng.normal(0.1, 1.2, n)) + 8 * np.sin(np.arange(n) / 20)
    close = np.maximum(close, 5)
    open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.002, n))
    high = np.maximum(open_, close) * 1.01
    low = np.minimum(open_, close) * 0.99
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close,
                         "volume": 1_000_000}, index=idx)
