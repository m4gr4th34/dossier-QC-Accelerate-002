# PREREG_gapshare.md — Pre-registration: the decoder-gap share measurement (S9, Entry 013)

Date: 2026-07-11. Registered BEFORE any run. Priors OPEN-UNVERIFIED.
Governs: `s9_gap.py`. Instrument: the FROZEN referee + the G0/G1-gated S6
stratified machinery (numpy paths — cross-machine exact). No referee change:
this measurement CLOSES Chapter 5; the intervention (referee-v2) is a
Chapter-6 matter.

## 1. Question and metric

Of the logical failures at the GM operating point (m=1), what fraction are
DECODER-CREATED — failing shots whose physical fault set flips NO logical
observable (truth = 0), where BP-OSD's correction introduces the logical
error? This is a hard LOWER BOUND on the decoder-induced share (truth≠0
failures are not attributed: they may be unavoidable degeneracy). Secondary
breakdown, recorded but not a registered claim: among truth≠0 failures,
pred=0 (missed) vs pred≠truth≠0 (misidentified).

## 2. Method

Per code: DEM via the referee's own reduction; stratified conditional-
Bernoulli sampling over fault-weight strata (gated at G1); per stratum w
record n_w, fails_w, benign_w (failures with truth=0). Weighted share
Q = Σ P(w)·benign_w/n_w ÷ Σ P(w)·fails_w/n_w, with a deterministic-seed
bootstrap (1000 resamples per stratum) for a 95% interval. Codes: the five
with observed failures — rep2⊗eh8, winner rep3⊗eh8, frontier eh8⊗eh8,
C3 (H from c3_find_H.json, hash-anchored), rep-7. rep-13 is a floor with
zero observed events and is not classifiable; recorded as such.
Pilot 300/stratum, then contribution-weighted allocation toward
failure-bearing strata; registered seeds 910000+code_index. Budgets TIERED by
failure rate: Tier A (rep2⊗eh8, C3; p_any ≥ 3e-4): 250,000 decodes each,
minutes. Tier B (winner 3e6, frontier 1.5e6, rep-7 3e6 decodes; wall-clock
kill 2.5h per code): the leaderboard codes, run overnight — for codes with
p_any ~ 5e-6, failure classification at operating-point proportions costs
near direct-MC prices (the Entry-010 parity mechanism applies to
classification too, measured in strategy-room validation). Per-code runs
are independent and seed-deterministic: an interrupted code reruns cleanly. Landmark selftest: G2 anchors
verbatim, decoder-config anchor, C3 hash anchor, and a synthetic
classification check (a planted truth=0 failing set and a planted truth≠0
failing set classify correctly).

## 3. Priors

| # | Claim | Prior |
|---|---|---|
| S1 | Q > 0.5 on at least 4 of the 5 codes (decoder-created failures are the majority) | 0.6 |
| S2 | Q spans a range wider than 20 percentage points across codes | 0.5 |
| S3 | ≥ 4 of 5 codes yield ≥ 30 classified failures within budget | 0.65 |
| S4 | Full campaign ≤ 8 h wall-clock on the workbench | 0.75 |

S1 is the finding-bet: "distance is not the axis" and the trap discovery
both point at the decoder, but 50% is a real line. S2: if Q is roughly
universal, the gap is a property of the DECODER; if it varies widely, it is
a code-decoder interaction — either is informative, S2 just prices which.

## 4. Kill criteria

KS1 — any code with < 30 classified failures at budget: that code's Q
publishes as "insufficient events," no share claimed. KS2 — per-code 2.5h wall-clock kill (Tier B): publish what the run
holds.

## Disclosure

A strategy-room validation preview exists (rep2⊗eh8 Q ≈ 0.23 tight; rep-7
unstable at small budget — the observation that motivated the tiered
budgets). Priors S1/S2 were drafted before the preview and stand unchanged;
the record run resolves them regardless (the S8 precedent).

## 5. What this does not claim

No attribution of truth≠0 failures; no referee change; no claim about
referee-v2's effect (Chapter 6); Q is a lower bound on decoder-induced
share, stated as such everywhere.

---
