# PREREG_sampler.md — Pre-registration: fault-weight stratified sampler (S6)

Date: 2026-07-10. Registered BEFORE any build or run (protocol: PREREG first;
dated addenda permitted pre-run). Status of every prior below: OPEN-UNVERIFIED
(FORECAST-type, resolved mechanically by the gates). Governs: `s6_sampler.py`
(to be built), gated per §4 before any campaign use.

## 1. Motivation (one paragraph)

Entries 002/003/004/007 established that operating-point per-logical eps of
strong codes is unmeasurable by direct MC (floors below shot noise; more shots
produced a confidently inverted order) and that every cheap proxy measures a
different axis. The one ungated route to a *measured* operating-point ranking
is rare-event sampling. This document pre-registers the design, its gates, and
the author-delegated priors before a line of campaign code runs.

## 2. Target capability

Estimate per-logical, per-round eps at the GM operating point
(nbar=11, k_ratio=1e-4, p_m=6e-3, mode=xonly, basis=X, ROUNDS=8 — the exact
`s5_rankmap.py` configuration) for codes with true eps ~ 1e-7..1e-10, with
honest 95% CIs, at cost small enough to run on the canonical Mac venv.

## 3. Design (D1–D9)

**D1 — Generative model = the referee's own DEM.** `evaluator_v1.logical_rate`
already reduces the circuit to independent Bernoulli mechanisms via
`circuit.detector_error_model(decompose_errors=False, flatten_loops=True)` →
`dem_to_matrices(dem)` → `(H, O, priors)`: mechanism j fires with prob p_j,
flips detector set H[:,j] and observable set O[:,j]. For a pure-Pauli circuit
(all noise here is Z_ERROR / X_ERROR / correlated E), the DEM distribution
over (dets, obs) equals the circuit sampler's distribution exactly — stim's
merging of identical-signature error locations into one mechanism with
XOR-combined probability is exact, not approximate. The sampler therefore
samples fault sets from the *same object the referee decodes against*. No
model gap by construction; G0 verifies it empirically anyway.

**D2 — Stratification by fault weight.** Let W = number of fired mechanisms
(Poisson-binomial over M mechanisms with probs p_j). Then
  P_any = Σ_w  P(W=w) · f_w,   f_w := Pr[decoder fails | exactly w faults].
Deep sub-threshold, P(W=w) concentrates at small w and f_w is O(1) in the
strata that matter — the rare-event bottleneck is removed by conditioning,
IF f_w at the dominant strata is not itself tiny (registered kill criterion
K1, §5).

**D3 — Exact stratum weights.** P(W=w) computed exactly by the standard
Poisson-binomial DP, O(M·w_max). No Poisson approximation anywhere in the
published number.

**D4 — Exact conditional sampling.** Conditioned on W=w, fault sets are NOT
uniform: Pr[S] ∝ Π_{j∈S} p_j/(1−p_j). Sample by conditional-Bernoulli
sequential inclusion using suffix Poisson-binomial tables (exact; O(M·w_max)
precompute, O(M) per draw). Pre-registered trap: uniform w-subsets
(hypergeometric) are BIASED here and are explicitly forbidden.

**D5 — Same-instrument decoding.** Each sampled fault set S is decoded as
dets = ⊕_{j∈S} H[:,j], truth = ⊕_{j∈S} O[:,j], with the *identical* decoder
object the referee uses: `make_bposd(H, priors)` — same bp_method="ms",
max_iter=30, osd_method="osd_e", osd_order=4, same priors vector. Failure iff
predicted observables ≠ truth. Any decoder divergence disqualifies the run
(this is the same_instrument discipline that governs s5_campaign.py ratios).

**D6 — Exhaust the bottom strata.** For w where C(M,w) is enumerable within
budget (w=1 always; w=2 if M(M−1)/2 decodes fit budget), compute f_w exactly
by enumeration — zero sampling error where the strata are cheapest and most
influential.

**D7 — Truncation with an explicit bracket.** Choose w_max such that the exact
tail T = Σ_{w>w_max} P(W=w) satisfies T ≤ 0.01 · P̂_any(lower). Publish
P_any as the bracket [Σ_{w≤w_max} P(w)·f̂_w,  same + T] (tail bounded by
f_w ≤ 1). If the bracket is wider than the CI discipline allows, the result
publishes as a bound, never a number.

**D8 — Honest CIs.** Var(P̂_any) = Σ_w P(w)² · Var(f̂_w); Wilson intervals per
stratum (small counts); zero-fail strata contribute rule-of-three upper bounds
(3/N_w), never zeros presented as measurements (landmine 11 carries over).
Allocation: pilot N0 per stratum, then Neyman-style reallocation
∝ P(w)·√(f̂_w(1−f̂_w)); allocation is an efficiency choice and cannot bias the
estimator.

**D9 — Conversion by the referee's own functions.** P̂_any → eps via the
imported `fom` conventions: pk = 1−(1−P_any)^(1/k), eps = per_round(pk, 8)
with its 0.5-saturation form. Re-derivation of these formulas inside
s6_sampler.py is forbidden; import them.

## 4. THE GATES (non-negotiable; pass in order; no campaign use before G2)

**G0 — DEM-equivalence (isolates model bugs).** Plain unstratified Bernoulli
sampling from (H, O, priors) with the D5 decoder, on rep2⊗eh8 at m=3 and m=8
(abundant events), same shots as a fresh direct `fom` run at a fresh seed:
PASS iff the two eps estimates agree within 3σ (two-proportion z on p_any).

