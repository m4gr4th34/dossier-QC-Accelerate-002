An Open Dossier · **QC-Accelerate-002**

# Accelerating Quantum Computing Research Using AI and Robotics

*Irfan Ali-Khan — Independent Researcher*

**Chapter 2 — What works, what loops, what looms.** *Robots have worked in labs for forty years; that is not news. The news is the closed loop — AI chooses the experiment, machines run it, results steer the next one, around the clock. This chapter maps where that already works in quantum computing, where it is half-built, what it would take to close the loop on qubits themselves — and the doors no amount of iteration can open. Every label below is exactly as strong as its evidence.*

## Avenues

| Avenue | Thesis | Status | Forecast | Sources |
|---|---|---|---|---|
| The control layer — reading errors, tuning gates | Neural decoders read the surface code in real time; learned pulses tune real hardware. AI is production machinery in today's quantum stack. | ESTABLISHED | — | alphaqubit, baum |
| The design layer — codes by search | Reinforcement learning discovers error-correcting codes from scratch against the Knill-Laflamme conditions. Search works — and every novelty claim must clear an already-crowded field. | ESTABLISHED | — | olle |
| The screening loop — wafers through a cold funnel | Cryogenic 300-mm probers test hundreds of spin-qubit devices per wafer at 1.6 K, feeding yield statistics straight back into fabrication. The measure-half of the loop, industrialized. | ESTABLISHED | — | neyens |
| Self-driving labs — closed loops, open questions | Mobile robot chemists run AI-planned campaigns for days unattended — in general materials, not yet on qubits. The flagship's novelty claims were formally corrected in Nature; the label here is the lesson. | REPORTED | — | burger, alab |
| The closed loop on qubit metrics | Join the halves: AI chooses, robots run, coherence numbers steer. The bet is that this compounds into the qubit pipeline. | FORECAST | ~65% by a closed-loop AI+robotic system credited with a materials or device advance adopted by a leading qubit platform — discovered by the loop, not merely verified by it, by 2031 | burger, neyens |
| The dissolving lab | Server farms do the theory; robots run the bench; the human job becomes understanding what the machines report. | FORECAST | ~40% by a peer-reviewed quantum-hardware result whose author-contribution statement credits no human with performing the experiment, by 2033 | — |
| The conceptual gates | Whether Majorana qubits exist is a physics question no loop speed settles. The doors iteration cannot open are the survey's honest boundary. | OPEN-UNVERIFIED | — | majorana |

**THE CHAPTER · THE ARGUMENT**

## 01 WHAT ALREADY WORKS

Start with the floor of documented fact. Google's AlphaQubit decodes the surface code (The workhorse error-correcting code of superconducting quantum computing: qubits on a grid, errors caught by repeatedly measuring their neighbors. Decoding those measurements fast enough is a live engineering race.) with a neural network — and its successor does it in real time, under a microsecond per round [Bausch et al. 2024]. Learned control pulses design error-robust gates on real superconducting hardware, beating the human-default pulses and staying calibrated for weeks [Baum et al. 2021]. And reinforcement-learning agents discover error-correcting codes from scratch, scored against the Knill-Laflamme conditions (The algebraic test a set of quantum states must pass to form a valid error-correcting code. Score candidates against it and code design becomes a search problem — which is exactly what the learning agents do.) [Olle et al. 2024]. Reading errors, driving gates, designing codes — AI is in production on three floors of the stack. One discipline before going further: this field is crowded. Automated code search is a populated subfield, and fault tolerance as a phase of matter is decades deep. Any claim of novelty must clear that thicket first; this survey claims none.

## 02 THE THREE RUNGS

Robotics in science is not news — motorized stages, liquid handlers, and fab lines have run for forty years. A robot executing a human's protocol is automation: rung one, prior art by construction. Rung two is the partial loop, and quantum computing already lives there: calibration software closes a loop on live hardware with no arms at all, and cryogenic probers close the measurement half at industrial scale. Rung three is the closed loop — AI chooses the next experiment, machines run it, the result steers the choice after that, and the cycle compounds at machine tempo, around the clock. Rung three is where the timeline-compression bet lives. The honest state of its evidence is the next section. Fig 1 draws the three rungs — watch where the loop waits.

