#!/usr/bin/env python3
"""s6_sampler.py -- S6 stratified sampler, stage G0 ONLY (DEM-equivalence).

Governed by expedition/PREREG_sampler.md (commit f78e376). This stage builds
NO stratification machinery (D2-D4 do not exist here to blame): it validates
that plain Bernoulli sampling from the referee's own DEM reduction
(evaluator_v1.dem_to_matrices on decompose_errors=False, flatten_loops=True),
decoded with the referee's own BP-OSD (evaluator_v1.make_bposd, verbatim),
reproduces a fresh-seed direct fom run on rep2(x)eh8 at m=3 and m=8.

G0 PASS criterion (PREREG section 4): |two-proportion z| < 3 on p_any at BOTH
elevations. Anything else is a FAIL and gets its own entry.

Registered G0 budgets (dated addendum-level detail, fixed before the run):
  m=3: 40000 shots per arm, direct seed 20260710, DEM seed 60710
  m=8: 20000 shots per arm, direct seed 20260711, DEM seed 60711

Usage:
  python -u s6_sampler.py --selftest
  python -u s6_sampler.py --g0                # both elevations, registered budgets
  python -u s6_sampler.py --g0 --quick        # reduced-shot smoke (NOT the gate)
Output: JSONL lines to stdout (python -u; an "empty log" is buffering).
"""
import argparse
import inspect
import json
import sys
import time

sys.path.insert(0, ".")
import numpy as np

# ---------------------------------------------------------------- anchors ---
# Landmark gate (PREREG section 7 / landmine 7): these constants are the four
# frozen G2 truths from s5_rankmap_data.json @ f78e376 and the referee decoder
# config. The selftest asserts them; a driver whose anchors drift is DISQUALIFIED.
G2_ANCHORS = {
    "rep2(x)eh8 [16,4,8]":  1.1721359996663683e-05,
    "C3 find [34,6,12]":    2.074077687191922e-05,
    "rep3(x)eh8 [24,4,12]": 3.125018555039105e-07,
    "eh8(x)eh8 [64,16,16]": 7.812540891993791e-08,
}
DECODER_ANCHOR = ('bp_method="ms"', "max_iter=30", 'osd_method="osd_e"',
                  "osd_order=4")
GM = dict(nbar=11.0, k_ratio=1e-4, p_m=6e-3)   # rankmap GM operating point
ROUNDS = 8
G0_BUDGETS = {3.0: dict(shots=40000, seed_direct=20260710, seed_dem=60710),
              8.0: dict(shots=20000, seed_direct=20260711, seed_dem=60711)}

# ------------------------------------------------------------------- code ---
def build_rep2eh8():
    """Exactly rankmap's construction: product_code(rep_H(2), ext_hamming8()), k=4."""
    from s2_seeds import product_code, rep_H, ext_hamming8
    H = product_code(rep_H(2), ext_hamming8())
    return H, 4

def referee_circuit(H, m):
    """The frozen referee circuit at elevation m -- mirrors rankmap eps_at."""
    from gm_css import gm_css_circuit
    Hz = np.zeros((0, H.shape[1]), dtype=np.uint8)
    circ, _, _ = gm_css_circuit(H, Hz, ROUNDS, GM["p_m"], GM["nbar"],
                                GM["k_ratio"] * m, "xonly")
    return circ

def dem_matrices(circ):
    """The referee's own reduction, same flags as logical_rate (verbatim)."""
    from evaluator_v1 import dem_to_matrices
    dem = circ.detector_error_model(decompose_errors=False, flatten_loops=True)
    return dem_to_matrices(dem)

# --------------------------------------------------------------- G0 arms ---
def g0_direct(H, k, m, shots, seed):
    """Fresh-seed direct referee run; returns raw p_any (not per-logical eps)."""
    from gm_css import fom
    Hz = np.zeros((0, H.shape[1]), dtype=np.uint8)
    _, p_any, _, _ = fom(H, Hz, k, ROUNDS, GM["p_m"], GM["nbar"],
                         GM["k_ratio"] * m, "xonly", shots, seed=seed)
    return p_any

def g0_dem_sample(Hd, O, priors, shots, seed):
    """Plain (unstratified) Bernoulli sampling from the DEM mechanisms,
    decoded with the referee's decoder object. Returns p_any."""
    from evaluator_v1 import make_bposd
    rng = np.random.default_rng(seed)
    dec = make_bposd(Hd, priors)
    M = len(priors)
    fails = 0
    decode_errors = 0
    for s in range(shots):
        fired = rng.random(M) < priors
        dets = (Hd @ fired.astype(np.uint8)) % 2
        truth = (O @ fired.astype(np.uint8)) % 2
        try:
            e_hat = dec.decode(dets.astype(np.uint8))
        except Exception:
            decode_errors += 1          # fail LOUDLY below; silent skip = bias
            continue
        pred = (O @ e_hat.astype(np.uint8)) % 2
        fails += int(np.any(pred != truth))
    if decode_errors:
        raise RuntimeError(f"{decode_errors} decoder exceptions -- run is void")
    return fails / shots

