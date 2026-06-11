# REPORT_R2_A2_EVENT_STUDY

**Task:** TASK_R2_A2_EVENT_STUDY
**Generated UTC:** 2026-06-11T14:46:21Z
**Conclusion:** FAILED

## Deliverables

- CODE: `06_RESEARCH/CODE/a2_event_study.py`
- JSON: `06_RESEARCH/CODE/output/a2_event_study_results.json`
- RESULTS: `06_RESEARCH/RESULTS/20260611_a2_event_study.md`
- TEST: `06_RESEARCH/CODE/tests/test_a2_event_study.py`

## Execution Summary

- Work events loaded: 874
- Price symbols loaded: BTCUSDT, ETHUSDT, SOLUSDT
- Seed fixed: 20260611
- Six registered tests completed: yes
- Final binary decision: **FAILED**

## Acceptance Self-check

- pytest green: 3 passed (`python3 -m pytest -q 06_RESEARCH/CODE/tests/test_a2_event_study.py`)
- `seed=20260611` fixed in code and output: pass
- Six tests include raw and Bonferroni p-values for t-test and bootstrap: pass
- Conclusion is binary PASSED/FAILED: pass
- Analysis script does not reference the sealed event path: pass
- UTC timestamps: pass
- No strategy performance metrics reported: pass

## Decision Rule Result

- Significant main windows by both methods: []
- Direction-wrong main windows: ['24h', '48h', '72h']
- Negative-side monotonicity all windows direction-consistent: True
