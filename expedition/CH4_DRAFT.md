# Chapter 4 -- The loop eats first (REVISED DRAFT v2 -- walk-through edition)

*For author review. Equations shown in plain text here; they become rendered
math (KaTeX) in the edition. Three figures: NEW Fig 1 (the loop schematic,
described below), Fig 2 = current severity map, Fig 3 = current campaign arc
with plain-language relabeling. Every number unchanged from the committed
record; only the explanation grew.*

---

## 01 THE LOOP, AND THE CHEAP WAY TO TEST IT

Strip science to its skeleton and it is a cycle with four stations: DECIDE
what to try next, MAKE the thing, MEASURE what you made, LEARN from the
result, and go around again. Most of this dossier asks one question about
that cycle: how much of it can machines run on their own, for quantum
computing? Chapter 2 found labs where machines hold one or two stations --
robots that grow crystals, algorithms that pick growth recipes -- but nowhere
on Earth does the full circle run unattended for quantum hardware. Chapter 3
bet money-where-mouth-is percentages on where it will close first.

This chapter does something more direct: it runs the loop. Not on hardware --
we own no lab -- but on the one problem in quantum computing where the MAKE
station is free, because making the thing means simulating it. That problem
is the search for error-correcting codes. Here is the whole loop, concretely,
station by station (Fig 1):

- **DECIDE** -- an AI drafts a candidate code. A code, as Section 02 explains,
  is literally a small grid of 0s and 1s, so a draft is cheap to write down.
- **MAKE** -- software builds the full error-correction machine that code
  implies: the qubits, the helper qubits, every gate and measurement,
  repeated cycle after cycle. This is the free fabrication step.
- **MEASURE** -- the simulator injects random errors at rates copied from a
  real, published chip, millions of runs per candidate, and a decoding
  algorithm tries to catch every error. Each time the decoder loses the
  stored information, that is one logical failure. Count them.
- **LEARN** -- compare the failure rate against the boring baseline everyone
  already uses. Keep the winners, kill the losers, and -- this matters --
  write down WHY each loser lost, so the next DECIDE is smarter.

One more discipline, borrowed from clinical medicine: before the loop ran at
all, we wrote four predictions about how it would go, attached a probability
to each, and committed them to a public, cryptographically timestamped
record. Pre-registration means nobody -- including us -- can quietly move the
goalposts after seeing the results. Two of the four predictions came true.
The other two are published at the same size as the wins. And one boundary,
stated up front: this chapter does not score Chapter 3's hardware bets; those
resolve on their own dates against the outside world.

*(NEW Fig 1 -- the loop schematic: five labeled stations in a ring --
PROPOSE / VERIFY / SIMULATE / SCORE / LEARN -- each with a one-line concrete
description; an annotation on VERIFY marking "the kill happened here" and on
SCORE marking "the win happened here". Static, no data.)*

## 02 THE GAME: WHAT A CODE IS, AND WHAT KILLS ONE

A qubit is a physical object that stores quantum information, and physical
objects forget. Quantum information can be corrupted in two distinct ways: a
**bit flip** (the 0-part and 1-part of the state swap) and a **phase flip**
(the sign between them silently reverses). Both are lethal to a computation;
a useful quantum memory has to survive both.

The oldest trick against forgetting is repetition. Store a classical bit
three times -- 000 or 111 -- and if one copy flips, majority vote restores it.
Quantum mechanics forbids the obvious version of this (you cannot copy a
qubit, and looking at one directly destroys it), but it permits something
subtler: you can ask a group of qubits a **parity question** -- "do qubits 1
and 2 currently agree?" -- without asking what either one holds. Helper
qubits (ancillas) extract these parities, one gate at a time. A pattern of
disagreements is a fingerprint; a decoding algorithm reads the fingerprint
and infers which qubit flipped. That is quantum error correction: parity
questions, asked over and over, forever.

