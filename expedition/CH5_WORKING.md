# CH5_WORKING.md — loop-lessons log (working memory, append-only)

This is the running record of the OUTER loop: each automated-search run is one
turn, and what it taught gets appended here so future sessions inherit it rather
than starting from scratch. Distinct from NOTEBOOK.md (the sealed narrative) —
this is the runbook. Newest entry at the bottom. Never rewrite past entries;
only append.

Standing disposition: a run that finds no better code is not a failed turn of
this loop — it's a data point about what to change next. Record the mechanism,
not just the outcome.

---

## Entry 001 — 2026-07-09 — broad X-only search vs repetition (Campaign 2)

**Ran:** automated proposer (elitism + crossover + per-compute bandit) vs a
matched-compute random control, one frozen circuit-level GM referee, ~4h each
arm, seed 20260708. PREREG_search2.md, driver s5_campaign.py @ 7d8b686.

**Found (codes):** nothing that beats the Ch4 winner, and nothing that beats
repetition in any load-bearing sense.
- Learn arm: 70 deep-refereed candidates, ZERO wins. Every one k=1, losing to
  its rep comparator by 2x-209x. Recurring families [16,1,9], [25,1,13].
- Random arm: 6 genuine but trivial point-wins — low distance (d=3-4), k=2-5,
  beating only the WEAKEST (d=3) rep, by modest 0.46-0.92x (Q4 wanted 0.255x).
- 3 high-distance codes (d=9,13,16) left UNRESOLVED (lower_bound_rep_floored
  with bound < 1) — the only ones that could be real; need the 2e6 finalist to
  settle. Expected losers, but not proven.
- Net: Q2 (repetition dominates) is the story. No Q3/Q4/Q5/Q6.

**The mechanism (why — this is the real result):**

1. **A saturating evaluator poisons the loop.** 44% of pilots read EXACTLY 0 at
   20k shots (shot-noise floor, not real perfection). A metric that returns 0
   for half the field has no gradient — the bandit/elitism had nothing to climb
   among floored candidates, and the pilot floor REWARDED high-distance codes,
   which is precisely where rep is unbeatable. The loop optimized the shallow
   signal straight AWAY from the winnable region. Random, not steering, wandered
   into the low-distance corner where the modest wins actually lived — so the
   loop performed WORSE than random, not because the idea is broken but because
   it was climbing a ruler that bottomed out.

2. **We steered on the cheap tier.** The two-tier triage (cheap pilot -> deep
   scoreboard) was right for COST but wrong for CONTROL: selection learned from
   the pilot, the exact signal that lied. The deep scoreboard was NOT degenerate
   — it cleanly separated every candidate — but nothing steered on it.

3. **We picked a near-unwinnable question.** Broad search vs repetition under
   high bias was ~decided going in (Ch4: rep is brutal; Q2 prior 60%). A useful
   loop needs a regime where (a) a better code plausibly exists AND (b) the
   evaluator can resolve it when found. We had neither cleanly.

**Machinery that held (keep):** shot-noise-floor credit clip absorbed ~238
floored pilots with 0 crashes; try/except net never had to fire; determinism +
resume verified; triage-vs-scoreboard wall + rule-of-three flooring convention
did exactly their job (caught 18 fake pilot-floor "winners" as deep losers).

**Redesign for the next run (what this turn implies):**

- **Fix the ruler: continuous, non-saturating FOM.** Never a metric that returns
  0. Score on distance-to-threshold, a sub-threshold scaling slope, or logical
  error extrapolated along a noise sweep — something that separates a d=16 from
  a d=13 even when both floor at a fixed shot budget.
- **Steer on the deep signal, gate on the cheap one.** Cheap tier becomes a
  pass/fail "worth deep-testing" gate only; selection/bandit/elitism act ONLY on
  the non-saturating deep number. The loop must never OPTIMIZE a metric it can't
  trust.
