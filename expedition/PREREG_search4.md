# PREREG -- Ch5 Campaign 4: gated-penalty search for a frontier-beating code
# (first campaign steered by a fitness that passed its own known-code gate)

**Pre-registered 2026-07-10, BEFORE the run.** Signpost 2026-07-31.

## Question
Can the closed loop find a k>=2 code with a better OPERATING-POINT ERROR PROXY
than the known frontier (eh8(x)eh8, S=4), within the Ch4 winner's qubit budget?

## Fitness (gated, Entry 008)
MAXIMIZE S = d - 2*col_deg_max  (lambda=2 = window midpoint of the gated
[0.8,4.0]; FROZEN, never re-tuned mid-campaign)
SUBJECT TO: k >= 2 (rep family excluded -- proxy ungated there and
contradicted by Ch4's measured 0.255), w <= 4, n <= 64, k <= 16 (exact d via
classical_verify), qubits-per-logical (n+r)/k <= 13.
Gate provenance: passes m=1 known-code ordering + floor-consistency on
s5_rankmap_data.json; distance alone fails; C3's col_deg=9 hotspot is the
mechanism (CX exposure per cycle).

## Landmarks (frozen)
eh8(x)eh8 [64,16,16] S=4 qlog=8 (frontier). Winner rep3(x)eh8 S=2 qlog=13.

## Loop changes from Campaign 3 (Entry 006 fixes, both implemented)
1. Bandit credit is PLATEAU-PROOF: credit = 0.7*relative-S-improvement
   + 0.3*feasibility (candidate passed all constraints), so the adaptive
   component retains gradient after best-S stalls.
2. Every new running-best logs b64+shape (reproducibility fix, already
   committed at 8555b7a).

## Structure
learn (elitism E=8 + crossover + bandit) vs matched random control,
sequential, 15 min/arm, pop 200, seed 20260711. Determinism gate: byte-
identical replay from seed at fixed generations, or results not reported.

## Priors (author-gauged 2026-07-10; resolve by 2026-07-31)
| # | Claim | Criterion | Prior |
|---|---|---|---|
| R1 | Loop learns (bandit fixed) | learn beats random on best-S AND bandit weights leave uniform (the E006 plateau pathology does not recur) | 70% |
| R2 | Matches the frontier | finds S >= 4 at qlog <= 13 (rediscovers eh8(x)eh8-class or equal) | 45% |
| R3 | BEATS the frontier | S > 4, k >= 2, all caps, NOT row-equivalent (rref2) to any committed landmark | 20% |
| R4 | Penalty survives out-of-sample | top find's operating-point referee verdict (point or bound) is CONSISTENT with its S-rank vs the landmarks it claims to beat; no C3-style hotspot inversion | 55% |

## STOP conditions
- Any R3 claimant: independent exact-d re-verification + col_deg audit +
  row-equivalence vs all committed landmarks before the claim stands.
- Referee finalist verdicts use the committed flooring conventions; an
  unresolvable floor does not count for OR against R4 -- it is recorded.
- Instruments frozen at aecffbe.

## PRE-RUN ADDENDUM (2026-07-10, recorded BEFORE the campaign run)

Probe finding (565 gens, seed 20260711, driver as first committed): the
bit-flip/crossover proposer plateaus at S=0.0 by gen 35 and NEVER reaches
S>0 -- it cannot assemble product structure (Campaign 2's built-not-stumbled
lesson resurfacing). Launching as-configured would trivially resolve R2/R3
FALSE without testing the gated fitness.

Proposer change (this addendum): a constructive "build" operator is added --
product of two classical factors from the small bank {rep2, rep3, rep4, eh8}
-- for BOTH arms (learn: bandit-selected; random control: 25% build draws,
matched access). Landmarks are NOT seeded directly.

Honest consequence, stated before any candidate: with "build", assembling the
frontier (eh8(x)eh8) is one lucky draw, so R2 DEFLATES to a sanity check
(effective prior ~95%; its resolution no longer evidences learning). The
campaign's real questions are now R1 (bandit leaves uniform; plateau-proof
credit works) and R3 (a frontier-BEATER not row-equivalent to any landmark --
prior unchanged at 20%; mutation must find off-landmark structure the bank
cannot assemble directly). R4 unchanged.

## Resolution log (2026-07-10, same day; 15 min/arm, seed 20260711)

| # | Verdict | Evidence |
|---|---|---|
| R1 | NOT DEMONSTRATED (test collapsed) | Both arms reached S=4 at GEN 0 via build -- the ceiling of the bank's assembly closure -- so "learn beats random on best-S" could not discriminate (tie at ceiling). Pass-rate favored random 2.1x (learn dwells on expensive k=16 exact-d). Bandit stayed only trivially off uniform (~1.6%): with no headroom above the ceiling, the plateau-proof credit had no gradient to act on. This is a failed EXPERIMENT about R1, not evidence against learning (Campaign 3 demonstrated learning); the design removed the headroom the test required. |
| R2 | TRUE (sanity, as pre-deflated) | Both top finds decode to eh8(x)eh8 [64,16,16] cd=6 exactly -- assembled, per the addendum's prediction; no learning evidence claimed. |
| R3 | FALSE | Zero frontier events across 51,700+ valid candidates (learn 16,695 + random 35,036); ~11,500 mutations and 13 crossovers off the frontier elite, none exceed S=4. eh8(x)eh8 is a HARD LOCAL OPTIMUM under w<=4, k in [2,16], qlog<=13. Existence of any S>4 code in-caps remains open (search not exhaustive); the loop found none. |
| R4 | NOT TESTED | The top find is a known landmark, not an off-landmark code -- nothing new existed to validate the penalty on. Carries forward. |

**Methods lesson (recorded):** the build operator over-corrected -- strong
enough to escape Campaign 4-probe's S=0 plateau, strong enough to trivialize
the target. A learning test needs HEADROOM between what operators assemble
directly and what the campaign asks for. Both edges of that window are now
mapped (can't-reach: bit-flip; trivially-reaches: build).
