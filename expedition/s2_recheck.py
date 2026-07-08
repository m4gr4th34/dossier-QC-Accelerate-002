#!/usr/bin/env python3
"""s2_recheck.py -- Campaign 1: adversarial re-check of the P2 candidate.

P2's frozen criterion requires the winner to SURVIVE adversarial re-check --
that clause binds P2's resolution itself, not just the >10x STOP trigger
(which correctly did not fire at ratio 0.155). Candidate:
H1c_rep3xextHam8 = rep(3) (x) extHamming[8,4,4] -> classical [24,4,12], w<=4,
q/log = 13.0, arena result eps = 1.25e-7 (8 fails / 2e6) vs rep-7 FIT 8.07e-7.

Re-check legs (each independently must keep the candidate under P2's 0.5 bar):
  R1 seed sensitivity    -- fresh sampling seed, standard decoder, 2e6 shots.
  R2 decoder sensitivity -- second BP-OSD config (osd_cs order 6, 60 iter),
                            fresh seed, 2e6 shots.
  R3 depth sensitivity   -- rounds 16 (vs arena's 8) at 1e6 shots; per-round
                            conversion must agree (guards boundary artifacts).
  R5 SAME-INSTRUMENT comparator -- rep-7 measured on THIS harness (pymatching,
                            2e7 shots). Kills the instrument-tilt asymmetry:
                            the arena compared our ~1.2-2x optimistic instrument
                            against Ruiz's fit; worst-case correction keeps
                            0.155 -> ~0.31 < 0.5, but the same-instrument ratio
                            is the clean number. Recorded BEFORE seeing R5.
  R4 Ocelot-point context -- calibrated-hardware look (labeled context only;
                            P2's operating point is the GM primary).
Verdict lines print per leg; P2 adjudication itself is the strategy room's.
"""
import sys, time
sys.path.insert(0, ".")
import numpy as np
from s2_seeds import build_bank, seed_stats, product_code, rep_H, ext_hamming8
from gm_css import fom, gm_css_circuit
from gm_corridor import ruiz_fit
from evaluator_v1 import Noise, logical_rate, per_round, dem_to_matrices, phase_rep

GM = dict(nbar=11.0, k_ratio=1e-4, p_m=6e-3)
KAPPA1 = 1.667e4
P2_BAR = 0.5

def bposd_alt_rate(circ, shots, seed):
    from ldpc import BpOsdDecoder
    dem = circ.detector_error_model(decompose_errors=False, flatten_loops=True)
    H, O, priors = dem_to_matrices(dem)
    try:
        dec = BpOsdDecoder(H, error_channel=list(priors), bp_method="ms",
                           max_iter=60, osd_method="osd_cs", osd_order=6)
    except TypeError:
        dec = BpOsdDecoder(H, channel_probs=list(priors), bp_method="ms",
                           max_iter=60, osd_method="osd_cs", osd_order=6)
    dets, obs = circ.compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    fails = 0
    for s in range(shots):
        e_hat = dec.decode(dets[s].astype(np.uint8))
        fails += int(np.any(((O @ e_hat.astype(np.uint8)) % 2) != obs[s].astype(np.uint8)))
    return fails / shots

def poisson95(fails, shots_eff):
    """~95% CI on a rate from a Poisson count (Garwood-ish simple bounds)."""
    import math
    if fails == 0: return (0.0, 3.0 / shots_eff)
    lo = fails * (1 - 1.96 / math.sqrt(fails)); hi = fails * (1 + 1.96 / math.sqrt(fails))
    return (max(lo, 0.0) / shots_eff, hi / shots_eff)

