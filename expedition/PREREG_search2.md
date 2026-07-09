# PREREG -- Ch5 Search Campaign 2: broad circuit-level outer-code search
#             (the automated proposer -- a closed AI loop)

**Pre-registered 2026-07-08, BEFORE any Ch5 campaign run.** Same logic as Ch4
Campaign 1: the bets must provably predate the findings. Every prior below is a
FORECAST (claim type), OPEN-UNVERIFIED until resolved by the campaign's own
published outputs; each resolves TRUE or FALSE by its stated criterion and is
published either way, misses included. Unresolved by the signpost date ->
EXPIRED-UNRESOLVED with reasons.

## What is new in Campaign 2

Campaign 1 turned the loop ONCE over a hand/LLM-seeded bank, proposals
human-guided. Campaign 2 stands up an AUTOMATED proposer -- no human in the loop
per candidate -- running for hours over many generations against the SAME
committed circuit-level referee. It REUSES, does not rebuild: search_demo.py's
evolutionary engine is PROMOTED from the Day-1 code-capacity FOM onto the
calibrated circuit-level GM referee (gm_css.fom), under the Ch4 hardware caps.
The point of the chapter is to DEMONSTRATE A CLOSED AI LOOP: propose -> verify ->
simulate -> score -> LEARN -> propose, unattended, and show it learns.

## The loop's five stations (LEARN is first-class, genuinely implemented)

- PROPOSE: generate arbitrary sparse classical parity-check matrices H (phase/Z
  checks; X-only extraction).
- VERIFY: classical_verify exact (n,k,d) + caps; milliseconds; kills the majority.
- SIMULATE + SCORE: gm_css.fom, X-only, GM primary point (pilot 2e4 shots/8
  rounds -> deep 4e5-2e6 shots/16 rounds, BP-OSD, elites only).
- LEARN (three mechanisms, all logged):
  (1) elitism -- retain top-E by FOM;
  (2) crossover -- recombine two elite matrices (row-union / row-swap, re-gated);
  (3) adaptive proposal -- a bandit over the mutation/crossover operators,
      reweighted each generation by the FOM improvement its offspring produced.
      Measurement steers the next generation. THIS is the closed part.

## The demonstration control (what makes "it learns" falsifiable)

A matched-compute PURE-RANDOM VERIFY-gated leg runs in the same campaign, same
referee, same triage, same total candidate-evaluation budget, no elitism /
crossover / learning. Best-FOM-per-generation, learning loop vs random control,
is the chapter's headline evidence.

## Generative space (BROAD) and caps (fixed pre-run)

Arbitrary sparse H, NOT confined to the product/HGP family; mutation may reach
any sparse H within the caps. Caps: row weight w <= 4; n <= 40; k >= 1;
structural d >= 3 at VERIFY. Column degree reported (self-penalizing via
schedule length). X-only extraction is primary (Ch4 measured the ~54x full-CSS
penalty under GM gates; re-searching it would rediscover it).

## Instrument: FROZEN

GM primary point nbar=11, kappa_1/kappa_2=1e-4, p_m=6e-3, reused verbatim from
Ch4. No re-calibration mid-campaign (moving-instrument STOP rule).

## Metric and baselines

