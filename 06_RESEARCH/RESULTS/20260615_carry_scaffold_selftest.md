# Carry Delta-Neutral Scaffold Self-Test

**Task:** `CARRY_SCAFFOLD`  
**Scope:** code and synthetic tests only  
**Data execution:** no real `*_FUNDING_8H.csv` or `*_MARK_1H.csv` was run

## Modules

- `carry/data.py`: strict pre-cutoff UTC CSV loading, column aliases, malformed/
  invalid/duplicate/cutoff row audit, and mark-as-spot fallback.
- `carry/costs.py`: explicit spot/perpetual fee, normal/event slippage, and
  entry/exit basis cost components.
- `carry/config.py`: frozen engine parameters and leverage validation.
- `carry/trigger.py`: OI percentile `<= 0.01` position scale and 24-hour
  refractory state machine.
- `carry/engine.py`: isolated-margin long-spot/short-perpetual state machine,
  funding, daily delta checks, costs, buffer events, and liquidation events.
- `carry/portfolio.py`: frozen BTCUSDT 70% / ETHUSDT 30% aggregation and
  with/without-trigger equity curves.
- `carry/metrics.py`: net E[R], profit factor, positive-year ratio, geometric
  growth, annualized log growth, MDD, three time-based WF segments, moving
  block bootstrap, and cluster bootstrap.
- `carry/cli.py`: future real-data runner with explicit blind-review,
  Holdout-seal, and pre-Holdout-only confirmation gates.

## Conservative Defaults

- Cutoff is exclusive: `< 2024-12-10T00:00:00Z`.
- Paths containing a `HOLDOUT` component and cutoffs later than the frozen
  date are rejected before input files are opened.
- All timestamps are normalized to UTC; malformed CSV records are skipped,
  invalid timestamp/value rows are dropped and counted.
- Spot price falls back to mark price unless an explicit spot column exists.
- Fee is 0.10% per traded leg; normal slippage is 0.10% per traded leg;
  event slippage is 0.30% per traded leg.
- Basis entry/exit rates default to zero because no fixed basis rate is frozen;
  both are explicit parameters and their absolute costs are reported.
- Perpetual leverage defaults to 2x and may not exceed 2x. Opening costs are
  pre-funded so fee deductions do not push effective leverage above the cap.
- Delta is checked only at exactly 00:00:00 UTC. Rebalancing uses a strict
  `drift > 5%` condition and synchronously reduces both legs if margin limits
  prevent restoring the prior notional.
- Minimum maintenance margin rate defaults to 0.50%; the buffer is 3x the
  exchange minimum. A `buffer_breach` reduces both legs to the buffered
  notional. Only a breach below exchange minimum logs `liquidation` and forces
  the short leg to zero, leaving spot delta exposure until normal closure.
- Funding at a timestamp is settled before a same-timestamp OI signal changes
  future position size. This avoids using contemporaneous OI to evade funding.
- OI trigger scale is 50% for 24 hours. Signals inside an active refractory
  period do not extend it; a still-active signal at expiry starts a new period.
- Moving-block bootstrap defaults: block size 9 funding observations,
  10,000 iterations, seed `20260615`. Block size remains parameterized.
- Three WF segments use equal elapsed-time thirds; no threshold is fitted.

## Synthetic Test Result

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest \
  06_RESEARCH/CODE/carry/tests -q
```

Result: `25 passed`.

Covered behaviors include UTC/cutoff/bad-row loading, funding direction, price
neutrality, strict daily rebalance timing, no hidden hourly retargeting, full
per-leg costs, 24-hour OI refractory behavior, separate buffer/liquidation
events, 2x leverage enforcement, frozen portfolio weights, and known
block/cluster bootstrap distributions. It also covers pre-funding and
post-negative-funding margin checks, equal starting capital for both trigger
variants, Holdout path rejection, and frozen-cutoff enforcement.

## Future Real-Data Command

Run only after blind-review approval and custodian Holdout sealing:

```bash
PYTHONPATH=06_RESEARCH/CODE python3 -m carry.cli \
  --data-dir 06_RESEARCH/DATA/FUTURES \
  --btc-oi 06_RESEARCH/DATA/FUTURES/BTCUSDT_OI_6H_PERCENTILE.csv \
  --eth-oi 06_RESEARCH/DATA/FUTURES/ETHUSDT_OI_6H_PERCENTILE.csv \
  --cutoff 2024-12-10T00:00:00Z \
  --output 06_RESEARCH/CODE/output/carry_backtest_summary.json \
  --confirm-prereg-approved \
  --confirm-holdout-sealed \
  --confirm-preholdout-only
```

This command was documented but not executed in this task.

## Scope Declaration

**This scaffold did not produce any real-data acceptance value, acceptance
decision, or edge conclusion. It did not read Holdout or `01_MEMORY_CORE/`.**