if __name__ == "__main__":
    Hc = product_code(rep_H(3), ext_hamming8())
    s = seed_stats(Hc)
    print(f"RE-CHECK target: rep3 (x) extHam8 = [{s['n']},{s['k']},{s['d']}] "
          f"w={s['w']} q/log={s['qlog']:.1f}  (mechanical floor re-verified)")
    assert (s["n"], s["k"], s["d"], s["w"]) == (24, 4, 12, 4), s
    Hz = np.zeros((0, 24), dtype=np.uint8)
    FIT7 = ruiz_fit(7)
    print(f"strict comparator rep-7: FIT={FIT7:.3e} (corridor-validated, "
          f"instrument tilt disclosed); same-instrument R5 below is primary.\n")

    # R1 -- fresh seed, standard decoder
    t0 = time.time()
    pk1, pa1, _, _ = fom(Hc, Hz, 4, 8, GM["p_m"], GM["nbar"], GM["k_ratio"],
                         "xonly", 2000000, seed=191)
    f1 = int(round(pa1 * 2000000))
    print(f"R1 fresh-seed:      eps={pk1:.3e} (fails={f1}/2e6) "
          f"ratio-to-FIT={pk1/FIT7:.3f}  [{time.time()-t0:.0f}s]")

    # R2 -- adversarial decoder config
    t0 = time.time()
    circ, _, _ = gm_css_circuit(Hc, Hz, 8, GM["p_m"], GM["nbar"], GM["k_ratio"], "xonly")
    pa2 = bposd_alt_rate(circ, 2000000, seed=191)
    pk2 = per_round(1 - (1 - pa2) ** 0.25, 8)
    f2 = int(round(pa2 * 2000000))
    print(f"R2 alt-decoder:     eps={pk2:.3e} (fails={f2}/2e6) "
          f"ratio-to-FIT={pk2/FIT7:.3f}  [{time.time()-t0:.0f}s]")

    # R3 -- depth sensitivity (rounds 16)
    t0 = time.time()
    pk3, pa3, _, _ = fom(Hc, Hz, 4, 16, GM["p_m"], GM["nbar"], GM["k_ratio"],
                         "xonly", 1000000, seed=191)
    f3 = int(round(pa3 * 1000000))
    print(f"R3 depth (16 rnds): eps={pk3:.3e} (fails={f3}/1e6) "
          f"ratio-to-FIT={pk3/FIT7:.3f}  [{time.time()-t0:.0f}s]")

    # R5 -- same-instrument comparator: rep-7 on THIS harness
    t0 = time.time()
    pk5, pa5, _, _ = fom(*phase_rep(7), 1, 8, GM["p_m"], GM["nbar"], GM["k_ratio"],
                         "xonly", 20000000, seed=191, decoder="pymatching")
    f5 = int(round(pa5 * 20000000))
    print(f"R5 rep-7 same-instrument: eps={pk5:.3e} (fails={f5}/2e7) "
          f"vs FIT {FIT7:.3e} (MC/FIT={pk5/FIT7:.2f})  [{time.time()-t0:.0f}s]")

    # R4 -- Ocelot-point context
    from s1_referee import ocelot_circuit
    nz = Noise(mode="transmon", p_m=0.0478, gamma_z=1.5 * KAPPA1, gamma_x=1571.0)
    c = ocelot_circuit(Hc, Hz, 6, nz, "X")
    pa4 = logical_rate(c, 20000, seed=191, decoder="bposd")
    pk4 = per_round(1 - (1 - pa4) ** 0.25, 6)
    print(f"R4 Ocelot context:  eps_phase={pk4:.3e} (context only)\n")

    # verdict lines (same-instrument primary)
    for nm, pk in (("R1", pk1), ("R2", pk2), ("R3", pk3)):
        r_fit = pk / FIT7
        r_same = pk / pk5 if pk5 > 0 else float("inf")
        v_fit = "PASS" if r_fit <= P2_BAR else "FAIL"
        v_same = "PASS" if r_same <= P2_BAR else "FAIL"
        print(f"VERDICT {nm}: ratio-to-FIT={r_fit:.3f} [{v_fit}] | "
              f"ratio-same-instrument={r_same:.3f} [{v_same}] (bar {P2_BAR})")
    print("\nRe-check complete. P2 adjudication happens in the strategy room; "
          "hits and misses both publish.")
