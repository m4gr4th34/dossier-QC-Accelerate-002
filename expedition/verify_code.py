#!/usr/bin/env python3
"""
verify_code.py — the expedition's mechanical floor (prototype v0).

A candidate CSS code is (Hx, Hz) over GF(2). NOTHING enters the search corpus
unless this module certifies it. Checks:
  1. CSS consistency: Hx @ Hz^T = 0 (mod 2)        [else not a stabilizer code]
  2. n, k = n - rank(Hx) - rank(Hz)
  3. Distances dx, dz:
     - EXACT by exhaustive coset enumeration when the logical space is small
       (dim ker <= EXACT_LIMIT), else a randomized information-set UPPER BOUND,
       labeled "<=" — the label always tells the truth about certainty grade.
  4. Stabilizer weights (max row weight — the hardware constraint knob).
Ground-truth test suite: [[4,2,2]], Steane [[7,1,3]], Shor [[9,1,3]],
repetition [[n,1]] (dx=n, dz=1). Fail-loud.
"""
import numpy as np
from itertools import combinations

EXACT_LIMIT = 22  # exhaustive enumeration up to 2^22 coset words

# ---------- GF(2) linear algebra ----------
def rref2(M):
    M = M.copy() % 2
    r, rows, cols = 0, M.shape[0], M.shape[1]
    pivots = []
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if M[i, c]:
                piv = i; break
        if piv is None: continue
        M[[r, piv]] = M[[piv, r]]
        for i in range(rows):
            if i != r and M[i, c]:
                M[i] ^= M[r]
        pivots.append(c); r += 1
        if r == rows: break
    return M[:r], pivots

def rank2(M):
    if M.size == 0: return 0
    return rref2(M)[0].shape[0]

def kernel2(M):
    """Basis of null space of M over GF(2), as rows."""
    n = M.shape[1]
    R, piv = rref2(M)
    free = [c for c in range(n) if c not in piv]
    basis = []
    for f in free:
        v = np.zeros(n, dtype=np.uint8); v[f] = 1
        for i, p in enumerate(piv):
            if R[i, f]: v[p] = 1
        basis.append(v)
    return np.array(basis, dtype=np.uint8) if basis else np.zeros((0, n), dtype=np.uint8)

def in_rowspace2(v, M):
    if M.size == 0: return not v.any()
    A = np.vstack([M, v])
    return rank2(A) == rank2(M)

# ---------- distance ----------
def logical_min_weight(H_stab, H_dual, rng=None, tries=4000):
    """Min weight of a vector in ker(H_dual) that is NOT in rowspace(H_stab).
    (For dx: H_stab=Hx, H_dual=Hz. For dz: swap.) Returns (d, exact_flag)."""
    K = kernel2(H_dual)
    dimK = K.shape[0]
    if dimK == 0: return None, True
    S, _ = rref2(H_stab) if H_stab.size else (np.zeros((0, H_dual.shape[1]), dtype=np.uint8), [])
    if dimK <= EXACT_LIMIT:
        best = None
        # enumerate all nonzero combos of kernel basis via gray-code walk
        v = np.zeros(K.shape[1], dtype=np.uint8)
        prev = 0
        for i in range(1, 1 << dimK):
            g = i ^ (i >> 1)
            diff = g ^ prev; prev = g
            b = diff.bit_length() - 1
            v ^= K[b]
            w = int(v.sum())
            if (best is None or w < best) and not in_rowspace2(v, S):
                best = w
        return best, True
    # randomized upper bound: random combos, small combos of low-weight rows
    rng = rng or np.random.default_rng(0)
    best = None
    order = np.argsort(K.sum(axis=1))
    for r in range(1, min(4, dimK) + 1):
        for combo in combinations(order[:min(dimK, 14)], r):
            v = np.bitwise_xor.reduce(K[list(combo)], axis=0)
            w = int(v.sum())
            if (best is None or w < best) and not in_rowspace2(v, S):
                best = w
    for _ in range(tries):
        mask = rng.integers(0, 2, dimK, dtype=np.uint8)
        if not mask.any(): continue
        v = (mask @ K) % 2
        w = int(v.sum())
        if (best is None or w < best) and not in_rowspace2(v, S):
            best = w
    return best, False

