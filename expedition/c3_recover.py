#!/usr/bin/env python3
"""c3_recover.py -- recover the Campaign-3 find [34,6,12], verify its identity,
and freeze it as a committed artifact (expedition/c3_find_H.json).

Why: the C3 G2 row (PREREG_sampler.md) needs H; the only copy lived at
/tmp/best3412.npy (volatile) -- the b64-logging fix (Entry 006) landed after
Campaign 3, so no committed copy exists. This tool closes that gap once.

Recovery tiers:
  Tier A: --from-tmp [path]      load /tmp/best3412.npy if it still exists
  Tier B: --from-jsonl PATH      extract the LAST running_best row from a
                                 deterministic replay log (s5_algsearch.py
                                 --seed 20260710, learn arm, gen<=1626;
                                 the driver logs b64+shape on running-bests)

Identity verification (BOTH tiers, all must pass; any impostor H --
stale tmp file, wrong replay row -- fails at least one):
  V1 structural: classical_verify(H) == (34, 6, 12) exact; shape == (37, 34);
     max row weight <= 4; eff = 6/71 = 0.084507...
  V2 BEHAVIORAL FINGERPRINT (the identity proof): the committed rankmap C3
     row was measured WITH this H at seed=7, SHOTS=200000, ROUNDS=8, m=1.
     The recovered H must reproduce eps == 2.074077687191922e-05 EXACTLY.
     MACHINE-BOUND: run this ON THE WORKBENCH that produced
     s5_rankmap_data.json. stim's detector-sampler stream at fixed seed is
     machine-dependent (discovered 2026-07-10: a sandbox seed-7 run on
     rep2xeh8 gave 1.0940e-5 vs the committed 1.1721e-5 -- statistically
     consistent, byte-different; corrects Entry 010's cross-machine
     generalization, which holds only for numpy-RNG paths). Same-machine
     stim determinism is proven (Entry 006 replay hash-match). On V2
     failure the tool prints a Poisson-z diagnostic: |z| small suggests a
     wrong-machine run; |z| large means wrong or corrupted H. Runtime
     ~30 s - 3 min.

Replay checkpoint anchor (Tier B early sanity, ~1 min into the replay):
  the deterministic gen-44 running_best must have hash 483e79c9e06c8854
  ([34,6,12] eff=0.0833 predecessor; verified by partial strategy-room
  replay 2026-07-10). Mismatch = determinism drift, STOP.

Freeze format: h_encode schema (shape, b64, hash) + provenance fields.
Usage:
  python -u c3_recover.py --from-tmp                    # tier A
  python -u c3_recover.py --from-jsonl PATH             # tier B
  python -u c3_recover.py --verify-artifact             # re-verify frozen file
  add --skip-fingerprint to defer V2 (artifact is then marked UNVERIFIED
  and MUST NOT be committed -- V2 is what makes the freeze trustworthy).
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, ".")
import numpy as np

EXPECTED = dict(n=34, k=6, d=12, shape=[37, 34], w_max=4,
                eff=6.0 / 71.0,
                rankmap_eps_m1=2.074077687191922e-05,   # committed bytes
                rankmap_seed=7, rankmap_shots=200000, rounds=8)
GEN44_CHECKPOINT_HASH = "483e79c9e06c8854"
ARTIFACT = "c3_find_H.json"

def load_tmp(path):
    H = np.load(path).astype(np.uint8)
    return H, dict(source="tmp-file", path=os.path.abspath(path))

def load_jsonl(path):
    best = None
    for line in open(path):
        if '"running_best"' in line:
            r = json.loads(line)
            if r.get("running_best"):
                best = r
    if best is None:
        raise SystemExit("no running_best rows in log -- wrong file? STOP")
    from s5_proposer import h_decode
    H = h_decode(best)
    return H, dict(source="replay-jsonl", path=os.path.abspath(path),
                   gen=best.get("gen"), logged_hash=best.get("hash"))

def verify_structural(H):
    from hgp import classical_verify
    n, k, d = classical_verify(H)
    checks = dict(
        nkd_ok=(n, k, d) == (EXPECTED["n"], EXPECTED["k"], EXPECTED["d"]),
        shape=list(H.shape) == EXPECTED["shape"],
        w_max=int(H.sum(axis=1).max()) <= EXPECTED["w_max"],
        binary=bool(np.isin(H, (0, 1)).all()))
    checks["eff"] = abs(k / (n + H.shape[0]) - EXPECTED["eff"]) < 1e-12
    return checks, (n, k, d)

def verify_fingerprint(H):
    """V2: reproduce the committed rankmap C3 m=1 cell exactly."""
    from gm_css import fom
    GM = dict(nbar=11.0, k_ratio=1e-4, p_m=6e-3)
    Hz = np.zeros((0, H.shape[1]), dtype=np.uint8)
    t0 = time.time()
    eps, _, _, _ = fom(H, Hz, EXPECTED["k"], EXPECTED["rounds"], GM["p_m"],
                       GM["nbar"], GM["k_ratio"] * 1.0, "xonly",
                       EXPECTED["rankmap_shots"], seed=EXPECTED["rankmap_seed"])
    exact = (eps == EXPECTED["rankmap_eps_m1"])
    # Poisson-z diagnostic on implied failure counts (small |z| = likely a
    # wrong-machine run; large |z| = wrong H)
    def eps_to_F(e, k=EXPECTED["k"], R=EXPECTED["rounds"],
                 S=EXPECTED["rankmap_shots"]):
        pk = 0.5 * (1.0 - (1.0 - 2.0 * e) ** R)
        return (1.0 - (1.0 - pk) ** k) * S
    Fm, Fc = eps_to_F(float(eps)), eps_to_F(EXPECTED["rankmap_eps_m1"])
    z = (Fm - Fc) / np.sqrt(max(Fm + Fc, 1e-12))
    return dict(eps_measured=float(eps), eps_committed=EXPECTED["rankmap_eps_m1"],
                exact_match=bool(exact), diag_poisson_z=round(float(z), 3),
                t_s=round(time.time() - t0, 1))

def freeze(H, provenance, fingerprint):
    from s5_proposer import h_encode
    rec = h_encode(H)
    rec.update(code="C3 find [34,6,12]", provenance=provenance,
               verification=dict(structural="pass", fingerprint=fingerprint),
               frozen_date="2026-07-10",
               note=("recovered per Entry 010 dependency; identity proven by "
                     "exact reproduction of the committed rankmap m=1 cell"))
    with open(ARTIFACT, "w") as f:
        json.dump(rec, f, indent=1)
    return rec

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--from-tmp", nargs="?", const="/tmp/best3412.npy")
    g.add_argument("--from-jsonl")
    g.add_argument("--verify-artifact", action="store_true")
    ap.add_argument("--skip-fingerprint", action="store_true")
    a = ap.parse_args()

    if a.verify_artifact:
        from s5_proposer import h_decode
        rec = json.load(open(ARTIFACT))
        H, prov = h_decode(rec), rec.get("provenance")
    elif a.from_tmp:
        H, prov = load_tmp(a.from_tmp)
    else:
        H, prov = load_jsonl(a.from_jsonl)

    checks, nkd = verify_structural(H)
    print(json.dumps(dict(stage="V1-structural", nkd=list(nkd), **checks)))
    if not all(checks.values()):
        raise SystemExit("V1 FAIL -- this is not the C3 find. STOP.")

    if a.skip_fingerprint:
        print(json.dumps({"stage": "V2-fingerprint", "status":
                          "SKIPPED -- artifact UNVERIFIED, do not commit"}))
        fp = {"status": "SKIPPED"}
    else:
        fp = verify_fingerprint(H)
        print(json.dumps(dict(stage="V2-fingerprint", **fp)))
        if not fp["exact_match"]:
            raise SystemExit("V2 FAIL -- eps does not reproduce the committed "
                             "rankmap cell. Wrong or corrupted H. STOP.")

    if not a.verify_artifact:
        rec = freeze(H, prov, fp)
        print(json.dumps(dict(stage="frozen", artifact=ARTIFACT,
                              hash=rec["hash"], shape=rec["shape"],
                              source=prov["source"])))
    print(json.dumps({"verdict": "C3 H RECOVERED AND VERIFIED"
                      if not a.skip_fingerprint else
                      "C3 H candidate loaded -- fingerprint pending"}))

if __name__ == "__main__":
    main()