A **code** is a recipe for which parity questions to ask. It is written as a
grid of 0s and 1s -- each row one parity check, each column one qubit, a 1
where check touches qubit. Three numbers grade the recipe, written [n, k, d]:
n physical qubits store k logical (useful) qubits, and the distance d says
how much abuse the code survives -- any combination of up to floor((d-1)/2)
simultaneous errors is corrected with certainty. Repetition on n qubits is
the code [n, 1, n]: superb protection, terrible economy -- one useful qubit
no matter how many you spend. The entire craft of code design is buying more
k per n without letting d collapse.

Now the hardware this chapter searches for. **Cat qubits** -- the technology
of Amazon's Ocelot chip, and the lineage this dossier has tracked since
Chapter 1 -- store a qubit in two laser-like states of a microwave cavity.
Their signature property, the reason anyone tolerates their complexity, is
lopsided noise. Make the cat "bigger" (more photons, n-bar) and bit flips
become exponentially rare while phase flips get only modestly worse:

    Gamma_bit ~ e^(-2.nbar)          (bit flips: exponentially suppressed -- eq. 1, the same law as Chapter 1)
    Gamma_phase = nbar . kappa_1     (phase flips: linearly worse -- eq. 2)

where kappa_1 is the cavity's photon-loss rate. At the sizes Ocelot runs,
bit flips happen thousands of times less often than phase flips. So the code
mostly has one job -- catch phase flips -- and it can be lighter and cheaper
than a code fighting both enemies at once.

Here is the seam this chapter lives on. Checking parities is itself physical
work: gates, helper qubits, measurements -- and every one of those can fail.
There are two honesty grades for evaluating a code. **Code capacity** grade:
pretend the checking machinery is perfect and only the stored qubits err --
cheap to simulate, flattering to clever codes. **Circuit level** grade: every
gate, every helper, every measurement fails at its own measured rate -- slow,
unflattering, honest. When we checked the literature, sentence by sentence,
every AI-driven code search ever published grades itself at code capacity
[CITE cards: Nautrup 2019; Olle 2024 -- "the encoding circuit is assumed to
be error-free," their words; He & Liu 2025; the 2026 LLM flurry -- IBM's
Cruz-Benito et al.; Liu & Marquardt -- "code-capacity depolarizing noise,"
their words; BayesOpt 2026]. Meanwhile, the one group that graded
bias-tailored codes at circuit level found the flattery evaporates -- "the
substantial advantages predicted... under code-capacity noise are strongly
reduced" [CITE: Benito 2026] -- but nobody runs a SEARCH at that grade. AI
search exists. Honest grading exists. The intersection was empty. This
chapter fills it.

## 03 THE SIMULATION, EXACTLY

What one "measurement" in our loop actually is, start to finish:

Build a circuit: n cat qubits prepared in a known state; each cycle, helper
qubits ask every parity question in the code's grid (one two-qubit gate per
1 in the grid), then get measured and reset; 8 to 16 cycles; a final readout
of every qubit. Then poison it: at every location in that circuit -- every
idle moment, every gate, every measurement -- flip a biased coin, and with
the appropriate probability insert an error. Run the poisoned circuit
millions of times (it is a stabilizer circuit, so a classical computer can
simulate it exactly -- this is the standard "stim" framework). Hand each
run's parity fingerprints to a decoder -- belief propagation with
ordered-statistics post-processing, the field's workhorse -- which guesses
the errors and undoes them. Count the runs where the guess was wrong in a
way that corrupted the stored information. Divide. That is epsilon_L, the
logical failure rate per cycle per stored qubit: the one number a memory is
graded on.

Every coin's bias comes from a real place, and this is the part we are most
careful about. The probability of an error over a time t follows from a rate:

    p(t) = 1 - e^(-Gamma.t)          (eq. 3)

and each rate traces to Amazon's published Ocelot results [CITE: Putterman
2025] or their released raw data:

- **Phase flips.** The photon-loss rate is kappa_1 = 1/(60 microseconds),
  from the paper's storage lifetime. Equation 2 then PREDICTS the phase-flip
  time at cat size nbar = 2: 1/(2.kappa_1) = 30 microseconds. Amazon
  measured 27-33. It also predicts the phase-error probability per 2.8
  microsecond correction cycle: 8.9%. Amazon measured 9.6 +/- 0.4%. Two
  independent bullseyes from one number we did not tune -- that closure is
  what licensed the model.
