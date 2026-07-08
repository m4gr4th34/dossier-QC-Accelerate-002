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
