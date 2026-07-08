An Open Dossier · **QC-Accelerate-002**

# Accelerating Quantum Computing Research Using AI and Robotics

*Irfan Ali-Khan — Independent Researcher*

**Chapter 4 — the loop eats first.** *Chapter 3 placed bets on where the closed loop closes first; this chapter runs the loop's cheapest case — no fabrication step — on ourselves: an AI-driven search for cat-qubit outer codes, refereed under circuit-level noise anchored to published hardware. Four priors were frozen and committed before the search ran. Two resolved true, two false, twenty-four days ahead of their signpost date, and every miss is published at the same prominence as the hits. The chapter's payload is a measured principle — codes must match their bias regime, and the penalty for mismatch is orders of magnitude in both directions — plus a nine-entry ledger of the machinery catching its own errors, which is half the point. Nothing here scores Chapter 3's hardware signposts; those resolve on their own dates.*

## Avenues

| Avenue | Thesis | Status | Forecast | Sources |
|---|---|---|---|---|
| Scored: the Day-1 headline survives circuit level | Frozen at 35% before the search ran: the best code-capacity discovery ([[42,3]] hypergraph product, 2.4x qubit-efficient at moderate bias) survives the circuit-level referee within 2x of budget-matched repetition. It lost by five orders of magnitude -- a moderate-bias code drowned at the high-bias operating point. The miss is the chapter's first structural lesson. | SCORED: FALSE | — | ocelot, ruiz |
| Scored: a searched code beats repetition 2x | Frozen at 55%: some searched code beats strict budget-matched repetition by 2x per logical under circuit-level noise at weight-4 checks. Resolved TRUE by rep3 x extended-Hamming [24,4,12] -- 13 qubits per logical, matched-depth same-instrument ratio 0.255 (CI 0.172-0.337) -- surviving fresh-seed, adversarial-decoder, and depth re-checks. Model-level result, not a hardware demonstration. | SCORED: TRUE | — | ruiz, gm2019 |
| Scored: the LLM layer earns a podium place | Frozen at 40%: an LLM-layer seed reaches the final leaderboard's top three. Resolved TRUE -- the winner itself is LLM-layer, with footnotes carried: the proposing agent played against its own mechanical referee, and the winning family was built from the referee's kill of the proposer's first family (a one-line structural distance ceiling, caught before any Monte-Carlo). | SCORED: TRUE | — | ibmllm, liumarq |
| Scored: the stretch target | Frozen at 20%: a searched weight-4 code matches the published cellular-automaton overhead (10 or fewer qubits per logical at 1e-8). Resolved FALSE -- the winning family's overhead grows with distance and nothing found approaches the bar. The stretch was a stretch; the frontier's overhead stands unmatched at this weight cap. | SCORED: FALSE | — | ruiz |
| Forward: low-weight codes reach the frontier overhead | Someone publishes a weight-4-or-less cat outer code matching the cellular-automaton overhead (8 or fewer qubits per logical at 1e-8, circuit-level). Our own campaign says the weight cap is the hard constraint -- but one campaign's search space is not the field's. | FORECAST | ~30% by a published, independently checkable construction meeting the bar by 2027-12-31 | ruiz, heliu |
| Forward: the field crosses the noise seam | An external group publishes an AI-in-the-loop code search evaluated under circuit-level noise (faulty syndrome extraction), not code capacity. The 2026 LLM flurry plus the frontier's own beyond-code-capacity finding make this the obvious next move; this chapter is evidence it is tractable. | FORECAST | ~55% by a published external AI-driven code search with circuit-level evaluation by 2027-06-30 | ibmllm, benito |
| Forward: a multi-logical outer cat code on hardware | A hardware demonstration of any k>1 outer code on cat qubits -- beyond the repetition codes demonstrated to date. The bias-regime map says today's devices want moderate-bias codes with both check types; whether any lab ships one is a hardware bet, not a theory bet. | FORECAST | ~25% by a peer-reviewed multi-logical-qubit outer-cat-code demonstration by 2028-12-31 | ocelot, ruiz |

**THE CHAPTER · THE EXPEDITION**

## 01 THE DEGENERATE LOOP

The dossier's thesis is a loop: propose, fabricate, verify, learn. Chapters 1 through 3 asked who is building that loop for quantum hardware and found the crown empty — Hefei has the robots, the allies have the referee, nobody has the loop. This chapter does something different: it runs the loop's degenerate case, the one with no fabrication step, on ourselves. Quantum error-correcting code space is a search problem where the "device" is a simulator and the "measurement" is a decoder — the cheapest possible place to test whether an AI-driven propose-referee-verify loop produces knowledge, and the most honest possible place to fail.

