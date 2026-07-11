# PREREG_union.md — Pre-registration: decoder-aware union sampler (S7)

Date: 2026-07-10. Registered BEFORE any build or run. Status of every prior:
OPEN-UNVERIFIED. Governs: `s7_union.py` (to be built) and the core-logging
extension to `s6_sampler.py`. Supersedes NOTHING: PREREG_sampler.md stays in
force for its instruments (G0/G1-gated DEM reduction, conditional-Bernoulli
draws, decoder path, conversions — all reused verbatim here).

## 0. Decision record (resolves the Entry-010 fork on the record)

Fork option (c): the parity finding is treated as the redesign trigger.
Rationale: (i) mechanism — λ(m=1)=8.36 means failures are conspiring fault
PATTERNS at typical weight; fault count is the wrong conditioning variable,
measured, not conjectured; (ii) economics — the remaining G2 rows at parity
efficiency cost hours each against K2's 4h line for no methodological gain.
The remaining G2 truth rows (winner rep3⊗eh8, eh8⊗eh8, C3-from-committed-
artifact) are RETAINED UNCHANGED as this design's acceptance gate — same
truths, same bands, same conventions. rep2⊗eh8 goes first, again.

## 1. The design (U1–U5)

**U1 — Failure cores.** A core is a minimal failing fault set: a set of DEM
mechanisms whose firing (alone) the referee's decoder miscorrects, minimal
under decode-checked single-removal. Failure is NOT assumed monotone
(bystanders can rescue); cores are a search basis, not an oracle. Sources:
(a) exact w≤2 enumeration with identity logging (s6 extension: the G2 row
found f_2=1.885e-7 > 0 but did not log WHICH pairs; re-run and log — ~139k
decodes, minutes); (b) harvest: every failing sample from any run is
minimalized by greedy decode-checked removal to a core; (c) closure: cores
found during U3 residual sampling feed back into the basis (registered
iteration, §3).

**U2 — Karp–Luby first term.** T1 = P(fail ∧ S contains a known core).
Estimator: draw core c w.p. ∝ π_c = Π_{j∈c} p_j; set S = c ∪ Bernoulli(rest);
correct union multiplicity by the standard Karp–Luby device (count |{known
cores ⊆ S}| when the basis is small; the "c is first contained core" Bernoulli
check when large); multiply by the DECODER's verdict fail(S) — rescues are
thereby handled exactly, the estimator stays unbiased for T1 by construction.
Same-instrument decoding (make_bposd verbatim), D9 conversions imported.

**U3 — Residual term.** T2 = P(fail ∧ S contains NO known core), estimated
with the G1-gated stratified sampler filtered to core-free samples
(rejection), reported with D7/D8 honesty (CI + rule-of-three + tail bracket).
P̂_L = T̂1 + T̂2 with combined CI; publish the bracket when T2 floors.

**U4 — Core-closure iteration.** Failing core-free samples from U3 are
minimalized into new cores; T1/T2 re-estimated. Registered stopping rule:
stop when T̂2's upper bound ≤ 10% of T̂1, or after 3 closure rounds —
whichever first. More rounds require a dated addendum.

**U5 — Efficiency is a REGISTERED criterion, not a hope.** The parity
baseline on rep2⊗eh8 is on record: ±16% at ~540k decodes (Entry 010). This
design exists to beat it or die: see gate U-G1.

## 2. Gates (pass in order; no strong-code row before U-G1)

**U-G0 — machinery selftest.** Exact w≤2 core identities on rep2⊗eh8
committed and reproduced; Karp–Luby estimator validated on a synthetic union
(known analytic answer, assertion ≤ 1e-12 where exact, 5σ where sampled);
multiplicity correction cross-checked both ways (count vs first-core) on a
small basis; minimalizer idempotent (minimalize(core) == core).

