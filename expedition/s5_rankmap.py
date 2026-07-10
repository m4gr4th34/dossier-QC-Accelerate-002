#!/usr/bin/env python3
"""s5_rankmap.py -- rank-stability map: direct eps for a known-code ladder at a
ladder of noise elevations, one frozen instrument, depth-matched.

WHY (Entries 002-006): the deep-eps ranking is the quantity FTQC needs; strong
codes floor at m=1; every single-axis proxy died. The surviving path is the
calibrated sub-threshold model eps ~ A*(m/m*)^t with all three parameters
measured -- but sub-threshold curves CROSS, so first we must MAP where
rankings invert vs elevation, and where floors start, on codes whose truth is
measurable. This experiment produces that map. No steering, no search --
pure instrument characterization on knowns.

Codes: the landmark ladder + the Campaign 3 find + rep comparators.
Elevations: m in (1, 1.5, 2, 3, 5, 8) on k_ratio (p_m held at GM -- the
single-knob convention from the sweep saga). Depth-matched: same rounds,
same shots for every (code, m) cell. Flooring cells reported as floors
(eps=0 at S shots -> rule-of-three UB 3/S), never as ranks.
"""
import sys, json, time
sys.path.insert(0, ".")
import numpy as np

GM = dict(nbar=11.0, k_ratio=1e-4, p_m=6e-3)
ELEV = (1.0, 1.5, 2.0, 3.0, 5.0, 8.0)
SHOTS = 200000
ROUNDS = 8

def eps_at(H, k, m, seed=7):
    from gm_css import fom
    Hz = np.zeros((0, H.shape[1]), dtype=np.uint8)
    pk, _, _, _ = fom(H, Hz, k, ROUNDS, GM["p_m"], GM["nbar"],
                      GM["k_ratio"] * m, "xonly", SHOTS, seed=seed)
    return pk

def build_ladder():
    from s2_seeds import product_code, rep_H, ext_hamming8
    L = [
        ("rep3(x)eh8 [24,4,12] (Ch4 winner)", product_code(rep_H(3), ext_hamming8()), 4),
        ("rep4(x)eh8 [32,4,16]",              product_code(rep_H(4), ext_hamming8()), 4),
        ("rep2(x)eh8 [16,4,8]",               product_code(rep_H(2), ext_hamming8()), 4),
        ("eh8(x)eh8 [64,16,16] (frontier)",   product_code(ext_hamming8(), ext_hamming8()), 16),
        ("rep3(x)rep3 [9,1,9]",               product_code(rep_H(3), rep_H(3)), 1),
        ("rep-7 [7,1,7]",                     rep_H(7), 1),
        ("rep-13 [13,1,13]",                  rep_H(13), 1),
    ]
    # Campaign 3 find, if its recovered H is still on disk
    try:
        H = np.load("/tmp/best3412.npy")
        L.append(("C3 find [34,6,12]", H, 6))
    except Exception:
        print("(C3 find /tmp/best3412.npy not present -- skipping)")
    return L

def main():
    ladder = build_ladder()
    floor_ub = 3.0 / SHOTS
    results = {}
    t0 = time.time()
    for nm, H, k in ladder:
        row = {}
        for m in ELEV:
            t1 = time.time()
            e = eps_at(H, k, m)
            row[m] = e
            print(f"{nm:38s} m={m:<4} eps={e:.3e}"
                  + ("  FLOOR (UB %.1e)" % floor_ub if e == 0 else "")
                  + f"  [{time.time()-t1:.0f}s]", flush=True)
        results[nm] = row
    print(f"\ntotal {time.time()-t0:.0f}s")

    # rank tables per elevation (floored cells excluded from ranking, listed)
    print("\n=== RANKS PER ELEVATION (per-logical eps ascending; floors excluded) ===")
    for m in ELEV:
        meas = sorted(((results[nm][m], nm) for nm in results if results[nm][m] > 0))
        fl = [nm for nm in results if results[nm][m] == 0]
        print(f"\nm={m}:")
        for i, (e, nm) in enumerate(meas, 1):
            print(f"  {i}. {nm}  eps={e:.3e}")
        if fl:
            print(f"  FLOORED (unrankable at this budget): {', '.join(fl)}")

    with open("/tmp/rankmap.json", "w") as f:
        json.dump({nm: {str(m): v for m, v in row.items()}
                   for nm, row in results.items()}, f, indent=2)
    print("\nsaved /tmp/rankmap.json -- hand the tables to the strategy room")

if __name__ == "__main__":
    main()
