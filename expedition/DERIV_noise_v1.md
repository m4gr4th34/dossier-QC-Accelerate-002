# DERIV -- v1 circuit-level finite-bias noise model (Ocelot-anchored)

**Chapter 4 expedition, item 1 of the dependency chain.** This is the citable DERIV
artifact for the v1 evaluator's noise model: every parameter carries a provenance
grade, and the model is anchored to *measured, published* device numbers rather than
recalled theory formulas. Prepared in the strategy room 2026-07-07; author decisions
D1-D4 recorded below; formalized by the executor with the reproduction gate.

ASCII notation throughout (mojibake defense): kappa_1, kappa_2, Gamma_Z, Gamma_X,
nbar = |alpha|^2, eps_L, T_phi, us = microseconds.

## Provenance grades

- **QUOTED** -- verbatim from the primary source (arXiv:2409.13025v2 HTML, fetched
  2026-07-07). Byte-verification against the published PDF is OPEN-3 (executor job).
- **DERIVED** -- computed from QUOTED numbers by a stated formula, with an
  independent consistency check against a *different* QUOTED number.
- **FITTED** -- free parameter fit to a QUOTED calibration target; labeled as such
  wherever it appears, never asserted as measured.
- **OPEN** -- needed later, not published in the fetched text; resolution path named.

## Primary sources

1. **Ocelot** -- H. Putterman et al., "Hardware-efficient quantum error correction
   via concatenated bosonic qubits," Nature 638, 927-934 (2025). DOI
   10.1038/s41586-025-08642-7; arXiv:2409.13025; data DOI 10.5281/zenodo.14257632.
   Role: *the measurement anchor* -- all v1 channel magnitudes trace here.
2. **Ruiz et al.** -- "LDPC-cat codes for low-overhead quantum computing in 2D,"
   Nat. Commun. 16, 1040 (2025). DOI 10.1038/s41467-025-56298-8. Role: *the
   comparability anchor* -- their published fit formulas give the corridor our
   evaluator must land near when run at their operating point (kappa_1/kappa_2 =
   1e-4, nbar = 11).

## QUOTED anchor set (Ocelot, verbatim)

| # | Quantity | Verbatim quote | Value used |
|---|----------|----------------|------------|
| Q1 | Storage T1 | "The storage modes have an average T1 (T2) time of over 60 us (80 us)." | T1 >= 60 us (floor) |
| Q2 | Phase-flip time, nbar=2 | "at \|alpha\|^2=2, we achieve greater than 1 ms bit-flip times and 27-33 us phase-flip times. This constitutes a sizable (> 30) noise bias" | T_phi = 27-33 us |
| Q3 | Bit-flip time, nbar=2 | same sentence as Q2 | T_bf >= 1 ms (floor) |
| Q4 | Cycle time | "Each syndrome measurement cycle has a conservatively chosen duration of 2.8 us" | 2.8 us |
| Q5 | CX gate length | "CX gate lengths across the device ranging from 292-552 ns" | 500 ns nominal |
| Q6 | CX^2 cycle errors, nbar=2 | "the bit-flip and phase-flip errors per cycle are respectively (3.5 +/- 0.4) x 10^-3 and (9.6 +/- 0.4) x 10^-2" | as stated |
| Q7 | d=5 logical error | "The best measured performance for the distance-5 section is eps_L = 1.65% +/- 0.03% at \|alpha\|^2 = 1.5." | calibration target |
| Q8 | d=3 logical error | "eps_L = 1.83% +/- 0.03% and eps_L = 1.67% +/- 0.04%" (two d=3 sections, minimized near \|alpha\|^2 = 1) | out-of-sample checks |
| Q9 | Bit-flip scaling | "The bit-flip times of our cat qubits increase exponentially with the mean photon number \|alpha\|^2"; also "phase-flip times degrade as 1/\|alpha\|^2 as expected" | qualitative (see OPEN-2); the 1/nbar phase law licenses Gamma_Z extrapolation across nbar |

## The derivation