- **Bit flips.** Re-fitted from Amazon's released shot-level data (their
  Zenodo archive), using their own fitting convention: suppression grows
  2.1-2.4x per added photon, saturating above nbar ~= 3. Measured, not
  assumed.
- **Measurement errors.** The one number we could not derive: how often a
  parity readout simply lies. We fit it -- 4.8% -- against exactly one
  published number (the distance-5 result, 1.65% per cycle) and then tested
  the fitted model against two other published numbers it had never seen.
  Both landed within 30%. One fitted parameter, honestly labeled, tested
  out-of-sample.
- **Gates in the high-bias regime.** For the future-hardware operating
  point, the gate error model comes from the founding cat-qubit theory paper
  [CITE: Guillaud & Mirrahimi 2019]. Its key term -- the price of a two-qubit
  gate of duration T on a cat of size nbar, with two-photon stabilization
  rate kappa_2:

      p_Z(control) = nbar.kappa_1.T + 1/(2.pi.nbar.kappa_2.T)     (eq. 4)

  The first term is ordinary decay; the second is the gate's own quantum
  clumsiness (a non-adiabatic error -- rushing the gate costs accuracy). At
  the frontier operating point this second term dominates everything else,
  which is exactly why lazy grading flatters and honest grading kills.

Final calibration check: we pointed the finished instrument at a code family
another group had already simulated with independent methods [CITE: Ruiz
2025] and compared curves at twelve grid points. All twelve within the
agreement band; at the main operating point, within +/-25%. The instrument's
two known flaws are printed on it: it reads 1.2-2x optimistic in absolute
terms (so all conclusions use same-instrument ratios, where the optimism
cancels), and short simulations flatter every code near their start and end
(so every comparison runs both codes at matched depth -- a rule we adopted
after this exact effect nearly produced a wrong verdict, and we caught it).

## 04 THE CAMPAIGN: FOUR BETS, ONE KILL, ONE WIN

The four pre-registered bets, in plain words, with what happened:

**Bet 1 (35%): "Day 1's discovery is real."** On Day 1, under the cheap
code-capacity grading, the search had found a hypergraph-product code that
looked 2.4x more qubit-efficient than anything comparable. Bet 1 said it
would survive honest grading. It did not -- it lost to plain repetition by a
factor of one hundred thousand. The autopsy is instructive: that code needs
BOTH kinds of parity checks, and under cat-qubit gate physics the second
kind (bit-flip checks) puts its worst errors directly onto the stored
qubits -- a ~54x penalty -- to guard against bit flips that equation 1 had
already made a thousand times rarer than the checks' own cost. Paying 54x to
insure against almost-nothing. At high bias you check phase only, which is
exactly the architecture the frontier proposal already uses [CITE: Ruiz
2025]. MISS, published, lesson banked.

**Bet 2 (55%): "the search will beat repetition anyway."** The first family
the AI proposed for the honest-grading campaign died before a single
simulation: the mechanical verifier -- the algebra station of the loop --
proved in one line that the family had a hidden ceiling (its error-survival
could never exceed d = 4, no matter the size). This is the loop working, not
failing: the kill was cheap, immediate, and explained. The repair bred the
winner: take 3x repetition, cross it with a classic 8-bit code (the extended
Hamming code -- four parity checks, each touching four qubits), and the
product is a [24, 4, 12] code: 24 cat qubits storing 4 logical qubits -- 13
per logical including helpers -- surviving any 5 simultaneous phase flips.
At the frontier operating point, graded honestly, depth-matched, same
instrument, it fails at ONE QUARTER the rate of budget-matched repetition
(ratio 0.255; 95% confidence interval 0.17-0.34). Then we tried to kill it
three ways -- fresh random seeds, a stronger decoder, doubled circuit depth
-- and it survived all three. HIT. One label rides with it everywhere: this
is a result about a validated model of hardware, not about hardware.

