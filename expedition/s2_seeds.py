#!/usr/bin/env python3
"""s2_seeds.py -- Campaign 1, stage S2: seed bank. LLM-proposes / verifier-referees.

Post-S1 arena: X-only extraction is first-class, so a candidate IS a classical
[n, k, d] code (parity check H = the phase checks; quantum X_L reps = weight-1;
bit floor analytic). Hardware caps: row weight w <= 4 (PREREG); column degree
reported (self-penalizing via schedule length -- more colors = more idle slots).

LLM-proposal hypotheses, recorded BEFORE refereeing (Day-1 llm_seeds.py pattern):
  H1 double-circulant [2m, m] with H = [I | C3] (C3 = circulant, row weight 3;
     total row weight 4): hypothesis -- best rate-distance family under w <= 4
     at small n; q/log = 3 flat, d grows with m for good taps.
  H2 Hamming [7,4,3] and its shortenings: hypothesis -- highest-rate w=4 seeds
     (q/log = 2.5) but d = 3 drowns in circuit-level syndrome noise; will lose
     to H1 at matched budget despite better rate.
  H3 expanded repetition x parity products (rep(a) (x) parity-ish): hypothesis --
     interpolates rep and LDPC; dominated by H1 (strictly worse d at same w cap).
  H4 controls: repetition [d, 1, d] (w=2) -- the baseline family the PREREG
     P2 criterion measures against.
Referee chain: classical_verify (exact n, k, d) -> weight/degree caps ->
circuit-level FOM (gm_css xonly, GM primary point) -> strict budget comparator.
"""
import sys
sys.path.insert(0, ".")
import numpy as np
from hgp import classical_verify
from gm_css import edge_color

def circ_taps(m, taps):
    C = np.zeros((m, m), dtype=np.uint8)
    for i in range(m):
        for t in taps:
            C[i, (i + t) % m] = 1
    return C

def double_circulant(m, taps):
    """[2m, m] code, H = [I_m | C(taps)]; row weight 1 + len(taps)."""
    return np.hstack([np.eye(m, dtype=np.uint8), circ_taps(m, taps)])

def hamming74():
    return np.array([[0,0,0,1,1,1,1],[0,1,1,0,0,1,1],[1,0,1,0,1,0,1]], dtype=np.uint8)

def shortened_hamming(cols):
    """Shorten Hamming [7,4,3] by deleting data coordinates (keep checks)."""
    H = hamming74()
    keep = [c for c in range(7) if c not in cols]
    return H[:, keep]

def ext_hamming8():
    """[8,4,4] extended Hamming; all four checks weight 4 -- the densest-rate
    w=4 seed with d=4 (self-dual). q/log = 3 at d=4 vs H1's structural d<=4 at
    the same q/log: strictly dominates H1's [2m,m] family."""
    H = np.array([[1,1,1,1,0,0,0,0],
                  [0,0,1,1,0,0,1,1],
                  [0,1,0,1,0,1,0,1],
                  [0,0,0,0,1,1,1,1]], dtype=np.uint8)
    return H

def product_code(H1, H2):
    """Classical product code C1 (x) C2: every column in C1, every row in C2.
    d = d1*d2; row weights = w(H1), w(H2) (caps preserved). Redundant checks
    kept deliberately: they cost ancillas but aid decoding under syndrome noise
    (conservatively costed)."""
    r1, n1 = H1.shape; r2, n2 = H2.shape
    top = np.kron(H1, np.eye(n2, dtype=np.uint8))
    bot = np.kron(np.eye(n1, dtype=np.uint8), H2)
    return np.vstack([top, bot]).astype(np.uint8) % 2

def rep_H(n):
    H = np.zeros((n - 1, n), dtype=np.uint8)
    for i in range(n - 1): H[i, i] = H[i, i + 1] = 1
    return H

def seed_stats(H):
    n, k, d = classical_verify(H)
    roww = int(H.sum(axis=1).max())
    colw = int(H.sum(axis=0).max())
    colors = len(edge_color(H))
    qlog = (n + H.shape[0]) / k if k else float("inf")
    return dict(n=n, k=k, d=d, w=roww, deg=colw, colors=colors, qlog=qlog)

def best_dc_taps(m, w_row=4, span=None):
    """Referee-side tap search for H1: maximize exact d over tap triples."""
    span = span or m
    best = None
    from itertools import combinations
    for taps in combinations(range(0, span), 3):
        H = double_circulant(m, taps)   # C row weight 3 + identity = row weight 4
        n, k, d = classical_verify(H)
        if k != m: continue
        if best is None or d > best[1]:
            best = (taps, d)
    return best

SEED_BANK = {}   # name -> H, filled by build_bank()

def build_bank(dc_ms=(6, 8, 10, 12, 14, 16), verbose=True):
    bank = {}
    for m in dc_ms:
        got = best_dc_taps(m)
        if got:
            taps, d = got
            bank[f"H1_dc_m{m}_t{'-'.join(map(str, taps))}"] = double_circulant(m, taps)
    bank["H1b_extHam8"] = ext_hamming8()
    bank["H1c_rep3xextHam8"] = product_code(rep_H(3), ext_hamming8())
    bank["H1c_rep5xextHam8"] = product_code(rep_H(5), ext_hamming8())
    bank["H2_hamming74"] = hamming74()
    bank["H2_shortHam6"] = shortened_hamming([6])
    bank["H4_rep5"] = rep_H(5); bank["H4_rep9"] = rep_H(9)
    bank["H4_rep11"] = rep_H(11); bank["H4_rep13"] = rep_H(13)
    if verbose:
        print(f"{'seed':<24}{'[n,k,d]':<12}{'w':>3}{'deg':>4}{'colors':>7}{'q/log':>7}")
        for nm, H in bank.items():
            s = seed_stats(H)
            flag = "" if s["w"] <= 4 else "  REJECT w>4"
            print(f"{nm:<24}[{s['n']},{s['k']},{s['d']}]{'':<3}{s['w']:>3}{s['deg']:>4}"
                  f"{s['colors']:>7}{s['qlog']:>7.1f}{flag}")
    SEED_BANK.update(bank)
    return bank

if __name__ == "__main__":
    build_bank()