The standard cat-qubit dephasing model says the phase-flip rate of a stabilized cat
is **Gamma_Z = nbar * kappa_1**. v1 does not assume this -- it *tests* it against
three independently measured Ocelot numbers, and only then adopts it:

**Step 1 (kappa_1 from Q1).** kappa_1 = 1/T1_storage = 1/(60 us) = 1.667e4 /s.

**Step 2 (predict T_phi, check vs Q2).** Gamma_Z(nbar=2) = 2*kappa_1 -> T_phi =
30.0 us. Measured window: 27-33 us. **PASS** -- dead center.

**Step 3 (predict per-cycle phase flip, check vs Q6).** Idling-dominated dephasing
over one 2.8 us cycle: p_Z = 1 - exp(-Gamma_Z * 2.8 us) = 0.0891. Measured: 0.096
+/- 0.004 (2-sigma window 0.088-0.104). **PASS** -- the CX^2-cycle phase-flip number
is explained by idle dephasing alone; CX gates add no large excess dephasing at this
anchor. (The residual, ~0.007/cycle, is an upper bound on total CX-excess dephasing
per cycle -- carried as stated model headroom, not a fitted term.)

**Step 4 (bit-flip rate during active cycles, from Q6).** Gamma_X_active =
3.5e-3 / 2.8 us = 1250 /s (effective T_bf = 0.80 ms during CX activity, vs >= 1 ms
idle from Q3 -- CX activity costs <= 25% of the bit-flip budget). Idle floor:
Gamma_X_idle = 1000 /s (conservative: uses the "> 1 ms" bound as equality, which
*over*-states bit flips).

**Step 5 (bias closure, check vs Q2).** Derived active-cycle bias Gamma_Z/Gamma_X =
26.7; idle bias >= 33. Quoted: "> 30". **CONSISTENT.**

Three independently measured quantities (Q1, Q2, Q6-phase) close on a single rate
parameter Gamma_Z = nbar*kappa_1 with no fitting. That closure is the license to
use the model.

## Author decisions (2026-07-07)