*(figure: Three small-multiple loop diagrams of the decide-make-measure-learn cycle, showing who holds each station across three rungs of automation: rung one a mostly-human loop with a single machine step, rung two a partial loop where machines make and measure while humans decide and learn, and rung three a fully closed machine loop with the human moved outside the loop to interpret its results. Solid arrows run at machine tempo; dashed arrows wait for a human. — Fig 1 — The three rungs, schematically: who holds each station of the decide-make-measure-learn cycle. Solid arrows run at machine tempo; dashed arrows wait for a human. Rung two is where quantum computing lives today; rung three is the chapter’s bet — the human moves outside the loop, reading what it reports. A taxonomy diagram of this chapter’s own framework; no measured data. [schematic])*

## 03 LOOPS, HALF-CLOSED

The halves exist; the join does not. Intel's cryogenic prober measures hundreds of spin-qubit devices per wafer and feeds the statistics back into fabrication — the measure-half, industrialized [Neyens et al. 2024]. In chemistry the decide-half is proven: a mobile robotic chemist ran a days-long Bayesian-steered search and found a better photocatalyst than its starting point, unattended [Burger et al. 2020]. And the flagship of autonomous materials discovery is also the cautionary tale: the A-Lab reported 41 novel compounds in 17 unattended days — and after independent re-analysis, Nature published a formal correction: new to the prediction platform, not necessarily new to science [Szymanski et al. 2023]. No public system yet closes the full loop on qubit metrics. That gap is exactly where the landscape's boldest card places its bet.

## 04 WHERE THE LOOP WAITS

**If the closed loop is the bet, honesty owes the reader the bottlenecks — ranked, with tentative horizons.** What follows is this program's own reasoning, forecast-grade: the analysis under the landscape's dated cards, not settled fact. Fig 1's dashed arrows mark exactly where each one lives.

**Hardest: fabrication in the loop.** Self-driving labs work where the make-step is robot-shaped — liquids, furnaces, powders [Burger et al. 2020]. A qubit device is a multi-week cleanroom flow across batch tools never designed for unattended iteration, with human judgment at a dozen stations. The near path is constrained loops: fix the process, let the AI iterate only over what a recipe file can change. Tentative horizon: constrained-subspace fabrication loops in roughly three to five years; loops over general device space, sometime in the 2030s. This is the structural ceiling on how much design space any loop can actually reach.

**Second: the learning signal.** Qubit figures of merit are cruel reward functions — coherence drifts in time on a single device and varies across nominally identical ones, so crediting an improvement to the loop's chosen variable takes statistics over many devices per iteration; that is the wafer-scale prober's real significance [Neyens et al. 2024]. And a loop that characterizes its own outputs is structurally tempted to over-credit itself — the A-Lab's formal correction is the standing lesson [Szymanski et al. 2023]. A per-iteration signal trustworthy enough to credit, with independent verification built into the cycle, looks like four to seven years — and it quietly gates the other bottlenecks.

**Third: cryogenic tempo.** Real coherence lives at millikelvin, and a dilution-refrigerator cycle is days. The working answer — probe warmer, accept proxy metrics, multiplex hundreds of devices per cooldown [Neyens et al. 2024] — is already here and improving: one to three years to routine. The honest cost is that fast loops run on proxies, and the proxy-to-millikelvin correlation must itself be validated — which folds straight back into the signal problem.

**Fourth, the unglamorous one: orchestration.** Cleanroom tools, probers, refrigerators and analysis stacks were never built to talk to each other, and a loop is only as autonomous as its least scriptable instrument. This is engineering, not physics — the self-driving-lab field solved its version with standard lab-robot interfaces — but someone has to do it for the cryogenic stack: call it two to four years of integration work nobody will write a paper about.

**Compound the four and the landscape's card prices itself.** A loop credibly credited with an adopted advance by 2031 threads constrained fabrication, statistics-heavy proxies, and independent verification — plausible, not promised. The general dissolving-lab bet sits behind fabrication's long tail, which is why its card carries the later date and the longer odds. The next section follows that tail to its end.

## 05 THE DISSOLVING LAB

If the loop closes, the benefit compounds three ways: cycle time (the loop does not wait for humans), information per cycle (active learning (A search strategy that picks the next experiment to maximize what you learn, rather than marching through a grid. It is why an AI-steered loop can beat brute-force automation with far fewer runs.) picks the most informative next experiment, not the next grid point), and unattended hours (the loop does not sleep). Follow that curve and the laboratory changes shape — server farms run the theory programs, robots run the benches, and the scarce human skill shifts from performing the experiment to understanding what the machines report. Posted here as dated bets, not prophecy: the landscape carries both, each with a signpost a hostile referee can score.

