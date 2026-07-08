# PREREG -- Ch4 Search Campaign 1: circuit-level outer-code search

**Pre-registered 2026-07-07, BEFORE any campaign run.** Same logic as sealing
Chapter 3 before the Chapter 4 recon: the bets must provably predate the
findings. Every prior below is a FORECAST (claim type) with status
OPEN-UNVERIFIED until resolved by the campaign's own published outputs; each
resolves TRUE or FALSE by its stated criterion and is published either way,
including misses. Unresolved by the signpost date -> published as
EXPIRED-UNRESOLVED with reasons.

## Campaign design

- **S1 -- re-referee Day-1.** The Day-1 code-capacity band-2 leaders (headlined
  by HGP(rep5, punctured-Hamming[6,3,3]) = [[42,3]], w<=5, 14 q/logical) run
  under the circuit-level v1 evaluator in GM-gate mode (kappa_1/kappa_2 = 1e-4,
  nbar = 11, matching the Ruiz baseline for comparability), Ocelot-anchored mode
  as secondary reality check. This is the dossier's own loop closing: does the
  cheap-model discovery survive the expensive-model referee?
- **S2 -- structured search.** LLM-proposed classical seeds -> classical
  verifier referee -> hypergraph product -> circuit-level FOM, under a hardware
  weight cap w <= 4. Enumerated/handcrafted seed families run in the same arena
  as controls.
- **S3 -- severity map.** Survivors mapped across kappa_1/kappa_2 in
  {1e-3, 1e-4} and (Ocelot mode) the D5 nbar axis on [1, 3].

## Metric and baselines

FOM: per-logical-qubit total logical error per cycle = circuit-level decoded
phase error + analytic bit-flip floor, at the stated operating point; qubit
budget counts data + ancilla. Baseline: the d-matched repetition curve; in GM
mode the published Ruiz repetition fit and CA overhead (~7.6 q/logical at
eps_L <= 1e-8) are the external yardsticks.

**Instrument property (disclosed up front):** the GM-gate mode reads ~1.2-2x
OPTIMISTIC in absolute terms against the Ruiz master-equation fit (all 12
corridor grid points at ratio <= 1; see NOTEBOOK Day-2 continued). Relative
comparisons between candidates -- the campaign's currency -- are unaffected.
Absolute claims will state this tilt in-sentence.

## STOP conditions

Any candidate claiming > 10x improvement over baseline: adversarial
re-verification (fresh seeds, both decoders, both hardware modes) before it
enters the notebook. Any inconsistency between the evaluator and the mechanical
verifier (verify_code.py): campaign halts, adjudication in the strategy room.
Any evaluator change mid-campaign: campaign restarts (no moving instruments).

## Pre-registered priors (author-judged 2026-07-07; resolve by 2026-07-31)

| # | Claim | Resolution criterion | Prior |
|---|-------|----------------------|-------|
| P1 | Day-1 [[42,3]] headline survives circuit level | In S1, per-logical error within 2x of the best matched-budget k=1 comparator, same mode and operating point | **35%** |
| P2 | Some searched code beats repetition >= 2x | Exists campaign output with per-logical error <= 0.5x the d-matched repetition baseline at equal qubit budget, kappa_1/kappa_2 = 1e-4, w <= 4, surviving adversarial re-check | **55%** |
| P3 | LLM seed layer earns its place | Final leaderboard top-3 contains >= 1 family whose classical seed originated from the LLM-proposal layer | **40%** |
| P4 | Stretch: beat Ruiz CA overhead at lower weight | Exists code with <= 10 total qubits/logical at eps_L <= 1e-8 (GM mode, nbar = 11, kappa_1/kappa_2 = 1e-4, w <= 4); any scaling extrapolation labeled as such | **20%** |

