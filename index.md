An Open Dossier · **QC-Accelerate-002**

# Accelerating Quantum Computing Research Using AI and Robotics

*Irfan Ali-Khan — Independent Researcher*

**Chapter 1 — The story so far.** *This dossier continues a program begun in a sibling lineage. This opening chapter is a recap of that prior, DOI'd work — every result here is cited to it, not claimed as new. New results begin in Chapter 2.*

## 01 AI IS ALREADY A CO-AUTHOR

**AI is already a co-author of quantum-computing research.** Walk up the stack and it is on every floor: it reads the error syndromes (neural decoders), it choreographs the gates (learned control pulses), and it has even drawn new error-correcting codes humans had not picked. The prior work sorted this into three distinct things AI does — *re-deriving* what humans designed, *discovering* what they did not, and a third, quieter one: *scoping* — using a search to map a hardware frontier rigorously and certify where human design is already optimal.

## 02 THE FLOOR: A QUBIT THAT PROTECTS ITSELF

**The floor: a qubit that protects itself.** The program's foundation (Chapter 1 of the prior lineage, [prior Ch.1 · DOI]) is the cat qubit (A qubit whose information is stored in two coherent states of an oscillator whose separation grows with the cat's size. As the cat grows, bit-flip errors are crushed exponentially while phase-flips rise only linearly. That exponentially growing noise bias is the whole point: it turns the qubit into a self-protecting memory.): information stored in two coherent states whose separation grows with the cat's size. As the cat grows, bit-flip errors are crushed *exponentially* while phase-flips rise only gently — an exponentially growing noise bias that turns the qubit into a self-protecting memory ([Mirrahimi et al. 2014]). That asymmetry is the whole point. Drag the cat size in Fig 1 and watch the two lobes pull apart — their shrinking overlap IS the bit-flip rate.

*(figure: Linked phase-space and rate view of the cat qubit: two coherent-state lobes separate as the cat grows, their overlap e^(-2n-bar) equals the bit-flip rate on the right chart — Fig 1 — Left: schematic phase space — the two coherent-state lobes |±α⟩ of the cat qubit; as the cat grows they separate and their overlap e^(−2n̄) is exactly the bit-flip amplitude. Right: the resulting rates — bit-flip crushed exponentially, phase-flip (dephasing, ~ n̄) the linear price of a bigger cat. Schematic lobes, not a computed Wigner function; rates normalized for legibility. Recap of the prior lineage’s Chapter 1 (Mirrahimi et al. 2014; DOI 10.5281/zenodo.20838233). [CITE · established])*

## 03 THE WALL: OPERATING WITHOUT BREAKING THE PROTECTION

**The wall: operating on it without breaking the protection.** Storing a protected qubit is one thing; running a *gate* on it without waking its errors is another. A bias-preserving gate (A logic gate run on a cat qubit that must stay slow enough to preserve the qubit's protection. But slowness lets ordinary photon loss accumulate, so the gate lives or dies on one ratio — the engineered protection versus the unavoidable loss (κ₁/κ₂).) must run slowly enough to stay protected, but slowness lets ordinary photon loss accumulate — a brutal requirement on one ratio, the engineered protection versus the unavoidable loss (κ₁/κ₂). The prior chapter handed an AI search *more* freedom than any human gate and seeded it with the best human design, asking whether it could tolerate a worse ratio.

## 04 THE KEPT NEGATIVE

**The result was a clean "no" — kept, not hidden.** The search landed on the hand-designed baseline and could not push past it; handed a tempting bias-breaking shortcut, it drove that knob to *zero* on its own, because the scorecard made cheating worthless. Toggle the control scheme in Fig 2 and watch the search sit on the baseline rather than beat it. Values are from the prior lineage's current working edition, [working edition].

*(figure: AI-search gain versus cat size: the search lands on the hand-designed baseline (gain about 1) and the bias-breaking knob is driven to zero; a single-quadrature pulse falls below baseline — Fig 2 — The kept negative: the AI search lands on the hand-designed baseline (gain ≈ 1) and drives the bias-breaking knob ε_y to zero; the single-quadrature pulse falls below baseline (margin −0.29). Values from the prior lineage’s current working edition (github.com/m4gr4th34/dossier-QC-Accelerate) — sparse (three cat sizes, as published), a working-draft result, not DOI-archived. [CITE · reported])*

An honestly-obtained negative is a map: it marks which doors are shut and points to the open ground.

## 05 WHY THIS IS THE RIGHT OPENING

**Why this is the right opening for what follows.** That kept negative is this program's thesis in miniature — AI is powerful at search *within* a paradigm and declines to fake what it cannot reach. Chapter 2 widens the lens to the whole landscape (decoders, calibration, code-search, autonomous labs) and asks where AI genuinely shortens the road to fault-tolerant quantum computing, and where the conceptual gates remain. That is where the new results begin.

## Avenues

| Avenue | Thesis | Status | Forecast | Sources |
|---|---|---|---|---|
| PLACEHOLDER avenue A | One-line thesis — what this avenue is and why it's in play. | ESTABLISHED | — | REF1, REF2 |
| PLACEHOLDER avenue B | One-line thesis for an avenue with a central open question. | OPEN-UNVERIFIED | — | REF3 |
| PLACEHOLDER avenue C | One-line thesis for an avenue you're making a forward bet on. | FORECAST | ~35% by 2030 | REF4 |
| PLACEHOLDER avenue D | One-line thesis sourced only to an interested party / roadmap. | REPORTED | — | REF5 |

## Consistency checks

Results from `verification/verify_numbers.py` — the same checks the in-page console runs; CI reruns them on every commit.

- [PASS] Consistency: at least one avenue in the landscape
- [PASS] Consistency: every FORECAST has a dated signpost
- [PASS] Consistency: all forecast probabilities lie in [0,100]

**TOTAL: 3 checks · 3 pass · 0 fail** — All checks pass — the survey is internally consistent.

## References

- **prior Ch.1 · DOI** — Prior lineage — Chapter 1 (Ali-Khan). Recap of the established cat-qubit self-protection: bit-flip suppressed exponentially with cat size, phase-flip only linearly (the Mirrahimi 2014 scaling) *DOI 10.5281/zenodo.20838233*

- **Mirrahimi et al. 2014** — Mirrahimi, Leghtas, Albert, Touzard, Schoelkopf, Jiang & Devoret (2014). Introduced the cat-qubit paradigm: encode a qubit in two opposite-phase coherent states |+/-alpha> of a microwave oscillator, held there by engineered two-photon driven dissipation. That dissipation pins the state into the two-lobe cat manifold, giving the exponential bit-flip protection the whole approach rests on. *New J. Phys. 16, 045014 (2014) - DOI 10.1088/1367-2630/16/4/045014*

- **working edition** — Prior lineage — current working edition (Ali-Khan). AI bias-preserving-gate search lands on the hand-designed baseline (gain ≈ 1); the bias-breaking knob ε_y is driven to 0; a single-quadrature shaped pulse falls below baseline (margin −0.29) *Working draft, OpenTimestamped - github.com/m4gr4th34/dossier-QC-Accelerate @ 080b2ca (not DOI-archived)*