**G1 — Stratification-correctness (isolates D2–D4 bugs).** The stratified
estimator vs the G0 plain-DEM estimator, same elevations, same code:
PASS iff 95% CIs overlap at both elevations and the stratified point sits
inside the plain estimator's 95% CI at m=3.

**G2 — The known-code gate (the four m=1 truths; from the handoff, quantified
here).** Direct-MC failure counts recovered from committed
`s5_rankmap_data.json` by inverting the exact fom conventions at
SHOTS=200000, ROUNDS=8 (counts land on exact integers — a self-check of the
reconstruction; Code must independently re-verify against the rankmap session
record before relying on them):

| truth | eps (m=1) | F (fails) | 95% Poisson eps-band (Garwood) |
|---|---|---|---|
| rep2⊗eh8 [16,4,8]  | 1.1721e-5 | 75  | [9.22e-6, 1.47e-5] |
| C3 find [34,6,12]  | 2.0741e-5 | 199 | [1.80e-5, 2.38e-5] |
| rep3⊗eh8 [24,4,12] | 3.1250e-7 | 2   | [3.79e-8, 1.13e-6] |
| eh8⊗eh8 [64,16,16] | 7.8125e-8 | 2   | [9.46e-9, 2.82e-7] |

PASS requires, per code: (a) sampler relative 95% CI half-width ≤ 25% at the
registered budget — else the run is INCONCLUSIVE, not a pass; (b) sampler CI
intersects the MC band; (c) for the two well-measured truths (rep2⊗eh8, C3)
the sampler *point* lies inside the MC band. The two strong-code truths are
2-event measurements; their bands are wide by nature and (b) is the only
criterion with power there — the sampler is expected to *sharpen* them, not
match their points. Gate order within G2: rep2⊗eh8 FIRST (cheapest measurable
truth); no generality — no second code — until it passes.

Dependency: C3's H must be replayed or recovered from the Campaign-3 log
before its G2 row can run (handoff note "H: replay or log").

**Only after G2:** the floored codes (rep-7/13, rep3⊗rep3, rep4⊗eh8) and the
winner-vs-repetition question. Objectives, rulers, operators, and samplers
all get gates; this sampler is UNPROVEN until G2 passes.

## 5. Registered kill criteria (what falsifies the design, cheaply)

**K1 — Conditional rarity.** If at the strata carrying ≥80% of Σ P(w)·f̂_w the
measured f_w < 1e-3, the conditioning has not removed the rare-event problem
and the cost advantage over direct MC collapses. Verdict: design killed for
this regime; fall back to the pre-registered alternates (splitting/RESTART,
weight-biased Pauli reweighting) in a NEW prereg.

**K2 — Budget.** If the rep2⊗eh8 G2 row cannot reach the 25% CI criterion
within 4h wall-clock in the canonical venv, the design is not tractable as
built. Profile before killing (BP-OSD per-decode cost is the lever), but the
4h line is the registered verdict boundary.

**K3 — Mechanism-count blowup.** If M for eh8⊗eh8 makes the O(M·w_max) DP or
the per-draw O(M) cost dominate decode cost by >10×, the exact-conditional
machinery needs redesign before that row runs (addendum required; not a
silent swap).

## 6. Priors (author-delegated; resolved mechanically by the gates)

| # | Claim | Prior |
|---|---|---|
| P1 | G0 passes at both elevations | 0.85 |
| P2 | G1 passes | 0.80 |
| P3 | G2 rep2⊗eh8 row passes (a+b+c) | 0.70 |
| P4 | G2 passes on all four truths | 0.55 |
| P5 | Post-G2, sampler separates rep3⊗eh8 vs eh8⊗eh8 at m=1 with non-overlapping 95% CIs | 0.55 |
| P6 | f_w = 0 exactly for all w ≤ 2 on rep2⊗eh8 (by D6 enumeration) | 0.65 |
| P7 | No kill criterion (K1–K3) fires before G2 completes | 0.65 |

Reasoning, one line each: P1 rides an exactness argument, residual risk is
implementation (correlated-E handling, observable bookkeeping). P2 is where
subtle bias hides (D4 is the classic mistake surface). P3/P4 discount for
decoder-path drift and the C3 replay dependency. P5: the sampler should
sharpen two 2-event bands into a ranking, but the true gap may be inside
achievable CIs. P6: circuit-level distance can undercut code distance; 0.65
reflects that d=8 suggests but does not prove empty low strata. P7 is the
joint survival of three independent hazards.

## 7. Carried-over discipline (binding on the build)

Venv sourced always; python -u for detached runs; per-candidate try/except
with shot-noise-floor clipping (1/N, never >0 gating); landmark-gate the
derived driver before launch (assert anchors: the four G2 eps values and the
decoder config string must appear verbatim in s6_sampler.py's selftest);
checkpoint + byte-identical resume for any long run; b64+shape logged for any
H it touches; zero-fail cells publish as rule-of-three bounds with
scoreboard_kind labels; transport via .txt file-download + sha256 guard.

## 8. What this PREREG does not claim

No claim that the sampler works (that is G0–G2's job); no claim about the
winner-vs-repetition answer; no claim that C3's H is recoverable (dependency,
not assertion). Negative results at any gate are first-class and get their
own entry.
