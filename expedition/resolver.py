#!/usr/bin/env python3
"""
resolver.py — band-2 leaders under harder noise (p=0.02), 60k shots: separates the
zeros that band-1 shots could not rank. Produces NOTEBOOK.md's R4 table verbatim
(fixed seeds). Usage: python3 resolver.py
"""
import numpy as np, time
from verify_code import verify
from fom import phase_rep, shor_ML, logical_error_rate
from hgp import hgp, c_rep, HAMMING74

punctHam6 = HAMMING74[:, :6].copy()
E = {"rep-33": phase_rep(33), "shor3x11": shor_ML(3, 11),
     "hgp r6r4": hgp(c_rep(6), c_rep(4)), "hgp r7r3": hgp(c_rep(7), c_rep(3)),
     "hgp r4xpH6 (k=3)": hgp(c_rep(4), punctHam6), "hgp r5xpH6 (k=3)": hgp(c_rep(5), punctHam6)}
P, SHOTS, etas = 0.02, 60000, [30, 100, 300]

if __name__ == "__main__":
    print(f"RESOLVER p={P} shots={SHOTS} | per-logical rates, 95% CI on P_any")
    print(f"{'code':<18}{'n':>4}{'k':>3}{'q/log':>6}", end="")
    for eta in etas: print(f" | eta={eta:<7}", end="")
    print()
    t0 = time.time()
    for nm, (Hx, Hz) in E.items():
        v = verify(Hx, Hz)
        line = f"{nm:<18}{v['n']:>4}{v['k']:>3}{v['n']/v['k']:>6.1f}"
        for i, eta in enumerate(etas):
            Pa = logical_error_rate(Hx, Hz, P, eta, shots=SHOTS, seed=71 + i)
            ci = 1.96 * np.sqrt(max(Pa * (1 - Pa), 1e-12) / SHOTS)
            Pk = 1 - (1 - Pa) ** (1.0 / v["k"])
            line += f" | {Pk:.5f}±{ci:.5f}"
        print(line, flush=True)
    print(f"[{time.time()-t0:.0f}s]")