**U-G1 — the efficiency gate (rep2⊗eh8, m=1).** PASS iff the sampler
reproduces the SAME MC band as G2 row 1 ([9.22e-6, 1.47e-5], point inside,
rel half-width ≤ 25%) at total decode cost ≤ 108,000 (5× under the parity
baseline, enumeration and harvest costs INCLUDED). Miss the band = FAIL;
make the band over budget = FAIL-ON-EFFICIENCY (kills the design's thesis
even if unbiased).

**U-G2 — the three remaining truth rows,** unchanged from PREREG_sampler §4:
winner rep3⊗eh8 [3.79e-8, 1.13e-6]; eh8⊗eh8 [9.46e-9, 2.82e-7]; C3 (H from
committed c3_find_H.json, hash f42569e3fb53016f) [1.80e-5, 2.38e-5]. Per row:
25%-CI conclusiveness, band intersection; point-inside required for C3 only
(the two strong-code truths are 2-event bands — the sampler is expected to
SHARPEN them; landing a tight interval inside the wide band resolves the row).
Budget ceiling per row: 4h wall-clock on the workbench (K2 carried over).

**Only after U-G2:** floored codes and the winner-vs-repetition question —
the operating-point ranking that four campaigns could not measure.

## 3. Kill criteria

**KU1 — non-sparse failure structure.** If after 3 closure rounds on
rep2⊗eh8 T̂2's upper bound is still > 25% of T̂1, failures are not
core-sparse; the union thesis is dead for this channel. Record and stop.
**KU2 — rescue blowup.** If the decoder rescues > 90% of planted minimal
cores at m=1 (T1 acceptance collapses), the core basis does not predict
failure in context; kill before burning budget.
**KU3 — basis explosion.** If |known cores| exceeds 50,000 before the U4
stopping rule fires, multiplicity handling and memory dominate; redesign
required by addendum, not silent capping.

## 4. Priors (author-delegated; resolved mechanically)

| # | Claim | Prior |
|---|---|---|
| Q1 | U-G0 passes | 0.85 |
| Q2 | w≤2 core identities: ≥1 and ≤50 distinct failing pairs on rep2⊗eh8 | 0.75 |
| Q3 | U-G1 passes (band AND ≤108k decodes) | 0.5 |
| Q4 | Closure converges on rep2⊗eh8 (T2-UB ≤ 10% of T1 within 3 rounds) | 0.5 |
| Q5 | Rescue rate of planted minimal cores at m=1 is < 50% | 0.6 |
| Q6 | U-G2: all three rows conclusive within their 4h ceilings | 0.45 |
| Q7 | Winner vs eh8⊗eh8 separated (non-overlapping 95% CIs at m=1) | 0.5 |
| Q8 | No kill criterion fires before U-G2 completes | 0.55 |

One line each: Q1 is machinery. Q2: f_2·C(139128 pairs) odds-weighted →
order 1-10 pairs expected; 50 is generous. Q3 is the thesis bet — genuine
uncertainty, priced at a coin flip. Q4/Q5 are the two mechanisms that could
quietly gut it. Q6 discounts for the eh8⊗eh8 circuit size (M grows ~4×,
KU3 watch). Q7: the truth gap may be inside achievable CIs. Q8: joint
survival of three hazards.

## 5. Carried discipline

Everything in PREREG_sampler §7 verbatim, plus: failing samples are LOGGED
(b64 of the fired-mechanism index set) from now on in every S6/S7 run —
harvested cores are first-class data; core basis committed as a JSON artifact
with h_encode-style hashing; the stim machine-boundedness note (Entry 010
correction, discovered 2026-07-10) governs every fingerprint claim: exact
seed-reproduction claims are per-machine for stim paths, cross-machine for
numpy paths.

## 6. What this PREREG does not claim

No claim the union thesis holds (U-G1/KU1 decide); no claim the strong-code
ranking is reachable (Q6/Q7 are priced at coin flips); no reuse of this
design's verdicts for any channel other than GM at the registered operating
point without a new gate run.

---