Identical to Ch4 for cross-chapter comparability: per-logical total logical
error per cycle (circuit-level decoded phase + analytic bit floor), reported as
the DEPTH-MATCHED SAME-INSTRUMENT ratio to the D6 strict repetition comparator
(repetition granted AT LEAST the candidate's qubit budget; anti-self-serving).
GM mode reads ~1.2-2x OPTIMISTIC in absolute terms (disclosed); the ratio --
the campaign's currency -- cancels it.

## Structured reference set (frozen pre-run; the rediscovery/escape yardstick)

All rep_H(a) (x) S and hgp(rep_H(a), S) for S in {ext_hamming8, hamming74,
shortened_hamming variants, punctHam6, rep_H(b)} and a,b in stated small ranges,
filtered to n <= 40 / w <= 4 / k >= 1, scored through the referee before the run.
Membership test at resolution: row-equivalence of the phase-check matrix to a
reference member (rref2, exact). This set is committed with the campaign.

## Run budget (ESTIMATE -- labeled as such)

~8 h, one canonical-stack machine. Plausibly thousands VERIFY-screened, hundreds
piloted, TENS deep-refereed. Checkpointed + resumable: a crash at hour 6 does not
lose the night, and partial results publish. Master-seeded and deterministic.

## STOP conditions

- Any candidate claiming >10x over baseline: adversarial re-verification (fresh
  seeds, both decoders, both hardware modes) before it enters the notebook.
- Any inconsistency between the evaluator and verify_code.py: campaign halts,
  strategy-room adjudication.
- Any evaluator change mid-campaign: restart (no moving instruments).
- Determinism gate: master seed + full generation log committed; a re-run from
  the seed reproduces the leaderboard, or the result is not reported.

## Honest scoreboard (mechanical)

Every candidate gets a logged row -- KEPT or KILLED -- with generation, a compact
H encoding + hash, [n,k,d], w, the stage it reached, and either its scores or its
kill reason. "Report what it finds, misses included" is enforced by the log.

## Pre-registered priors (author-judged 2026-07-08; resolve by 2026-08-15)

| #  | Claim | Resolution criterion | Prior |
|----|-------|----------------------|-------|
| Q1 | The closed loop learns | Learning loop's best campaign FOM beats the matched-compute random-search control (95% CI clear), AND best-FOM-per-generation improves rather than staying flat | 60% |
| Q2 | Broad search rediscovers / the structured neighborhood dominates | No campaign output beats the best structured-reference-set FOM (no CI-clear improvement of campaign-best over structured-best) | 60% |
| Q3 | Genuine escape: a non-product code beats the whole structured family | Exists a surviving elite with FOM beating the best structured-reference member (CI-clear), NOT row-equivalent to any reference member, w <= 4, GM point, surviving adversarial re-check | 22% |
| Q4 | The automated search beats the Ch4 hand/LLM winner | Exists an elite with depth-matched same-instrument ratio < 0.255 (95% CI clear) at <= 13 qubits/logical, GM point | 40% |
| Q5 | Some found code is more bias-robust than repetition | Exists a candidate retaining ratio < 1 at BOTH the GM primary point AND the Ocelot-anchored measured point, where the d-matched repetition comparator does not | 30% |
| Q6 | Stretch (long shot): beat the Ruiz frontier at low weight | Exists a code with <= 10 total qubits/logical at eps_L <= 1e-8 (GM, nbar=11, kappa_1/kappa_2=1e-4, w <= 4); any scaling extrapolation labeled as such | 8% |

Reasoning sketches (calibration off Ch4's resolution log):
- Q1 60%: evolution should beat random on a landscape with a strong attractor
  (Ch4's product family); docked from ~70 because random may also reach the
  neighborhood quickly, shrinking the measured gap.
- Q2 60%: the w<=4 product space is the cheap-distance-per-weight attractor under
  high bias (Ch4 central lesson); Day-1's 0/4000-valid-from-random says good
  codes are built, not stumbled onto.
- Q3 22%: strictly harder than Ch4-P2 (55%, TRUE but satisfied by a PRODUCT
  code); a structurally novel non-product winner under w<=4 in 8h is the real
  long-ish shot.
- Q4 40%: the Ch4 winner was hand/LLM-picked, not optimized -- real headroom;
  but Ch4-P4 showed q/log grows with d, so the <=13 q/log budget clause bites.
- Q5 30%: flagged in Ch4 as the plausible modest win; S3's bias-regime-matching
  lesson cuts against a code that stays sub-rep at both points.
- Q6 8%: Ch4-P4 was 20% and FALSE with the scaling running the wrong way; we now
  know it is harder, so lower. Carried to keep the frontier bet honestly on record.

## Resolution log

(empty until the campaign closes)
