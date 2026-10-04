# QuantArc

Python backtesting framework: pluggable strategies, a no-look-ahead engine (signal on bar *t* fills at the open of *t+1*), commission/slippage, stop-loss/take-profit, analytics, a FastAPI service and a Streamlit dashboard.

```bash
pip install -r requirements.txt
pytest                              # run tests
uvicorn api.main:app --reload       # API  -> http://localhost:8000/docs
streamlit run dashboard/app.py      # dashboard
```

```python
from quantarc.runner import load_data, run_backtest
data = load_data("csv")             # bundled AAPL sample, or load_data("yfinance", "MSFT", start="2020-01-01")
res = run_backtest(data, "rsi", {"period": 14}, stop_loss=0.05)
print(res.metrics)
```

Add a strategy: subclass `Strategy`, return a 0/1 target-position Series from `generate_signals`, register it in `quantarc/strategies/__init__.py`.
