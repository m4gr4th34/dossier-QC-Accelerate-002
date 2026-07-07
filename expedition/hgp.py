#!/usr/bin/env python3
"""
hgp.py — structured, correct-by-construction code families for the expedition.

WHY: the micro-search proved random entry to CSS space is barren (0/4000 valid).
Structured constructions satisfy commutation BY CONSTRUCTION:
  Hypergraph product HGP(H1, H2):
    Hx = [ H1 (x) I_n2   |  I_r1 (x) H2^T ]
    Hz = [ I_n1 (x) H2   |  H1^T (x) I_r2 ]
  commutation holds identically for ANY classical H1 (r1 x n1), H2 (r2 x n2).
  Asymmetric classical seeds -> asymmetric quantum distances = bias-tailoring dial.
GROUND TRUTH: HGP(rep3, rep3) must be the [[13,1,3]] surface code.
Classical seeds get their own verifier (k, exact min distance for small n).
"""
import numpy as np
from itertools import combinations
from verify_code import verify, rank2

# ---------- classical toolkit ----------
def c_rep(n):
    H = np.zeros((n - 1, n), dtype=np.uint8)
    for i in range(n - 1): H[i, i] = H[i, i + 1] = 1
    return H

HAMMING74 = np.array([[0,0,0,1,1,1,1],[0,1,1,0,0,1,1],[1,0,1,0,1,0,1]], dtype=np.uint8)

def classical_verify(H):
    """(n, k, d_exact) for a classical code given parity check H (exhaustive over codewords)."""
    n = H.shape[1]; k = n - rank2(H)
    if k == 0: return n, 0, None
    # codewords = kernel of H
    from verify_code import kernel2
    K = kernel2(H)
    best, v, prev = None, np.zeros(n, dtype=np.uint8), 0
    for i in range(1, 1 << K.shape[0]):
        g = i ^ (i >> 1); b = (g ^ prev).bit_length() - 1; prev = g
        v ^= K[b]
        w = int(v.sum())
        if best is None or w < best: best = w
    return n, k, best

def hgp(H1, H2):
    r1, n1 = H1.shape; r2, n2 = H2.shape
    Hx = np.hstack([np.kron(H1, np.eye(n2, dtype=np.uint8)),
                    np.kron(np.eye(r1, dtype=np.uint8), H2.T)]) % 2
    Hz = np.hstack([np.kron(np.eye(n1, dtype=np.uint8), H2),
                    np.kron(H1.T, np.eye(r2, dtype=np.uint8))]) % 2
    return Hx.astype(np.uint8), Hz.astype(np.uint8)

if __name__ == "__main__":
    fails = 0
    def check(name, cond, extra=""):
        global fails
        print(("PASS " if cond else "FAIL "), name, extra)
        if not cond: fails += 1

    n,k,d = classical_verify(c_rep(3));   check("classical rep3 = [3,1,3]", (n,k,d)==(3,1,3))
    n,k,d = classical_verify(HAMMING74); check("classical Hamming = [7,4,3]", (n,k,d)==(7,4,3))

    # GROUND TRUTH: HGP(rep3,rep3) = [[13,1,3]] surface code
    v = verify(*hgp(c_rep(3), c_rep(3)))
    check("HGP(rep3,rep3) = [[13,1,3]]", v["valid"] and (v["n"],v["k"],v["d"])==(13,1,3), str(v))
    # asymmetric: HGP(rep5, rep2) — verifier measures, we predict d = min(5,2)-ish family behavior
    v = verify(*hgp(c_rep(5), c_rep(2)))
    check("HGP(rep5,rep2) valid k=1", v["valid"] and v["k"]==1,
          f"[[{v['n']},{v['k']}]] dx={v['dx']} dz={v['dz']} wmax={v['wmax']}")
    v = verify(*hgp(c_rep(4), c_rep(3)))
    check("HGP(rep4,rep3) valid k=1", v["valid"] and v["k"]==1,
          f"[[{v['n']},{v['k']}]] dx={v['dx']} dz={v['dz']} wmax={v['wmax']}")
    # higher-rate seed: HGP(Hamming, rep2)
    v = verify(*hgp(HAMMING74, c_rep(2)))
    check("HGP(Hamming74,rep2) valid", v["valid"],
          f"[[{v['n']},{v['k']}]] dx={v['dx']}{'' if v['dx_exact'] else '<='} dz={v['dz']}{'' if v['dz_exact'] else '<='} wmax={v['wmax']}")
    print("\n" + ("ALL HGP GROUND TRUTHS PASS" if fails==0 else f"{fails} FAILURES"))
    raise SystemExit(fails)
