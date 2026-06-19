# REPORT_CARRY_FEASIBILITY

**Generated UTC:** 2026-06-19T10:48:27Z  
**Task:** `CARRY_FEASIBILITY`  
**Protocol:** `06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v4.md`  
**Status:** failed  
**Verdict:** FAILED

## [专业异议]

The approved v4 feasibility executor cannot be run compliantly with the currently available repository inputs and sandbox permissions.

I did not run the existing simplified `06_RESEARCH/CODE/carry/` scaffold as v4 acceptance evidence, because it does not implement the frozen v4 cross-margin, historical leverage-bracket, event-stress, and 1H synthetic bootstrap accounting protocol. Running it would violate the single-spec requirement and could misstate a failed/N.A. protocol state as a historical result.

## Completed Steps

- Read the frozen v4 preregistration and task handoff.
- Audited available BTC/ETH funding, mark, spot, and futures metrics files without reading `HOLDOUT` or `sealed` inputs.
- Added `06_RESEARCH/CODE/carry_feasibility_v4_audit.py`.
- Generated `06_RESEARCH/CODE/output/carry_feasibility_v4_input_audit.json`.
- Recorded custodian key-path blocker in `06_RESEARCH/DATA/CARRY_WORK/CARRY_HOLDOUT_PERMTEST.log`.
- Wrote result report `06_RESEARCH/RESULTS/20260615_carry_feasibility.md`.
- Wrote TASK_INBOX completion event to `04_AI_TEAM/TASK_INBOX/CARRY_FEASIBILITY_DONE.json`; the scheduler consumed it and moved it to `04_AI_TEAM/TASK_INBOX/PROCESSED/CARRY_FEASIBILITY_DONE.json`.

## Blocked / Failed Steps

- Stage 1 sealed holdout creation failed before encryption because the required external key directory is not writable in this execution sandbox:

```text
mkdir: /Users/yaomingyu/.aiquant_sealed/carry: Operation not permitted
```

- No fallback key path was used.
- `sealed.enc` was not created.
- `CARRY_HOLDOUT_MANIFEST.json` was not created, because there is no sealed artifact to manifest.
- Executor was not run, because v4-required inputs are missing or incomplete.
- Git commit was not performed because the sandbox denied writing `.git/index.lock`:

```text
fatal: Unable to create '/Users/yaomingyu/Documents/AI_QUANT_COMPANY/.git/index.lock': Operation not permitted
```

## V4 Missing Inputs

| Required input | Status |
|---|---:|
| Spot 1H open/close | missing open |
| Perpetual contract 1H OHLC separate from mark | missing |
| Binance index 1H close | missing |
| Historical leverage brackets with floor/cap/mmr/cum | missing |
| Historical liquidation clearance fee rate | missing |
| Binance withdrawal status or announcement event source | missing |
| USDTUSD cross-index event source | missing |
| ADL official execution records | missing |

## Acceptance Self-Check

| Requirement | Result |
|---|---:|
| Net E[R] annualized, bootstrap p | N.A. => FAIL |
| Win/loss ratio >= 1.5 | N.A. => FAIL |
| Positive years strict majority | N.A. => FAIL |
| Annualized log growth > 0 | N.A. => FAIL |
| Cash zero benchmark | N.A. => FAIL |
| 2000-path 1H liquidation/MDD ladder | N.A. => FAIL |
| MDD <= 15% and fixed event replay | N.A. => FAIL |
| WF >= 2 positive segments | N.A. => FAIL |
| A-1 x Carry trigger retention | NOT EVALUATED; baseline failed |

## Prohibition Self-Check

- HOLDOUT read: no.
- Sealed input read: no.
- Preregistration modified: no.
- Cost model simplified for acceptance: no acceptance run was performed.
- Full-sample percentile: no acceptance signal calculation was performed.
- Black-box dependency introduced: no.
- Failed result framed as partial success: no; report verdict is `FAILED`.

## Recovery Preconditions

To resume this task as an executable v4 feasibility run:

- Run in an environment allowed to write `~/.aiquant_sealed/carry/carry_key.bin`.
- Provide v4-required source files for spot open, contract OHLC, index close, historical bracket rows, clearance fees, withdrawal/USDT depeg event sources, and ADL records.
- Re-run custodian split and AES-256-GCM seal.
- Only then run the work-only executor under v4 without using the simplified scaffold as a substitute.
