from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

OHLCV = ["open", "high", "low", "close", "volume"]


def normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce raw provider/CSV output into a clean lowercase OHLCV frame with a
    sorted DatetimeIndex. Handles yfinance MultiIndex columns and the extra
    header rows (Ticker / Date) that newer yfinance versions write to CSV."""
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if not isinstance(df.index, pd.DatetimeIndex):
        first = df.columns[0]  # date column in a CSV
        raw = df[first]
        parsed = pd.to_datetime(raw, format="ISO8601", errors="coerce")
        if parsed.isna().all():  # non-ISO dates: fall back to flexible parsing
            parsed = pd.to_datetime(raw, errors="coerce")
        df.index = parsed
        df = df.drop(columns=[first])
    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[~df.index.isna()]

    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = [c for c in OHLCV if c not in df.columns]
    if missing:
        raise ValueError(f"Data is missing required columns: {missing}")

    df = df[OHLCV].apply(pd.to_numeric, errors="coerce").dropna()
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    df.index.name = "date"
    return df[~df.index.duplicated(keep="last")].sort_index()


class DataProvider(ABC):
    """Interface every market-data source implements."""

    @abstractmethod
    def fetch(self, symbol: str, start: str | None = None, end: str | None = None,
              interval: str = "1d") -> pd.DataFrame:
        """Return a normalized OHLCV DataFrame."""