Two disciplines were fixed before anything ran. First, pre-registration: Chapter 3 was sealed before this chapter's search began, so the bets provably predate the findings — and the same logic was applied inside the chapter itself, four priors with dated criteria frozen and committed before the search harness evaluated a single candidate. Second, a boundary: this chapter does not score Chapter 3's hardware signposts. Those resolve on their own dates against the outside world.

The search target sits at the frontier's seam. Cat qubits suppress bit-flips exponentially in photon number, leaving a phase-biased error channel that an outer code must clean up [Nature 2025] [PRX 2019]. AI-driven code search exists — reinforcement learning since 2019 [Quantum 2019], noise-aware RL that adapts to channel bias but assumes error-free encoding circuits [npj QI 2024], RL under weight constraints [arXiv 2025], and a 2026 flurry of LLM-guided searches [arXiv 2026] [arXiv 2026] and Bayesian optimization [arXiv 2026] — but all of it, checked against each paper's own words, evaluates candidates under code-capacity noise: perfect syndrome extraction, errors on data qubits only. Meanwhile circuit-level analysis of bias-tailored codes exists and is sobering [arXiv 2026], but nobody runs an automated search under that honest noise. The seam — AI search times circuit-level finite-bias noise times hardware weight caps — was uncrossed. This chapter crosses it and reports what survived.

## 02 THE INSTRUMENT

A search is only as honest as its referee, so the referee was built first and calibrated against published hardware before it judged anything. The noise model anchors to Amazon's Ocelot chip [Nature 2025], and the anchoring is a derivation, not a fit: the standard cat dephasing law — phase-flip rate equals photon number times single-photon loss — was tested against three independently measured Ocelot numbers (storage lifetime, phase-flip time at two photons, per-cycle phase error during gate activity) and adopted only after all three closed on one parameter with no fitting. The bit-flip sector was refit from Ocelot's own released shot data with the paper's free-amplitude convention, resolving the suppression scaling at 2.1-2.4x per photon, saturating above three photons — measured, not assumed. One fitted parameter remains: the syndrome measurement error, fit to the published distance-5 result (1.65% per cycle) with both distance-3 results held out as honest out-of-sample checks, landing within 30% — the spread between the device's two distance-3 sections itself bounding what any model may claim. For the high-bias regime the search targets, a second gate model was taken from the founding theory paper [PRX 2019] and cross-checked against an independent group's published simulation fit [Nat. Commun. 2025]: twelve of twelve grid points landed within the same-order corridor, within about 25% at the operating point.

The instrument's flaws are content, not footnotes. It reads 1.2-2x optimistic in absolute terms against that published fit — disclosed everywhere it matters, and cancelled in the same-instrument ratios all conclusions rest on. Finite-depth memory experiments flatter both codes near their boundaries, so every cross-code comparison in this chapter is depth-matched by standing rule — a rule adopted after the effect nearly produced a wrong verdict, was named, predicted quantitatively, and closed by measurement. And the error ledger (Section 05) records nine mistakes made and caught while building all of this, because an instrument whose failure modes are hidden is not calibrated.

## 03 THE CAMPAIGN

Four priors were frozen before the first run: 35% that Day-1's best code-capacity discovery would survive circuit-level refereeing; 55% that some searched code would beat budget-matched repetition by 2x under honest noise at weight-4 checks; 40% that an LLM-layer seed would reach the final leaderboard's top three; 20% for a stretch target matching the published cellular-automaton overhead at lower check weight. Resolution criteria, dates, and stop conditions went into the repository with them. Then the referee ran.

It ate the proposer's food first. The Day-1 headline — a hypergraph-product code that looked 2.4x more qubit-efficient than the best comparator at moderate bias under code-capacity noise — lost to plain repetition by five orders of magnitude at the high-bias operating point. Prior one resolved FALSE, published at full prominence: the cheap model proposes, the expensive model disposes. The miss taught the campaign's first structural lesson — measuring both stabilizer types under these gates costs a factor of about 54 to guard a bit-flip floor far smaller than anything it protects against. At high bias you measure phase checks only, which is exactly the architecture the leading proposal already uses [Nat. Commun. 2025].

Then the referee ate the proposer's first repair. A double-circulant family proposed for the second stage carried a structural distance ceiling its proposer missed — provable in one line, found by the mechanical verifier before a single Monte-Carlo shot. The family that survived was built from the kill: repetition crossed with the extended Hamming code, distance twelve at weight-4 checks, thirteen qubits per logical. At the high-bias operating point, depth-matched on the same instrument, it runs at one quarter the per-logical error of the strictest budget-matched repetition comparator — ratio 0.255, 95% confidence interval 0.172 to 0.337 — surviving a fresh-seed re-run, a stronger adversarial decoder, and the depth-artifact diagnosis along the way. Prior two resolved TRUE. The claim carries its scope label in the same breath: this is a model-level result under a verified gate channel at one operating point, not a hardware demonstration.

