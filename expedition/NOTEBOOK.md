# Expedition notebook — AI search for cat-qubit outer codes

**Chapter 4 research infrastructure.** This directory is the working instrument of an
AI-driven search for quantum error-correcting outer codes tailored to biased-noise
(cat-qubit) hardware. Everything here follows the dossier's rules: every claimed code
parameter is machine-verified, negatives are kept, and every label tells the truth
about its certainty grade.

**Honesty header for everything below:** all Day-1 results use a *code-capacity*
biased-Pauli noise model (px = p/(η+1), pz = p·η/(η+1), Y folded — stated convention)
at small n. Family-level behaviors reproduced here are qualitatively known in the
bias-tailoring and qLDPC literature; Day-1 is **calibration of the instrument plus
instrument-produced measurements**, not novelty claims. Novelty claims wait for the
circuit-level finite-bias evaluator (v1, next), derived from published Ocelot device
parameters (Putterman et al., Nature 638, 927–934 (2025); data DOI
10.5281/zenodo.14257632).

## Environment (Day 1 — 2026-07-07)

**Canonical stack (all measured tables below):** Python 3.12.13 · numpy==2.5.1 ·
ldpc==2.4.1 (BP-OSD). All seeds fixed in-source: on this stack every table reproduces
bit-exact. Deterministic ground-truth suites run in CI (`expedition-tests.yml`, numpy
only). Development also ran on a second build (Python 3.12.3 · numpy 2.4.4 · ldpc
2.4.1; stim 1.16.0 installed, unused in v0) — see Reproducibility.

## Reproducibility (a Day-1 finding in its own right)

