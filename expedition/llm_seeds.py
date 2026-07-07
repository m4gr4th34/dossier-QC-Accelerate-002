#!/usr/bin/env python3
"""
llm_seeds.py — the structured-proposal layer, round 1: LLM-composed classical seeds.

METHOD: the author (an LLM) PROPOSES classical parity-check matrices aiming at
(k >= 2, d >= 3, low column weight so the HGP stays under wmax <= 6). The classical
verifier MEASURES (n, k, d) exhaustively — proposals are hypotheses, the verifier is
the referee, and rejected seeds are printed, not hidden.
Accepted seeds are hypergraph-multiplied with repetition (long side on Z, the cat
orientation) and enter BAND 2 (n <= 45) against scaled k=1 incumbents.
QUESTION: does rate pay per LOGICAL qubit under bias at this scale?
"""
import numpy as np, time
from verify_code import verify
from fom import phase_rep, shor_ML, logical_error_rate
from hgp import hgp, c_rep, classical_verify, HAMMING74

# ---- proposed seeds (hypotheses; the verifier decides) ----
PROPOSALS = {
  # A: last column of Hamming(7,4) deleted — puncturing may cost distance; measure it.
  "punctHam6": HAMMING74[:, :6].copy(),
  # B: two disjoint weight-3 checks + one stitching check
  "stitch6": np.array([[1,1,1,0,0,0],
                       [0,0,0,1,1,1],
                       [1,0,1,1,0,1]], dtype=np.uint8),
  # C: ring of weight-3 checks on 6 bits (circulant)
  "ring6":   np.array([[1,1,0,1,0,0],
                       [0,1,1,0,1,0],
                       [0,0,1,1,0,1],
                       [1,0,0,0,1,1]], dtype=np.uint8),
  # D: [8,2] attempt — two rate bits, aiming d=4, weight <=3 columns
  "oct8":    np.array([[1,1,1,0,0,0,0,0],
                       [0,1,1,1,0,0,0,0],
                       [0,0,0,0,1,1,1,0],
                       [0,0,0,0,0,1,1,1],
                       [1,0,0,1,1,0,0,1]], dtype=np.uint8),
}

if __name__ == "__main__":
    accepted = {}
    print("SEED REFEREEING (classical verifier is the judge):")
    for nm, H in PROPOSALS.items():
        n, k, d = classical_verify(H)
        colw = int(H.sum(axis=0).max()); roww = int(H.sum(axis=1).max())
        ok = (k >= 2 and (d or 0) >= 3 and colw <= 3 and roww <= 4)
        print(f"  {'ACCEPT' if ok else 'reject'} {nm}: [{n},{k},{d}] colw={colw} roww={roww}")
        if ok: accepted[nm] = H
    if not accepted:
        print("no seeds accepted — kept negative for this proposal round"); raise SystemExit(0)

    # ---- band 2 entrants ----
    E = {"rep-33": phase_rep(33), "shor3x11": shor_ML(3, 11),
         "hgp r6r4": hgp(c_rep(6), c_rep(4)), "hgp r7r3": hgp(c_rep(7), c_rep(3))}
    for nm, H in accepted.items():
        for a in (4, 5):
            E[f"hgp r{a}x{nm}"] = hgp(c_rep(a), H)   # rep on the Z-long side
    P_PHYS, WMAX, SHOTS = 0.01, 6, 10000
    print(f"\nBAND 2 (n<=45, wmax<={WMAX}) p={P_PHYS} shots={SHOTS} | per-logical rates")
    etas = [30, 100, 300]
    print(f"{'code':<18}{'n':>4}{'k':>3}{'dx':>4}{'dz':>4}{'w':>3}", end="")
    for eta in etas: print(f" | eta={eta:<6}", end="")
    print()
    t0 = time.time(); rows = []
    for nm, (Hx, Hz) in E.items():
        v = verify(Hx, Hz)
        if not (v["valid"] and v["wmax"] <= WMAX and v["n"] <= 45 and v["k"] >= 1):
            print(f"  gate EXCLUDED {nm}: {v.get('n')}q wmax={v.get('wmax')}"); continue
        dxs = f"{v['dx']}{'' if v['dx_exact'] else '~'}"; dzs = f"{v['dz']}{'' if v['dz_exact'] else '~'}"
        line = f"{nm:<18}{v['n']:>4}{v['k']:>3}{dxs:>4}{dzs:>4}{v['wmax']:>3}"
        vals = []
        for i, eta in enumerate(etas):
            P = logical_error_rate(Hx, Hz, P_PHYS, eta, shots=SHOTS, seed=57 + i)
            ci = 1.96 * np.sqrt(max(P * (1 - P), 1e-12) / SHOTS)
            Pk = 1 - (1 - P) ** (1.0 / v["k"])
            vals.append(Pk); line += f" | {Pk:.5f}±{ci:.5f}"
        rows.append((nm, v, vals)); print(line, flush=True)
    print(f"[{time.time()-t0:.0f}s]")
    for i, eta in enumerate(etas):
        best = min(rows, key=lambda r: r[2][i])
        print(f"eta={eta}: best per-logical = {best[0]} [[{best[1]['n']},{best[1]['k']}]] at {best[2][i]:.5f}")
    print("\nHONESTY NOTE: code-capacity model, small-n regime; family-level behavior is "
          "calibration against known theory. Novelty claims wait for the circuit-level evaluator.")