Prior three resolved TRUE with its footnotes attached — the winning seed is "LLM-layer" in the sense that the drafting agent proposed it against its own mechanical referee, and the win required the referee's kill first. Prior four resolved FALSE: the winning family's overhead grows with distance, and nothing found at weight-4 approaches the published cellular-automaton overhead [Nat. Commun. 2025]. The stretch was a stretch. Final score: two hits, two misses, twenty-four days ahead of the signpost date.

## 04 THE MAP

The severity map is the chapter's payload, because it converts one win and three losses into a single measured principle: codes must match their bias regime, and the penalty for mismatch is not percentage points — it is orders of magnitude, in both directions. Down-bias: at ten times dirtier gate quality the winner's advantage does not shrink, it inverts — twelve times worse than repetition, its deeper sibling sixty-three times worse; the deeper the code, the faster it drowns when syndrome noise rises. Up-bias: the Day-1 moderate-bias champion, correct in its own regime, lost by a hundred thousand at high bias. And at today's measured hardware — Ocelot's bias of roughly thirty, with its calibrated measurement error — both the winner and its repetition comparator drown together in the unprotected bit-flip floor, at percent-per-cycle rates that make the phase-sector contest between them irrelevant. Independent circuit-level work on other biased-noise platforms reports the same cliff from the other side [arXiv 2026].

The map's reading for roadmaps: today's cat hardware wants moderate-bias codes with both check types; tomorrow's high-bias hardware wants phase-only classical structure [Quantum 2023] [Nat. Commun. 2025]; and a code search that does not know which regime it is searching for will win the wrong war. This is the science-versus-scale-up spine of the whole dossier, measured inside a single chapter.

## 05 THE SCOREBOARD

What can an AI-driven search loop actually do today, on this chapter's evidence? It can build and calibrate its own referee from published data. It can propose, get refereed, and repair — the winning code exists because the mechanical verifier killed its predecessor. It can win on the frontier's own terms at one operating point, and map the boundaries of that win honestly. What it cannot do, on this evidence, is skip the expensive referee: every code-capacity promise this campaign tested either shrank or died at circuit level, which is precisely what the field's own frontier reports [arXiv 2026]. The dossier's boldest claim — that AI materially shortens the road to fault tolerance — gains a small, honest data point: the loop produced one model-level structural result and nine caught errors in one day, and the errors were half the value.

Three new forecasts join the landscape above, posted OPEN-UNVERIFIED with dated signposts, scored in later editions: a published low-weight cat outer code matching the cellular-automaton overhead by end of 2027 (30%); an external AI-in-the-loop code search under circuit-level noise by mid-2027 (55%); a hardware demonstration of any multi-logical outer cat code by end of 2028 (25%). Misses will publish like hits.

The error ledger is the chapter's second result. Nine entries: a phantom environment, a misread definition, a biased fit, a wrong corridor, a tool's bad arithmetic, a missing observable, an imprecise preview, a depth-biased comparison, and a one-character drift in the machinery's own handoff — each caught by the discipline built for exactly that failure, each credited to its catcher, each published in the expedition notebook. A loop that cannot catch its own errors cannot be trusted to catch nature's. This one, on one day's evidence, catches both.

## Consistency checks

Results from `verification/verify_numbers.py` — the same checks the in-page console runs; CI reruns them on every commit.

- [PASS] Consistency: at least one avenue in the landscape
- [PASS] Consistency: every FORECAST has a dated signpost
- [PASS] Consistency: all forecast probabilities lie in [0,100]
- [PASS] Ch4: derived phase-flip time at two photons falls in Ocelot's measured 27-33 us
- [PASS] Ch4: idle-dominated per-cycle dephasing matches Ocelot's 9.6(4)e-2 (2-sigma window)
- [PASS] Ch4: bit-flip suppression per photon, lower section (e^0.735) sits in the 2.1-2.4x claim band
- [PASS] Ch4: bit-flip suppression per photon, upper section (e^0.882) sits in the 2.1-2.4x claim band
- [PASS] Ch4: out-of-sample d3 holdouts within the claimed 30% (worst of +22.5%/+28.4%)
- [PASS] Ch4: corridor grid points inside the same-order band (twelve of twelve)
- [PASS] Ch4: corridor agreement at the operating point ~25% (worst |1-ratio| of 0.86..0.94 grid)
- [PASS] Ch4: disclosed instrument optimism 1.2-2x (same-instrument rep-7 MC/FIT = 0.57 -> 1/0.57)
- [PASS] Ch4: P1 loss 'five orders of magnitude' (2.92e-4 / 2.74e-9)
- [PASS] Ch4: full-CSS extraction penalty 'a factor of about 54' (1.59e-2 / 2.92e-4)
- [PASS] Ch4: winner distance twelve = rep(3) x extHamming d(4) product
- [PASS] Ch4: winner thirteen qubits per logical = (24 data + 28 checks) / 4 logical
- [PASS] Ch4: matched-depth ratio 'one quarter' = 1.719e-7 / 6.750e-7 in stated CI [0.172, 0.337]
- [PASS] Ch4: matched-depth CI upper bound clears the frozen 0.5 bar
- [PASS] Ch4: scoreboard -- two hits + two misses = four frozen priors
- [PASS] Ch4: 'twenty-four days ahead' (2026-07-31 minus 2026-07-07)
- [PASS] Ch4: down-bias inversion, winner vs repetition ('twelve times worse')
- [PASS] Ch4: down-bias inversion, deeper sibling ('sixty-three times worse')
- [PASS] Ch4: Day-1 headline's code-capacity efficiency claim ('2.4x') as reported on Day 1