## 06 THE DOORS THAT STAY SHUT

None of this touches the conceptual gates. Whether Majorana zero modes exist in InAs-Al devices is a physics question — the claimed readout is published, the critique arguing its diagnostic is unreliable is published, the reply is published, and the question stands open in Nature's own pages [Microsoft 2025 / Legg 2026]. No loop speed settles an existence question; iteration optimizes within a paradigm, it does not supply one. That is the lesson this program sealed in Chapter 1: an AI search handed every freedom recovered the human gate, declined the cheat, and could not move the wall [Chapter 1, v1.0.0]. Faster loops will find better answers inside known physics. The doors that stay shut are where the next chapters knock.

## Consistency checks

Results from `verification/verify_numbers.py` — the same checks the in-page console runs; CI reruns them on every commit.

- [PASS] Consistency: at least one avenue in the landscape
- [PASS] Consistency: every FORECAST has a dated signpost
- [PASS] Consistency: all forecast probabilities lie in [0,100]

**TOTAL: 3 checks · 3 pass · 0 fail** — All checks pass — the survey is internally consistent.

## References

- **Bausch et al. 2024** — Bausch et al. (2024). AlphaQubit: a transformer neural network that decodes the surface code, beating state-of-the-art decoders on Google's real Sycamore data; its 2025 successor decodes in real time, under a microsecond per round, to distance 11 (arXiv 2512.07737). *Nature 635, 834-840 (2024), DOI 10.1038/s41586-024-08148-8*

- **Baum et al. 2021** — Baum et al. (2021). Deep reinforcement learning designed an error-robust universal gate set directly on a real superconducting processor — learned single-qubit gates up to 3x faster than the default DRAG pulses, staying robust for weeks without recalibration. *PRX Quantum 2, 040324 (2021), DOI 10.1103/PRXQuantum.2.040324*

- **Olle et al. 2024** — Olle, Zen, Puviani & Marquardt (2024). A reinforcement-learning agent discovers quantum error-correcting codes and their encoding circuits from scratch, scored against the Knill-Laflamme conditions — one entry in an already-populated subfield of automated code search. *npj Quantum Information (2024), arXiv 2311.04750*

- **Neyens et al. 2024** — Neyens et al. (2024). Intel's cryogenic 300-mm wafer prober measured hundreds of industry-manufactured silicon spin-qubit devices at 1.6 K, feeding statistical yield data back into CMOS-compatible fabrication — the measurement bottleneck, industrialized. *Nature (2024), arXiv 2307.04812*

- **Burger et al. 2020** — Burger et al. (2020). A mobile robot autonomously operated a wet-chemistry lab, running a days-long Bayesian-steered photocatalyst search far faster than a human team; 2024 successors from the same group do exploratory synthesis unattended (Dai et al., Nature 635, 890). *Nature 583, 237-241 (2020), DOI 10.1038/s41586-020-2442-2*

- **Szymanski et al. 2023** — Szymanski et al. (2023; corrected 2026). The A-Lab ran 17 days of autonomous solid-state synthesis and reported 41 novel compounds — after independent re-analysis (Leeman et al., ChemRxiv 10.26434/chemrxiv-2024-5p9j4), Nature published a formal correction: novel meant new to the prediction platform, not necessarily new to science. *Nature 624, 86-91 (2023), DOI 10.1038/s41586-023-06734-w; correction: Nature 650, E1 (2026), DOI 10.1038/s41586-025-09992-y*

- **Microsoft 2025 / Legg 2026** — Microsoft Azure Quantum (2025); Legg (2026). Microsoft's interferometric parity readout in InAs-Al devices is the claimed foundation of a topological qubit; a formally published critique argues the gap diagnostic is unreliable and the core findings should be revisited, with a Reply alongside (DOI 10.1038/s41586-026-10568-7). The existence question is open in Nature's own pages. *Nature 638, 651-655 (2025); critique: Nature (2026), DOI 10.1038/s41586-026-10567-8*

- **Chapter 1, v1.0.0** — This dossier — Chapter 1 (v1.0.0, sealed 2026-07-06). The recap bridge: the cat-qubit floor, the bias-preserving-gate wall, and the kept negative — an AI search handed every freedom recovered the human gate and drove the bias-breaking knob to zero. *github.com/m4gr4th34/dossier-QC-Accelerate-002 @ v1.0.0, OpenTimestamped — not DOI-archived*