Reasoning sketches: P1 -- circuit level adds measurement + hook errors that
punish w<=5 checks harder than rep's w=2; most code-capacity advantages shrink.
P2 -- Ruiz's CA result is an existence proof in a kin model, but our weight cap
is tighter and our search space smaller. P3 -- Day-1 evidence mixed: referee
rejected 2 of 4 LLM hypotheses, champion was handcrafted. P4 -- a real long
shot; the weight cap is the hard constraint; a TRUE here is a publishable
structural result.

## Resolution log

**P1 -- RESOLVED FALSE (2026-07-07; canonical S1 run at commit 721a9b4).**
Criterion: [[42,3]] per-logical error within 2x of the best matched-budget k=1
comparator at the S1 primary point (GM, kappa_1/kappa_2 = 1e-4, nbar = 11; point
clarified pre-run in the anti-self-serving direction, NOTEBOOK Day-2). Measured:
[[42,3]] X-only (22 q/logical) = 2.92e-4 vs rep-11 (21 q/logical,
corridor-validated FIT) = 2.74e-9 -> ratio ~1.1e5. FALSE by five orders of
magnitude; the disclosed ~1.2-2x instrument optimism is immaterial at this gap.
The Ocelot calibrated leg is directionally consistent: no matched-budget
advantage at today's measured hardware either, once the FITTED p_m = 0.0478 and
the bit sector are priced in. The prior was 35%; the miss publishes with the
same prominence a hit would have received.

What the miss established: (1) the Day-1 [[42,3]] headline is a MODERATE-BIAS,
code-capacity artifact -- found at eta = 30-100, correct there, drowned at the
GM point's effective bias ~1e7 where repetition thrives. This is Day-1's own R3
lesson (optimal dx -> 1 as eta rises) writ large, now measured at circuit level.
(2) Full-CSS extraction is crushed under GM gates (~54x for [[42,3]]; the
Z-check-on-data non-adiabatic tax), so X-only extraction is promoted to
first-class in S2 -- a consequence flagged in the NOTEBOOK before the canonical
run. P2, P3, and P4 remain OPEN pending S2/S3.

**P2 -- RESOLVED TRUE (2026-07-07; evidence chain across commits bddf09f,
671fa62, eea98d5).** Criterion walk-through, every clause:
- "per-logical error <= 0.5x the d-matched repetition baseline at equal qubit
  budget": candidate rep3(x)extHam8 = classical [24,4,12] at 13.0 q/logical,
  X-only extraction; strict comparator (D6, repetition granted AT LEAST the
  candidate's budget) rep-7. Depth-matched, same-instrument ratio at 16 rounds:
  0.255, 95% CI [0.172, 0.337] (44 and 216 fails) -- upper bound clear of the
  bar. The arena's 8-round depth-matched ratio (0.155-to-FIT, ~0.31
  same-instrument) is consistent.
- "kappa_1/kappa_2 = 1e-4, w <= 4": the GM primary point; all checks weight 4.
- "surviving adversarial re-check": R1 fresh-seed and R2 alt-decoder passed
  outright; R3's marginal 0.479 was diagnosed as a cross-depth comparator bias
  (ledger E8), closed by the matched-depth leg with the mechanism exhibited on
  the comparator itself (rep-7 boundary factor 1.23), and the pre-frozen ~0.3
  prediction confirmed at 0.255.
Prior was 55%; a hit, published with the same scrutiny the P1 miss received.

**Scope label, carried wherever this result is stated:** this is a MODEL-LEVEL
result under the v1 GM-gate circuit channel (verified-by-fetch constants,
OPEN-7 byte-check pending; disclosed ~1.2-2x optimistic tilt -- which cancels
in this same-instrument ratio) with a fitted-free but assumed p_m = 6e-3
mid-corridor. It is NOT a hardware demonstration. Within that stated scope:
a w<=4, 13-qubits-per-logical product code (rep3 (x) extended-Hamming[8,4,4],
d = 12, an LLM-layer seed born from a refereed kill) outperforms budget-matched
repetition by ~4x per logical at the Ruiz-class operating point.

**Standing instrument rule adopted (from E8):** all future cross-code
comparisons are depth-matched on the same instrument, by construction.

