# AI Appendix: Phase 4

## 1. Prompt as sent

```
[Prep] Act as a partner reviewing an analytics deliverable before it
goes to a client board. You are looking for the objection that would
embarrass us in the room.

[Request] I audited a retailer's "average basket value" metric. I found
the naive mean was inflated by a right-skewed B2B tail and by a change
in what was logged between years. I recommend the dashboard show a
trimmed mean with an explicit B2B exclusion rule. Give me the three
strongest objections to that recommendation, ordered by how likely the
client is to raise them, and for each one tell me what evidence would
settle it.

[Iterate] Be specific to this metric. Do not give me generic data
quality advice.

[Mechanism Check] For each objection, say whether it is a question
about the data, about the statistic, or about the business definition
of the metric -- these need different kinds of answer.

[Evaluate] Which single additional analysis would most reduce our
exposure?
```

## 2. Raw reply

I don't know what changed in the logging, so where it matters I state the assumption.

### 1. "This doesn't tie to anything we know." (business definition)

**Objection:** Finance computes basket value as revenue divided by transactions. A trimmed mean with B2B removed won't reconcile to that, and it will sit well below the number the client has reported for years. They'll ask which number is right, whether past targets and bonuses were set against a wrong metric, and why they should drop large baskets that are real revenue. If B2B is 3% of transactions but 20% of revenue, the dashboard hides a fifth of the business.

**Evidence that settles it:** A reconciliation bridge from the legacy figure to the recommended figure, with separate steps for B2B removal, the trim, and the logging change. Alongside it, B2B's share of transactions versus revenue. Also ask who uses the metric and for what decision. If the answer is revenue forecasting, the recommendation is wrong for that use, and we should say so now.

### 2. "How do you know what's B2B?" (data)

**Objection:** If the rule is a basket-size threshold, it's circular: you're defining the exclusion by the outcome you're measuring. If it's an account flag or tax-exempt status, they'll ask whether it was populated consistently across the logging change. They'll also point out that you've excluded legitimate large consumer baskets (furniture, holiday, appliances) and kept small B2B orders.

**Evidence that settles it:** Validate the rule against ground truth: account IDs, invoice terms, resale certificates. Report precision and recall, and show how the metric and the year-over-year change move as the threshold varies. If the flag's coverage changed when the logging changed, the rule has a break of its own.

### 3. "Why a trimmed mean, and does it fix the year-over-year problem?" (statistic)

**Objection:** On a right-skewed distribution, symmetric trimming doesn't estimate a meaningful quantity. It lands somewhere between the mean and the median, depending on the trim percentage you chose. Why not the median, a winsorized mean, or segment-level means? The sharper version is that the trim addresses skew but not the logging change. If what was logged shifted the distribution (for example, items consolidated into baskets, or returns and voids treated differently), trimming across that break doesn't restore comparability. You'd have fixed one problem and quietly carried the other.

**Evidence that settles it:** A sensitivity grid of ABV and the year-over-year change across trim levels (0 to 10%) and alternative estimators (median, winsorized, consumer-only mean). If the conclusion is stable across the grid, the choice of trim is defensible. Separately, check whether the trim removes the logging effect, ideally by re-aggregating raw line-item data under one consistent definition for both years.

### Ordering

Number 1 comes first because it's the first thing anyone in the room will see: the number changed, and it doesn't tie to revenue. Number 2 comes next because any thoughtful reader asks how the exclusion works once they accept the premise. Number 3 is the most technical, so it's less likely to come up from a business audience, but it's the one that would embarrass us most if raised.

### The single analysis to run

**A year-over-year bridge on a harmonized basis.** Re-derive both years under one consistent logging definition, then decompose the change from the legacy figure to the recommended figure into B2B mix, the logging change, the trim, and the real change in consumer baskets. This answers objection 1 directly, exposes how much rides on the B2B rule (2) and the trim level (3), and gives the board the explanation they'll want. If the logging change can't be harmonized from raw data, that step in the bridge is an estimate, and we should label it as one and show a range rather than a point.

## 3. Changes I made to my code

I changed `build_bridge` so it ends at the true consumer mean instead of the trimmed mean. Before, the trim was treated as a correction step, which made the slide say the dashboard was off by 11 and 13 dollars. That didn't match the 3.36 and 5.89 gaps from Phase 1. Now the steps run in a fixed order (naive, then remove B2B, then remove cancelled orders), so the pieces add up exactly to the total gap, and I added an `assert` that fails if the bridge doesn't close. I moved the trimmed mean out of the bridge and into its own sensitivity columns (`trimmed_mean` and `trim_bias_vs_true`), where it shows up as about 7.5 too low. I also updated the findings text and the slide to the corrected numbers, and I kept my Phase 2 recommendation of B2B exclusion but added removing cancelled orders in both years.
