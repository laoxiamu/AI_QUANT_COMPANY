# REPORT 0B6 - Backtest Unit Tests

**Task:** `0B-6-v5`  
**Date:** 2026-06-06  
**Result:** PASS

## Delivered

- Added `06_RESEARCH/CODE/backtest_rules.py`, a standalone deterministic
  rule module with no market-data or network dependency.
- Added `06_RESEARCH/CODE/tests/test_backtest_rules.py`.
- Added `06_RESEARCH/CODE/tests/README_TESTS.md`.
- Installed pytest 9.0.3 in the current Python 3.13.5 environment.
- Did not modify any full strategy backtest, Memory Core, project management
  file, or `CLAUDE.md`.

## Coverage

| Rule | Variants | Result |
|---|---:|---|
| Same-bar stop priority | TP only; stop only; both touched | 3 PASS |
| Position conflict | duplicate rejected; other symbol accepted; reopen after close | 3 PASS |
| Funding cost | three settlements; variable rates/notionals; stop after close | 3 PASS |
| **Total** | **9 tests** | **9 PASS** |

The old `06_RESEARCH/CODE/test_backtest_rules.py` was reviewed before
implementation. Its useful coverage was retained:

- same-bar stop wins over profit targets;
- an active same-direction position rejects another signal;
- a positive funding rate is paid by a long position.

The old file was not edited because this task's write boundary only permits
the new `tests/` suite and the independent rule module.

## Test Output

Command:

```bash
cd 06_RESEARCH/CODE
python3 -m pytest tests/ -v
```

Output:

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.0.3, pluggy-1.6.0
collected 9 items

tests/test_backtest_rules.py::test_take_profit_executes_when_stop_is_not_touched PASSED
tests/test_backtest_rules.py::test_stop_executes_when_take_profit_is_not_touched PASSED
tests/test_backtest_rules.py::test_stop_wins_when_same_bar_touches_stop_and_take_profit PASSED
tests/test_backtest_rules.py::test_same_symbol_same_direction_signal_is_rejected PASSED
tests/test_backtest_rules.py::test_different_symbol_same_direction_signal_is_accepted PASSED
tests/test_backtest_rules.py::test_same_symbol_signal_is_accepted_after_position_closes PASSED
tests/test_backtest_rules.py::test_three_funding_settlements_are_charged_once_each PASSED
tests/test_backtest_rules.py::test_multiple_settlements_use_each_rate_and_notional_once PASSED
tests/test_backtest_rules.py::test_funding_stops_after_position_closes PASSED

============================== 9 passed in 0.01s ===============================
```

Timed quiet run: `9 passed in 0.03s`; total process time `0.34s`, below the
5-second requirement.

## Notes

The task example says that 24 four-hour bars equal four days but expects only
three funding settlements. Four days normally contain twelve 8-hour
settlements. The tests avoid encoding that contradiction: settlement events
are explicit, and the three-event case verifies that each event is charged
exactly once.

No confirmed bug was found in the reviewed existing backtest logic for these
three rules. The new tests validate the independent canonical primitives;
the full strategy backtest does not yet import this module, so these are unit
tests rather than full-script integration tests.

## Claude 待处理事项

1. **PASS/FAIL:** 9 PASS, 0 FAIL, 0 ERROR.
2. **P1-4 audit item:** May be marked resolved for the requested repeatable
   unit-test infrastructure. Track full-backtest integration as a separate
   follow-up if production scripts should be forced to use these primitives.
3. **Existing backtest bugs:** None confirmed. Integration drift remains a
   residual risk because the full backtest currently has its own inline rule
   implementation.
4. **Suggested `CURRENT_STATE` draft:**  
   `回测规则自动测试：✅ 2026-06-06完成；pytest 9/9通过，覆盖同K线止损优先、同品种同向持仓冲突、资金费率结算；纯合成离线数据，总运行<1秒。`

【需要Claude】
