# Chapter 4 -- The loop eats first

*Draft for author review -- strategy room, 2026-07-07. Every number below is
locked to the committed record (NOTEBOOK.md / PREREG_search1.md at cac735c) and
will enter verify_numbers.py at build time. Labels in-sentence per doctrine.
Cite cards inline in [square brackets]; full cards in the References section.*

---

## 01 THE DEGENERATE LOOP

The dossier's thesis is a loop: propose, fabricate, verify, learn. Chapters 1
through 3 asked who is building that loop for quantum hardware and found the
crown empty -- Hefei has the robots, the allies have the referee, nobody has
the loop. This chapter does something different. It runs the loop's degenerate
case -- the one with no fabrication step -- on ourselves. Quantum
error-correcting code space is a search problem where the "device" is a
simulator and the "measurement" is a decoder, which makes it the cheapest
possible place to test whether an AI-driven propose-referee-verify loop
actually produces knowledge, and the most honest possible place to fail.

Two disciplines were fixed before anything ran. First, pre-registration:
Chapter 3 was sealed before this chapter's search began, so the bets provably
predate the findings; the same logic was then applied inside the chapter
itself -- four priors with dated criteria were frozen and committed before the
search harness evaluated a single candidate. Second, a boundary: this chapter
does NOT score Chapter 3's hardware signposts. Those resolve on their own
dates against the outside world; nothing here touches them.

The search target was chosen at the frontier's seam. Cat qubits suppress
bit-flips exponentially in photon number, leaving a phase-biased error channel
that a classical outer code must clean up [CITE: Putterman 2025; CITE:
Guillaud & Mirrahimi 2019]. AI-driven code search exists -- reinforcement
learning since 2019 [CITE: Nautrup 2019], noise-aware RL that adapts to
channel bias but assumes error-free encoding circuits [CITE: Olle 2024],
RL for low-weight codes [CITE: He & Liu 2025], and a 2026 flurry of
LLM-guided searches [CITE: Cruz-Benito 2026; CITE: Liu & Marquardt 2026] and
Bayesian optimization [CITE: BayesOpt 2026] -- but all of it, checked against
each paper's own words, evaluates candidates under code-capacity noise:
perfect syndrome extraction, errors on data qubits only. Meanwhile the
circuit-level analysis of bias-tailored codes exists and is sobering [CITE:
Benito 2026 -- "the substantial advantages predicted ... under code-capacity
noise are strongly reduced once realistic syndrome extraction and
circuit-level noise models are considered"], but no one runs an automated
search under that honest noise. The seam -- AI search x circuit-level
finite-bias noise x hardware weight caps -- was uncrossed. This chapter
crosses it, and reports what survived.

## 02 THE INSTRUMENT

A search is only as honest as its referee, so the referee was built first and
calibrated against published hardware before it judged anything.

The noise model is anchored to Amazon's Ocelot chip [CITE: Putterman 2025],
and the anchoring is a derivation, not a fit: the standard cat dephasing law
(phase-flip rate = photon number times single-photon loss) was tested against
three independently measured Ocelot numbers -- storage lifetime, phase-flip
time at two photons, and per-cycle phase error during gate activity -- and
adopted only after all three closed on one parameter with no fitting. The
bit-flip sector was refit from Ocelot's own released shot data (data DOI
10.5281/zenodo.14257632) with the paper's free-amplitude convention,
resolving the suppression scaling at 2.1-2.4x per photon, saturating above
three photons -- measured, not assumed. One fitted parameter remains -- the
syndrome measurement error, fit to the published distance-5 result (1.65% per
cycle) with both distance-3 results held out as honest checks (landing within
+/-30%, the spread between the two device sections itself bounding what any
model can claim). For the high-bias regime the search targets, a second gate
model was verified from the founding theory paper [CITE: Guillaud & Mirrahimi
2019] and cross-checked against an independent group's published simulation
fit [CITE: Ruiz 2025]: twelve of twelve grid points landed within the
same-order corridor, within +/-25% at the operating point.

The instrument's flaws are content, not footnotes. It reads 1.2-2x optimistic
in absolute terms against the Ruiz fit (disclosed everywhere; it cancels in
the same-instrument ratios all conclusions rest on). Finite-depth memory
experiments flatter both codes near their boundaries, so every cross-code
comparison in this chapter is depth-matched by standing rule -- a rule
adopted after the effect nearly produced a wrong verdict, was named,
predicted quantitatively, and closed by measurement. And the error ledger
(Section 05) records nine mistakes made and caught building all of this,
because an instrument whose failure modes are hidden is not calibrated.

## 03 THE CAMPAIGN

