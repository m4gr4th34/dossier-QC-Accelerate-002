#!/usr/bin/env python3
"""s1_referee.py -- Campaign 1, stage S1: circuit-level re-referee of the Day-1
band-2 leaders. PREREG_search1.md governs; priors frozen at commit 3255fb9.

Two legs:
  GM leg    -- primary operating point (kappa_1/kappa_2 = 1e-4, nbar = 11,
               p_m = 6e-3 mid-corridor assumption, stated). P1 resolves HERE
               (clarification recorded in NOTEBOOK before this canonical run).
  Ocelot leg -- calibrated hardware reality check: transmon mode, FITTED
               p_m = 0.0478, measured Gamma_X (v1.1 d5-section values),
               Gamma_Z = nbar*kappa_1; both memories, total = phase + bit.

Repetition baselines at the GM point: d in {9,11,13} cited from the
corridor-validated Ruiz fit (labeled FIT; MC at those rates needs >1e8 shots).
rep-5 is spot-checked by direct MC against the same fit as an in-run control.
Self-gating: noiseless-floor asserts run first; any failure aborts the tables.
"""
import sys, time
sys.path.insert(0, ".")
import numpy as np
from hgp import hgp, c_rep, HAMMING74
from verify_code import verify
from gm_css import fom, gm_css_circuit
from gm_corridor import ruiz_fit
from evaluator_v1 import (Noise, css_memory_circuit, logical_rate, per_round,
                          phase_rep)

punctHam6 = HAMMING74[:, :6].copy()
CODES = {
    "hgp_r5xpH6_[[42,3]]": hgp(c_rep(5), punctHam6),
    "hgp_r7r3_[[33,1]]": hgp(c_rep(7), c_rep(3)),
}
KAPPA1 = 1.667e4
# v1.1 measured in-array per-cat Gamma_X (DERIV v1.1 addendum, d5-section refit)
OCELOT_POINTS = {"nbar=1.5": (1.5 * KAPPA1, 1571.0), "nbar=2.0": (2.0 * KAPPA1, 1051.0)}
P_M_OCELOT = 0.0478   # FITTED (DERIV v1.1)
GM = dict(nbar=11.0, k_ratio=1e-4, p_m=6e-3)

def ocelot_circuit(Hx, Hz, rounds, nz, basis):
    """css_memory_circuit tracks only logical #0 (evaluator v1 limitation, caught
    in S1 smoke BEFORE the canonical run); complete the remaining k-1 observables.
    Final data measurements are the last n records, qubit q at rec -(n-q)."""
    from gm_css import logical_basis
    c = css_memory_circuit(Hx, Hz, rounds, nz, basis=basis)
    n = (np.atleast_2d(Hx).shape[1] if np.asarray(Hx).size else np.atleast_2d(Hz).shape[1])
    L = logical_basis(Hx, Hz, basis)
    import stim
    for li, v in enumerate(L[1:], start=1):
        c.append("OBSERVABLE_INCLUDE",
                 [stim.target_rec(-(n - int(q))) for q in np.flatnonzero(v)], li)
    assert c.num_observables == len(L), (c.num_observables, len(L))
    return c

def raw_obs_rate(circ, shots, seed):
    """For circuits with no detectors (undecodable memory): raw observable flip rate."""
    dets, obs = circ.compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    return float(np.mean(np.any(obs, axis=1)))

def floor_gate():
    print("S0 -- noiseless floor gate")
    ok = True
    for nm, (Hx, Hz) in CODES.items():
        for mode in ("xonly", "full"):
            pk, p_any, _, _ = fom(Hx, Hz, verify(Hx, Hz)["k"], 3, 0.0, 11.0, 0.0,
                                  mode, 2000, seed=7, nonadiabatic=False)
            ok &= (p_any == 0.0)
            print(f"  {nm} {mode}: p_any={p_any}  {'PASS' if p_any == 0.0 else 'FAIL'}")
    if not ok:
        print("STOP: floor gate failed -- do not run tables; report and wait.")
        sys.exit(1)

