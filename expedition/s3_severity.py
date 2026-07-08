#!/usr/bin/env python3
"""s3_severity.py -- Campaign 1, stage S3: the severity map (campaign closer).

PREREG governs. Standing rule from E8: every cross-code comparison is
depth-matched (16 rounds) on the same instrument. Legs:

  L1  GM decade map: winner [24,4,12] vs rep-7, and [40,4,20] vs rep-13,
      at kappa_1/kappa_2 = 1e-3 (all measurable there). The 1e-4 values for
      [40,4,20]/rep-13 remain the S2 labeled bound (rep-13 at 1e-4 sits at
      ~1.6e-10 -- not measurable at any sane shot budget; stated, not hidden).
  L2  Ocelot nbar axis for the winner vs rep-7: nbar in {1.0, 1.5, 2.0, 2.5,
      3.0}; Gamma_Z = nbar*kappa_1; Gamma_X(nbar) from the measured d5-section
      refit at 1.0/1.5/2.0 and k-extrapolated (k = 0.735/nbar, measured) at
      2.5/3.0 -- inside the D5 saturation cap, extrapolation LABELED.
      X-only architectures carry NO bit protection, so the bit floor is
      analytic and exact for independent flips: per-logical per-cycle
      bit floor = (n_data/k) * (1 - exp(-Gamma_X * T_CYCLE)). Totals reported.
  L3  P4 assessment data: family scaling (q/log vs d for rep-a (x) extHam8)
      plus the measured points -- the inputs P4's resolution needs.

Adjudication of P3 (final leaderboard) and P4 happens in the strategy room
after this output closes the campaign.
"""
import sys, time, math
sys.path.insert(0, ".")
import numpy as np
from s2_seeds import product_code, rep_H, ext_hamming8, seed_stats
from gm_css import fom
from gm_corridor import ruiz_fit
from evaluator_v1 import Noise, logical_rate, per_round, phase_rep
from s1_referee import ocelot_circuit

KAPPA1 = 1.667e4
T_CYCLE = 2.8e-6
GX_MEASURED = {1.0: 2890.0, 1.5: 1571.0, 2.0: 1051.0}   # d5-section refit [DERIV v1.1]
K_D5 = 0.735                                             # measured scale [DERIV v1.1]

def gx_of(nbar):
    if nbar in GX_MEASURED: return GX_MEASURED[nbar], "measured"
    return GX_MEASURED[2.0] * math.exp(-K_D5 * (nbar - 2.0)), "k-extrapolated"

if __name__ == "__main__":
    W24 = product_code(rep_H(3), ext_hamming8())
    W40 = product_code(rep_H(5), ext_hamming8())
    for H, want in ((W24, (24, 4, 12, 4)), (W40, (40, 4, 20, 4))):
        s = seed_stats(H)
        assert (s["n"], s["k"], s["d"], s["w"]) == want, s
    Hz24 = np.zeros((0, 24), dtype=np.uint8); Hz40 = np.zeros((0, 40), dtype=np.uint8)

    print("S3 -- SEVERITY MAP (depth-matched 16 rounds throughout, per the E8 rule)")
    print("\nL1 -- GM decade kappa_1/kappa_2 = 1e-3 (p_m = 6e-3 assumption unchanged)")
    pairs = [("[24,4,12]", W24, Hz24, 4, 400000, "rep-7", phase_rep(7), 2000000),
             ("[40,4,20]", W40, Hz40, 4, 400000, "rep-13", phase_rep(13), 2000000)]
    for cname, Hc, Hzc, k, cshots, rname, (Hr, Hzr), rshots in pairs:
        t0 = time.time()
        pkc, pac, _, _ = fom(Hc, Hzc, k, 16, 6e-3, 11.0, 1e-3, "xonly", cshots, seed=391)
        pkr, par, _, _ = fom(Hr, Hzr, 1, 16, 6e-3, 11.0, 1e-3, "xonly", rshots,
                             seed=391, decoder="pymatching")
        fc, fr = int(round(pac * cshots)), int(round(par * rshots))
        ratio = pkc / pkr if pkr > 0 else float("inf")
        h = 1.96 * math.sqrt(1.0 / max(fc, 1) + 1.0 / max(fr, 1))
        print(f"  {cname} eps={pkc:.3e} (fails={fc}) vs {rname} eps={pkr:.3e} "
              f"(fails={fr}) -> ratio={ratio:.3f} CI [{ratio*(1-h):.3f}, {ratio*(1+h):.3f}] "
              f"[{time.time()-t0:.0f}s]")
    print("  (1e-4 for [40,4,20]/rep-13: NOT measurable at sane budgets; the S2 "
          "labeled upper bound stands. rep-13 FIT there = %.2e.)" % ruiz_fit(13))

    print("\nL2 -- Ocelot nbar axis: winner [24,4,12] vs rep-7 (transmon mode, "
          "FITTED p_m=0.0478, 6 rounds phase-decode; bit floor analytic, X-only)")
    print(f"  {'nbar':>5} {'Gx(/s)':>8} {'src':<14} | {'win phase':>10} {'win bitfl':>10} "
          f"{'win TOTAL':>10} | {'rep7 phase':>10} {'rep7 bitfl':>10} {'rep7 TOTAL':>10}")
    for nbar in (1.0, 1.5, 2.0, 2.5, 3.0):
        gx, src = gx_of(nbar)
        nz = Noise(mode="transmon", p_m=0.0478, gamma_z=nbar * KAPPA1, gamma_x=gx)
        row = []
        for nm, Hc, Hzc, k, ndata in (("win", W24, Hz24, 4, 24), ("rep7", *phase_rep(7), 1, 7)):
            c = ocelot_circuit(Hc, Hzc, 6, nz, "X")
            pa = logical_rate(c, 20000, seed=395,
                              decoder="pymatching" if nm == "rep7" else "bposd")
            ph = per_round(1 - (1 - pa) ** (1.0 / k), 6)
            bf = (ndata / k) * (1 - math.exp(-gx * T_CYCLE))
            row.append((ph, bf, ph + bf))
        print(f"  {nbar:>5.1f} {gx:>8.0f} {src:<14} | {row[0][0]:>10.3e} {row[0][1]:>10.3e} "
              f"{row[0][2]:>10.3e} | {row[1][0]:>10.3e} {row[1][1]:>10.3e} {row[1][2]:>10.3e}")
    print("  NOTE: rep-7's phase column is decoded protection; BOTH architectures "
          "are X-only here, so both bit floors are unprotected and analytic.")

    print("\nL3 -- P4 assessment data (family scaling, rep-a (x) extHam8, w<=4):")
    for a in (3, 5, 7):
        Hp = product_code(rep_H(a), ext_hamming8())
        sp = seed_stats(Hp)
        print(f"  a={a}: [{sp['n']},{sp['k']},{sp['d']}] q/log={sp['qlog']:.1f}")
    print("  q/log GROWS with distance in this family (13.0 at d=12); P4 requires "
          "<= 10 q/log at eps <= 1e-8. Measured: [24,4,12] at 1e-4 = 1.72e-7 at "
          "13 q/log. No campaign output reaches the P4 operating point; any "
          "extrapolation beyond measured points would be labeled, and none helps.")

    print("\nS3 complete -- campaign data closed. P3 (final leaderboard) and P4 "
          "adjudication happen in the strategy room; hits and misses both publish.")
