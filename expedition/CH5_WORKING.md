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
