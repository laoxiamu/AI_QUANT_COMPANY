# Backtest Rule Tests

These pytest tests use only synthetic in-memory inputs. They do not read
market data, call an exchange, or make network requests.

From the project root:

```bash
cd 06_RESEARCH/CODE
python3 -m pytest tests/
```

The suite covers:

- same-bar stop-loss priority over take-profit;
- rejection of an active same-symbol, same-direction position;
- long-position funding costs at explicit settlement timestamps.

The small rule implementations live in `06_RESEARCH/CODE/backtest_rules.py`.
The tests intentionally do not import or modify the full strategy backtest.
