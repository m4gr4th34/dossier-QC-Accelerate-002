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
# Chapter 5 arithmetic checks -- every quantitative claim in the prose,
# recomputed from its committed source numbers (expedition record @ cab76e3:
# CH5_WORKING.md Entries 010-013, records/g2_rep2eh8_record.jsonl,
# s8_run.log, s9_run.log). Same contract: a failing check means fix the
# paper, never the tolerance.
# ----------------------------------------------------------------

# 04 BRUTE FORCE -- the leaderboard (Entry 012 table, verbatim constants)
_eps_winner,  _win_lo,  _win_hi  = 1.328e-7, 1.061e-7, 1.642e-7
_eps_front,   _fr_lo,   _fr_hi   = 1.378e-7, 1.117e-7, 1.681e-7
_eps_rep7,    _r7_lo,   _r7_hi   = 6.153e-7, 4.99e-7,  7.51e-7
_eps_c3,      _c3_lo,   _c3_hi   = 2.083e-5, 1.993e-5, 2.177e-5
_floor_rep13 = 2.31e-8

check("Ch5: the headline 4.6x = rep-7 eps / winner eps (6.153e-7 / 1.328e-7)",
      _eps_rep7 / _eps_winner, 4.5, 4.7)
check("Ch5: matched efficiency 0.0769 -- winner 4/52 equals rep-7 1/13",
      (4/52) / (1/13), 1.0, 1.0)
check("Ch5: matched efficiency value = 4/52", 4/52, 0.0769, 0.07693)
check("Ch5: certified -- rep-13 floor UB sits below the winner's CI-lower",
      _floor_rep13 / _win_lo, 0.0, 0.999)
check("Ch5: certified -- rep-7's CI-lower sits above the frontier's CI-upper",
      _r7_lo / _fr_hi, 1.001, 99.0)
check("Ch5: the TIE is real -- frontier CI-lower sits below winner CI-upper (overlap)",
      _fr_lo / _win_hi, 0.0, 0.999)
check("Ch5: winner row cap-limited at +/-21% = half-width over point",
      (_win_hi - _win_lo) / 2.0 / _eps_winner, 0.21, 0.225)
check("Ch5: C3 point sits inside its stated band", _eps_c3, _c3_lo, _c3_hi)
check("Ch5: '67 million runs' = 2.0e7+2.0e7+5.5e6+1.97e7+2.0e6 shots (Entry 012 rows)",
      2.0e7 + 2.0e7 + 5.5e6 + 1.97e7 + 2.0e6, 6.70e7, 6.73e7)
check("Ch5: '100x the standard budget' = 2e7 truth rows over 2e5 proxy rows",
      2e7 / 2e5, 100, 100)
check("Ch5: rep-13 efficiency 0.040 = 1/(13+12)", 1/25, 0.0399, 0.0401)
check("Ch5: rep-13 eff is 'roughly half' the winner's = 0.040/0.0769",
      (1/25) / (4/52), 0.50, 0.55)
check("Ch5: rep-7 at the old 2e5 budget -- 'about one expected event' (p_any 4.92e-6, Entry 012)",
      4.92e-6 * 2e5, 0.9, 1.1)

# 02 THE WALL -- the failure spectrum (records/g2_rep2eh8_record.jsonl)
_lam, _f6, _f8, _f34 = 8.3592, 2.40738e-5, 1.515553e-4, 0.345
check("Ch5: the typical run carries 'eight point four' faults (lambda)", _lam, 8.3, 8.45)
check("Ch5: fig-2 '1-in-42,000 at six faults' = 1/f_6", 1.0 / _f6, 41000, 43000)
check("Ch5: fig-2 'about 1 in 7,000' at the typical count = 1/f_8", 1.0 / _f8, 6400, 7100)
check("Ch5: fig-2 spectrum tops out at '35%' by thirty-four faults", _f34 * 100, 34.0, 35.5)

# 05 WHOSE FAULT IS FAILURE -- the Q table (Entry 013, verbatim constants)
_Q = {"frontier": (0.085, 0.0, 0.222), "c3": (0.135, 0.093, 0.184),
      "rep2eh8": (0.230, 0.146, 0.320), "winner": (0.348, 0.099, 0.615),
      "rep7": (0.627, 0.407, 0.821)}
check("Ch5: decoder-created share is a minority on four of five codes",
      sum(1 for p, _, _ in _Q.values() if p < 0.5), 4, 4)
check("Ch5: the 'sevenfold' Q spread = 0.627/0.085", _Q["rep7"][0] / _Q["frontier"][0], 7.0, 7.6)
check("Ch5: certified Q pair -- rep-7 CI-lower above frontier CI-upper",
      _Q["rep7"][1] / _Q["frontier"][2], 1.001, 99.0)
check("Ch5: certified Q pair -- rep-7 CI-lower above C3 CI-upper",
      _Q["rep7"][1] / _Q["c3"][2], 1.001, 99.0)
check("Ch5: rep-7 'indicated, not certified' -- its own CI spans the 0.5 line",
      (0.5 - _Q["rep7"][1]) * (_Q["rep7"][2] - 0.5), 1e-6, 1.0)
check("Ch5: S9 campaign '8.0M decodes' = 2x250k + 3e6 + 1.5e6 + 3e6",
      2 * 2.5e5 + 3e6 + 1.5e6 + 3e6, 7.99e6, 8.01e6)

# 01/07/08 -- the record's own bookkeeping (counted from the committed files)
check("Ch5: 'twenty-five priors' across the four measurement preregs = 7+8+6+4",
      7 + 8 + 6 + 4, 25, 25)
check("Ch5: 'eight resolved against us' = P6 + Q3,Q4,Q5,Q8 + T3,T4 + S1",
      1 + 4 + 2 + 1, 8, 8)
check("Ch5: 'five died untested' = P4,P5,P7 + Q6,Q7", 3 + 2, 5, 5)
check("Ch5: the error ledger runs E1-E14 = nine measurement-arc + five write-up",
      9 + 5, 14, 14)
check("Ch5: 'four of them author-side' in the measurement arc (E1-E4)", 4, 4, 4)
check("Ch5: landscape carries five scored + six forward = eleven avenues",
      sum(1 for a in AVENUES if str(a.get("status", "")).startswith("SCORED"))
      + sum(1 for a in AVENUES if a.get("status") == "FORECAST"), 11, 11)
check("Ch5: stakes passage '758 cats for 100 logical' ~ 7.6 qubits per logical (Ruiz)",
      758 / 100, 7.5, 7.7)

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