The executor's pre-commit reproduction gate caught a divergence between two builds
differing only in numpy (2.4.4 vs 2.5.1, same ldpc): **deterministic artifacts are
bit-exact across builds** (all verifier outputs, distances, gates, the seed
refereeing, the search's structural results), while **Monte-Carlo digits from
nontrivial BP-OSD decoding are build-sensitive** — trivial wmax=2 repetition decodes
reproduce bit-exact, higher-weight codes tip a small fraction of shots differently
through floating-point paths. Every observed deviation fell within the stated 95%
intervals and no qualitative conclusion changed. Policy adopted: tables are the
canonical stack's bytes; reproduction on the pinned stack must be exact; on other
builds, CI-consistent agreement is the expected grade. The gate that caught this
was the point of having it.

## Modules

- `verify_code.py` — the mechanical floor. CSS commutation, k via GF(2) rank, exact
  distances by Gray-code coset enumeration up to 2^22 (randomized upper bound above,
  always labeled). Ground truths: [[4,2,2]], Steane [[7,1,3]], Shor [[9,1,3]],
  repetition [[n,1]] (dx=n, dz=1), plus a non-commuting negative control. CI-run.
- `hgp.py` — correct-by-construction hypergraph products + classical seed verifier.
  Ground truth: HGP(rep3, rep3) = [[13,1,3]] (the distance-3 surface code). CI-run.
- `fom.py` — biased-noise Monte-Carlo FOM (BP-OSD both sides) + the calibration
  experiment. `python3 fom.py`
- `search_demo.py` — the closed loop (decide→make→verify→measure→learn) at micro
  scale, baselines in-arena. `python3 search_demo.py`
- `arena.py` — matched-budget family sweep vs bias. `python3 arena.py 10 30 100 300 1000`
- `llm_seeds.py` — the structured-proposal layer: LLM-composed classical seeds,
  refereed by the classical verifier, hypergraph-multiplied into band-2.
  `python3 llm_seeds.py`
- `resolver.py` — band-2 leaders under harder noise (p=0.02, 60k shots); produces
  the R4 table verbatim. `python3 resolver.py`

## Day-1 results (canonical stack)

### R1 — Calibration: the harness reproduces the bias-tailoring crossover
n=15 budget, p=0.01, 20k shots. Logical error per round:

| η | phase-rep-15 (dz=15,dx=1) | shor 3×5 (dx=3,dz=5) | shor 5×3 (dx=5,dz=3) |
|---|---|---|---|
| 10 | 0.01290 | **0.00120** | 0.00575 |
| 30 | 0.00465 | **0.00120** | 0.00655 |
| 100 | **0.00095** | 0.00120 | 0.00695 |
| 300 | **0.00040** | 0.00120 | 0.00695 |
| 1000 | **0.00005** | 0.00130 | 0.00695 |
| 3000 | **0.00000** | 0.00130 | 0.00705 |

Repetition rules at extreme bias; the mixed split wins >10× at moderate bias;
crossover between η=30 and η=100 at these parameters. Literature-shaped, quantified
by our own instrument. Over-investing in X (5×3) never wins — monotone sanity.

### R2 — The loop closes; random entry is barren; the kept negative
Micro-search at n=12, wmax≤6, η=30, p=0.01 (8 generations, 22-pop, elitism):
- **0 of 4,000 random sparse draws produced a valid code** — CSS commutation is a
  needle's eye; every arena entrant descended from a valid seed. Structured
  proposals are mandatory (independently corroborates the 2026 LLM-guided-search
  literature's premise).
- 134 verifier-gated candidates in 6 s, unattended.
- **Kept negative (on the mutation operator):** naive bit-flip evolution converged
  back to the hand design — the champion's matrices are shor 3×4 *verbatim* — and
  found nothing better in 134 candidates. The run's printed verdict is "SEARCH LOST"
  (champion 0.00237 at seed 2027 vs best baseline 0.00200 at seed 999), but the
  champion IS that best baseline: the gap is the same code re-scored under different
  seeds, within overlapping ±0.0006 CIs. Honest reading: rediscovery-grade, zero
  improvement — bit-flip mutation will not do it.
- The weight gate excluded shor 4×3 and 6×2 (weight-8/-12 checks): the hardware
  constraint prunes hand designs too.

### R3 — The bias map: optimal dx tracks η monotonically
Matched budget n≤23, wmax≤6, p=0.01, 10k shots (per-logical rates; CIs in-source):
best entrant per η — η=10: hgp r4r3 (dx=3) 0.00040 · η=30: hgp r4r3 (dx=3) 0.00040 ·
η=100: hgp r5r2 (dx=2) 0.00050 · η=300: hgp r5r2 (dx=2) 0.00020 · η=1000: rep-12
(dx=1) 0.00010. The dx ladder steps 3→2→1 as bias climbs. Weight-4 HGP rectangles
match or beat weight-6 Shor splits at similar footprint — hardware-relevant.

### R4 — Propose→referee→arena: the LLM-seed round and the Day-1 headline
Four classical seeds proposed by the author-LLM; the classical verifier refereed:
**accepted** punctHam6 [6,3,3] and ring6 [6,3,3]; **rejected** stitch6 [6,3,2] and
oct8 [8,4,2] (hypotheses wrong; printed, kept). Band-2 resolver (p=0.02, 60k shots,
per-logical rates ± 95% CI on P_any):

| code | n | k | q/logical | η=30 | η=100 | η=300 |
|---|---|---|---|---|---|---|
| rep-33 | 33 | 1 | 33 | 0.02063±0.00114 | 0.00683±0.00066 | 0.00227±0.00038 |
| shor 3×11 | 33 | 1 | 33 | 0.00043±0.00017 | 0.00087±0.00024 | 0.00063±0.00020 |
| hgp r6r4 | 39 | 1 | 39 | 0.00063±0.00020 | 0.00075±0.00022 | 0.00068±0.00021 |
| hgp r7r3 | 33 | 1 | 33 | 0.00015±0.00010 | 0.00022±0.00012 | 0.00007±0.00007 |
| hgp r4×pH6 | 33 | 3 | 11 | 0.00224±0.00065 | 0.00234±0.00067 | 0.00234±0.00067 |
| **hgp r5×pH6** | **42** | **3** | **14** | **0.00024±0.00022** | **0.00018±0.00019** | **0.00022±0.00020** |

**Headline (calibration-grade):** the rate-carrying [[42,3]] product built from a
referee-accepted seed delivers per-logical error statistically indistinguishable
from the best k=1 entrant (hgp r7r3) at η=30–100, with r7r3 edging it at η=300 at
marginal CI overlap — at **14 physical qubits per logical vs 33** (~2.4× qubit
efficiency at matched error), ~100× lower error than same-budget repetition, and
outright better than the shor 3×11 split. HGP rate advantages are qualitatively
expected — the specific measured datum under this bias/budget/weight regime is the
instrument's.

## Next (v1 — the seam)
Circuit-level finite-bias evaluator: noise model derived from published Ocelot
parameters (the derivation is itself a citable artifact), stim circuits for
cat+outer syndrome extraction, BP-OSD decoding on the circuit-level detector graph;
then the structured search (LLM proposals + referee + arena) under the realistic
model — the regime the published AI searches have not evaluated. Prior-art table to
CITE grade accompanies the first chapter prose.

## Day 2 (2026-07-07, continued session) -- v1 circuit-level evaluator: derived, formalized, calibrated

**What landed before this entry.** Commit 0a568b3: DERIV_noise_v1.md (Ocelot-
anchored noise-model derivation, author decisions D1-D4), evaluator_v1.py (stim
CSS-memory circuits for arbitrary outer codes, two ancilla modes, DEM -> BP-OSD or
matching), validate_v1.py (data-free battery), requirements-canonical.txt (the
canonical stack is now reconstructible from the repo; the Day-1 venv was not
persisted -- ledger E1). This commit adds fit_pm.py, refit_bitflip.py, this entry,
and the DERIV v1.1 addendum.

**Validation battery (canonical stack: py 3.12.13 / numpy 2.5.1 / ldpc 2.4.1 /
stim 1.16.0 / pymatching 2.4.0) -- ALL PASS:**
  V1 noiseless floor: rate = 0.0 (d=3,5; both bases)
  V2 analytic majority vote: measured 0.02212 vs analytic 0.02240 (4-sigma 0.00242)
  V3 decoder cross-check: bposd 0.0653 vs matching 0.0643
  V4 bit-flip sector: per-round 0.01984, corridor [0.01398, 0.03144]
  V5 distance scaling: eps(d5) 0.0124 < eps(d3) 0.0362

**Ocelot Zenodo dataset (DOI 10.5281/zenodo.14257632; 139 MB zip, kept outside the
repo).** Raw shot-level parquet, six sections ({first_d3, second_d3, d5} x
{bit_flip, phase_flip}); no pre-computed rates -- the published figures are decoded
results. Measured erasure fraction 6.6-7.9% per syndrome. Per-cat readout inferred
from XOR-compounded fit amplitudes A^(1/n): ~4.4-5.6%. Schema limit: readout
symmetrizations leave only the n-cat logical XOR well-defined (per-cat marginals
sit at 0.50), so per-cat bit-flip times are inference-only from this data.

**Amplitude-free bit-flip refit** (refit_bitflip.py, run against the dataset;
corr(C) = A*e^(-C/tau), the paper's convention; eps_bit = 1/(2*tau); key rows):
  d5:        nbar=1.0: T_Z 34.6us, eps_bit 4.05% | 1.5: 63.7us, 2.20% | 2.0: 95.1us, 1.47%
  first_d3:  nbar=1.0: T_Z 57.6us, eps_bit 2.43% | 1.5: 121.5us, 1.15% | 2.0: 201.9us, 0.69%
  second_d3: nbar=1.0: T_Z 64.6us, eps_bit 2.17% | 1.5: 124.8us, 1.12% | 2.0: 187.6us, 0.75%
  Scale factors k = 0.882 / 0.733 / 0.735 per nbar (x2.1-2.4 per photon),
  saturating above nbar ~ 3. Closure C1 PASS: eps_bit(d5,1) = 4.05% vs the paper's
  stated ~4%.

**Calibration fit (fit_pm.py; targets decoder-independent:
eps_phase = 2*eps_L_published - eps_bit_refit):**
  Inputs: target_d5 0.01101 (Gx15 1571/s); targets_d3 0.01231 / 0.01174
  (Gx10 2735/s). FITTED p_m = 0.0478 (D2 corridor PASS). Cross-check at the fitted
  point: bposd 0.01160 vs matching 0.01157 (0.3%). Out-of-sample d3: predicted
  0.01508 vs 0.01231 (+22.5%) and 0.01174 (+28.4%) -- both within +/-30%; the
  section spread is device variability, bounding honest model accuracy at ~+/-25%.

**Retired, kept for the record:** the first-look MWPM-decoded phase table (carry-
forward erasure handling) is labeled NOT calibration-grade -- a known-
overestimating upper bound (d5 at nbar=1.5 decoded 1.98% vs derived target 1.10%).
It never enters the calibration chain.

**Error ledger (credit where due):**
  E1 The strategy room asserted a persisted Day-1 venv; none existed. Caught by
     the executor; fixed structurally (requirements-canonical.txt).
  E2 The strategy room read the published eps_L as a bit+phase total; the paper
     defines the AVERAGE. Surfaced by the executor's data pull colliding with the
     published number; resolved by a primary-source definition fetch.
  E3 The executor's first bit-flip fit pinned the correlator amplitude, biasing
     tau ~2x low. Diagnosed by the strategy room from the paper's fit convention;
     refit by the executor; closure C1 then landed +1.3% from the paper's value.
  E4 The strategy room's C3 amplitude corridor used raw A; the observable is an
     n-cat XOR, so the corridor must be A^(1/n). Caught and corrected by the
     executor.

**Status.** Calibration protocol steps 1-3 complete. Step 4 (the Ruiz
comparability corridor) is OPEN-6 -- the remaining gate before any candidate code
is refereed. nbar unlocked as a search axis on [1, 3] with a hard saturation cap
(author decision D5). Analysis extras (pandas/pyarrow/scipy) live only in the
off-repo analysis environment; the canonical stack is unchanged.

## Day 2 (continued) -- OPEN-6: Ruiz comparability corridor

Calibration protocol step 4. Design: repetition-code (phase) memory under the
Guillaud-Mirrahimi dissipative-gate cat channel at Ruiz's operating point
(kappa_1/kappa_2 = 1e-4, nbar = 11, every op T = 1/kappa_2 [QUOTED, Ruiz]),
plus a second decade (1e-3) for robustness. CNOT channel [Guillaud & Mirrahimi,
PRX 9, 041053 (2019), Sec. VI]: p_Z(ctrl) = nbar*k1*T + 1/(2*pi*nbar*k2*T);
p_Z(tgt) = p_Z1Z2 = nbar*k1*T/2. Constants pending PDF byte-check (OPEN-7).
The measurement flip p_m is not verified from primary source, so it is SWEPT over
a decade (2e-3 to 2e-2) and the verdict must hold across the sweep -- robustness,
not tuning. Target curve computed IN CODE from the quoted form
eps_zL = 0.07*(486*k1/k2)^(0.94*floor((d+1)/2)) [QUOTED, Ruiz Fig. 3 caption].

Corridor grade: same-order agreement (factor ~3). Honesty note: a pass validates
the circuit machinery and channel implementation against an independent group's
published simulation fit -- the GM channel is the intellectual ancestor of Ruiz's
own master-equation model, so this is a consistency check between kin models, not
independent physics.

Ledger E5: a fetch-summarizer evaluation of the Ruiz fit formula was
arithmetically wrong (exponent 0.94 instead of 0.94*floor((d+1)/2) = 1.88 at
d=3, giving 4.4e-3 instead of the correct 2.38e-4). Caught in the strategy room
by computing the target from the quoted formula in code rather than adopting the
summarizer's derived numbers. Protocol vindicated: quote formulas, compute
locally, never trust tool-derived arithmetic.

Output of expedition/gm_corridor.py (canonical stack, verbatim):
```
k1/k2=1e-04: p_idle=1.10e-03 p_cx_ctrl=1.56e-02 p_cx_tgt=5.50e-04 p_zz=5.50e-04
  d=3: Ruiz fit target = 2.377e-04  (rounds=6, shots=200000)
    p_m=2e-03: eps_zL/cycle = 2.052e-04 (fails=246)  ratio to fit =  0.86
    p_m=6e-03: eps_zL/cycle = 2.244e-04 (fails=269)  ratio to fit =  0.94
    p_m=2e-02: eps_zL/cycle = 2.244e-04 (fails=269)  ratio to fit =  0.94
  d=5: Ruiz fit target = 1.385e-05  (rounds=10, shots=2000000)
    p_m=2e-03: eps_zL/cycle = 9.851e-06 (fails=197)  ratio to fit =  0.71
    p_m=6e-03: eps_zL/cycle = 1.110e-05 (fails=222)  ratio to fit =  0.80
    p_m=2e-02: eps_zL/cycle = 1.305e-05 (fails=261)  ratio to fit =  0.94
k1/k2=1e-03: p_idle=1.10e-02 p_cx_ctrl=2.55e-02 p_cx_tgt=5.50e-03 p_zz=5.50e-03
  d=3: Ruiz fit target = 1.803e-02  (rounds=6, shots=200000)
    p_m=2e-03: eps_zL/cycle = 1.327e-02 (fails=14908)  ratio to fit =  0.74
    p_m=6e-03: eps_zL/cycle = 1.340e-02 (fails=15039)  ratio to fit =  0.74
    p_m=2e-02: eps_zL/cycle = 1.416e-02 (fails=15830)  ratio to fit =  0.79
  d=5: Ruiz fit target = 9.150e-03  (rounds=10, shots=200000)
    p_m=2e-03: eps_zL/cycle = 4.867e-03 (fails=9318)  ratio to fit =  0.53
    p_m=6e-03: eps_zL/cycle = 4.990e-03 (fails=9543)  ratio to fit =  0.55
    p_m=2e-02: eps_zL/cycle = 5.679e-03 (fails=10794)  ratio to fit =  0.62
```

All grid points inside the same-order corridor on the canonical stack -> OPEN-6 PASS.
Calibration protocol steps 1-4 complete; the evaluator is cleared to referee candidate codes.

## Day 2 (continued) -- Campaign 1 pre-registration (BEFORE any search run)

Priors and signposts for the first circuit-level search campaign are frozen in
expedition/PREREG_search1.md and committed before the search harness runs any
candidate -- the Ch3 pattern applied to the expedition itself: the bets provably
predate the findings. Author-judged priors: P1 (Day-1 [[42,3]] survives circuit
level) 35%; P2 (some code beats repetition >= 2x at matched budget, w <= 4) 55%;
P3 (LLM seed family reaches leaderboard top-3) 40%; P4 (stretch: <= 10 q/logical
at eps_L <= 1e-8, beating Ruiz CA overhead at lower weight) 20%. All resolve by
2026-07-31 against the campaign's own published outputs, hits and misses alike.

## Day 2 (continued) -- S1 instruments land; pre-run clarifications and catches

Three records, all made BEFORE the canonical S1 run below.

**P1 resolution clarification.** The frozen P1 criterion says "same mode and
operating point" without naming the point. Clarified per the PREREG's own S1
design (GM mode primary): P1 resolves at the GM primary point (kappa_1/kappa_2
= 1e-4, nbar = 11); the Ocelot-point result publishes alongside as context, not
as P1's verdict. Transparency: a strategy-room sandbox dry-run of the harness
preceded this clarification and suggested the GM point is HARSH for the Day-1
headline (effective bias there is ~1e7; the [[42,3]] is a moderate-bias code
found at eta = 30-100). The clarification therefore leans AGAINST our own 35%
prior -- the anti-self-serving direction.

**Ledger E6.** evaluator_v1.css_memory_circuit tracks only logical observable
#0; for k > 1 codes this understates P_any. Caught by the strategy room in the
S1 smoke test BEFORE any canonical or campaign run; handled by an
observable-completion wrapper inside s1_referee.py (the committed evaluator is
untouched -- the campaign instrument includes the wrapper from the start, so no
mid-campaign instrument change).

**Sandbox preview, to be confirmed or refuted by the canonical output below:**
under GM gates, full-CSS extraction appears heavily penalized -- Z-check
extraction places the control-side non-adiabatic term directly on data qubits
while guarding a ~1e-9 bit floor. If canonical S1 confirms, S2's search space
should include X-only extraction architectures (classical-seeded, Ruiz-like) as
first-class candidates.

Output of expedition/s1_referee.py (canonical stack, verbatim):
```
S0 -- noiseless floor gate
  hgp_r5xpH6_[[42,3]] xonly: p_any=0.0  PASS
  hgp_r5xpH6_[[42,3]] full: p_any=0.0  PASS
  hgp_r7r3_[[33,1]] xonly: p_any=0.0  PASS
  hgp_r7r3_[[33,1]] full: p_any=0.0  PASS

S1 GM LEG (PRIMARY) -- k1/k2=0.0001, nbar=11.0, p_m=0.006 (mid-corridor assumption), rounds=8, shots=50000, BP-OSD
  hgp_r5xpH6_[[42,3]]     xonly  q/log= 22.0 slots= 8 eps_perlog/cycle=2.921e-04 (fails=349) [10s]
  hgp_r5xpH6_[[42,3]]     full   q/log= 27.0 slots=13 eps_perlog/cycle=1.587e-02 (fails=15189) [33s]
  hgp_r7r3_[[33,1]]       xonly  q/log= 51.0 slots= 6 eps_perlog/cycle=2.000e-05 (fails=8) [4s]
  hgp_r7r3_[[33,1]]       full   q/log= 65.0 slots=10 eps_perlog/cycle=1.100e-02 (fails=4077) [17s]
  rep-5 spot-check: MC=1.190e-05 vs FIT=1.385e-05 ratio=0.86 (corridor-validated instrument)
  rep-9  q/log= 17.0  eps_perlog/cycle=4.702e-08 [FIT -- corridor-validated at d=3,5; instrument reads ~1.2-2x optimistic]
  rep-11 q/log= 21.0  eps_perlog/cycle=2.740e-09 [FIT -- corridor-validated at d=3,5; instrument reads ~1.2-2x optimistic]
  rep-13 q/log= 25.0  eps_perlog/cycle=1.596e-10 [FIT -- corridor-validated at d=3,5; instrument reads ~1.2-2x optimistic]
  P1 DATA: [[42,3]] xonly (22 q/log) = 2.921e-04 vs matched-budget k=1 comparator rep-11 (21 q/log, FIT) = 2.740e-09 -> ratio = 1.1e+05

S1 OCELOT LEG (calibrated reality check) -- transmon mode, p_m=0.0478 (FITTED), rounds=6, shots=20000, total = phase + bit per logical
  operating point nbar=1.5: Gamma_Z=2.5e+04/s Gamma_X=1571/s
    hgp_r5xpH6_[[42,3]]      q/log= 27.0 phase=4.825e-02 bit=2.598e-03 TOTAL=5.085e-02
    hgp_r7r3_[[33,1]]        q/log= 65.0 phase=5.026e-02 bit=3.364e-03 TOTAL=5.362e-02
    rep-9                    q/log= 17.0 phase=2.046e-03 bit=3.718e-02 TOTAL=3.923e-02
    rep-11                   q/log= 21.0 phase=1.013e-03 bit=4.617e-02 TOTAL=4.718e-02
    rep-13                   q/log= 25.0 phase=5.013e-04 bit=5.424e-02 TOTAL=5.474e-02
  operating point nbar=2.0: Gamma_Z=3.33e+04/s Gamma_X=1051/s
    hgp_r5xpH6_[[42,3]]      q/log= 27.0 phase=8.953e-02 bit=1.159e-03 TOTAL=9.069e-02
    hgp_r7r3_[[33,1]]        q/log= 65.0 phase=9.302e-02 bit=1.478e-03 TOTAL=9.450e-02
    rep-9                    q/log= 17.0 phase=4.832e-03 bit=2.635e-02 TOTAL=3.119e-02
    rep-11                   q/log= 21.0 phase=2.960e-03 bit=3.109e-02 TOTAL=3.405e-02
    rep-13                   q/log= 25.0 phase=1.562e-03 bit=3.665e-02 TOTAL=3.822e-02

S1 complete. P1 adjudication happens in the strategy room against PREREG_search1.md; hits and misses both publish.
```

## Day 2 (continued) -- P1 resolved: FALSE (published miss)

P1 (prior 35%, frozen at commit 3255fb9) resolves FALSE against its criterion:
at the S1 primary point the Day-1 [[42,3]] headline sits ~1.1e5 above the
matched-budget repetition comparator -- not within 2x. Full resolution text in
PREREG_search1.md's resolution log; canonical numbers in the S1 entry above.

Forecaster calibration, on the record: the 35% prior overweighted the
code-capacity signal and underweighted the operating-point mismatch (the
headline was found at eta = 30-100; the primary point is effectively eta ~
1e7). The information was available at prereg time in Day-1's own R3 bias map;
the forecast failed to propagate it. Noted for the next round of priors.

What the miss bought: the expensive referee's first two durable findings --
X-only extraction is the only sane mode at high bias (full-CSS pays ~54x for
guarding a ~1e-9 bit floor), and the Day-1 headline now carries its honest
circuit-level label (moderate-bias, code-capacity grade; not a high-bias
architecture candidate). S2 proceeds with X-only extraction first-class and
classical-LDPC-seeded candidates in the arena, per the pre-run note. The
dossier's loop thesis worked as designed: cheap model proposes, expensive
model disposes, and pre-registration makes the disposal creditable.

## Day 2 (continued) -- S2 arena: pre-run decisions, seed provenance, and a referee kill

Records made BEFORE the canonical S2 run below.

**D6 (author decision): STRICT budget comparator.** P2's frozen "equal qubit
budget" is resolved as: comparator = the smallest odd-d repetition code with
2d-1 >= the candidate's q/log -- repetition granted at least the candidate's
budget. Anti-self-serving, consistent with the P1-clarification precedent.
**D7 (author decision): deep-shot budget 2e6** per product-code candidate;
zero-fail outcomes publish as rule-of-three 95% upper bounds, not as numbers.

**Seed provenance (P3 bookkeeping).** LLM-layer proposals this session: H1
(double-circulant [I|C3]), H1b (extended Hamming [8,4,4] w=4 basis), H1c
(product codes rep-a (x) [8,4,4], d = 4a at w <= 4). Controls: H2 (Hamming
family, literature), H4 (repetition). A top-3 leaderboard entry from
H1/H1b/H1c resolves P3 TRUE.

**Referee kill, recorded with credit to the mechanical verifier:** the
proposer's first family H1 has a structural distance ceiling the proposer
missed -- for H = [I | C], any unit-weight message y yields the codeword
(Cy | y) of weight 1 + colweight(C) = 4, so d <= 4 for ALL m and ALL weight-3
taps. The tap search confirmed: d = 4 across m = 6..16. H1 is dead on arrival;
H1b/H1c are the repair, proposed AFTER the kill. The Day-1 pattern
(LLM-proposes / verifier-referees) working against the proposer, as designed.

**Sandbox pilot preview (canonical numbers below decide):** every low-budget
high-rate seed (q/log ~ 3, d = 3-4) LOSES to rep-3 by 3-4x at the GM point --
w=4 syndrome noise (~6e-2/check) drowns small distances, confirming hypothesis
H2's prediction against itself. The product-code family returned zero pilot
fails and is the live P2 candidate; the deep leg below resolves it.

Output of expedition/s2_arena.py (canonical stack, verbatim):
```
S2 ARENA -- GM primary point, xonly extraction, D6 strict comparator, D7 2e6 deep shots
seed                    [n,k,d]       w deg colors  q/log
H1_dc_m8_t0-1-2         [16,8,4]     4   3      5    3.0
H1_dc_m12_t0-1-2        [24,12,4]     4   3      5    3.0
H1b_extHam8             [8,4,4]     4   3      6    3.0
H1c_rep3xextHam8        [24,4,12]     4   5      8   13.0
H1c_rep5xextHam8        [40,4,20]     4   5      8   23.0
H2_hamming74            [7,4,3]     4   3      4    2.5
H2_shortHam6            [6,3,3]     3   2      4    3.0
H4_rep5                 [5,1,5]     2   2      2    9.0
H4_rep9                 [9,1,9]     2   2      2   17.0
H4_rep11                [11,1,11]     2   2      2   21.0
H4_rep13                [13,1,13]     2   2      2   25.0

Provenance for P3: LLM-layer = H1 (refereed DEAD: structural ceiling d <= 1 + colw(C) = 4), H1b, H1c. Controls = H2 (literature), H4 (repetition).

LEG B -- pilot (20k shots, rounds=8)
  H1_dc_m8_t0-1-2         [16,8,4] q/log=  3.0 eps=6.497e-04 vs rep-3 FIT=2.377e-04 ratio=2.73e+00 (fails=813, 1s)
  H1_dc_m12_t0-1-2        [24,12,4] q/log=  3.0 eps=6.842e-04 vs rep-3 FIT=2.377e-04 ratio=2.88e+00 (fails=1269, 2s)
  H1b_extHam8             [8,4,4] q/log=  3.0 eps=1.018e-03 vs rep-3 FIT=2.377e-04 ratio=4.28e+00 (fails=639, 0s)
  H1c_rep3xextHam8        [24,4,12] q/log= 13.0 eps=1.563e-06 vs rep-7 FIT=8.070e-07 ratio=1.94e+00 (fails=1, 4s)
  H1c_rep5xextHam8        [40,4,20] q/log= 23.0 eps=0.000e+00 vs rep-13 FIT=1.596e-10 ratio=0.00e+00 (fails=0, 9s)
  H2_hamming74            [7,4,3] q/log=  2.5 eps=1.060e-03 vs rep-3 FIT=2.377e-04 ratio=4.46e+00 (fails=665, 0s)
  H2_shortHam6            [6,3,3] q/log=  3.0 eps=9.145e-04 vs rep-3 FIT=2.377e-04 ratio=3.85e+00 (fails=433, 0s)
  H4_rep5                 [5,1,5] q/log=  9.0 eps=1.250e-05 vs rep-5 FIT=1.385e-05 ratio=9.03e-01 (fails=2, 0s)
  H4_rep9                 [9,1,9] q/log= 17.0 eps=0.000e+00 vs rep-9 FIT=4.702e-08 ratio=0.00e+00 (fails=0, 0s)
  H4_rep11                [11,1,11] q/log= 21.0 eps=0.000e+00 vs rep-11 FIT=2.740e-09 ratio=0.00e+00 (fails=0, 0s)
  H4_rep13                [13,1,13] q/log= 25.0 eps=0.000e+00 vs rep-13 FIT=1.596e-10 ratio=0.00e+00 (fails=0, 1s)

LEG C -- deep shots (2e6) on the product-code family
  H1c_rep3xextHam8         eps=1.250e-07 (fails=8) vs rep-7 FIT=8.070e-07 ratio=1.55e-01 [326s]
  P2 DATA: H1c_rep3xextHam8 ratio-to-strict-comparator = 1.55e-01 (P2 bar: <= 0.5; PREREG adversarial re-check bar: < 0.1)
  H1c_rep5xextHam8         0 fails/2e6 -> eps <= 4.688e-08 (95% UB) vs rep-13 FIT=1.596e-10 -> ratio <= 2.94e+02 [870s]
  P2 DATA: H1c_rep5xextHam8 ratio-to-strict-comparator <= 2.94e+02 (P2 bar: <= 0.5; PREREG adversarial re-check bar: < 0.1)

S2 arena complete. P2/P3 adjudication happens in the strategy room against PREREG_search1.md; hits and misses both publish.
```

## Day 2 (continued) -- P2 adversarial re-check: pre-run records

**Why this runs at all:** P2's frozen criterion reads "...surviving adversarial
re-check" -- that clause binds P2's own resolution, not just the >10x STOP
trigger (which correctly did not fire at ratio 0.155). No resolution before
the re-check.

**Instrument-tilt argument, recorded BEFORE seeing leg R5:** the arena compared
the candidate on OUR instrument (disclosed ~1.2-2x optimistic) against the
comparator's Ruiz FIT value -- an asymmetry that inflates the candidate's
advantage by up to ~2x. Worst-case correction: 0.155 -> ~0.31, still under the
0.5 bar. R5 removes the asymmetry entirely by measuring rep-7 on the same
harness (pymatching, 2e7 shots); the same-instrument ratio is the primary
number for adjudication.

**Ledger E7 (minor, credited to the executor):** the S2 pre-run intro's
"returned zero pilot fails" was true of the strategy-room sandbox pilot but
read as a family property; the canonical pilot showed 1 fail / 20k for
rep3xextHam8 -- within cross-build MC variation per the published policy, and
the verbatim canonical table sits directly beneath the preview, so the record
self-corrects. Surfaced by the executor at the S2 gate. No label violated;
noted for preview-sentence discipline.

Output of expedition/s2_recheck.py (canonical stack, verbatim):
```
RE-CHECK target: rep3 (x) extHam8 = [24,4,12] w=4 q/log=13.0  (mechanical floor re-verified)
strict comparator rep-7: FIT=8.070e-07 (corridor-validated, instrument tilt disclosed); same-instrument R5 below is primary.

R1 fresh-seed:      eps=1.406e-07 (fails=9/2e6) ratio-to-FIT=0.174  [322s]
R2 alt-decoder:     eps=3.125e-08 (fails=2/2e6) ratio-to-FIT=0.039  [408s]
R3 depth (16 rnds): eps=2.188e-07 (fails=14/1e6) ratio-to-FIT=0.271  [2380s]
R5 rep-7 same-instrument: eps=4.563e-07 (fails=73/2e7) vs FIT 8.070e-07 (MC/FIT=0.57)  [12s]
R4 Ocelot context:  eps_phase=8.709e-04 (context only)

VERDICT R1: ratio-to-FIT=0.174 [PASS] | ratio-same-instrument=0.308 [PASS] (bar 0.5)
VERDICT R2: ratio-to-FIT=0.039 [PASS] | ratio-same-instrument=0.068 [PASS] (bar 0.5)
VERDICT R3: ratio-to-FIT=0.271 [PASS] | ratio-same-instrument=0.479 [PASS] (bar 0.5)

Re-check complete. P2 adjudication happens in the strategy room; hits and misses both publish.
```

## Day 2 (continued) -- matched-depth leg: E8 recorded, prediction frozen

**Ledger E8 (design gap in the re-check, recorded before this run):** the
re-check's R3 leg compared the 16-round candidate against the 8-round rep-7
comparator. Finite-depth memory experiments are flattered by their
deterministic boundaries -- short runs read LOW per-round for BOTH codes -- so
R3's cross-depth ratio (0.479) is biased AGAINST the candidate; the candidate's
own 8->16 round drift (x1.55) is the steady-state correction surfacing. The
arena's 8-round comparison was depth-matched and fair. Surfaced by the
executor's marginality flag at the re-check gate; diagnosed in the strategy
room; closed by this leg (both codes at 16 rounds, same instrument, same
fresh seed).

**Falsifiable prediction, frozen before the run:** rep-7's own boundary
correction will restore the matched-depth ratio to ~0.3, comfortably under
P2's 0.5 bar. If instead the ratio stays at or above the bar at matched depth,
the candidate's advantage does not survive steady state and P2 does not
resolve TRUE on it.

Output of expedition/s2_depth.py (canonical stack, verbatim):
```
MATCHED-DEPTH LEG (E8 closure): both codes at 16 rounds, same instrument, seed 291
candidate [24,4,12] 16r: eps=1.719e-07 (fails=44/4e6) [2044s]
rep-7  8r: eps=5.500e-07 (fails=88/2e7) [12s]   16r: eps=6.750e-07 (fails=216/2e7) [25s]
boundary-effect factor on comparator: rep-7 16r/8r = 1.23 (candidate's own was ~1.55 across the same depths)

MATCHED-DEPTH RATIO (candidate/rep-7, both 16r, same instrument): 0.255  95% CI [0.172, 0.337]  vs bar 0.5 -> PASS
Context: arena depth-matched (8r) ratio was 0.155-to-FIT / ~0.31 same-instrument; prediction recorded pre-run: ~0.3.

Matched-depth leg complete. P2 adjudication happens in the strategy room; hits and misses both publish.
```

## Day 2 (continued) -- P2 resolved: TRUE (the campaign's first hit)

P2 (prior 55%, frozen at 3255fb9) resolves TRUE: full criterion walk-through in
PREREG_search1.md's resolution log. The one-line version: rep3(x)extHam8
[24,4,12] (w<=4, 13 q/logical, LLM-layer seed) beats strict budget-matched
repetition by ~4x per logical at the GM primary point -- depth-matched,
same-instrument, CI clear of the bar, adversarial re-check survived with its
one marginal leg diagnosed (E8) and closed rather than waved through. Scope
label carried in-sentence: a model-level result under the v1 GM-gate channel,
not a hardware demonstration.

Forecaster calibration: 55% was about right, and for the right reasons -- the
Ruiz CA result was a strong existence proof, the untested w<=4 cap was the real
risk, and it nearly bit (the naive small-seed families all lost; only the
product construction cleared it). Contrast with P1's miscalibration, where
available evidence went unpropagated.

The result's pedigree, for the chapter prose: proposer's first family killed
by the mechanical verifier (structural d <= 4 ceiling); repair proposed under
the same w-cap; survived pilot, deep shots, fresh-seed and alt-decoder
re-checks; its one apparent weakness (depth trend) traced to an instrument
artifact that was named, predicted, and closed by measurement. The loop thesis
in one arc: propose, referee, repair, verify, adversarially attack, publish.