def verify(Hx, Hz):
    Hx = np.atleast_2d(np.array(Hx, dtype=np.uint8))
    Hz = np.atleast_2d(np.array(Hz, dtype=np.uint8))
    n = Hx.shape[1]
    assert Hz.shape[1] == n, "Hx/Hz width mismatch"
    comm = (Hx @ Hz.T) % 2
    if comm.any():
        return {"valid": False, "reason": "CSS commutation fails"}
    k = n - rank2(Hx) - rank2(Hz)
    dx, dx_exact = logical_min_weight(Hx, Hz)     # X-logicals live in ker(Hz)
    dz, dz_exact = logical_min_weight(Hz, Hx)
    wmax = int(max(Hx.sum(axis=1).max() if Hx.size else 0,
                   Hz.sum(axis=1).max() if Hz.size else 0))
    return {"valid": True, "n": int(n), "k": int(k),
            "dx": dx, "dx_exact": dx_exact, "dz": dz, "dz_exact": dz_exact,
            "d": (None if (dx is None or dz is None) else min(dx, dz)),
            "wmax": wmax}

# ---------- ground-truth suite ----------
def _rep(n):
    Hz = np.zeros((n - 1, n), dtype=np.uint8)
    for i in range(n - 1): Hz[i, i] = Hz[i, i + 1] = 1
    Hx = np.zeros((0, n), dtype=np.uint8)
    return Hx, Hz

STEANE_H = np.array([[0,0,0,1,1,1,1],[0,1,1,0,0,1,1],[1,0,1,0,1,0,1]], dtype=np.uint8)

def _shor():
    Hz = np.zeros((6, 9), dtype=np.uint8)
    pairs = [(0,1),(1,2),(3,4),(4,5),(6,7),(7,8)]
    for i,(a,b) in enumerate(pairs): Hz[i,a]=Hz[i,b]=1
    Hx = np.zeros((2, 9), dtype=np.uint8)
    Hx[0,0:6]=1; Hx[1,3:9]=1
    return Hx, Hz

if __name__ == "__main__":
    fails = 0
    def check(name, got, want):
        global fails
        ok = all(got.get(k2) == v for k2, v in want.items())
        print(("PASS " if ok else "FAIL "), name, "->",
              {k2: got.get(k2) for k2 in want} if not ok else want)
        if not ok: fails += 1

    Hx, Hz = np.array([[1,1,1,1]],dtype=np.uint8), np.array([[1,1,1,1]],dtype=np.uint8)
    check("[[4,2,2]]", verify(Hx,Hz), {"valid":True,"n":4,"k":2,"d":2,"dx":2,"dz":2})
    check("Steane [[7,1,3]]", verify(STEANE_H, STEANE_H), {"valid":True,"n":7,"k":1,"d":3,"dx":3,"dz":3})
    check("Shor [[9,1,3]]", verify(*_shor()), {"valid":True,"n":9,"k":1,"d":3})
    check("rep-5 [[5,1]] dz=1,dx=5", verify(*_rep(5)), {"valid":True,"n":5,"k":1,"dz":1,"dx":5})
    check("rep-11 [[11,1]]", verify(*_rep(11)), {"valid":True,"n":11,"k":1,"dz":1,"dx":11})
    # negative control: broken commutation must be rejected
    bad = verify(np.array([[1,1,0,0]],dtype=np.uint8), np.array([[1,0,0,0]],dtype=np.uint8))
    check("negative control (non-commuting rejected)", bad, {"valid": False})
    print("\n" + ("ALL GROUND TRUTHS PASS" if fails == 0 else f"{fails} FAILURES"))
    raise SystemExit(fails)
