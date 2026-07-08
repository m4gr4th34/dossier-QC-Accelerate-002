#!/usr/bin/env python3
"""Data-free validation battery for evaluator_v1 (sandbox, prototype-grade).
V1 noiseless -> exactly 0.  V2 analytic single-round majority vote.  V3 decoder
cross-check (BP-OSD vs pymatching).  V4 unprotected bit-flip sector ~ n*px.
V5 distance scaling direction + magnitude preview at the Ocelot anchor."""
import math
import numpy as np
from evaluator_v1 import (Noise, css_memory_circuit, logical_rate, per_round,
                          phase_rep, p_of, GAMMA_Z, GAMMA_X_ACTIVE, T_CYCLE)

def check(name, ok, detail):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    return ok

allok = True

print("V1 -- noiseless floor (d=3,5 phase-rep, both bases, cat mode, 3 rounds)")
for d in (3, 5):
    Hx, Hz = phase_rep(d)
    nz = Noise(mode="cat", p_m=0.0, gamma_z=0.0, gamma_x=0.0)
    nz.pz_cx = nz.px_cx = 0.0
    for basis in ("X", "Z"):
        c = css_memory_circuit(Hx, Hz, 3, nz, basis=basis)
        r = logical_rate(c, 2000, seed=11)
        allok &= check(f"d={d} basis={basis}", r == 0.0, f"rate={r}")

print("V2 -- analytic majority vote: d=3, 1 round, Z-only lump, p_m=0, perfect readout")
# configure: no CX-step errors, all Z in residual; Gamma_X=0
p_lump = p_of(GAMMA_Z, T_CYCLE)                       # 0.0891 per round
nz = Noise(mode="transmon", p_m=0.0, gamma_x=0.0)
nz.px_cx = 0.0; nz.pz_cx = 0.0                        # push all Z into residual
nz.t_cx = 0.0                                          # residual = full cycle
Hx, Hz = phase_rep(3)
c = css_memory_circuit(Hx, Hz, 1, nz, basis="X")
r = logical_rate(c, 60000, seed=13)
analytic = 3 * p_lump**2 * (1 - p_lump) + p_lump**3
sigma = math.sqrt(analytic * (1 - analytic) / 60000)
ok = abs(r - analytic) < 4 * sigma
allok &= check("d=3 1-round", ok, f"measured={r:.5f} analytic={analytic:.5f} (4sig={4*sigma:.5f})")

print("V3 -- decoder cross-check: d=5, 5 rounds, full anchor noise, transmon p_m=0.02")
nz = Noise(mode="transmon", p_m=0.02)
Hx, Hz = phase_rep(5)
c = css_memory_circuit(Hx, Hz, 5, nz, basis="X")
r_b = logical_rate(c, 4000, seed=17, decoder="bposd")
r_m = logical_rate(c, 4000, seed=17, decoder="pymatching")
ok = abs(r_b - r_m) < 0.25 * max(r_b, r_m) + 0.01
allok &= check("bposd vs matching", ok, f"bposd={r_b:.4f} matching={r_m:.4f}")

print("V4 -- unprotected bit-flip sector: d=5 phase-rep, Z-memory (observable weight-n)")
nz = Noise(mode="cat", p_m=0.0)
c = css_memory_circuit(Hx, Hz, 3, nz, basis="Z")
r = logical_rate(c, 20000, seed=19)
rr = per_round(r, 3)
# expectation: ~ n * px_round (5 data qubits, any single X flips Z_L; ancilla hooks add)
px_round = p_of(GAMMA_X_ACTIVE, T_CYCLE)
lo, hi = 4.0 * px_round, 9.0 * px_round
ok = lo <= rr <= hi
allok &= check("bit sector magnitude", ok,
               f"per-round={rr:.5f} corridor=[{lo:.5f},{hi:.5f}] (5*px={5*px_round:.5f})")

print("V5 -- phase sector distance scaling at anchor (transmon, p_m=0.02, 5 rounds)")
res = {}
for d in (3, 5):
    Hx, Hz = phase_rep(d)
    c = css_memory_circuit(Hx, Hz, 5, Noise(mode="transmon", p_m=0.02), basis="X")
    res[d] = per_round(logical_rate(c, 6000, seed=23), 5)
ok = res[5] < res[3]
allok &= check("eps(d=5) < eps(d=3)", ok, f"d3={res[3]:.4f} d5={res[5]:.4f} ratio={res[3]/max(res[5],1e-9):.2f}")

print(f"\n{'ALL PASS' if allok else 'FAILURES PRESENT'}")
