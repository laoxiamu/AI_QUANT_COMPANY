# X2 RV Redteam B1 Result - 2026-06-22

**Task:** P1-RES-037-B1  
**Verdict:** KILL  
**B1 gates run:** No. Stage 0 killed the line before statistical testing.

Stage 0 red-team conclusion: the payer is too soft and too competitive, crypto cointegration is not stable enough to treat as a prior, and the four-fill pair-trade cost hurdle is structurally too large.

Key reproducible numbers from `06_RESEARCH/CODE/output/x2_rv_redteam_b1_audit.json`:

| Case | Spread-return hurdle |
|---|---:|
| maker lower bound + adverse selection | 0.48% |
| protocol base taker | 0.80% |
| taker slippage stress 0.30% | 1.60% |
| taker slippage stress 0.50% | 2.40% |
| taker slippage stress 1.00% | 4.40% |

The cited arXiv paper `2602.23762` exists and is titled **“One Rising Ship Sinks Other Ships: Cross-Chain Negative Spillovers in Crypto Markets”**. It supports the existence of cross-chain spillover risk, not tradable mean reversion.

No Holdout files were read. The expected `127 parquet` files were not found under `06_RESEARCH/DATA/`; the audit found `0` parquet files and `35` expanded `*_4H.csv` files.