Four priors were frozen before the first run: 35% that Day-1's best
code-capacity discovery would survive circuit-level refereeing; 55% that some
searched code would beat budget-matched repetition by 2x under honest noise
at weight-4 checks; 40% that an LLM-layer seed would reach the final
leaderboard's top three; 20% for a stretch target matching the published
cellular-automaton overhead at lower check weight. Resolution criteria, dates,
and stop conditions went into the repository with them. Then the referee ran.

It ate the proposer's food first. The Day-1 headline -- a hypergraph-product
code that looked 2.4x more qubit-efficient than the best comparison at
moderate bias under code-capacity noise -- lost to plain repetition by five
orders of magnitude at the high-bias operating point. Prior one resolved
FALSE, published at full prominence: the cheap model proposes, the expensive
model disposes, and the miss taught the campaign's first structural lesson --
measuring both stabilizer types under these gates costs a factor ~54 to guard
a bit-flip floor a hundred times smaller than anything it protects against.
At high bias you measure phase checks only, which is exactly the architecture
the leading proposal already uses [CITE: Ruiz 2025].

Then the referee ate the proposer's first repair. A double-circulant family
proposed for the second stage carried a structural distance ceiling its
proposer missed -- provable in one line, found by the mechanical verifier
before a single Monte-Carlo shot. The family that survived was built from the
kill: repetition crossed with the extended Hamming code, distance twelve at
weight-4 checks, thirteen qubits per logical. At the high-bias operating
point, depth-matched on the same instrument, it runs at one quarter the
per-logical error of the strictest budget-matched repetition comparator
(ratio 0.255, 95% CI [0.172, 0.337]) -- surviving a fresh-seed re-run, a
stronger adversarial decoder, and the depth-artifact diagnosis along the way.
Prior two resolved TRUE. The claim carries its scope label in the same
breath: a model-level result under a verified gate channel at one operating
point, not a hardware demonstration.

Prior three resolved TRUE with its footnotes attached -- the winning seed is
"LLM-layer" in the sense that the strategy room proposed it against its own
mechanical referee, and the win required the referee's kill first. Prior four
resolved FALSE: the winning family's overhead grows with distance, and
nothing found at weight-4 approaches the published cellular-automaton
overhead [CITE: Ruiz 2025]. The stretch was a stretch. Final score: two hits,
two misses, twenty-four days ahead of the signpost date.

## 04 THE MAP

The severity map is the chapter's payload, because it converts one win and
three losses into a single measured principle: codes must match their bias
regime, and the penalty for mismatch is not percentage points -- it is orders
of magnitude, in both directions.

Down-bias: at ten times dirtier gate quality the winner's advantage does not
shrink, it inverts -- twelve times worse than repetition, its deeper sibling
sixty-three times worse. The deeper the code, the faster it drowns when
syndrome noise rises. Up-bias: the Day-1 moderate-bias champion, correct in
its own regime, lost by a hundred thousand at high bias. And at today's
measured hardware -- Ocelot's bias of roughly thirty, with its calibrated
measurement error -- both the winner and its repetition comparator drown
together in the unprotected bit-flip floor, at percent-per-cycle rates that
make the phase-sector contest between them irrelevant. Independent
circuit-level work on other biased-noise platforms reports the same cliff
from the other side [CITE: Benito 2026]. The map's reading for roadmaps:
today's cat hardware wants moderate-bias codes with both check types;
tomorrow's high-bias hardware wants phase-only classical structure; and a
code search that does not know which regime it is searching for will win the
wrong war. This is the science-versus-scale-up spine of the whole dossier,
measured inside a single chapter.

## 05 THE SCOREBOARD

What can an AI-driven search loop actually do today, on the evidence of this
chapter? It can build and calibrate its own referee from published data. It
can propose, get refereed, and repair -- the winning code exists because the
mechanical verifier killed its predecessor. It can win on the frontier's own
terms at one operating point, and map the boundaries of that win honestly.
What it cannot do, on this evidence, is skip the expensive referee: every
code-capacity promise this campaign tested either shrank or died at circuit
level, which is precisely what the field's own frontier reports [CITE: Benito
2026]. The dossier's boldest claim -- that AI materially shortens the road to
fault tolerance -- gains a small, honest data point: the loop produced one
model-level structural result and nine caught errors in one day, and the
errors were half the value.

Three forecasts, posted OPEN-UNVERIFIED with dated signposts. F1: a published
weight-<=4 cat outer code matching the cellular-automaton overhead
(<=8 qubits per logical at 1e-8, circuit-level) by 2027-12-31 -- 30%. F2: an
external group publishes an AI-in-the-loop code search under circuit-level
(not code-capacity) noise by 2027-06-30 -- 55%. F3: a hardware demonstration
of any k>1 outer cat code, beyond repetition, by 2028-12-31 -- 25%. Each
resolves against the public record; misses publish like hits.

