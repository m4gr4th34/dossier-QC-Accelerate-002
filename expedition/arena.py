#!/usr/bin/env python3
"""
arena.py — the expedition's first real data run.

QUESTION: at a matched physical-qubit budget (n <= 23) and hardware weight wmax <= 6,
which structured family minimizes logical error per LOGICAL qubit, as a function of
noise bias eta?  Families: phase-repetition (the incumbent), generalized Shor splits,
asymmetric hypergraph products (bias-tailored rectangles), and a rate-4 Hamming product.
Per-shot ANY-logical failure P is measured; per-logical-qubit rate reported as
P_k = 1-(1-P)^(1/k). 95% CI = 1.96*sqrt(P(1-P)/shots) on P.
Every entrant passes the verifier gate; distances printed are the verifier's own.
Usage: python3 arena.py 30 100      (eta values as argv)
"""
import sys, time
import numpy as np
from verify_code import verify
from fom import phase_rep, shor_ML, logical_error_rate
from hgp import hgp, c_rep, HAMMING74

P_PHYS, WMAX, SHOTS = 0.01, 6, 10000

def entrants():
    E = {
        "rep-12":  phase_rep(12),
        "rep-15":  phase_rep(15),
        "shor3x4": shor_ML(3, 4),
        "shor3x5": shor_ML(3, 5),
        "shor2x6": shor_ML(2, 6),
        "hgp r3r3 (surface d3)": hgp(c_rep(3), c_rep(3)),
        "hgp r4r2": hgp(c_rep(4), c_rep(2)),
        "hgp r5r2": hgp(c_rep(5), c_rep(2)),
        "hgp r4r3": hgp(c_rep(4), c_rep(3)),
        "hgp r6r2": hgp(c_rep(6), c_rep(2)),
        "hgp Ham,r2 (k=4)": hgp(HAMMING74, c_rep(2)),
    }
    out = {}
    for nm, (Hx, Hz) in E.items():
        v = verify(Hx, Hz)
        if not v["valid"] or v["wmax"] > WMAX or v["n"] > 23:
            print(f"  gate EXCLUDED {nm}: valid={v['valid']} wmax={v.get('wmax')} n={v.get('n')}")
            continue
        out[nm] = (Hx, Hz, v)
    return out

if __name__ == "__main__":
    etas = [int(a) for a in sys.argv[1:]] or [30, 100]
    E = entrants()
    print(f"ARENA p={P_PHYS} wmax<={WMAX} shots={SHOTS} | per-logical-qubit rates, 95% CI on P_any")
    print(f"{'code':<22}{'n':>4}{'k':>3}{'dx':>4}{'dz':>4}{'w':>3}", end="")
    for eta in etas: print(f" | eta={eta:<6}", end="")
    print()
    t0 = time.time()
    rows = []
    for nm, (Hx, Hz, v) in E.items():
        line = f"{nm:<22}{v['n']:>4}{v['k']:>3}{v['dx']:>4}{v['dz']:>4}{v['wmax']:>3}"
        vals = []
        for i, eta in enumerate(etas):
            P = logical_error_rate(Hx, Hz, P_PHYS, eta, shots=SHOTS, seed=31 + i)
            ci = 1.96 * np.sqrt(max(P * (1 - P), 1e-12) / SHOTS)
            Pk = 1 - (1 - P) ** (1.0 / v["k"])
            vals.append((Pk, P, ci))
            line += f" | {Pk:.5f}±{ci:.5f}"
        rows.append((nm, v, vals))
        print(line, flush=True)
    print(f"\n[{time.time()-t0:.0f}s]")
    for i, eta in enumerate(etas):
        best = min(rows, key=lambda r: r[2][i][0])
        nm, v, vals = best
        print(f"eta={eta}: best per-logical = {nm} [[{v['n']},{v['k']}]] at {vals[i][0]:.5f}")