def gm_leg():
    print(f"\nS1 GM LEG (PRIMARY) -- k1/k2={GM['k_ratio']}, nbar={GM['nbar']}, "
          f"p_m={GM['p_m']} (mid-corridor assumption), rounds=8, shots=50000, BP-OSD")
    results = {}
    for nm, (Hx, Hz) in CODES.items():
        v = verify(Hx, Hz)
        for mode in ("xonly", "full"):
            anc = Hx.shape[0] + (Hz.shape[0] if mode == "full" else 0)
            t0 = time.time()
            pk, p_any, cxs, czs = fom(Hx, Hz, v["k"], 8, GM["p_m"], GM["nbar"],
                                      GM["k_ratio"], mode, 50000, seed=91)
            qlog = (v["n"] + anc) / v["k"]
            results[(nm, mode)] = (pk, qlog)
            print(f"  {nm:<24}{mode:<6} q/log={qlog:5.1f} slots={2+cxs+czs:>2} "
                  f"eps_perlog/cycle={pk:.3e} (fails={int(round(p_any*50000))}) [{time.time()-t0:.0f}s]")
    # rep-5 spot check vs corridor-validated fit
    Hx, Hz = phase_rep(5)
    pk5, p5, _, _ = fom(Hx, Hz, 1, 10, GM["p_m"], GM["nbar"], GM["k_ratio"],
                        "xonly", 2000000, seed=91, decoder="pymatching")
    print(f"  rep-5 spot-check: MC={pk5:.3e} vs FIT={ruiz_fit(5):.3e} "
          f"ratio={pk5/ruiz_fit(5):.2f} (corridor-validated instrument)")
    for d in (9, 11, 13):
        print(f"  rep-{d:<2} q/log={2*d-1:5.1f}  eps_perlog/cycle={ruiz_fit(d):.3e} "
              f"[FIT -- corridor-validated at d=3,5; instrument reads ~1.2-2x optimistic]")
    # P1 ratio line (adjudication itself happens in the strategy room)
    pk42, q42 = results[("hgp_r5xpH6_[[42,3]]", "xonly")]
    comp = ruiz_fit(11)   # rep-11 at 21 q/log: matched-budget k=1 comparator for 22 q/log
    print(f"  P1 DATA: [[42,3]] xonly ({q42:.0f} q/log) = {pk42:.3e} vs matched-budget "
          f"k=1 comparator rep-11 (21 q/log, FIT) = {comp:.3e} -> ratio = {pk42/comp:.1e}")

def ocelot_leg():
    print(f"\nS1 OCELOT LEG (calibrated reality check) -- transmon mode, "
          f"p_m={P_M_OCELOT} (FITTED), rounds=6, shots=20000, total = phase + bit per logical")
    for pt, (gz, gx) in OCELOT_POINTS.items():
        print(f"  operating point {pt}: Gamma_Z={gz:.3g}/s Gamma_X={gx:.0f}/s")
        entries = list(CODES.items()) + [(f"rep-{d}", phase_rep(d)) for d in (9, 11, 13)]
        for nm, (Hx, Hz) in entries:
            v = verify(Hx, Hz)
            nz = Noise(mode="transmon", p_m=P_M_OCELOT, gamma_z=gz, gamma_x=gx)
            tot, parts = 0.0, []
            for basis in ("X", "Z"):
                c = ocelot_circuit(Hx, Hz, 6, nz, basis)
                if c.num_detectors == 0:
                    pa = raw_obs_rate(c, 20000, seed=95)
                else:
                    dec = "pymatching" if nm.startswith("rep-") and basis == "X" else "bposd"
                    pa = logical_rate(c, 20000, seed=95, decoder=dec)
                pk = per_round(1 - (1 - pa) ** (1.0 / v["k"]), 6)
                parts.append(pk); tot += pk
            anc = Hx.shape[0] + Hz.shape[0]
            print(f"    {nm:<24} q/log={(v['n']+anc)/v['k']:5.1f} "
                  f"phase={parts[0]:.3e} bit={parts[1]:.3e} TOTAL={tot:.3e}")

if __name__ == "__main__":
    floor_gate()
    gm_leg()
    ocelot_leg()
    print("\nS1 complete. P1 adjudication happens in the strategy room against "
          "PREREG_search1.md; hits and misses both publish.")
