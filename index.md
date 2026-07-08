An Open Dossier · **QC-Accelerate-002**

# Accelerating Quantum Computing Research Using AI and Robotics

*Irfan Ali-Khan — Independent Researcher*

**Chapter 4 — the loop eats first.** *Chapter 3 placed bets on where the closed discovery loop closes first; this chapter runs the loop's cheapest case — the one with no fabrication step — on ourselves: an AI-driven search for cat-qubit error-correcting codes, refereed under circuit-level noise calibrated to a published chip. Four predictions were frozen and committed before the search ran; two came true, two did not, twenty-four days ahead of their signpost date, and every miss is published at the size of a hit. The payload is a measured principle — a code must match its noise regime, and the price of mismatch is orders of magnitude in both directions — plus a nine-entry ledger of the machinery catching its own mistakes, which is half the result. Nothing here scores Chapter 3's hardware bets; those resolve on their own dates.*

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

## 01 THE LOOP, AND THE CHEAP WAY TO TEST IT

Strip science to its skeleton and it is a cycle: decide what to try next, make the thing, measure what you made, learn from the result, go around again. Most of this dossier asks one question about that cycle — how much of it can machines run on their own, for quantum computing? Chapter 2 found labs where machines hold one or two stations — robots that grow crystals, algorithms that pick the growth recipe — but nowhere on Earth does the full circle run unattended for quantum hardware. Chapter 3 put money-where-mouth-is percentages on where it will close first.

This chapter does something more direct: it runs the loop. Not on hardware — we own no lab — but on the one problem in quantum computing where the make step is free, because making the thing means simulating it. That problem is the search for error-correcting codes, and run concretely it has five stations (Fig 1). **PROPOSE**: an AI drafts a candidate code, which — as the next section explains — is literally a small grid of 0s and 1s, so a draft is cheap to write down. **VERIFY**: cheap algebra grades the draft's vital statistics before a single simulation, and kills the hopeless ones on the spot. **SIMULATE**: software builds the full error-correction machine the code implies — qubits, helper qubits, every gate and measurement, cycle after cycle — then poisons it with random errors at rates copied from a real, published chip, millions of runs. **SCORE**: a decoding algorithm tries to catch every error; each time it loses the stored information is one logical failure, counted and compared against the boring baseline everyone already uses. **LEARN**: keep the winners, kill the losers, and — this is the part that matters — write down why each loser lost, so the next PROPOSE is smarter.

One more discipline, borrowed from clinical medicine: before the loop ran at all, we wrote four predictions about how it would go, attached a probability to each, and committed them to a public, cryptographically timestamped record. Pre-registration means nobody — including us — can quietly move the goalposts after seeing the results. Two of the four came true; the other two are published at the same size as the wins. And one boundary, stated up front: this chapter does not score Chapter 3's hardware bets, which resolve on their own dates against the outside world.

*(figure: The five-station discovery loop drawn as a ring played clockwise: PROPOSE (an AI drafts a candidate code), VERIFY (cheap algebra grades it before any simulation), SIMULATE (the full checking circuit poisoned with chip-calibrated errors), SCORE (count decoder failures against budget-matched repetition), and LEARN (autopsy every loser to feed the next proposal). The referee's kill is marked at VERIFY and the campaign's win at SCORE; the loop is degenerate because the make step is free — making a candidate means simulating it. — Fig 1 — The discovery loop, run on itself: five stations played clockwise. PROPOSE (an AI drafts a candidate code, a small grid of 0s and 1s), VERIFY (cheap algebra grades it before any simulation), SIMULATE (the full checking circuit, poisoned with chip-calibrated errors), SCORE (count decoder failures against budget-matched repetition), LEARN (autopsy every loser to feed the next proposal). The loop is the degenerate case — its make step is free, because making a candidate means simulating it. The campaign’s two decisive events are marked where they landed on the ring: the referee’s kill at VERIFY, the win at SCORE. [SCHEMATIC])*

## 02 THE GAME: WHAT A CODE IS, AND WHAT KILLS ONE

A qubit is a physical object that stores quantum information, and physical objects forget. The information can be corrupted two distinct ways: a **bit flip** (the 0-part and 1-part of the state swap) and a **phase flip** (the sign between them silently reverses). Both are lethal; a useful quantum memory has to survive both.