The error ledger is the chapter's second result. Nine entries, E1-E9: a
phantom environment, a misread definition, a biased fit, a wrong corridor, a
tool's bad arithmetic, a missing observable, an imprecise preview, a
depth-biased comparison, and a one-character drift in the machinery's own
handoff -- each caught by the discipline built for exactly that failure, each
credited to its catcher, each published. A loop that cannot catch its own
errors cannot be trusted to catch nature's. This one, on one day's evidence,
catches both.

---

## References (cite cards, verified-to-primary this session)

- **Putterman 2025** -- H. Putterman et al., "Hardware-efficient quantum error
  correction via concatenated bosonic qubits," Nature 638, 927-934 (2025),
  DOI 10.1038/s41586-025-08642-7; data DOI 10.5281/zenodo.14257632. Measured
  cat-qubit repetition code (distance-5, 1.65% per cycle); this chapter's
  noise-model anchor -- every hardware-mode rate traces to its published or
  released numbers.
- **Guillaud & Mirrahimi 2019** -- J. Guillaud, M. Mirrahimi, "Repetition Cat
  Qubits for Fault-Tolerant Quantum Computation," PRX 9, 041053 (2019). The
  founding cat-architecture theory; source of the verified CNOT error channel
  used in this chapter's high-bias gate model (constants pending PDF
  byte-check, OPEN-7).
- **Ruiz 2025** -- D. Ruiz et al., "LDPC-cat codes for low-overhead quantum
  computing in 2D," Nat. Commun. 16, 1040 (2025), DOI
  10.1038/s41467-025-56298-8. The frontier proposal this chapter's search is
  benchmarked against: phase-only extraction, 758 cat qubits for 100 logical
  at 1e-8; source of the published repetition fit our corridor validates
  against.
- **Nautrup 2019** -- H. P. Nautrup et al., "Optimizing Quantum Error
  Correction Codes with Reinforcement Learning," Quantum 3, 215 (2019),
  arXiv:1812.08451. The RL code-search origin point; code-capacity setting.
- **Olle 2024** -- J. Olle et al., "Simultaneous discovery of quantum error
  correction codes and encoders with a noise-aware reinforcement learning
  agent," npj Quantum Information 10 (2024), arXiv:2311.04750. Noise-aware
  means channel-bias-aware: "the encoding circuit is assumed to be error-free
  (non fault-tolerant encoding)" -- the seam this chapter crosses, in the
  prior art's own words.
- **He & Liu 2025** -- arXiv:2502.14372, "Discovering highly efficient
  low-weight quantum error-correcting codes with reinforcement learning."
  RL under weight constraints; code-capacity evaluation.
- **Cruz-Benito 2026** -- J. Cruz-Benito, A. W. Cross, D. Kremer, I. Faro
  (IBM), "Evolutionary Discovery of Bivariate Bicycle Codes with LLM-Guided
  Search," arXiv:2606.02418 (2026). LLM-guided evolutionary search scored on
  distance and code-capacity simulations.
- **Liu & Marquardt 2026** -- Z. Liu, F. Marquardt,
  "Large-Language-Model Discovery of Quantum LDPC Codes through Structured
  Concept Evolution," arXiv:2606.24808 (2026). LLM concept evolution;
  evaluation "under code-capacity depolarizing noise" (verbatim).
- **BayesOpt 2026** -- arXiv:2601.18562, "Bayesian Optimization for Quantum
  Error-Correcting Code Discovery" (2026). Identity verified; noise model to
  be quoted at final cite-card pass.
- **Benito 2026** -- C. Benito, I. J. Velazquez-Resendiz, A. Bermudez,
  "Optimizing bias-tailored quantum error correction beyond code-capacity
  noise," arXiv:2606.17709 (2026). Circuit-level analysis of existing
  bias-tailored families (no automated search); independently reports the
  code-capacity-to-circuit-level cliff this chapter measured -- external
  corroboration of our P1 result.
- **Roffe 2023** -- J. Roffe et al., "Bias-tailored quantum LDPC codes,"
  Quantum 7, 1005 (2023), arXiv:2202.01702. The bias-tailoring program for
  LDPC codes; context for the bias-regime map.

## Open items carried in this chapter's audit trail

OPEN-1 (Ocelot kappa_2, paper appendices); OPEN-3 (PDF byte-verification of
all quoted anchors and figure definitions); OPEN-4 (CX^2 protocol detail);
OPEN-7 (Guillaud-Mirrahimi channel constants vs the PRX PDF); the BayesOpt
noise-model quote. Published as open verification work, not asserted.
