# econ5200-PS1
## The Measurement Audit — Diagnosing a Dashboard's Average Basket Value

**Objective:** Trace a dashboard's inflated average-basket-value metric back to its two root causes, quantify each one's contribution, and ship a tested module that produces a defensible number.

### Methodology

- **Synthetic ground truth.** Generated 20,000 transactions across 2020–2021 with a log-normal consumer basket distribution (mean=3.5, sigma=0.8), 20 planted B2B orders inflated 100x, and 10% of 2021 orders flagged as cancelled (0% in 2020, simulating a change in what gets logged). Recorded the true consumer average — B2C, non-cancelled — for each year before contaminating the data.
- **Reproduced the dashboard's error.** Computed the naive `mean(basket_value)` per year with no filtering and measured its gap from the true consumer mean.
- **Decomposed the gap into its two mechanisms.** Isolated the B2B contribution (mean after removing cancellations, minus the fully clean mean) from the logging-change contribution (naive mean minus the cancellations-removed mean), so the two pieces sum to the total gap.
- **Compared robust alternatives.** Computed the median, a 10%-trimmed mean, and the mean after excluding B2B orders, and evaluated the assumption each one depends on.
- **Shipped `basket_metrics.py`.** Built `audit_report()` (missingness, dtype, skew, and IQR-based outlier count per column) and `robust_mean()` (median, trimmed, or rule-based B2C-only, selected by a `method` parameter), then verified both against a held-out ten-row test set with `assert` checks.
- **Built a reconciliation bridge.** Wrote `build_bridge()` to walk naive → drop B2B → drop cancelled → true mean in a fixed order per year, asserting the steps sum exactly to the total gap, with the trimmed mean reported separately as a sensitivity check rather than a step in the bridge.

### Key Findings

- **Size of the error:** The dashboard overstated the average consumer basket by **$3.36 in 2020** and **$5.89 in 2021**, against true consumer means of $45.98 and $45.72.
- **Decomposition:** B2B orders account for essentially the entire gap — $3.36 of $3.36 in 2020 and $6.30 of $5.89 in 2021 (B2B contribution, before the logging adjustment nets it to $5.86). The change in what got logged (cancellations) contributed $0.00 in 2020 and **−$0.41** in 2021, i.e. it pulled the naive mean slightly *toward* the truth rather than away from it.
- **Robust alternatives compared:** median = $33.29/$33.39, 10%-trimmed mean = $38.46/$38.33, mean after B2B exclusion = $45.98/$45.75. The trimmed mean runs about **$7.5 too low** against the true consumer mean, because it discards real high-value consumer purchases along with the B2B tail rather than targeting the B2B contamination specifically.
- **Recommendation:** Report the mean after excluding B2B orders and removing cancelled orders in both years. Once B2B is stripped out, the consumer basket is essentially **flat** from 2020 to 2021 ($45.98 → $45.72), so the apparent rise in the dashboard's naive number was almost entirely a B2B artifact, not real consumer behavior.
- **Before betting on it:** Confirm that B2B orders and cancellations are labeled correctly in the real (non-synthetic) data — the whole correction depends on those two flags being trustworthy.
