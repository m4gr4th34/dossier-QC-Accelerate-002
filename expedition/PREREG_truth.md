# PREREG_truth.md — Pre-registration: operating-point truth campaign (S8)

Date: 2026-07-10. Registered BEFORE any run. Status of every prior:
OPEN-UNVERIFIED. Governs: `s8_truth.py` (to be built). Instrument: the
FROZEN referee (gm_css.fom / evaluator_v1), unchanged — no new physics
instrument, hence no new instrument gate beyond the runner's landmark
selftest. This campaign is Entry 011's fork option (a): direct MC at cost,
now the defensible default after two sampler designs died by measurement
(parity, Entry 010; KU1/KU2 kill, Entry 011).

## 1. Question

The chapter's founding question, unmeasured since Entry 002 declared it
floored at 2e5 shots: at the GM operating point (nbar=11, k_ratio=1e-4,
p_m=6e-3, xonly, ROUNDS=8, m=1), what is the per-logical per-round eps
ordering of the automated finds vs the repetition champions?

## 2. Rows and staged budgets

All rows at m=1, frozen referee, per-chunk seeds (500,000 shots/chunk,
seed = row_base + chunk_index), checkpointed JSONL, byte-identical resume.
Stage 1 fixed; Stage 2 extends toward a target of ~96 observed events
(±20% at 95%) using the Stage-1 estimate, under hard caps. Rows that stay
event-starved publish as rule-of-three floors — floors are results.

| row | H source | k | stage1 | cap (shots) | wall-clock kill |
|---|---|---|---|---|---|
| rep3⊗eh8 (winner) | s2_seeds product | 4 | 2e6 | 2e7 | 6h |
| eh8⊗eh8 (frontier) | s2_seeds product | 16 | 2e6 | 1e7 | 6h |
| C3 find | c3_find_H.json (f42569e3fb53016f) | 6 | 2e6 | 4e6 | 2h |
| rep-7 | s2_seeds rep_H(7) | 1 | 2e6 | 2e7 | 3h |
| rep-13 | s2_seeds rep_H(13) | 1 | 2e6 | 2e7 | 3h |

Precision at caps if the 2-event bands' points are real: winner p_any≈1e-5
→ ~200 events at 2e7 → ±14%; frontier ≈1e-5 → ~100 at 1e7 → ±20%; C3
≈1e-3 → ~4000 → ±3%; repetition rows: if still unmeasurable at 2e7, the
floor improves 100× over the rankmap floor — informative either way.

## 3. Statistics discipline

Exact Garwood 95% Poisson intervals on total fails per row (pure-python
incomplete-gamma implementation, anchored in the selftest against
scipy-computed reference quantiles — scipy is absent from the canonical
venv); conversion to eps by the imported referee conventions only; zero-
event rows publish floors (3/S convention, scoreboard_kind honest); NO
cross-row conclusions from overlapping intervals — ordering claims require
non-overlapping 95% intervals, full stop. stim is per-machine
deterministic only (Entry 011): the record is the workbench's; strategy-
room runs are statistical previews.

## 4. Priors (author-delegated; resolved mechanically)

| # | Claim | Prior |
|---|---|---|
| T1 | Winner row conclusive (≥40 events by cap) | 0.75 |
| T2 | Frontier row conclusive (≥40 events by cap) | 0.65 |
| T3 | Frontier beats winner per-logical (non-overlapping, frontier lower) | 0.5 |
| T4 | Repetition still unmeasured at caps (both rep rows < 10 events) AND their floors sit below both product-code measurements | 0.55 |
| T5 | C3 lands inside its rankmap band [1.80e-5, 2.38e-5] | 0.8 |
| T6 | All five rows complete or hit registered kills within one overnight (≤ 12h total wall-clock) | 0.7 |

One line each: T1/T2 discount for the 2-event bands being consistent with
much lower truths (band bottoms → event-starved at caps). T3: the 2-event
points say frontier < winner, but both bands are factor-4 wide — a coin
flip with a lean. T4 is the Ch4 throughline priced with humility. T5: C3
was a 199-event measurement; its band should hold. T6: eh8⊗eh8 decode cost
is the risk (~2-5x rep2⊗eh8 per shot).

## 5. Kill criteria

KT1 — per-row wall-clock kills (table above): the row publishes whatever
its checkpoints contain (floor or wide interval), labeled as capped.
KT2 — referee drift: the runner's landmark selftest re-verifies the four
committed G2 anchors and the C3 artifact hash before any row runs; any
drift aborts the campaign.

## 6. What this PREREG does not claim

No claim any row reaches its target precision (floors are first-class);
no proxy, no extrapolation, no m>1 anywhere — this is the operating point
or nothing; no decoder changes (the six known traps stay in the referee —
fixing them is an instrument change requiring its own ritual).

---
