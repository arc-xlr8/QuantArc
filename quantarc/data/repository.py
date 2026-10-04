from __future__ import annotations

from pathlib import Path

import pandas as pd

from .providers.base import DataProvider, normalize_ohlcv
from .providers.yfinance_provider import YFinanceProvider

DEFAULT_CACHE = Path.home() / ".cache" / "quantarc"


class DataRepository:
    """Single entry point for price data: local CSVs or a provider,
    with an on-disk CSV cache for provider downloads."""

    def __init__(self, provider: DataProvider | None = None,
                 cache_dir: Path | str | None = DEFAULT_CACHE):
        self.provider = provider or YFinanceProvider()
        self.cache_dir = Path(cache_dir) if cache_dir else None

    @staticmethod
    def load_csv(path: str | Path) -> pd.DataFrame:
        return normalize_ohlcv(pd.read_csv(path))

    def get(self, symbol, start=None, end=None, interval="1d", use_cache=True) -> pd.DataFrame:
        cache_file = None
        if self.cache_dir and use_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = self.cache_dir / f"{symbol}_{interval}_{start}_{end}.csv"
            if cache_file.exists():
                return self.load_csv(cache_file)
        df = self.provider.fetch(symbol, start, end, interval)
        if cache_file is not None:
            df.to_csv(cache_file)
        return df

    @staticmethod
    def slice(df: pd.DataFrame, start=None, end=None) -> pd.DataFrame:
        if start:
            df = df[df.index >= pd.Timestamp(start)]
        if end:
            df = df[df.index <= pd.Timestamp(end)]
        return df