**TOTAL: 22 checks · 22 pass · 0 fail** — All checks pass — the survey is internally consistent.

## References

- **Nature 2025** — Putterman et al. (2025). Amazon's Ocelot chip: measured concatenated cat-qubit error correction -- distance-5 repetition code at 1.65% logical error per cycle, with released shot-level data. This chapter's noise-model anchor: every hardware-mode rate traces to its published or released numbers. *Nature 638, 927-934 (2025), DOI 10.1038/s41586-025-08642-7; data DOI 10.5281/zenodo.14257632*

- **PRX 2019** — Guillaud & Mirrahimi (2019). The founding repetition-cat architecture theory; source of the CNOT error channel used in this chapter's high-bias gate model (channel constants pending PDF byte-check, carried as open verification work on the audit page). *PRX 9, 041053 (2019), arXiv 1904.09474*

- **Quantum 2019** — Nautrup et al. (2019). The reinforcement-learning code-search origin point: RL agents optimizing surface-code layouts. Code-capacity setting -- part of the seam this chapter crosses. *Quantum 3, 215 (2019), arXiv 1812.08451*

- **npj QI 2024** — Olle et al. (2024). Noise-aware RL discovery of codes and encoders, where noise-aware means channel-bias-aware: in the authors' own words, 'the encoding circuit is assumed to be error-free (non fault-tolerant encoding)' -- the prior art stating the seam in its own words. *npj Quantum Information 10 (2024), DOI 10.1038/s41534-024-00920-y, arXiv 2311.04750*

- **arXiv 2025** — He & Liu (2025). RL discovery of low-weight quantum codes under weight constraints -- the hardware-cap half of this chapter's search space, evaluated at code capacity. *arXiv 2502.14372 (2025)*

- **arXiv 2026** — Cruz-Benito et al., IBM (2026). LLM-guided evolutionary discovery of bivariate bicycle codes, scored on distance and code-capacity simulations -- the 2026 LLM-search flurry's flagship, still on the cheap side of the noise seam. *arXiv 2606.02418 (2026)*

- **arXiv 2026** — Liu & Marquardt (2026). LLM discovery of qLDPC codes through structured concept evolution, evaluated 'under code-capacity depolarizing noise' (verbatim) -- BP+OSD-scored fitness, no syndrome-extraction errors. *arXiv 2606.24808 (2026)*

- **arXiv 2026** — Bayesian-optimization code discovery (2026). Bayesian optimization applied to quantum code discovery. Identity verified against arXiv; its noise-model statement is still to be quoted verbatim -- carried as open verification work, not asserted. *arXiv 2601.18562 (2026)*

- **arXiv 2026** — Benito, Velazquez-Resendiz & Bermudez (2026). Circuit-level optimization of existing bias-tailored code families (no automated search): 'the substantial advantages predicted ... under code-capacity noise are strongly reduced once realistic syndrome extraction and circuit-level noise models are considered' -- independent corroboration of this chapter's first published miss. *arXiv 2606.17709 (2026)*

- **Nat. Commun. 2025** — Ruiz et al. (2025). LDPC-cat codes: the frontier proposal this chapter's search is benchmarked against -- phase-only extraction, 758 cat qubits for 100 logical at 1e-8 -- and the source of the published repetition fit our evaluator's corridor validates against. *Nat. Commun. 16, 1040 (2025), DOI 10.1038/s41467-025-56298-8*

- **Quantum 2023** — Roffe et al. (2023). Bias-tailored quantum LDPC codes: the program of shaping code structure to the noise channel's bias -- the theory context for this chapter's measured bias-regime map. *Quantum 7, 1005 (2023), arXiv 2202.01702*
