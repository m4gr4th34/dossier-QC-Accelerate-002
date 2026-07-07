#!/usr/bin/env python3
"""
fom.py — figure-of-merit evaluator v0 (code-capacity, biased Pauli noise) + calibration.

MODEL (v0, documented; circuit-level finite-bias is the v1 seam):
  Independent X and Z errors per data qubit per round:
    pz = p * eta/(eta+1),  px = p * 1/(eta+1)      (Y folded, stated convention)
  Decode Z-errors with Hx (X-checks) and X-errors with Hz (Z-checks), each via BP-OSD.
  Logical failure = residual (error XOR correction) is a logical operator.
FOM = total logical error probability per round (lower is better).

CALIBRATION QUESTION (known qualitative answer in the bias-tailoring literature):
  at fixed n, does pure phase-repetition (all budget on Z-protection, dx=1) lose to a
  Shor-type [[M x L, 1]] split (some budget on X) once bias is finite? Where's the crossover?
"""
import numpy as np
from verify_code import verify, in_rowspace2, kernel2, rank2

try:
    from ldpc import BpOsdDecoder
    def make_decoder(H, p):
        return BpOsdDecoder(H, error_rate=float(p), bp_method="ms", max_iter=30,
                            osd_method="osd_e", osd_order=4)
except Exception:
    from ldpc import bposd_decoder
    def make_decoder(H, p):
        return bposd_decoder(H, error_rate=float(p), bp_method="ms", max_iter=30,
                             osd_method="osd_e", osd_order=4)

def phase_rep(n):
    """Phase-flip repetition code (cat orientation): X-type pair checks; dz=n, dx=1."""
    Hx = np.zeros((n - 1, n), dtype=np.uint8)
    for i in range(n - 1): Hx[i, i] = Hx[i, i + 1] = 1
    return Hx, np.zeros((0, n), dtype=np.uint8)

def shor_ML(M, L):
    """Generalized Shor [[M*L,1]]: inner bit-rep(M) blocks (ZZ checks), outer phase-rep(L)
    across blocks (X-type block checks). Distances measured by the verifier, not assumed."""
    n = M * L
    Hz = np.zeros(((M - 1) * L, n), dtype=np.uint8)
    r = 0
    for b in range(L):
        for i in range(M - 1):
            Hz[r, b * M + i] = Hz[r, b * M + i + 1] = 1; r += 1
    Hx = np.zeros((L - 1, n), dtype=np.uint8)
    for b in range(L - 1):
        Hx[b, b * M:(b + 1) * M] = 1
        Hx[b, (b + 1) * M:(b + 2) * M] = 1
    return Hx, Hz

def logical_error_rate(Hx, Hz, p, eta, shots=20000, seed=7):
    rng = np.random.default_rng(seed)
    n = Hx.shape[1]
    pz = p * eta / (eta + 1.0); px = p / (eta + 1.0)
    fails = 0
    decZ = make_decoder(Hx, pz) if Hx.shape[0] else None   # X-checks decode Z errors
    decX = make_decoder(Hz, px) if Hz.shape[0] else None   # Z-checks decode X errors
    for _ in range(shots):
        fail = False
        ez = (rng.random(n) < pz).astype(np.uint8)
        if ez.any():
            if decZ is None:
                fail = True
            else:
                syn = (Hx @ ez) % 2
                corr = decZ.decode(syn).astype(np.uint8)
                res = ez ^ corr
                if res.any() and not in_rowspace2(res, Hz):
                    fail = True
        if not fail:
            ex = (rng.random(n) < px).astype(np.uint8)
            if ex.any():
                if decX is None:
                    fail = True
                else:
                    syn = (Hz @ ex) % 2
                    corr = decX.decode(syn).astype(np.uint8)
                    res = ex ^ corr
                    if res.any() and not in_rowspace2(res, Hx):
                        fail = True
        fails += fail
    return fails / shots

if __name__ == "__main__":
    p = 0.01
    print(f"CALIBRATION — n=15 budget, p={p}, code-capacity biased noise")
    cands = {
        "phase-rep-15  ": phase_rep(15),
        "shor 3x5 (M=3,L=5)": shor_ML(3, 5),
        "shor 5x3 (M=5,L=3)": shor_ML(5, 3),
    }
    for name, (Hx, Hz) in cands.items():
        v = verify(Hx, Hz)
        assert v["valid"] and v["k"] == 1, (name, v)
        print(f"  {name} [[{v['n']},{v['k']}]] dx={v['dx']}{'' if v['dx_exact'] else '<='} "
              f"dz={v['dz']}{'' if v['dz_exact'] else '<='} wmax={v['wmax']}")
    print(f"\n  {'eta':>6} | " + " | ".join(f"{nm.strip():>18}" for nm in cands))
    for eta in [10, 30, 100, 300, 1000, 3000]:
        row = []
        for name, (Hx, Hz) in cands.items():
            r = logical_error_rate(Hx, Hz, p, eta, shots=20000)
            row.append(f"{r:18.5f}")
        print(f"  {eta:>6} | " + " | ".join(row))
    print("\nEXPECTATION (literature-shaped): rep wins at extreme bias; a mixed split "
          "overtakes as bias drops. The harness must show that crossover to earn trust.")