P3 and P4 remain OPEN: P3's "final leaderboard" requires the campaign to close
(S3 pending); P4 requires the S3 severity map and labeled scaling analysis.

**P3 -- RESOLVED TRUE (2026-07-07; campaign leaderboard final at commit 0300eac).**
Criterion: final leaderboard top-3 contains >= 1 family whose classical seed
originated from the LLM-proposal layer. Final leaderboard by campaign FOM
(per-logical ratio to own strict comparator, depth-matched, GM primary point):
1. rep3(x)extHam8 [24,4,12] -- ratio 0.255 -- LLM-layer (H1c). 2-3. repetition
controls (H4) at ratio ~0.9-1.0. The top entry is LLM-layer: TRUE. Honest
footnotes, carried with the claim: (a) the "LLM layer" is the strategy room
acting as proposer against its own mechanical referee -- the Day-1 llm_seeds
pattern, not an external model; (b) the layer's full record is 1 win (H1c),
1 mid-tier (H1b extHam8 alone, ratio 4.4 -- beaten by plain repetition), and
1 family killed before MC by the referee (H1, structural d <= 4 ceiling); the
win required the kill first. Prior was 40%; a hit. Calibration note: 40% was
conservative -- it underweighted that the proposer iterates after referee
kills, which is precisely the loop's design advantage.

**P4 -- RESOLVED FALSE (2026-07-07; S3 L3 data at commit 0300eac).**
Criterion: exists code with <= 10 total qubits/logical at eps_L <= 1e-8 (GM
mode, nbar = 11, kappa_1/kappa_2 = 1e-4, w <= 4). No campaign output reaches
the operating point: the winning family's q/log GROWS with distance (13.0 at
d = 12 -> 23.0 at d = 20 -> 33.0 at d = 28); the high-rate w <= 4 seeds
(q/log ~ 2.5-3) cap at d <= 4 and lose to repetition outright at circuit
level; and the measured winner sits at 1.72e-7 at 13 q/log -- 17x above the
eps bar at 1.3x the budget bar. No labeled extrapolation helps (the scaling
runs the wrong way). Ruiz's CA overhead (~7.6 q/log at 1e-8) remains
unmatched by any w <= 4 construction this campaign found. Prior was 20%;
a miss in the direction the prior expected -- the stretch was a stretch.

## Campaign 1 -- CLOSED (2026-07-07; signpost date 2026-07-31 beaten by 24 days)

Scoreboard: P1 FALSE (35%) -- P2 TRUE (55%) -- P3 TRUE (40%) -- P4 FALSE (20%).
Two hits, two misses, all four resolved against frozen criteria with every
clarification made in the anti-self-serving direction, all published at equal
prominence.

What the campaign established (each with its scope label in the record):
1. The bias-regime matching principle, measured three ways: the Day-1
   moderate-bias headline drowned at high bias (P1); the high-bias winner
   inverts in the dirty decade and drowns at today's measured bias (S3);
   full-CSS extraction pays ~54x under GM gates to guard a ~1e-9 floor (S1).
2. A model-level positive: rep3(x)extHam8 [24,4,12], w <= 4, 13 q/logical,
   ~4x below strict budget-matched repetition at the Ruiz-class operating
   point -- adversarially re-checked, depth-matched, instrument-tilt-free.
3. Instrument science: the boundary-effect rule (depth-matched comparisons
   only), the disclosed GM-mode tilt, and a calibration chain anchored
   entirely in published measurements.
Ledger for the campaign: E1-E9, every catch credited (executor: E1, E2
surface, E4, E7 surface, E9 STOP; strategy room: E3 diagnosis, E5, E8
diagnosis; the byte-guard machinery: E9).

Standing OPEN items carried out of the campaign: OPEN-1 (kappa_2, paper
appendices), OPEN-3 (PDF byte-verification of Q1-Q9 + the Fig. 4b/Fig. 5
definitions), OPEN-4 (CX^2 protocol detail), OPEN-7 (GM channel constants
vs the PRX PDF).
