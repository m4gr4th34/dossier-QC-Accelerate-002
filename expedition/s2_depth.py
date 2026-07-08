#!/usr/bin/env python3
"""s2_depth.py -- Campaign 1: matched-depth decisive leg for P2.

Ledger E8 (recorded in the NOTEBOOK before this run): the re-check's R3 leg
compared the 16-round candidate against the 8-round rep-7 (R5). Finite-depth
memory experiments are flattered by their deterministic boundaries, so short
runs read LOW per-round for BOTH codes; a cross-depth ratio is therefore
biased AGAINST the deeper-measured code. The arena's 0.155 was depth-matched
(both 8 rounds) and fair; R3's 0.479 was not. This leg closes E8 by measuring
BOTH codes at 16 rounds on the same instrument, same fresh seed.

Design: candidate rep3(x)extHam8 [24,4,12] at 16 rounds, 4e6 shots (BP-OSD);
rep-7 at 16 rounds, 2e7 shots (pymatching); plus rep-7 at 8 rounds, 2e7 shots
to EXHIBIT the boundary-effect factor on the comparator itself. Poisson CIs
propagated to the ratio. Verdict vs P2's 0.5 bar; adjudication is the
strategy room's.
"""
import sys, time, math
sys.path.insert(0, ".")
import numpy as np
from s2_seeds import product_code, rep_H, ext_hamming8, seed_stats
from gm_css import fom
from gm_corridor import ruiz_fit
from evaluator_v1 import phase_rep

GM = dict(nbar=11.0, k_ratio=1e-4, p_m=6e-3)

def ci95(fails):
    if fails == 0: return (0.0, 3.0)
    h = 1.96 / math.sqrt(fails)
    return (max(1 - h, 0.0), 1 + h)

if __name__ == "__main__":
    Hc = product_code(rep_H(3), ext_hamming8())
    s = seed_stats(Hc)
    assert (s["n"], s["k"], s["d"], s["w"]) == (24, 4, 12, 4), s
    Hz = np.zeros((0, 24), dtype=np.uint8)
    print("MATCHED-DEPTH LEG (E8 closure): both codes at 16 rounds, same instrument, seed 291")

    t0 = time.time()
    pkc, pac, _, _ = fom(Hc, Hz, 4, 16, GM["p_m"], GM["nbar"], GM["k_ratio"],
                         "xonly", 4000000, seed=291)
    fc = int(round(pac * 4000000))
    print(f"candidate [24,4,12] 16r: eps={pkc:.3e} (fails={fc}/4e6) [{time.time()-t0:.0f}s]")

    t0 = time.time()
    pk8, pa8, _, _ = fom(*phase_rep(7), 1, 8, GM["p_m"], GM["nbar"], GM["k_ratio"],
                         "xonly", 20000000, seed=291, decoder="pymatching")
    f8 = int(round(pa8 * 20000000))
    t1 = time.time()
    pk16, pa16, _, _ = fom(*phase_rep(7), 1, 16, GM["p_m"], GM["nbar"], GM["k_ratio"],
                           "xonly", 20000000, seed=291, decoder="pymatching")
    f16 = int(round(pa16 * 20000000))
    print(f"rep-7  8r: eps={pk8:.3e} (fails={f8}/2e7) [{t1-t0:.0f}s]   "
          f"16r: eps={pk16:.3e} (fails={f16}/2e7) [{time.time()-t1:.0f}s]")
    print(f"boundary-effect factor on comparator: rep-7 16r/8r = {pk16/pk8:.2f} "
          f"(candidate's own was ~1.55 across the same depths)")

    ratio = pkc / pk16 if pk16 > 0 else float("inf")
    # ratio CI from Poisson counts on both numerator and denominator
    h = 1.96 * math.sqrt((1.0 / max(fc, 1)) + (1.0 / max(f16, 1)))
    lo, hi = ratio * (1 - h), ratio * (1 + h)
    verdict = "PASS" if hi <= 0.5 else ("FAIL" if lo > 0.5 else "STRADDLES BAR")
    print(f"\nMATCHED-DEPTH RATIO (candidate/rep-7, both 16r, same instrument): "
          f"{ratio:.3f}  95% CI [{lo:.3f}, {hi:.3f}]  vs bar 0.5 -> {verdict}")
    print("Context: arena depth-matched (8r) ratio was 0.155-to-FIT / ~0.31 "
          "same-instrument; prediction recorded pre-run: ~0.3.")
    print("\nMatched-depth leg complete. P2 adjudication happens in the strategy "
          "room; hits and misses both publish.")
