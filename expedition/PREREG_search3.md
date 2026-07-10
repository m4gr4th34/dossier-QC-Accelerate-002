# PREREG -- Ch5 Campaign 3: algebraic efficiency-frontier search
# (fitness that cannot saturate, floor, or lie -- Entry 005's decision)

**Pre-registered 2026-07-10, BEFORE the campaign run.** Priors resolve
TRUE/FALSE by stated criteria, published either way. Signpost 2026-07-31.

## Question
Can the automated closed loop beat the Ch4 hand-picked winner -- and the known
structured frontier -- on QUBIT EFFICIENCY AT MATCHED PROTECTION?

## Fitness (exact algebra from VERIFY; Entries 002-005 killed all proxies)
MAXIMIZE eff = k/(n+r) SUBJECT TO d >= 12 (exact, classical_verify), w <= 4,
n <= 64, k <= 16 (exact-distance region). Constraint form is rate-proof:
distance is a floor, not a divisor. Cheap kills: Singleton (d<=n-k+1).
k > 16: NO fitness, NO claim (randomized lmw gives an UPPER bound -- cannot
certify d >= 12); frontier-efficiency k>16 candidates are logged with full H
as a WATCHLIST for offline extended verification only.

## Frozen landmark frontier (enumerated pre-run: products of committed seeds
under caps, 54 members)
- BEST: eh8(x)eh8 [64,16,16] eff=0.1250
- Ch4 winner: rep3(x)eh8 [24,4,12] eff=0.0769
Rediscovery = reaching these unaided; discovery = exceeding them.

## Structure
s5_algsearch.py @ sha256 3baff3ce... : learn (elitism E=8 + crossover +
per-compute bandit, credit = relative eff improvement) vs matched random
control, sequential, 15 min/arm, pop 200/gen, seed 20260710. Deterministic
at fixed generations (verified byte-identical). Referee (stim) appears NOWHERE
in the loop; finalist verification is a separate post-run step using the
committed same-instrument machinery with flooring conventions (point values
where measurable; rule-of-three bounds where floored; both-floored honestly
unresolved -- per Entry 002 the deep ratio may be UNMEASURABLE for d>=12
finalists, and a bounded/unresolved verdict is an accepted outcome).

## DISCLOSED PILOT (ran during driver validation, 2026-07-10, 45 s/arm):
learn found [34,6,12] w=4 eff=0.0845 (beats winner 0.0769) via crossover;
random plateaued at 0.0769. Priors below are set WITH this knowledge -- the
pilot informs P1/P2 upward; it cannot be un-known and is not hidden.

## Priors (author-gauged 2026-07-10; resolve by 2026-07-31)
| # | Claim | Criterion | Prior |
|---|---|---|---|
| P1 | Loop learns | learn best-eff beats random best-eff at matched budget AND learn's passing-candidate rate exceeds random's 10x+ (pilot: 2403 vs 25) | 85% |
| P2 | Beats the Ch4 winner | exact-d candidate with eff > 0.0769, d>=12, w<=4 (pilot already shows one; full run must reproduce from seed) | 90% |
| P3 | Reaches the frontier | exact-d candidate with eff >= 0.1250, d>=12 (rediscovers eh8(x)eh8-level or equal) | 45% |
| P4 | EXCEEDS the frontier | exact-d candidate with eff > 0.1250, d >= 12, w <= 4, not row-equivalent (rref2) to any of the 54 landmarks | 20% |
| P5 | A finalist survives the referee | top exact-d find gets same-instrument deep verification: measurable-point or bounded verdict consistent with its algebraic rank; NOT contradicted (an unresolved floor does not count against) | 55% |

## STOP conditions
- Determinism gate: full run reproduces byte-identical from seed at fixed
  generations, or results are not reported.
- Any P4 claimant: independent exact-d re-verification (fresh code path) +
  row-equivalence audit against all 54 landmarks before the claim stands.
- Instruments frozen: classical_verify/rank2/rref2 byte-identical to HEAD.
