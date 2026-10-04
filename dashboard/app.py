"""Run:  streamlit run dashboard/app.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import streamlit as st

from quantarc.analytics.drawdown import drawdown_series
from quantarc.runner import SAMPLE_CSV, load_data, run_backtest
from quantarc.strategies import REGISTRY

st.set_page_config(page_title="QuantArc", layout="wide")
st.title("QuantArc backtester")

with st.sidebar:
    st.header("Data")
    source = st.radio("Source", ["csv", "yfinance"], format_func=lambda s: "Sample CSV" if s == "csv" else "Yahoo Finance")
    symbol = st.text_input("Symbol", "AAPL", disabled=source == "csv")
    c1, c2 = st.columns(2)
    start = c1.text_input("Start", "")
    end = c2.text_input("End", "")

    st.header("Strategy")
    name = st.selectbox("Strategy", list(REGISTRY))
    params = {}
    if name == "sma":
        params = {"fast": st.number_input("Fast", 2, 200, 20), "slow": st.number_input("Slow", 3, 400, 50)}
    elif name == "rsi":
        params = {"period": st.number_input("Period", 2, 50, 14),
                  "oversold": st.number_input("Oversold", 5, 50, 30),
                  "overbought": st.number_input("Overbought", 50, 95, 70)}
    elif name == "macd":
        params = {"fast": st.number_input("Fast", 2, 50, 12), "slow": st.number_input("Slow", 3, 100, 26),
                  "signal": st.number_input("Signal", 2, 50, 9)}

    st.header("Execution & risk")
    cash = st.number_input("Initial cash", 1_000.0, 10_000_000.0, 100_000.0, step=1_000.0)
    commission = st.number_input("Commission (%)", 0.0, 2.0, 0.1, step=0.01) / 100
    slippage = st.number_input("Slippage (%)", 0.0, 2.0, 0.05, step=0.01) / 100
    use_sl = st.checkbox("Stop loss")
    sl = st.number_input("Stop loss (%)", 0.5, 50.0, 5.0) / 100 if use_sl else None
    use_tp = st.checkbox("Take profit")
    tp = st.number_input("Take profit (%)", 0.5, 100.0, 10.0) / 100 if use_tp else None
    frac = st.slider("Position fraction", 0.1, 1.0, 1.0)
    run = st.button("Run backtest", type="primary", use_container_width=True)

if run:
    try:
        data = load_data(source, symbol, None, start or None, end or None)
        res = run_backtest(data, name, params, cash, commission, slippage, sl, tp, frac)
    except Exception as e:  # surface any input problem in the UI
        st.error(str(e))
        st.stop()

    m = res.metrics
    cols = st.columns(6)
    cols[0].metric("Total return", f"{m['total_return']:.1%}", f"B&H {m['buy_hold_return']:.1%}")
    cols[1].metric("CAGR", f"{m['cagr']:.1%}")
    cols[2].metric("Sharpe", f"{m['sharpe']:.2f}")
    cols[3].metric("Max drawdown", f"{m['max_drawdown']:.1%}")
    cols[4].metric("Trades", m["num_trades"])
    cols[5].metric("Win rate", f"{m['win_rate']:.0%}")

    bh = data["close"].loc[res.equity_curve.index]
    bh = bh / bh.iloc[0] * cash
    st.subheader("Equity curve vs buy & hold")
    st.line_chart(pd.DataFrame({"Strategy": res.equity_curve, "Buy & hold": bh}))
    st.subheader("Drawdown")
    st.area_chart(drawdown_series(res.equity_curve))

    left, right = st.columns(2)
    with left:
        st.subheader("Metrics")
        st.dataframe(pd.Series(m, name="value").astype(str), use_container_width=True)
    with right:
        st.subheader("Trades")
        st.dataframe(res.trades_frame(), use_container_width=True)
else:
    st.info(f"Pick a strategy and press **Run backtest**. Sample data: `{SAMPLE_CSV.name}`")