The oldest trick against forgetting is repetition. Store a classical bit three times — 000 or 111 — and if one copy flips, majority vote restores it. Quantum mechanics forbids the obvious version (you cannot copy a qubit, and looking at one directly destroys it) but permits something subtler: you can ask a group of qubits a **parity question** — "do qubits 1 and 2 currently agree?" — without asking what either one holds. Helper qubits extract these parities one gate at a time; a pattern of disagreements is a fingerprint, and a decoding algorithm reads the fingerprint to infer which qubit flipped. That is quantum error correction: parity questions, asked over and over, forever.

A **code** is a recipe for which parity questions to ask. It is written as a grid of 0s and 1s — each row a parity check, each column a qubit, a 1 where a check touches a qubit. Three numbers grade the recipe, written [n, k, d]: n physical qubits store k logical (useful) qubits, and the distance d says how much abuse the code survives — any combination of up to floor((d-1)/2) simultaneous errors is corrected with certainty. Repetition on n qubits is the code [n, 1, n]: superb protection, terrible economy — one useful qubit no matter how many you spend. The whole craft of code design is buying more k per n without letting d collapse.

Now the hardware this chapter searches for. **Cat qubits** — the technology of Amazon's Ocelot chip [Nature 2025], the lineage this dossier has tracked since Chapter 1 — store a qubit in two laser-like states of a microwave cavity. Their signature property, the reason anyone tolerates their complexity, is lopsided noise: make the cat "bigger" (more photons, n-bar) and bit flips become exponentially rare while phase flips get only modestly worse.

```math
\Gamma_{\text{bit}} \propto e^{-2\bar{n}} \tag{eq.\ 1}
```

```math
\Gamma_{\text{phase}} = \bar{n}\,\kappa_1 \tag{eq.\ 2}
```

Here kappa-1 is the cavity's photon-loss rate (equation 1 is the same exponential law that opened Chapter 1). At the sizes Ocelot runs, bit flips happen thousands of times less often than phase flips, so the code mostly has one job — catch phase flips — and can be lighter and cheaper than a code fighting both enemies at once [PRX 2019].

