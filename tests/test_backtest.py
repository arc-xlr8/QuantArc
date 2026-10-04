import pytest

from quantarc.engine.backtest import Backtester
from quantarc.engine.execution import ExecutionHandler
from quantarc.engine.risk import RiskManager
from quantarc.runner import run_backtest
from quantarc.strategies import get_strategy


def test_runs_and_reports_metrics(ohlcv):
    res = run_backtest(ohlcv, "sma", {"fast": 10, "slow": 30})
    assert len(res.equity_curve) == len(ohlcv)
    assert res.metrics["num_trades"] == len(res.trades) > 0
    assert res.final_equity > 0


def test_no_costs_cash_conservation(ohlcv):
    """Final equity must equal initial cash + sum of trade P&L (no open position at end)."""
    res = run_backtest(ohlcv, "sma", {"fast": 10, "slow": 30}, commission=0.0, slippage=0.0)
    assert res.final_equity == pytest.approx(res.initial_cash + sum(t.pnl for t in res.trades))


def test_costs_reduce_returns(ohlcv):
    free = run_backtest(ohlcv, "macd", commission=0.0, slippage=0.0)
    costly = run_backtest(ohlcv, "macd", commission=0.005, slippage=0.002)
    assert costly.final_equity < free.final_equity


def test_executes_next_bar_open(ohlcv):
    res = run_backtest(ohlcv, "sma", {"fast": 10, "slow": 30}, commission=0.0, slippage=0.0)
    first = res.trades[0]
    signal_day = res.signals[res.signals == 1].index[0]
    assert first.entry_time > signal_day
    assert first.entry_price == pytest.approx(ohlcv.loc[first.entry_time, "open"])


def test_stop_loss_limits_trade_loss(ohlcv):
    res = run_backtest(ohlcv, "sma", {"fast": 5, "slow": 20}, stop_loss=0.03,
                       commission=0.0, slippage=0.0)
    stopped = [t for t in res.trades if t.exit_reason == "stop_loss"]
    assert stopped, "expected at least one stop-out on this series"
    # gap-downs can exceed the stop, but a stop exit is never above the stop level
    assert all(t.exit_price <= t.entry_price * 0.97 + 1e-9 for t in stopped)


def test_never_invests_more_than_cash(ohlcv):
    res = run_backtest(ohlcv, "sma", {"fast": 10, "slow": 30})
    assert (res.equity_curve > 0).all()
    assert all(t.quantity == int(t.quantity) for t in res.trades)


def test_empty_data_raises(ohlcv):
    bt = Backtester(get_strategy("sma"), execution=ExecutionHandler(), risk=RiskManager())
    with pytest.raises(ValueError):
        bt.run(ohlcv.iloc[0:0])


def test_sample_csv_if_present():
    from quantarc.runner import SAMPLE_CSV, load_data
    if not SAMPLE_CSV.exists():
        pytest.skip("sample CSV not in this checkout")
    data = load_data("csv")
    res = run_backtest(data, "sma")
    assert len(res.equity_curve) == len(data)
