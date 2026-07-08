#!/usr/bin/env python3
"""fit_pm.py -- calibration fit for the v1 evaluator's single FITTED parameter p_m.

Targets are DERIVED, decoder-independent quantities computed upstream from the
Zenodo refit + published averages (eps_phase_target = 2*eps_L_published - eps_bit_refit).
Nothing is hardcoded: all measured inputs arrive as CLI arguments so every number
in the report is produced by committed code from stated inputs.

Method: pymatching for the p_m grid (repetition codes are matchable; fast batch
decode), monotone interpolation to invert eps_phase(p_m) = target, then a BP-OSD
cross-check at the fitted p_m (the search harness's decoder). Corridor per D2:
fit outside [0.005, 0.10] -> STOP.

Usage:
  python fit_pm.py --target-d5 <eps> --gx15 <Gamma_X at nbar=1.5, /s> \
                   --target-d3a <eps> --target-d3b <eps> --gx10 <Gamma_X at nbar=1.0, /s>
All eps as per-cycle probabilities (e.g. 0.010 for 1%).
"""
import argparse
import numpy as np
from evaluator_v1 import Noise, css_memory_circuit, logical_rate, per_round, phase_rep

KAPPA1 = 1.667e4      # /s [DERIVED, DERIV Step 1]
ROUNDS = 8
SHOTS_GRID = 40000
SHOTS_XCHECK = 8000
PM_GRID = [0.005, 0.01, 0.02, 0.035, 0.05, 0.075, 0.10]

def eps_phase(d, nbar, gx, p_m, shots, seed, decoder="pymatching"):
    Hx, Hz = phase_rep(d)
    nz = Noise(mode="transmon", p_m=p_m, gamma_z=nbar * KAPPA1, gamma_x=gx)
    c = css_memory_circuit(Hx, Hz, ROUNDS, nz, basis="X")
    return per_round(logical_rate(c, shots, seed=seed, decoder=decoder), ROUNDS)

def invert(pms, epss, target):
    """Monotone linear interpolation of eps(p_m); None if target outside range."""
    pms, epss = np.asarray(pms, float), np.asarray(epss, float)
    order = np.argsort(epss)
    e_s, p_s = epss[order], pms[order]
    if not (e_s[0] <= target <= e_s[-1]):
        return None
    return float(np.interp(target, e_s, p_s))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-d5", type=float, required=True)
    ap.add_argument("--gx15", type=float, required=True)
    ap.add_argument("--target-d3a", type=float, required=True)
    ap.add_argument("--target-d3b", type=float, required=True)
    ap.add_argument("--gx10", type=float, required=True)
    a = ap.parse_args()

    print(f"FIT INPUTS: target_d5={a.target_d5:.5f} (nbar=1.5, Gx={a.gx15:.0f}/s), "
          f"targets_d3={a.target_d3a:.5f}/{a.target_d3b:.5f} (nbar=1.0, Gx={a.gx10:.0f}/s)")
    print(f"grid rounds={ROUNDS} shots={SHOTS_GRID}")

    # -- grid on d=5 at nbar=1.5 --
    epss = []
    for i, pm in enumerate(PM_GRID):
        e = eps_phase(5, 1.5, a.gx15, pm, SHOTS_GRID, seed=101 + i)
        epss.append(e)
        print(f"  p_m={pm:5.3f} -> eps_phase(d5, nbar=1.5) = {e:.5f}")
    pm_fit = invert(PM_GRID, epss, a.target_d5)
    if pm_fit is None:
        print(f"STOP: target {a.target_d5:.5f} outside reachable range "
              f"[{min(epss):.5f}, {max(epss):.5f}] -- model missing physics; adjudicate.")
        return
    print(f"FITTED p_m = {pm_fit:.4f}")
    if not (0.005 <= pm_fit <= 0.10):
        print("STOP: fitted p_m outside D2 plausibility corridor [0.005, 0.10]; adjudicate.")
        return

    # -- BP-OSD cross-check at the fitted point (search-harness decoder) --
    e_b = eps_phase(5, 1.5, a.gx15, pm_fit, SHOTS_XCHECK, seed=301, decoder="bposd")
    e_m = eps_phase(5, 1.5, a.gx15, pm_fit, SHOTS_XCHECK, seed=301, decoder="pymatching")
    print(f"cross-check at p_m={pm_fit:.4f}: bposd={e_b:.5f} matching={e_m:.5f} "
          f"(rel diff {abs(e_b-e_m)/max(e_m,1e-9):.1%})")

    # -- out-of-sample: both d=3 sections at nbar=1.0, fitted p_m untouched --
    print("OUT-OF-SAMPLE (d=3, nbar=1.0, fitted p_m):")
    e3 = eps_phase(3, 1.0, a.gx10, pm_fit, SHOTS_GRID, seed=401)
    for name, tgt in (("d3a", a.target_d3a), ("d3b", a.target_d3b)):
        rel = (e3 - tgt) / tgt
        verdict = "WITHIN +/-30%" if abs(rel) <= 0.30 else "MISS -> STOP, adjudicate"
        print(f"  predicted={e3:.5f} vs {name} target={tgt:.5f} rel={rel:+.1%}  [{verdict}]")
    print("NOTE: the evaluator cannot distinguish the two d3 sections (same code, one "
          "Gx input); their spread is device variability and bounds the honest accuracy.")

if __name__ == "__main__":
    main()