def two_prop_z(p1, n1, p2, n2):
    x1, x2 = p1 * n1, p2 * n2
    p = (x1 + x2) / (n1 + n2)
    se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return 0.0 if se == 0 else (p1 - p2) / se

# --------------------------------------------------------------- selftest ---
def selftest():
    out = {"stage": "selftest"}
    # (1) G2 anchors verbatim against the committed rankmap data if present
    try:
        d = json.load(open("s5_rankmap_data.json"))
        lookup = {"rep2(x)eh8 [16,4,8]": "rep2(x)eh8 [16,4,8]",
                  "C3 find [34,6,12]": "C3 find [34,6,12]",
                  "rep3(x)eh8 [24,4,12]": "rep3(x)eh8 [24,4,12] (Ch4 winner)",
                  "eh8(x)eh8 [64,16,16]": "eh8(x)eh8 [64,16,16] (frontier)"}
        for k, kk in lookup.items():
            assert abs(d[kk]["1.0"] - G2_ANCHORS[k]) < 1e-18, f"anchor drift: {k}"
        out["anchors_vs_json"] = "ok"
    except FileNotFoundError:
        out["anchors_vs_json"] = "json not on path (hardcoded anchors only)"
    # (2) decoder config anchored to the referee source, not to memory
    import evaluator_v1
    src = inspect.getsource(evaluator_v1.make_bposd)
    for tok in DECODER_ANCHOR:
        assert tok in src, f"decoder config drift: {tok} missing"
    out["decoder_anchor"] = "ok"
    # (3) structural: DEM matrices of rep2(x)eh8 at m=8
    H, k = build_rep2eh8()
    assert H.shape == (16, 16) and k == 4
    circ = referee_circuit(H, 8.0)
    Hd, O, priors = dem_matrices(circ)
    assert Hd.shape[1] == O.shape[1] == len(priors)
    assert O.shape[0] == k, f"observables {O.shape[0]} != k {k}"
    assert np.all((priors > 0) & (priors < 1))
    out["dem"] = dict(mechanisms=int(len(priors)), detectors=int(Hd.shape[0]))
    # (4) zero-fault sanity: empty syndrome decodes to no logical flip
    from evaluator_v1 import make_bposd
    dec = make_bposd(Hd, priors)
    e_hat = dec.decode(np.zeros(Hd.shape[0], dtype=np.uint8))
    assert not np.any((O @ e_hat.astype(np.uint8)) % 2), "zero-syndrome flip"
    out["zero_syndrome"] = "ok"
    # (5) micro cross-check on rep-3 at m=8 (cheap, deterministic, loose 5-sigma)
    from s2_seeds import rep_H
    H3 = rep_H(3)
    c3 = referee_circuit(H3, 8.0)
    Hd3, O3, pr3 = dem_matrices(c3)
    p_dem = g0_dem_sample(Hd3, O3, pr3, 2000, seed=1)
    p_dir = g0_direct(H3, 1, 8.0, 2000, seed=2)
    z = two_prop_z(p_dem, 2000, p_dir, 2000)
    assert abs(z) < 5, f"micro cross-check z={z:.2f}"
    out["micro_z"] = round(float(z), 3)
    print(json.dumps(out)); print(json.dumps({"selftest": "PASS"}))

# --------------------------------------------------------------- G0 gate ---
def run_g0(quick=False):
    H, k = build_rep2eh8()
    verdicts = []
    for m, cfg in G0_BUDGETS.items():
        shots = 2000 if quick else cfg["shots"]
        t0 = time.time()
        circ = referee_circuit(H, m)
        Hd, O, priors = dem_matrices(circ)
        p_dem = g0_dem_sample(Hd, O, priors, shots, cfg["seed_dem"])
        t1 = time.time()
        p_dir = g0_direct(H, k, m, shots, cfg["seed_direct"])
        t2 = time.time()
        z = two_prop_z(p_dem, shots, p_dir, shots)
        ok = abs(z) < 3
        verdicts.append(ok)
        print(json.dumps(dict(
            stage="G0", code="rep2(x)eh8 [16,4,8]", m=m, shots=shots,
            quick=quick, mechanisms=int(len(priors)),
            p_any_dem=p_dem, p_any_direct=p_dir, z=round(float(z), 4),
            criterion="|z|<3", cell="PASS" if ok else "FAIL",
            t_dem_s=round(t1 - t0, 1), t_direct_s=round(t2 - t1, 1),
            seeds=dict(dem=cfg["seed_dem"], direct=cfg["seed_direct"]))))
    label = ("G0 PASS" if all(verdicts) else "G0 FAIL") + \
            (" (quick smoke -- NOT the gate)" if quick else "")
    print(json.dumps({"verdict": label}))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--g0", action="store_true")
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.g0:
        run_g0(quick=a.quick)
    else:
        ap.print_help()
