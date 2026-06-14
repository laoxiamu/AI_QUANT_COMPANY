# A1 Forward Liquidation Event Count

**Generated UTC:** 2026-06-14T04:10:42Z  
**Data status:** NO INPUT JSONL FOUND  
**Readiness gate:** NOT_READY

## Governance

This is a count-only monitoring artifact. It computes no event-forward returns,
performance metrics, or edge conclusion. All trigger parameters below are
placeholders and must be frozen only by the formal Path B preregistration.

## Placeholder Parameters

| parameter | value |
| --- | --- |
| symbols | BTCUSDT, ETHUSDT, SOLUSDT |
| rolling SELL window | 1h |
| historical quantile | 0.99 |
| minimum prior rolling observations | 24 |
| count mode | episode_start |
| readiness target n_min | 120 |

The historical quantile at time `t` uses only rolling sums strictly before `t`.
`episode_start` counts the first exceedance in a continuous pulse; a gap of at
least one rolling window resets the pulse.

## Pooled Readiness

| metric | value |
| --- | --- |
| cumulative n | 0 |
| target n_min | 120 |
| remaining n | 120 |
| first candidate UTC | N/A |
| last candidate UTC | N/A |
| observed start UTC | N/A |
| observed end UTC | N/A |
| event rate / elapsed day | N/A |
| projected target date | N/A |

Projection is a linear extrapolation from elapsed calendar coverage and is
unavailable until at least one candidate exists across a positive time span.
It does not adjust for collector downtime or changing market regimes.

## By Symbol

| symbol | cumulative_n | first_candidate_utc | last_candidate_utc |
| --- | --- | --- | --- |
| BTCUSDT | 0 | N/A | N/A |
| ETHUSDT | 0 | N/A | N/A |
| SOLUSDT | 0 | N/A | N/A |

## By Symbol And UTC Month

_No rows._

## Parser Audit

```json
{
  "files": 0,
  "total_lines": 0,
  "parsed_rows": 0,
  "bad_lines": 0,
  "duplicate_lines": 0,
  "cross_file_duplicates": 0,
  "bad_line_ratio": 0.0
}
```
