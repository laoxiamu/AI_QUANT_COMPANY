# A-2 Funding Extreme Reversal Event Study

**Generated UTC:** 2026-06-11T14:46:21Z
**Conclusion:** FAILED

## Six Registered Tests

| pool | window | n | mean log return | t | t p raw | t p bonf | boot p raw | boot p bonf | direction ok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| neg/P5 | 24h | 318 | -0.00267837 | -0.931137 | 0.823754 | 1 | 0.797241 | 1 | False |
| neg/P5 | 48h | 318 | -0.00434667 | -0.985897 | 0.837532 | 1 | 0.810238 | 1 | False |
| neg/P5 | 72h | 318 | -0.00186797 | -0.399502 | 0.655104 | 1 | 0.609678 | 1 | False |
| pos/P95 | 24h | 91 | 0.00344508 | 0.704523 | 0.758537 | 1 | 0.717856 | 1 | False |
| pos/P95 | 48h | 91 | 0.0079327 | 1.13902 | 0.871142 | 1 | 0.855229 | 1 | False |
| pos/P95 | 72h | 91 | 0.015771 | 1.90813 | 0.970219 | 1 | 0.977405 | 1 | False |

## Non-overlap Recheck

| pool | window | n | mean | t p bonf | boot p bonf |
| --- | --- | --- | --- | --- | --- |
| neg/P5 | 24h | 179 | -0.00316 | 1 | 1 |
| neg/P5 | 48h | 179 | -0.00330901 | 1 | 1 |
| neg/P5 | 72h | 179 | -0.000897541 | 1 | 1 |

## Monotonicity

| side | window | tier means | direction consistent |
| --- | --- | --- | --- |
| neg | 24h | P5 n=318 mean=-0.00267837, P2.5 n=218 mean=-0.00204921, P1 n=91 mean=-0.00189047 | True |
| neg | 48h | P5 n=318 mean=-0.00434667, P2.5 n=218 mean=-0.00277559, P1 n=91 mean=0.00230384 | True |
| neg | 72h | P5 n=318 mean=-0.00186797, P2.5 n=218 mean=0.00070291, P1 n=90 mean=0.0125852 | True |
| pos | 24h | P95 n=91 mean=0.00344508, P97.5 n=85 mean=0.00748926, P99 n=70 mean=-0.00326846 | False |
| pos | 48h | P95 n=91 mean=0.0079327, P97.5 n=85 mean=0.0151564, P99 n=70 mean=-0.0103755 | False |
| pos | 72h | P95 n=91 mean=0.015771, P97.5 n=85 mean=0.0214121, P99 n=70 mean=-0.00502497 | False |

## BTC SMA200 State Breakdown

| pool | state | window | n | mean |
| --- | --- | --- | --- | --- |
| neg_P5 | bull | 24h | 95 | 0.00282539 |
| neg_P5 | bull | 48h | 95 | -0.00351523 |
| neg_P5 | bull | 72h | 95 | -0.00447842 |
| neg_P5 | bear | 24h | 161 | 0.000525847 |
| neg_P5 | bear | 48h | 161 | 0.0011349 |
| neg_P5 | bear | 72h | 161 | 0.000587926 |
| pos_P95 | bull | 24h | 77 | 0.00638178 |
| pos_P95 | bull | 48h | 77 | 0.0107861 |
| pos_P95 | bull | 72h | 77 | 0.0195848 |
| pos_P95 | bear | 24h | 0 | NA |
| pos_P95 | bear | 48h | 0 | NA |
| pos_P95 | bear | 72h | 0 | NA |

## Preregistered Criteria Check

- Main neg/P5 Bonferroni-significant windows by both t-test and bootstrap: []
- Direction-wrong main windows: ['24h', '48h', '72h']
- Negative-side monotonicity all windows direction-consistent: True
- Final binary decision: **FAILED**

## Protocol Notes

- t-test method: scipy.stats.ttest_1samp
- Block bootstrap: block=168 1H bars, N=5000, seed=20260611.
- Bonferroni multiplier: m=6.
- t0 is the first available 1H close strictly after `event_time`; returns use only closes at t0 and later.
- This is an event study only: no costs and no strategy performance metrics.
