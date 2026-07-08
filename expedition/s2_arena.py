#!/usr/bin/env python3
"""s2_arena.py -- Campaign 1, stage S2: the structured search arena.
PREREG_search1.md governs (frozen 3255fb9; P1 resolved FALSE at 6616004).

Pre-run decisions (author, 2026-07-07): D6 -- STRICT budget comparator: the
repetition baseline is the smallest odd-d rep with 2d-1 >= candidate q/log
(repetition granted at least the candidate's budget; anti-self-serving).
D7 -- deep-shot budget 2e6 per product-code candidate.

Legs:
  A. seed bank + referee stats (provenance printed for P3: H1/H1b/H1c are
     LLM-layer proposals; H2/H4 are literature/handcrafted controls).
  B. pilot leg: every w<=4 survivor, GM primary point, xonly, 20k shots.
  C. deep leg: product-code family at 2e6 shots vs strict comparators (FIT,
     corridor-validated). P2 DATA lines printed; adjudication is the strategy
     room's. PREREG STOP condition honored in-script: any candidate >10x better
     than its comparator triggers the adversarial re-check (fresh seed,
     second decoder config, Ocelot-point run) before the script declares done.
"""
import sys, time
sys.path.insert(0, ".")
import numpy as np
from s2_seeds import build_bank, seed_stats
from gm_css import fom, gm_css_circuit
from gm_corridor import ruiz_fit
from evaluator_v1 import (Noise, logical_rate, per_round, dem_to_matrices)

GM = dict(nbar=11.0, k_ratio=1e-4, p_m=6e-3)
KAPPA1 = 1.667e4

def strict_comparator(qlog):
    d = 3
    while 2 * d - 1 < qlog: d += 2
    return d

def bposd_alt_rate(circ, shots, seed):
    """Adversarial second decoder config: osd_cs order 6, more BP iterations."""
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

def run_leg(name, H, k, rounds, shots, seed):
    Hz = np.zeros((0, H.shape[1]), dtype=np.uint8)
    pk, p_any, cxs, czs = fom(H, Hz, k, rounds, GM["p_m"], GM["nbar"],
                              GM["k_ratio"], "xonly", shots, seed=seed)
    return pk, p_any

if __name__ == "__main__":
    print("S2 ARENA -- GM primary point, xonly extraction, D6 strict comparator, D7 2e6 deep shots")
    bank = build_bank(dc_ms=(8, 12), verbose=True)
    print("\nProvenance for P3: LLM-layer = H1 (refereed DEAD: structural ceiling "
          "d <= 1 + colw(C) = 4), H1b, H1c. Controls = H2 (literature), H4 (repetition).")

    print("\nLEG B -- pilot (20k shots, rounds=8)")
    survivors = {}
    for nm, Hc in bank.items():
        s = seed_stats(Hc)
        if s["w"] > 4:
            print(f"  {nm}: REJECT w={s['w']}>4"); continue
        t0 = time.time()
        pk, p_any = run_leg(nm, Hc, s["k"], 8, 20000, 91)
        dstar = strict_comparator(s["qlog"]); er = ruiz_fit(dstar)
        survivors[nm] = (Hc, s, pk)
        print(f"  {nm:<24}[{s['n']},{s['k']},{s['d']}] q/log={s['qlog']:5.1f} "
              f"eps={pk:.3e} vs rep-{dstar} FIT={er:.3e} ratio={pk/er if er else 0:.2e} "
              f"(fails={int(round(p_any*20000))}, {time.time()-t0:.0f}s)")

    print("\nLEG C -- deep shots (2e6) on the product-code family")
    for nm in ("H1c_rep3xextHam8", "H1c_rep5xextHam8"):
        Hc, s, _ = survivors[nm]
        t0 = time.time()
        pk, p_any = run_leg(nm, Hc, s["k"], 8, 2000000, 91)
        dstar = strict_comparator(s["qlog"]); er = ruiz_fit(dstar)
        fails = int(round(p_any * 2000000))
        if fails == 0:
            # 95% upper bound on p_any: 3/shots (rule of three), propagated
            ub_any = 3.0 / 2000000
            ub = per_round(1 - (1 - ub_any) ** (1.0 / s["k"]), 8)
            print(f"  {nm:<24} 0 fails/2e6 -> eps <= {ub:.3e} (95% UB) vs rep-{dstar} "
                  f"FIT={er:.3e} -> ratio <= {ub/er:.2e} [{time.time()-t0:.0f}s]")
            ratio_for_stop = ub / er
        else:
            print(f"  {nm:<24} eps={pk:.3e} (fails={fails}) vs rep-{dstar} FIT={er:.3e} "
                  f"ratio={pk/er:.2e} [{time.time()-t0:.0f}s]")
            ratio_for_stop = pk / er
        print(f"  P2 DATA: {nm} ratio-to-strict-comparator "
              f"{'<=' if fails == 0 else '='} {ratio_for_stop:.2e} "
              f"(P2 bar: <= 0.5; PREREG adversarial re-check bar: < 0.1)")
        if ratio_for_stop < 0.1:
            print(f"  >10x claim -> ADVERSARIAL RE-CHECK for {nm}:")
            Hz = np.zeros((0, Hc.shape[1]), dtype=np.uint8)
            circ, _, _ = gm_css_circuit(Hc, Hz, 8, GM["p_m"], GM["nbar"],
                                        GM["k_ratio"], "xonly")
            pa2 = bposd_alt_rate(circ, 400000, seed=191)
            pk2 = per_round(1 - (1 - pa2) ** (1.0 / s["k"]), 8)
            print(f"    fresh seed 191 + osd_cs(6)/60it: eps={pk2:.3e} "
                  f"(fails={int(round(pa2*400000))}/4e5)")
            # Ocelot-point cross-mode look (phase memory; xonly structure)
            nz = Noise(mode="transmon", p_m=0.0478, gamma_z=1.5 * KAPPA1, gamma_x=1571.0)
            from evaluator_v1 import css_memory_circuit
            from s1_referee import ocelot_circuit
            c = ocelot_circuit(Hc, Hz, 6, nz, "X")
            pa3 = logical_rate(c, 20000, seed=191, decoder="bposd")
            pk3 = per_round(1 - (1 - pa3) ** (1.0 / s["k"]), 6)
            print(f"    Ocelot point (nbar=1.5, FITTED p_m): eps_phase={pk3:.3e} "
                  f"(context, not P2's operating point)")
    print("\nS2 arena complete. P2/P3 adjudication happens in the strategy room "
          "against PREREG_search1.md; hits and misses both publish.")