**Bet 3 (40%): "the AI's own proposal reaches the podium."** It did -- the
winner IS the AI-layer proposal, with the footnote printed at equal size:
the proposing agent and the strategy running this dossier are the same
system, refereed by its own mechanical verifier, and the win only exists
because the verifier killed the first attempt. HIT, footnotes attached.

**Bet 4 (20%): "match the frontier's overhead."** The published frontier
architecture achieves about 7.6 qubits per logical at error rates of one in
a hundred million [CITE: Ruiz 2025]. Bet 4 asked our weight-limited search
to match that. Nothing came close -- the winning family's overhead GROWS with
protection, the wrong direction entirely. MISS: the stretch was a stretch.

*(Fig 3 -- the campaign arc, relabeled: subtitle now reads "read left to
right: each bet starts hollow with its pre-registered probability, and ends
filled -- green if it came true, coral if it did not.")*

## 05 THE MAP, AND WHAT A LOOP IS GOOD FOR

Put the win under a moving spotlight and the chapter's real finding appears
(Fig 2, the severity map). Make the gates ten times dirtier and the winner
doesn't merely shrink -- it inverts, losing 12x to repetition (its deeper
sibling, 63x): sophisticated codes drown FIRST when the checking machinery
degrades, because they lean on it hardest. Move to today's actual measured
hardware and neither code matters: both drown in unprotected bit flips at
percent-per-cycle rates, because at today's cat sizes equation 1 has not yet
pushed bit flips low enough to ignore. Only at the future high-bias
operating point -- the regime the search was aimed at -- does the win exist.
Codes are like tires: the racing slick that wins on a dry track loses on
gravel and kills you on ice. A code search that does not know what weather
it is designing for will win the wrong race. That is this dossier's
science-versus-scale-up spine, measured three ways inside one chapter.

So what is an AI-driven discovery loop actually good for, today, on this
evidence? It can build its own honest referee from published data -- the
calibration chain above is machine work end to end. It can propose, be
refuted, and grow from the refutation -- the winner is literally made of its
predecessor's autopsy. It can produce a real, checkable, model-level result
at the field's own frontier operating point. What it cannot do is skip the
expensive referee: every cheap-grade promise this campaign tested shrank or
died under honest grading, matching what the field's own frontier reports
[CITE: Benito 2026]. And it catches its own mistakes: nine errors made
building all this -- a misread definition, a biased fit, a one-character
drift in our own file-transfer machinery -- every one caught by a discipline
built for exactly that failure, every one published with credit to its
catcher. The nine dots at the bottom of Fig 3 are not decoration; they are
the chapter's second result. A loop that cannot catch its own errors cannot
be trusted to catch nature's.

Three new bets go on the board, hollow until scored: someone publishes a
low-weight cat code matching the frontier's overhead by end of 2027 (30%);
an outside group runs an AI code search under honest circuit-level grading
by mid-2027 (55%); someone demonstrates a multi-logical cat code on real
hardware by end of 2028 (25%). Misses will publish like hits. They always
do here.

---

## Build notes (not part of the chapter)

- NEW Fig 1: qc-degenloop schematic (5 stations, concrete labels, kill/win
  annotations). Fig 2 = existing severity map (unchanged). Fig 3 = existing
  campaign arc with the new "how to read this" subtitle.
- Equations 1-4 as data-tex display math (KaTeX; eq. 1 deliberately echoes
  Chapter 1's eq. 1 -- same law, same lineage).
- New verify_numbers mirrors: 1/(2.kappa_1) = 30 us; 54x penalty; 1e5 ratio;
  floor((12-1)/2) = 5 corrected errors; 13 q/logical; 0.255 CI -- most
  already exist from v1; adds: corrected-errors=5 check.
- Cite cards unchanged (all 11 verified); Olle/Liu-Marquardt/Benito verbatim
  quotes now carried IN prose where the seam claim is made.
- All existing numbers unchanged; label discipline unchanged; the fluff is
  gone because the mechanism is now on the page.
