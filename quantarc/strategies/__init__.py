from .base import Strategy
from .macd import MACDStrategy
from .rsi import RSIMeanReversion
from .sma import SMACrossover

REGISTRY: dict[str, type[Strategy]] = {
    "sma": SMACrossover,
    "rsi": RSIMeanReversion,
    "macd": MACDStrategy,
}


def get_strategy(name: str, **params) -> Strategy:
    try:
        cls = REGISTRY[name.lower()]
    except KeyError:
        raise ValueError(f"Unknown strategy {name!r}. Available: {sorted(REGISTRY)}") from None
    return cls(**params)


__all__ = ["Strategy", "SMACrossover", "RSIMeanReversion", "MACDStrategy", "REGISTRY", "get_strategy"]
