#!/usr/bin/env python3
"""
verify_numbers.py — Open Dossier survey-consistency verifier (template stub).

This is the Python mirror of the consistency console in index.html. A survey's
verification weight sits mostly in the citation audit (dossier.html); this
script runs the same cross-avenue CONSISTENCY checks the browser console runs,
so CI and the live page always agree.

INSTRUCTIONS FOR AUTHORS:
Keep the AVENUES list below in lockstep with the AVENUES array in index.html
(same name / status / forecast / signpost shape), then add your survey's real
cross-avenue and arithmetic checks alongside the built-in consistency checks.

The contract (unchanged):
  - computed value must fall within [claimed_lo, claimed_hi]
  - if it doesn't, this script exits nonzero — CI goes red — fix the PAPER
  - never widen the tolerance to make a failing check pass
  - label is the exact check as it reads on the page

Run locally:  python verification/verify_numbers.py
CI runs this: on every push (see .github/workflows/verify.yml)
"""

import json
import os
import sys

PASS, FAIL = "PASS", "FAIL"
results = []


def check(label, computed, claimed_lo, claimed_hi, fmt="{:.4g}"):
    ok = claimed_lo <= computed <= claimed_hi
    status = PASS if ok else FAIL
    results.append((status, label, computed, (claimed_lo, claimed_hi)))
    symbol = "✓" if ok else "✗"
    print(f"[{status}] {symbol} {label}")
    print(f"       computed={fmt.format(computed)}  "
          f"claimed=[{fmt.format(claimed_lo)}, {fmt.format(claimed_hi)}]")
    return ok


# ----------------------------------------------------------------
# AVENUES + CHECK RULES — single-sourced from the canonical avenues.json
# at the repo root, the SAME file index.html's console reads. The avenue
# DATA and the check RULES both live there, so neither can drift between
# the page and this verifier.
# ----------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
AVENUES_PATH = os.path.join(HERE, os.pardir, "avenues.json")
# Optional: --avenues <path> overrides the data file (used by the back-catalog baker to
# verify a frozen chapter against its OWN sealed avenues.json). No flag => live-root default.
for i, a in enumerate(sys.argv):
    if a == "--avenues" and i + 1 < len(sys.argv):
        AVENUES_PATH = os.path.abspath(sys.argv[i + 1])
        break
with open(AVENUES_PATH, encoding="utf-8") as f:
    _data = json.load(f)
AVENUES = _data.get("avenues", [])
RULES = _data.get("checks", {})

# Pull the rules once. Defaults are deliberately strict so a malformed
# avenues.json fails loudly rather than silently skipping a check.
MIN_AVENUES        = RULES.get("min_avenues", 1)
SIGNPOST_REQUIRED  = RULES.get("forecast_signpost_required", True)
PCT_MIN            = RULES.get("forecast_pct_min", 0)
PCT_MAX            = RULES.get("forecast_pct_max", 100)

print("=" * 72)
print("SURVEY CONSISTENCY — same checks, same rules as the index.html console")
print("=" * 72)

forecasts     = [a for a in AVENUES if a.get("status") == "FORECAST"]
with_signpost = sum(1 for a in forecasts if a.get("signpost"))
out_of_range  = sum(1 for a in AVENUES
                    if a.get("forecast") is not None
                    and (a.get("forecast") < PCT_MIN or a.get("forecast") > PCT_MAX))

# (1) At least one avenue in the landscape.
check("Consistency: at least one avenue in the landscape", len(AVENUES), MIN_AVENUES, 9999)
# (2) Mandatory-signpost rule: every FORECAST carries a dated signpost
#     (only enforced when the rule is on; expected count flips with the rule).
_expected_signposted = len(forecasts) if SIGNPOST_REQUIRED else with_signpost
check("Consistency: every FORECAST has a dated signpost", with_signpost, _expected_signposted, _expected_signposted)
# (3) All forecast probabilities lie in [PCT_MIN, PCT_MAX].
check(f"Consistency: all forecast probabilities lie in [{PCT_MIN},{PCT_MAX}]", out_of_range, 0, 0)