- **D1 -- both ancilla modes from day one.** 'transmon' mode: ancilla physics folded
  into the fitted measurement flip p_m (faithful to how Ocelot's measured eps_L
  already includes its transmon+erasure ancilla; full erasure machinery NOT
  modeled -- stated simplification). 'cat' mode: ancilla is a cat qubit with the
  same derived biased rates during its CX window (hook errors propagate through the
  circuit), plus the same p_m readout flip (stated assumption A1: readout-flip
  magnitude carried over from the transmon fit; the mode difference is then purely
  the ancilla's in-circuit biased noise and its propagation).
- **D2 -- one FITTED parameter p_m**, fit to Q7, with Q8 held out as out-of-sample
  checks, and a plausibility corridor: if the fit demands p_m > ~10% or < ~0.5%,
  the model is missing physics -> STOP, adjudicate, never accept silently.
- **D3 -- nbar pinned at 2** (the characterization anchor) for all v1 runs; nbar as
  a search axis unlocks only when OPEN-2 resolves.
- **D4 -- correlated ZZ during CX deferred to v1.1**, pending verification of the
  analytic non-adiabatic formula against Guillaud & Mirrahimi, PRX 9, 041053 (2019)
  and/or Le Regent et al., Quantum 7, 1198 (2023). Verify-don't-recall: no formula
  ships unverified. (Step 3 bounds the omitted CX-excess dephasing at ~0.007/cycle
  at the anchor.)

## The v1 model (implemented in evaluator_v1.py)

Time-resolved circuit-level Pauli channel on the outer code's syndrome-extraction
schedule; all data qubits are cat qubits at nbar = 2:

- **Rates:** Gamma_Z = 3.333e4 /s; Gamma_X_active = 1250 /s; Gamma_X_idle = 1000 /s
  [all DERIVED]. Errors are time-driven: each CX applies Z/X error over t_cx = 500 ns
  on its participants; an end-of-round residual tops every data qubit up to exactly
  t_cycle = 2.8 us, so total per-round data dephasing is 1 - exp(-Gamma_Z*t_cycle)
  independent of gate count (licensed by Step 3).
- **Ancilla prep + measurement:** one parameter p_m per syndrome extraction
  [FITTED per D2; fit pending the calibration dataset, OPEN-5].
- **Search severity axis:** a dimensionless multiplier lambda scaling Gamma_Z
  (lambda = 1 <-> Ocelot today; lambda < 1 <-> better kappa_1/kappa_2), avoiding any
  unpublished kappa_2 value while giving the search a finite-bias severity knob.
- **Comparability leg:** repetition-code sweep at Ruiz's operating point vs their
  published repetition fit p_zl = 0.07*(486*kappa_1/kappa_2)^(0.94*floor((d+1)/2))
  [QUOTED, Nat. Commun. 16, 1040, Fig. 3 caption]. Corridor check, not bit-exact:
  their gate-level model differs in detail.

## Stated limitations

- **L1** -- correlated ZZ during CX omitted (see D4).
- **L2** -- nbar is not an optimization axis yet (see D3 / OPEN-2).
- **L3** -- transmon mode does not model erasure flagging explicitly; all ancilla
  physics is folded into fitted p_m (see D1). Ocelot reports erasure cut measurement
  error "by over a factor of two" at nbar = 1 -- a fidelity upgrade path, not a v1
  requirement.

## OPEN items and resolution paths

- **OPEN-1: kappa_2 / kappa_1-kappa_2 ratio for Ocelot.** Main text gives only
  g2/2pi = 300-450 kHz. Path: paper appendices / Zenodo dataset
  (10.5281/zenodo.14257632). Needed only to map lambda onto physical kappa_1/kappa_2
  claims -- not to run the search.
- **OPEN-2: bit-flip-time-vs-nbar scale factor.** Path: same appendix/dataset route.
  Unblocks L2/D3.
- **OPEN-3: byte-verification of Q1-Q9 against the published PDF.** Executor job at
  formalization, per the reproduction gate.
- **OPEN-4: exact protocol definition of the "CX^2 cycle"** (affects only the Step-4
  decomposition, not the total rates, which are used as measured). Path: paper
  Section III + appendices.
- **OPEN-5: the calibration dataset.** The fit targets Q7/Q8 sit at nbar = 1.5 and
  nbar = 1, where Gamma_X is not derivable until OPEN-2 resolves; the honest fit
  point is nbar = 2, whose measured eps_L (and its phase/bit split, paper Figs. 3f
  and 4b) lives in the Zenodo dataset. Path: pull the dataset, extract the measured
  logical rates vs nbar for d=3 and d=5, then fit p_m at nbar = 2 and use ALL other
  points as out-of-sample checks.

## Calibration protocol (the gate before any search runs)

1. Extract measured (eps_phase, eps_bit) vs nbar for d=3, d=5 from the Zenodo
   dataset (resolves OPEN-5, likely OPEN-1/OPEN-2 as well).
2. Fit p_m (transmon mode) to the d=5 point at nbar = 2; corridor per D2.
3. Out-of-sample: predict the d=3 sections at nbar = 2 with the fitted p_m -- must
   land within +/-30% relative; miss -> STOP, adjudicate.
4. Ruiz comparability corridor (same-order agreement).
5. Only after 1-4 pass does the evaluator referee any candidate outer code.

## Validation battery (data-free; validate_v1.py)

V1 noiseless floor -> exactly 0. V2 analytic single-round majority vote (4-sigma
gate). V3 BP-OSD vs minimum-weight-matching decoder cross-check. V4 unprotected
bit-flip sector magnitude corridor. V5 distance-scaling direction. All five PASS on
the strategy sandbox (py 3.12.3 / numpy 2.5.1 / stim 1.16.0 / ldpc 2.4.1 /
pymatching 2.4.0); canonical numbers are the executor's on the pinned venv.
New pinned dependencies vs Day-1 stack: stim==1.16.0 (already installed, first use),
pymatching==2.4.0 (new).