- **Aim at a winnable regime.** Bias the generator toward higher-k / structured
  families (where Ch4's winner lived), and/or reward "beat rep at matched
  QUBITS" (favors high-k) rather than a metric that just piles on distance.

**Gate before building any of that — prove the ruler first.** A search is only
as good as the ruler it climbs, and this run's ruler lied. Before turning a new
loop loose, confirm the candidate evaluator can rank codes we ALREADY KNOW
differ, with margin, and find the depth at which it stops saturating. If it
can't distinguish known-different codes, no loop on top will work.

Ready-to-run diagnostic skeleton (canonical venv; reuses committed modules — do
NOT rebuild the referee). The known-ordering claim is verified by construction
(winner [24,4,12] vs weaker rep3(x)rep3 [9,1,9]: d 12 vs 9, k 4 vs 1); the
referee calls themselves need the canonical stack, so validate output there:

    # diag_ruler.py — does the evaluator resolve KNOWN codes, and at what depth?
    import numpy as np, sys; sys.path.insert(0, ".")
    from s2_seeds import product_code, rep_H, ext_hamming8
    from gm_css import fom
    GM = dict(nbar=11.0, k_ratio=1e-4, p_m=6e-3)

    def eps(H, k, shots, rounds=16, seed=7):
        Hz = np.zeros((0, H.shape[1]), np.uint8)
        pk, _, _, _ = fom(H, Hz, k, rounds, GM["p_m"], GM["nbar"],
                          GM["k_ratio"], "xonly", shots, seed=seed)
        return pk

    # known-ordering ladder (stronger -> weaker BY CONSTRUCTION):
    winner = product_code(rep_H(3), ext_hamming8())   # Ch4 winner [24,4,12]
    weaker = product_code(rep_H(3), rep_H(3))         # [9,1,9] — strictly weaker

    print("shots     eps(winner)   eps(weaker)   resolved?")
    for shots in (20000, 100000, 500000, 2000000):
        ew = eps(winner, 4, shots); ek = eps(weaker, 1, shots)
        # "resolved" = both nonzero AND separation beyond shot noise
        sn = 1.0 / shots
        ok = (ew > 0 and ek > 0 and abs(ek - ew) > max(sn, 0.1 * max(ek, ew)))
        print(f"{shots:>8} {ew:>12.3e} {ek:>12.3e}   {ok}")
    # OUTPUT WE WANT: the smallest `shots` where resolved==True for known-
    # different codes. THAT depth (not 20k) is the floor for the next loop's
    # steering signal. If nothing resolves at any depth, the FOM itself (not
    # just its depth) must change first. Extend the ladder with true near-
    # neighbors of the winner once the two-point version behaves.

**Next session, start here:** run the diagnostic, read off the non-saturating
depth (or conclude the FOM needs replacing), THEN build the loop with
deep-signal steering in a winnable regime. Don't re-run a broad-vs-rep search —
that answer is in this entry.

---

## Entry 002 — 2026-07-09 — ruler-gate verdict: the FOM cannot rank strong codes (NO-GO)

**Ran:** the Entry 001 known-ordering diagnostic (diag_ruler.py, extracted
verbatim from this file), canonical stack, read-only. Two codes known-different
by construction: winner = Ch4 [24,4,12] vs weaker = rep3(x)rep3 [9,1,9]
(d 12 vs 9, k 4 vs 1).

**Result — the current FOM fails the gate at every depth:**

    shots     eps(winner)   eps(weaker)   resolved?
       20000    0.000e+00    0.000e+00   False
      100000    1.563e-07    0.000e+00   False
      500000    9.375e-08    1.250e-07   False
     2000000    1.719e-07    9.375e-08   False

Worse than unresolved: the ordering is INVERTED and inconsistent across depths
(100k and 2M rank the known-weaker code better; 500k ranks correctly). At the
GM point both codes' true eps sits BELOW the shot-noise floor 1/shots even at
2e6 shots — these are 0-vs-1-failure-event measurements; the "ranking" is
Monte-Carlo noise. **More shots does not help: the deepest, most expensive rung
gave a confidently wrong answer.**

**What this explains retroactively:** Campaign 2's deep leg looked healthy
because it was separating LOSERS (measurable eps ~1e-4), which it did cleanly.
The instrument works on bad codes and lies about good ones — the worst failure
mode for a search whose job is finding good ones. Direct Monte-Carlo eps at a
fixed deep operating point cannot rank strong codes, at any budget.

**Decision (strategy room, this date): replace the FOM with a noise-sweep
evaluator; steer on the sub-threshold slope.** Raise the physical noise
(nbar / k_ratio / p_m are already parameters of the frozen gm_css.fom referee)
to operating points where failures are COMMON, measure eps at a small fixed
ladder of points, fit, and rank by the suppression slope (Lambda). Threshold
crossing and extrapolated-eps-at-GM-point are logged alongside as secondary
observables from the same fit. Properties:
- Continuous by construction — never returns 0; ranks strong codes analytically.
- CHEAPER than what it replaces: at eps ~1e-3–1e-2, thousands of failure events
  per 20k shots — real statistics at pilot cost, vs 2e6 shots observing zero.
- NOT a moving-instrument violation: the referee (circuit, decoder, calibration)
  stays frozen; the sweep is a pre-registered protocol of fixed points read
  through it. The sweep ladder is fixed in the next PREREG before any candidate.

**Proof burden — explicitly unmet until measured:** the sweep evaluator is
UNPROVEN until it passes THIS SAME known-ordering diagnostic (winner vs weaker,
correct ordering, with margin, at every sweep budget). No loop gets built on it
before that. The gate that just failed the old ruler is the gate for the new one.

**Next session, start here:** build the sweep evaluator over the frozen referee
-> re-run the known-ordering diagnostic through it -> only on a pass, PREREG
Campaign 3 (efficiency-frontier, structured neighborhood, Lambda steering) with
priors gauged against the new ruler's measured cost per candidate.

---

## Entry 003 — 2026-07-09 — slope-ruler hardening FAIL: curvature confound (NO-GO #2); pivot to threshold-crossing

**Ran:** the sweep/Lambda evaluator (s5_sweep.py, adaptive ladder) through the
two-code gate, then the HARDER test Entry 001 prescribed: a 4-code known
ladder (rep4/rep3/rep2 (x) eh8 = d16>d12>d8, + [9,1,9] weak anchor) x 3 seeds.

**Two-code gate PASSED (seed 7): winner slope 3.80 vs weaker 2.24, margin
+1.57, secondary observable agreeing. Then hardening OVERTURNED it:**

    seed   rep4[32,4,16]  rep3[24,4,12]  rep2[16,4,8]  weak[9,1,9]  ordering
      7      +0.765          +3.803        +1.185       +2.238      SCRAMBLED (d16 lowest)
     101     +2.713          +3.768        +2.643       +2.180      d12>d16 swapped
    2026     +2.742          +2.906        +3.329       +2.114      d8 ranked best

Strongest code ranked lowest/middle/middle across seeds; the weak anchor beat
two structured codes at seed 7; slopes swing 3.5x seed-to-seed. **The gate
PASS was a lucky-seed artifact.**

**Root cause (deep, not tunable):** the slope FOM assumes a clean sub-threshold
power law, but the measurable-window constraint samples DIFFERENT codes on
NON-COMPARABLE parts of a curved relationship. A strong code only fails
measurably near its threshold — where the log-log curve FLATTENS — so better
codes return flatter slopes. The FOM inverts the ranking it exists to produce.
The selftest could not catch this: it validates fit arithmetic on synthetic
power laws, never the real near-threshold curvature.

**Scoreboard of dead rulers (both root-caused):**
- Direct-MC eps at the GM point (Entry 002): floors below shot noise for strong
  codes; 2e6 shots gave a confidently inverted order.
- Noise-sweep slope (this entry): curvature confound; multi-seed scrambling.
Cost note: strong-code sweeps are not cheap either (d=16 ~190-260s each).

**Method lesson (general):** a two-point single-seed gate is NECESSARY but not
sufficient — hardening (near-neighbors, multi-seed) before commit is what
caught this. A ruler is proven at the granularity the search needs, not the
granularity that is convenient to test.

**Decision: pivot to a threshold-crossing metric.** Find the noise multiplier
m* at which each code's eps crosses ONE FIXED common target (eps = 0.1); rank
by m* (higher = better). Every code is measured at the same observable, so the
curvature confound cannot arise — there is no slope to fit. Reuses the adaptive
probe/bisection machinery. More referee calls per code (a root-find), accepted.

**Proof burden (unmet):** the threshold evaluator must pass BOTH the two-code
gate AND the 4-code x 3-seed hardening ladder before anything steers on it.
The bar is now the hardened test; the two-code gate alone proved insufficient.

**Next session, start here:** s5_threshold.py --gate then --harden; only on a
hardened pass, PREREG Campaign 3.

---

## Entry 004 — 2026-07-09 — threshold-crossing NO-GO at the gate (dead ruler #3); composite hypothesis

**Ran:** s5_threshold.py --selftest (PASS, including on the saturating curves
that broke ruler #2) then --gate on the real referee. **GATE FAIL, inverted on
the easiest pair:** winner [24,4,12] m*=17.4 vs weaker [9,1,9] m*=36.3
(margin 0.48x). Hardening not run as a verdict -- moot after a failed gate.

**Root cause (third, distinct):** threshold and deep-sub-threshold performance
are DIFFERENT PHYSICAL AXES. m*-at-eps=0.1 asks "where does the code stop
working" (high-noise property); the search needs "which code has lower error
at the deep GM point." These do not co-order: the k=4 product code has better
deep suppression but a LOWER threshold (more logicals, higher-weight checks);
the simple k=1 product survives to higher noise but suppresses worse. The
metric measured its axis correctly -- it is the wrong axis.

**Three dead rulers, three root causes:**

| ruler | fails because |
|---|---|
| direct-MC eps @ GM (E002) | target floors below shot noise -- unmeasurable |
| noise-sweep slope (E003) | curvature confound -- non-comparable noise ranges |
| threshold m* (E004) | measures threshold, a different axis than deep eps |

**Meta-lesson:** every cheap HIGH-NOISE proxy measures a real quantity that is
correlated-but-not-identical to deep-sub-threshold eps, because high-noise
physics (threshold, near-threshold curvature) is governed by different
mechanisms than deep suppression. The quantity the search needs is precisely
the one that is unmeasurably rare at the operating point. This is a structural
obstacle, not a tuning problem.

**Composite hypothesis (ruler #4, PRE-REGISTERED before its test data):**
predict deep suppression analytically from two measurable ingredients:
    score = t * log10(m*),  t = the fault exponent, d exact from VERIFY,
                            m* from s5_threshold.py (the axis it measures RIGHT)
Higher score = better. KNOWN CAVEATS, stated before the data: (1) the exponent
convention decides the seed-7 gate pair -- t=ceil(d/2) orders it WRONG
(-7.45 vs -7.80), t=floor(d/2)+1 orders it RIGHT (-8.68 vs -7.80); two
defensible conventions, opposite verdicts on the only measured pair. (2) the
prefactor A (combinatorial, grows with n) is ignored. So this is a HYPOTHESIS.
Proof burden: the hardened 4-code x 3-seed ladder, using measured m* for all
four codes -- BOTH exponent conventions computed, published either way.

**Status of s5_threshold.py:** committed as the m*-MEASUREMENT INSTRUMENT
(selftest + correct threshold-axis measurement), NOT as a ranking ruler --
its gate failure as a standalone ruler is this entry.

**Next step:** run s5_threshold.py --harden to COLLECT m* for the 4-code x
3-seed ladder (purpose changed: ingredient collection, not ruler validation),
then compute the composite ordering under both exponent conventions.

---

## Entry 005 — 2026-07-09 — composite is distance-dominated; the ruler quest ends: steer on distance-per-weight

**Ran:** m* collection, 4 codes x 3 seeds (s5_threshold.py --harden, purpose:
ingredients). m* is highly reproducible (e.g. rep4: 18.6/18.5/18.6) -- the
INSTRUMENT is solid. Composite computed under both pre-registered conventions:

| convention | composite order | vs pure distance |
|---|---|---|
| A: ceil(d/2)    | rep4 > weak > rep3 > rep2 | FAIL (weak leapfrogs d12) |
| B: floor(d/2)+1 | rep4 > rep3 > weak > rep2 | matches |

**Why this kills the composite (not saves convention B):**
1. Decomposition: the exponent t -- i.e. DISTANCE, free from VERIFY -- does
   essentially all the ranking work. m* (the only expensive ingredient) is at
   best a one-bit tie-breaker (B) and at worst actively destroys a correct
   distance ordering (A). Picking B because it "works" would be post-hoc; the
   caveat pre-registered in Entry 004 fired exactly as feared.
2. The two candidate ground truths (harness-assumed vs pure-distance) disagree
   precisely on the one pair m* decides (weak d=9 vs rep2 d=8) -- and that
   ground truth is UNMEASURABLE at the GM point (Entry 002). We were validating
   a proxy against a truth we cannot obtain. Also noted: the harden harness's
   built-in "known order" was itself distance-inconsistent (ranked d=8 above
   d=9); its FAIL verdicts were against a flawed reference.

**The wall (final synthesis of the ruler quest, Entries 002-005):**
- The quantity the search needs (GM-point per-logical eps) is unmeasurable by
  direct simulation -- it floors below shot noise.
- Every cheap high-noise proxy measures a DIFFERENT physical axis (threshold,
  near-threshold slope) that does not co-order with deep performance.
- The one signal that tracks deep performance -- code distance -- is FREE from
  VERIFY, and no simulated proxy demonstrated robust value on top of it.
Four rulers, four root causes. This is a structural result about closed-loop
QEC code search, not a tuning failure.

**DECISION: Campaign 3 steers on distance-per-weight (and per-qubit) from
VERIFY.** Free, exact, reproducible, and literally Ch4's central lesson. The
simulated referee is demoted to FINALIST VERIFICATION ONLY: deep same-
instrument ratios on the top handful of candidates (rule-of-three bounds where
floored) -- the machinery that already works. Honest reframe recorded: with an
algebraic fitness, "the loop learns" means fast exploration of code space, not
per-candidate physics; the referee arbitrates only at the end.

**Parked (escalation path, not default):** rare-event / importance sampling to
measure true GM-point eps -- only if algebraic steering proves insufficient or
a finalist comparison genuinely requires a measured deep ratio.

**Next session, start here:** PREREG Campaign 3 -- structured neighborhood,
fitness = distance-per-weight/qubit from VERIFY (exact via classical_verify,
KMAX-gated), learn-vs-random control retrying Q1 under a fitness that cannot
saturate or lie, finalists verified deep same-instrument. The ruler saga
(Entries 002-005) is the methods backbone of whatever chapter this becomes.

---

## Entry 006 — 2026-07-10 — Campaign 3: the loop works; the objective was the gap

**Ran:** algebraic efficiency-frontier search (PREREG_search3, driver
s5_algsearch.py @ a8cf602), 15 min/arm, learn vs random, seed 20260710.
Full resolutions in PREREG_search3.md; verdicts P1 TRUE, P2 TRUE, P3/P4
FALSE, P5 TRUE-with-decisive-caveat.

**The first positive of the arc, properly bounded:** the loop genuinely
learned (452x valid-code rate vs random; beat the hand-picked Ch4 winner at
gen 44) -- Q1's redemption under a fitness that cannot saturate or lie. And
then the capstone: the deep referee showed the efficiency winner [34,6,12] is
30-49x WORSE than a d=7 repetition code on actual per-qubit logical error.
The optimizer was faithful; the objective was wrong. Efficiency-at-fixed-
distance does not proxy error performance under GM bias.

**Mechanisms recorded (feed Campaign 4 design):**
1. PLATEAU KILLS THE BANDIT: credit = relative best-improvement goes to ~0
   once best stalls (gen 44 of 1646) -> weights renormalize to uniform -> the
   adaptive component contributes nothing for 96% of the run. Same family as
   Campaign 2's saturation, new guise: the steering signal died, this time
   from success-then-stall rather than measurement floor. Fix candidates:
   credit on feasibility yield or diversity gain, not only frontier delta.
2. EFFICIENCY != ERROR: the objective optimized (k/(n+r) at d>=12) rewards
   packing logicals; GM-bias error performance rewards something else
   (repetition still wins). Any future objective must be validated against
   the referee's verdict on KNOWN codes before a campaign optimizes it --
   the ruler-gate discipline (Entries 002-005) applies to OBJECTIVES too.
3. REPRODUCIBILITY GAP (driver lesson): stage="fit" rows log hash only; full
   H (b64) rode only on frontier events, of which there were none -- so the
   top find was recoverable only by a 15-min deterministic replay (which
   worked, hash-match, and doubled as the full-scale determinism proof).
   One-line fix before Campaign 4: log b64 for every new running-best.

**Standing throughline, three campaigns in:** repetition dominates practical
error under realistic bias; the loop's demonstrated value is fast honest
exploration + exposing wrong objectives cheaply. That IS acceleration -- of
learning, which is the loop's actual product so far.

**Next session, start here:** Campaign 4 needs an objective the referee
endorses on known codes FIRST (objective-gate, analogous to the ruler-gate).
Candidate: same-instrument error ratio at matched qubits IS the objective --
but Entry 002 says it floors for strong codes, so the honest version is
constrained: only objectives measurable on their intended winners. Design
work, fresh eyes.

---

## Entry 007 — 2026-07-10 — the wall, fully mapped: all measurable-error objectives disqualified; Campaign 4 steers algebraic

**Ran (read-only, objective-gate):** (1) rank-stability map -- 8 known codes x
6 noise elevations m=(1,1.5,2,3,5,8), one frozen instrument, depth-matched,
2e5 shots/cell (data: s5_rankmap_data.json). (2) power-law extrapolation gate
on the same data -- predict eps(m=1) from each code's lowest measurable anchor
via eps(1)=eps(ma)/ma^t, both exponent conventions, pre-stated pass bar
(every measurable truth within ~3x AND floor-consistent).

**Map result -- the ranking FULLY INVERTS across the noise range:** eh8(x)eh8
[64,16,16] is #1 (best, 7.8e-8) at the operating point and #8 (worst, 2.4e-2)
at m=8; repetition codes are floored-or-worst at m=1 and best at m=8. The
threshold-vs-suppression anti-correlation (E004's axis) is now a measured
crossover map. At m=1, half the ladder floors (E002 confirmed across 8 codes).
=> No single measurable elevation's error-ranking is a faithful proxy for
operating-point performance. Elevated-noise error objectives: DISQUALIFIED.

**Extrapolation gate result -- MODEL DIES:** both conventions fail 2 of 4
measurable truths, including the Ch4 winner (off 5.7x / 8.5x) and the C3 find
(3.3x / 4.9x). Mechanism: the lowest measurable anchor (m=1.5) sits in the
floor-flattened region, not the clean power-law regime, so the exponent
over-predicts suppression toward m=1 -- E003's curvature confound in
extrapolation form. Floor-consistency passed (necessary, not sufficient).

**The completed ledger -- six cheap error-objectives, six pre-registered kills:**

| approach | gate failure |
|---|---|
| direct-MC eps @ operating pt (E002) | floors -- unmeasurable |
| noise-sweep slope (E003) | curvature confound + seed-scramble |
| threshold m* (E004) | wrong physical axis |
| composite d + m* (E005) | distance-dominated; m* null-or-harmful |
| elevated-noise error ranking (E007) | INVERTS vs operating point |
| power-law extrapolation (E007) | off 5.7-8.5x on the codes that matter |

Structural conclusion, now proven not inferred: the quantity the search needs
is unmeasurable at the operating point, and everything cheap that IS
measurable either lies, inverts, or adds nothing over free algebra.

**Refinement from the map (handle with care):** at m=1 the ordering is roughly
by distance, but NOT purely: at matched d=12, the structured winner (k=4,
3.1e-7) beats the C3 crossover product (k=6, 2.1e-5) by ~70x -- far more than
packing alone explains -- while eh8(x)eh8 (k=16, maximally packed) is #1
overall. So "penalize high k" is too crude; the deficit looks STRUCTURAL, not
purely packing. Any penalty term in Campaign 4's fitness must itself pass a
known-code gate before it steers (the objective-gate applies to fitness
REFINEMENTS too). Until a penalty form is gated: fitness = distance under the
caps, unadorned.

**DECISION (empirically forced):** Campaign 4 steers on exact algebraic
distance from VERIFY under the caps; any structure/packing penalty enters only
after passing its own known-code gate; the referee is used solely for
operating-point floor/bound verdicts on finalists. Importance sampling remains
the parked escalation -- now provably the ONLY route to a measured
operating-point ranking of strong codes.

**Next session, start here:** gate a penalty form on the m=1 column of
s5_rankmap_data.json (knowns only, no new shots), then PREREG Campaign 4.

---

## Entry 008 — 2026-07-10 — first gated fitness refinement: d − λ·col_deg_max (scoped)

**The C3 anomaly root-caused:** the C3 find [34,6,12] carries a col_deg_max=9
hotspot qubit (winner 5, rep2 4, eh8x8 6) -- column degree = CX exposure per
cycle, so a degree-9 qubit accumulates ~9x gate noise. The efficiency search
exploited the UNCAPPED constraint dimension: row weight was capped (w<=4),
column degree was not. The optimizer gamed the constraint nobody wrote down.

**Penalty gate (knowns only, zero new shots, s5_rankmap_data.json m=1 column):**
score = d - lambda*col_deg_max reproduces the full measurable ordering AND
stays floor-consistent for a WIDE window lambda in [0.8, 4.0] (33 contiguous
steps). Distance alone (lambda=0) FAILS both. Binding constraints are
physically clean: lambda>0.8 demotes the hotspot below a lower-d clean code;
lambda<4 keeps distance dominant among clean codes. First fitness refinement
in the saga to pass a known-code gate.

**Caveats (recorded before use):** 4 measurable codes = 3 pairwise
comparisons; feature and form chosen after seeing C3 fail -- admissible
hypothesis, not law; real test is out-of-sample on Campaign 4's own finds.

**CROSS-FAMILY SCOPE LIMIT (caught at the gate, decisive):** against
repetition the proxy CONTRADICTS the measured record -- it scores rep-7 (3)
above the winner (2), but Ch4's same-instrument scoreboard measured the
winner BEATING its d=7 rep comparator at 0.255. And within the rep family the
proxy grows unboundedly (rep-n scores n-4), so an unscoped search would
trivially converge to long repetition -- a claim the gate never licensed.
THEREFORE: the fitness is gated for the k>=2 product/structured space ONLY;
repetition is excluded from the search space and reserved as the finalist
referee baseline (its historical role). Landmark check inside scope holds:
eh8(x)eh8 S=4 > winner S=2, matching measured m=1 truth.

**Campaign 4 (PREREG_search4.md):** maximize S = d - 2*col_deg_max (lambda=2,
window midpoint, frozen) over k>=2, w<=4, n<=64, k<=16 (exact d),
qubits-per-logical <= 13 (the winner's budget; also keeps the search inside
the gated region). Frontier to beat: eh8(x)eh8 S=4 at qlog=8. Bandit credit
fixed per Entry 006: feasibility-blended, plateau-proof. Referee verifies
finalists at the operating point (floors -> bounds, honestly).