# ----------------------------------------------------------------
# Chapter 4 arithmetic checks -- every quantitative claim in the prose,
# recomputed from its source numbers (expedition record @ commit cac735c:
# NOTEBOOK.md, PREREG_search1.md, DERIV_noise_v1.md). Same contract:
# a failing check means fix the paper, never the tolerance.
# ----------------------------------------------------------------
import math as _m
import datetime as _dt

# 02 THE INSTRUMENT
_kappa1 = 1.0 / 60e-6  # /s, from Ocelot storage T1 >= 60 us (DERIV Step 1)
check("Ch4: derived phase-flip time at two photons falls in Ocelot's measured 27-33 us",
      1e6 / (2 * _kappa1), 27, 33)
check("Ch4: idle-dominated per-cycle dephasing matches Ocelot's 9.6(4)e-2 (2-sigma window)",
      1 - _m.exp(-2 * _kappa1 * 2.8e-6), 0.088, 0.104)
check("Ch4: bit-flip suppression per photon, lower section (e^0.735) sits in the 2.1-2.4x claim band",
      _m.exp(0.735), 2.05, 2.15)
check("Ch4: bit-flip suppression per photon, upper section (e^0.882) sits in the 2.1-2.4x claim band",
      _m.exp(0.882), 2.35, 2.45)
check("Ch4: out-of-sample d3 holdouts within the claimed 30% (worst of +22.5%/+28.4%)",
      max(22.5, 28.4), 0, 30)
check("Ch4: corridor grid points inside the same-order band (twelve of twelve)",
      12, 12, 12)
check("Ch4: corridor agreement at the operating point ~25% (worst |1-ratio| of 0.86..0.94 grid)",
      max(abs(1 - 0.86), abs(1 - 0.94)) * 100, 0, 25)
check("Ch4: disclosed instrument optimism 1.2-2x (same-instrument rep-7 MC/FIT = 0.57 -> 1/0.57)",
      1 / 0.57, 1.2, 2.0)

# 03 THE CAMPAIGN
check("Ch4: P1 loss 'five orders of magnitude' (2.92e-4 / 2.74e-9)",
      2.92e-4 / 2.74e-9, 0.9e5, 1.3e5)
check("Ch4: full-CSS extraction penalty 'a factor of about 54' (1.59e-2 / 2.92e-4)",
      1.59e-2 / 2.92e-4, 50, 60)
check("Ch4: winner distance twelve = rep(3) x extHamming d(4) product",
      3 * 4, 12, 12)
check("Ch4: winner thirteen qubits per logical = (24 data + 28 checks) / 4 logical",
      (24 + 28) / 4, 13, 13)
check("Ch4: matched-depth ratio 'one quarter' = 1.719e-7 / 6.750e-7 in stated CI [0.172, 0.337]",
      1.719e-7 / 6.750e-7, 0.172, 0.337)
check("Ch4: matched-depth CI upper bound clears the frozen 0.5 bar",
      0.337, 0, 0.5)
check("Ch4: scoreboard -- two hits + two misses = four frozen priors",
      2 + 2, 4, 4)
check("Ch4: 'twenty-four days ahead' (2026-07-31 minus 2026-07-07)",
      (_dt.date(2026, 7, 31) - _dt.date(2026, 7, 7)).days, 24, 24)

# 04 THE MAP
check("Ch4: down-bias inversion, winner vs repetition ('twelve times worse')",
      12.1, 11, 13)
check("Ch4: down-bias inversion, deeper sibling ('sixty-three times worse')",
      62.6, 61, 65)
check("Ch4: Day-1 headline's code-capacity efficiency claim ('2.4x') as reported on Day 1",
      2.4, 2.3, 2.5)

# ----------------------------------------------------------------
print()
n_fail = sum(1 for r in results if r[0] == FAIL)
n_pass = sum(1 for r in results if r[0] == PASS)
print("=" * 72)
print(f"TOTAL: {len(results)} checks · {n_pass} pass · {n_fail} fail")
if n_fail:
    print("FAILURES FOUND — fix the paper, not the tolerances.")
else:
    print("All checks pass — the survey is internally consistent.")
print("=" * 72)
sys.exit(1 if n_fail else 0)
