from __future__ import annotations

import pandas as pd

from .base import DataProvider, normalize_ohlcv


class YFinanceProvider(DataProvider):
    def fetch(self, symbol, start=None, end=None, interval="1d") -> pd.DataFrame:
        import yfinance as yf  # lazy: offline/CSV use doesn't need it

        raw = yf.download(symbol, start=start, end=end, interval=interval,
                          auto_adjust=True, progress=False)
        if raw is None or raw.empty:
            raise ValueError(f"No data returned for {symbol!r}")
        return normalize_ohlcv(raw)