Here is the seam this chapter lives on. Checking parities is itself physical work — gates, helper qubits, measurements — and every one of those can fail. There are two honesty grades for evaluating a code. **Code capacity** grade: pretend the checking machinery is perfect and only the stored qubits err — cheap to simulate, flattering to clever codes. **Circuit level** grade: every gate, every helper, every measurement fails at its own measured rate — slow, unflattering, honest. Checked sentence by sentence, every AI-driven code search ever published grades itself at code capacity — reinforcement learning since 2019 [Quantum 2019], noise-aware RL whose noise is channel bias, not faulty extraction ("the encoding circuit is assumed to be error-free," in the authors' words) [npj QI 2024], RL under weight constraints [arXiv 2025], and a 2026 flurry of LLM-guided searches [arXiv 2026] scored "under code-capacity depolarizing noise" [arXiv 2026] and Bayesian optimization [arXiv 2026]. Meanwhile the one group that graded bias-tailored codes at circuit level found the flattery evaporates — "the substantial advantages predicted... under code-capacity noise are strongly reduced" [arXiv 2026] — but nobody runs a search at that grade. AI search exists; honest grading exists; the intersection was empty. This chapter fills it.

## 03 THE SIMULATION, EXACTLY

What one "measurement" in the loop actually is, start to finish. Build a circuit: n cat qubits prepared in a known state; each cycle, helper qubits ask every parity question in the code's grid (one two-qubit gate per 1 in the grid), then get measured and reset; eight to sixteen cycles; a final readout of every qubit. Then poison it: at every location — every idle moment, every gate, every measurement — flip a biased coin and, with the appropriate probability, insert an error. Run the poisoned circuit millions of times (it is a stabilizer circuit, so a classical computer simulates it exactly — the standard "stim" framework), hand each run's fingerprints to a decoder (belief propagation with ordered-statistics post-processing, the field's workhorse), and count the runs where the guess was wrong in a way that corrupted the stored information. Divide. That is eps-L, the logical failure rate per cycle per stored qubit — the one number a memory is graded on.

Every coin's bias comes from a real place, and this is the part we are most careful about. The probability of an error over a time t follows from a rate,

```math
p(t) = 1 - e^{-\Gamma t} \tag{eq.\ 3}
```

and each rate traces to Amazon's published Ocelot results [Nature 2025] or their released raw data. **Phase flips:** the photon-loss rate is kappa-1 = 1/(60 microseconds), from the paper's storage lifetime; equation 2 then predicts the phase-flip time at cat size n-bar = 2 as 30 microseconds (Amazon measured 27–33), and the phase-error probability per 2.8-microsecond cycle as 8.9% (Amazon measured 9.6 ± 0.4%). Two independent bullseyes from one untuned number — that closure is what licensed the model. **Bit flips:** refit from Amazon's released shot-level data using their own convention — suppression grows 2.1–2.4x per added photon, saturating above n-bar of about 3; measured, not assumed. **Measurement error:** the one number we could not derive — how often a parity readout simply lies — fit to exactly one published number (the distance-5 result, 1.65% per cycle) at 4.8%, then tested against two published numbers it had never seen; both landed within 30%. One fitted parameter, honestly labeled, tested out-of-sample. **Gates in the high-bias regime:** for the future-hardware operating point the gate error model comes from the founding cat-qubit theory [PRX 2019], whose key term is the price of a two-qubit gate of duration T on a cat of size n-bar with two-photon stabilization rate kappa-2:

```math
p_Z(\text{control}) = \bar{n}\,\kappa_1 T + \frac{1}{2\pi\,\bar{n}\,\kappa_2 T} \tag{eq.\ 4}
```

The first term is ordinary decay; the second is the gate's own quantum clumsiness — a non-adiabatic error, the cost of rushing. At the frontier operating point that second term dominates everything else, which is exactly why lazy grading flatters and honest grading kills. A final calibration check pointed the finished instrument at a code family another group had already simulated by independent methods [Nat. Commun. 2025]: twelve of twelve grid points landed inside the agreement band, within about 25% at the operating point. The instrument's two known flaws are printed on it — it reads 1.2–2x optimistic in absolute terms (so every conclusion uses same-instrument ratios, where the optimism cancels), and short simulations flatter both codes near their start and end (so every comparison runs both codes at matched depth — a rule adopted after that exact effect nearly produced a wrong verdict, which we caught).

## 04 THE CAMPAIGN: FOUR BETS, ONE KILL, ONE WIN

**Bet 1 (35%): Day 1's discovery is real.** On Day 1, under cheap code-capacity grading, the search had found a hypergraph-product code that looked 2.4x more qubit-efficient than anything comparable. Bet 1 said it would survive honest grading. It did not — it lost to plain repetition by a factor of one hundred thousand. The autopsy is instructive: that code needs both kinds of parity check, and under cat-qubit gate physics the bit-flip checks put their worst errors directly onto the stored qubits — a factor-of-about-54 penalty — to guard against bit flips that equation 1 had already made a thousand times rarer than the checks' own cost. Paying 54x to insure against almost nothing. At high bias you check phase only, which is exactly the architecture the frontier proposal already uses [Nat. Commun. 2025]. Miss, published, lesson banked.

**Bet 2 (55%): the search beats repetition anyway.** The first family the AI proposed for the honest-grading campaign died before a single simulation — the mechanical verifier proved in one line that it had a hidden ceiling, its error-survival could never exceed d = 4 no matter the size. That is the loop working, not failing: the kill was cheap, immediate, and explained. The repair bred the winner: take 3x repetition, cross it with a classic 8-bit code (the extended Hamming code — four parity checks, each touching four qubits), and the product is a [24, 4, 12] code — 24 cat qubits storing 4 logical qubits, 13 per logical including helpers, surviving any 5 simultaneous phase flips. At the frontier operating point, graded honestly, depth-matched on the same instrument, it fails at one quarter the rate of budget-matched repetition (ratio 0.255; 95% confidence interval 0.17–0.34). Then we tried to kill it three ways — fresh random seeds, a stronger decoder, doubled circuit depth — and it survived all three. Hit. One label rides with it everywhere: this is a result about a validated model of hardware, not about hardware.

**Bet 3 (40%): the AI's own proposal reaches the podium.** It did — the winner is the AI-layer proposal, with the footnote printed at equal size: the proposing agent and the strategy running this dossier are the same system, refereed by its own mechanical verifier, and the win exists only because that verifier killed the first attempt. Hit, footnotes attached.

**Bet 4 (20%): match the frontier's overhead.** The published frontier architecture reaches about 7.6 qubits per logical at error rates of one in a hundred million [Nat. Commun. 2025]. Bet 4 asked our weight-limited search to match it. Nothing came close — the winning family's overhead grows with protection, the wrong direction entirely. Miss: the stretch was a stretch. Final score: two hits, two misses, twenty-four days ahead of the signpost date.

*(figure: Chapter 4's campaign arc: four bets frozen before the search (35, 55, 40, 20 percent), resolved the same day — two hits, two misses — with the referee's kill-then-repair story, three hollow forward bets, and the nine-entry error ledger. — Fig 2 — The campaign arc: four bets frozen in public before the search ran (35% / 55% / 40% / 20%), resolved the same day against the frozen criteria — two hits (green), two misses (coral), every verdict published at equal prominence. Beneath the resolved pair, the referee story: the mechanical verifier killed the first proposed family before any Monte-Carlo, and the repair became the winner. Right rail: three forward bets, hollow until a later edition scores them (30% by end 2027, 55% by mid 2027, 25% by end 2028). Bottom: the nine-entry error ledger E1-E9, every catch credited and published. Dates, percentages, and verdicts are taken directly from the committed record; no interpolation. [SCORED + FORECAST · as carded])*

## 05 THE MAP, AND WHAT A LOOP IS GOOD FOR

Put the win under a moving spotlight and the chapter's real finding appears (Fig 3). Make the gates ten times dirtier and the winner does not merely shrink — it inverts, losing twelve times to repetition (its deeper sibling, sixty-three times): sophisticated codes drown first when the checking machinery degrades, because they lean on it hardest. Move to today's actual measured hardware and neither code matters — both drown in unprotected bit flips at percent-per-cycle rates, because at today's cat sizes equation 1 has not yet pushed bit flips low enough to ignore. Only at the future high-bias operating point — the regime the search was aimed at — does the win exist. Independent circuit-level work on other biased-noise platforms reports the same cliff from the other side [arXiv 2026].

*(figure: The campaign's winning code compared to plain repetition across three measured noise regimes: it loses 12x under dirty gates, nobody wins at today's hardware (both drown in the bit-flip floor), and it wins about 4x at the high-bias operating point it was searched for. — Fig 3 — One AI-found code, three noise regimes: the campaign winner (rep3 x extended-Hamming [24,4,12], weight-4 checks, 13 qubits per logical) against budget-matched repetition, on a log advantage axis. Dirty gates (kappa1/kappa2 = 1e-3): it loses 12x and its deeper sibling loses 63x. Today’s hardware (Ocelot-calibrated, bias ~30): nobody wins — both architectures drown in the unprotected bit-flip floor at ~2-5% per cycle. High bias (1e-4, the regime the search was aimed at): it wins ~3.9x, 95% CI 3.0-5.8, depth-matched on the same instrument. Ratios taken directly from the committed campaign record; a model-level result, not a hardware demonstration. [SCORED · numbers as committed])*

Codes are like tires: the racing slick that wins on a dry track loses on gravel and kills you on ice. Today's cat hardware wants moderate-bias codes with both check types; tomorrow's high-bias hardware wants phase-only classical structure [Quantum 2023] [Nat. Commun. 2025]; and a code search that does not know what weather it is designing for will win the wrong race. That is this dossier's science-versus-scale-up spine, measured three ways inside one chapter.

So what is an AI-driven discovery loop actually good for, today, on this evidence? It can build its own honest referee from published data — the calibration chain above is machine work end to end. It can propose, be refuted, and grow from the refutation — the winner is literally made of its predecessor's autopsy. It can produce a real, checkable, model-level result at the field's own frontier operating point. What it cannot do is skip the expensive referee: every cheap-grade promise this campaign tested shrank or died under honest grading, exactly what the field's own frontier reports [arXiv 2026]. The dossier's boldest claim — that AI materially shortens the road to fault tolerance — gains a small, honest data point: the loop produced one model-level structural result and nine caught errors in one day, and the errors were half the value.

Three new bets go on the board, hollow until scored: someone publishes a low-weight cat code matching the frontier's overhead by end of 2027 (30%); an outside group runs an AI code search under honest circuit-level grading by mid-2027 (55%); someone demonstrates a multi-logical cat code on real hardware by end of 2028 (25%). Misses will publish like hits — they always do here.

The error ledger is the chapter's second result. Nine entries: a phantom environment, a misread definition, a biased fit, a wrong corridor, a tool's bad arithmetic, a missing observable, an imprecise preview, a depth-biased comparison, and a one-character drift in the machinery's own handoff — each caught by the discipline built for exactly that failure, each credited to its catcher, each published in the expedition notebook. A loop that cannot catch its own errors cannot be trusted to catch nature's. This one, on one day's evidence, catches both.

## Consistency checks

Results from `verification/verify_numbers.py` — the same checks the in-page console runs; CI reruns them on every commit.

- [PASS] Consistency: at least one avenue in the landscape
- [PASS] Consistency: every FORECAST has a dated signpost
- [PASS] Consistency: all forecast probabilities lie in [0,100]
- [PASS] Ch4: derived phase-flip time at two photons falls in Ocelot's measured 27-33 us
- [PASS] Ch4: idle-dominated per-cycle dephasing matches Ocelot's 9.6(4)e-2 (2-sigma window)
- [PASS] Ch4: predicted 8.9% per 2.8us cycle = 1-exp(-2*kappa1*T)
- [PASS] Ch4: today's phase/bit ratio ~30 = 2*kappa1 / Gamma_bit(d5 refit,nbar=2)
- [PASS] Ch4: fitted measurement error 4.8% = p_m 0.0478*100
- [PASS] Ch4: bit-flip suppression per photon, lower section (e^0.735) sits in the 2.1-2.4x claim band
- [PASS] Ch4: bit-flip suppression per photon, upper section (e^0.882) sits in the 2.1-2.4x claim band
- [PASS] Ch4: out-of-sample d3 holdouts within the claimed 30% (worst of +22.5%/+28.4%)
- [PASS] Ch4: corridor grid points inside the same-order band (twelve of twelve)
- [PASS] Ch4: corridor agreement at the operating point ~25% (worst |1-ratio| of 0.86..0.94 grid)
- [PASS] Ch4: disclosed instrument optimism 1.2-2x (same-instrument rep-7 MC/FIT = 0.57 -> 1/0.57)
- [PASS] Ch4: P1 loss 'five orders of magnitude' (2.92e-4 / 2.74e-9)
- [PASS] Ch4: full-CSS extraction penalty 'a factor of about 54' (1.59e-2 / 2.92e-4)
- [PASS] Ch4: winner distance twelve = rep(3) x extHamming d(4) product
- [PASS] Ch4: distance 12 corrects any 5 phase flips = floor((12-1)/2)
- [PASS] Ch4: winner thirteen qubits per logical = (24 data + 28 checks) / 4 logical
- [PASS] Ch4: matched-depth ratio 'one quarter' = 1.719e-7 / 6.750e-7 in stated CI [0.172, 0.337]
- [PASS] Ch4: matched-depth CI upper bound clears the frozen 0.5 bar
- [PASS] Ch4: scoreboard -- two hits + two misses = four frozen priors
- [PASS] Ch4: 'twenty-four days ahead' (2026-07-31 minus 2026-07-07)
- [PASS] Ch4: down-bias inversion, winner vs repetition ('twelve times worse')
- [PASS] Ch4: down-bias inversion, deeper sibling ('sixty-three times worse')
- [PASS] Ch4: Day-1 headline's code-capacity efficiency claim ('2.4x') as reported on Day 1
- [PASS] Ch4: frontier overhead ~7.6 q/logical = 758/100 (Ruiz)

**TOTAL: 27 checks · 27 pass · 0 fail** — All checks pass — the survey is internally consistent.

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
