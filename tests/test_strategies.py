import pytest

from quantarc.strategies import get_strategy


@pytest.mark.parametrize("name", ["sma", "rsi", "macd"])
def test_signals_are_binary_and_aligned(ohlcv, name):
    sig = get_strategy(name).generate_signals(ohlcv)
    assert sig.index.equals(ohlcv.index)
    assert set(sig.unique()) <= {0, 1}


def test_sma_flat_during_warmup(ohlcv):
    sig = get_strategy("sma", fast=10, slow=30).generate_signals(ohlcv)
    assert (sig.iloc[:29] == 0).all()


def test_sma_no_lookahead(ohlcv):
    s = get_strategy("sma", fast=10, slow=30)
    full = s.generate_signals(ohlcv)
    truncated = s.generate_signals(ohlcv.iloc[:300])
    assert full.iloc[:300].equals(truncated)


def test_invalid_params():
    with pytest.raises(ValueError):
        get_strategy("sma", fast=50, slow=20)
    with pytest.raises(ValueError):
        get_strategy("rsi", oversold=80, overbought=20)
    with pytest.raises(ValueError):
        get_strategy("nope")
