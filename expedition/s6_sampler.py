#!/usr/bin/env python3
"""s6_sampler.py -- S6 stratified sampler, stages G0 + G1.

Governed by expedition/PREREG_sampler.md (commit f78e376).
G0 (PASSED on record 2026-07-10: m=3 z=1.1389, m=8 z=2.0894): plain Bernoulli
sampling from the referee's own DEM reduction (evaluator_v1.dem_to_matrices,
decompose_errors=False, flatten_loops=True), decoded with the referee's own
BP-OSD (evaluator_v1.make_bposd, verbatim), vs fresh-seed direct fom on
rep2(x)eh8 at m=3 and m=8. Criterion: |two-proportion z| < 3 at BOTH.

G1 (this stage): the stratified estimator (D2-D8: exact Poisson-binomial
stratum weights, exact conditional-Bernoulli draws, odds-weighted enumeration
of cheap strata, pilot+Neyman allocation, explicit tail bracket, rule-of-three
on zero-fail strata) vs the G0 plain-DEM estimator, same code, same
elevations. PASS iff 95% CIs overlap at BOTH elevations AND the stratified
point sits inside the plain estimator's 95% CI at m=3.

Registered budgets (fixed before the runs):
  G0 m=3: 40000/arm, seeds direct 20260710 / dem 60710
  G0 m=8: 20000/arm, seeds direct 20260711 / dem 60711
  G1 m=3: plain 40000 (seed 30710); stratified budget 30000, pilot 400,
          enum_cap 200000 (seed 30711)
  G1 m=8: plain 20000 (seed 30810); stratified budget 30000, pilot 400,
          enum_cap 200000 (seed 30811)

Usage:
  python -u s6_sampler.py --selftest
  python -u s6_sampler.py --g0 [--quick]
  python -u s6_sampler.py --g1 [--quick]      # --quick = smoke, NOT the gate
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

# ------------------------------------------------- stratified core (D2-D8) ---
def pb_suffix_table(priors, w_max):
    """R[i][w] = P(exactly w of mechanisms i..M-1 fire). Exact Poisson-binomial
    DP (D3). R[0] is the stratum-weight vector P(W=w), w=0..w_max; the tail
    P(W>w_max) is 1 - R[0].sum()."""
    M = len(priors)
    R = np.zeros((M + 1, w_max + 1))
    R[M, 0] = 1.0
    for i in range(M - 1, -1, -1):
        p = priors[i]
        R[i, 0] = (1 - p) * R[i + 1, 0]
        for w in range(1, w_max + 1):
            R[i, w] = (1 - p) * R[i + 1, w] + p * R[i + 1, w - 1]
    return R

def cond_bernoulli_draw(priors, R, w, rng):
    """Exact conditional-Bernoulli draw of a fault set given W=w (D4).
    Sequential inclusion: P(include i | r still needed from i..M-1) =
    p_i * R[i+1][r-1] / R[i][r]. Uniform w-subsets are BIASED and forbidden."""
    S = []
    r = w
    for i in range(len(priors)):
        if r == 0:
            break
        denom = R[i][r]
        if denom <= 0:          # numerically dead branch; remaining must fire
            S.extend(range(i, i + r)); r = 0; break
        p_inc = priors[i] * R[i + 1][r - 1] / denom
        if rng.random() < p_inc:
            S.append(i); r -= 1
    return S

def _decode_set(dec, Hd, O, cols):
    dets = np.zeros(Hd.shape[0], dtype=np.uint8)
    truth = np.zeros(O.shape[0], dtype=np.uint8)
    for j in cols:
        dets ^= Hd[:, j]; truth ^= O[:, j]
    e_hat = dec.decode(dets)
    pred = (O @ e_hat.astype(np.uint8)) % 2
    return int(np.any(pred != truth))

def stratified_estimate(Hd, O, priors, seed, budget=30000, pilot=400,
                        enum_cap=200000, tail_frac=0.01,
                        enum_mass_floor=0.01, force_enum_w=-1):
    """D2+D6+D7+D8: exact stratum weights, odds-weighted enumeration of cheap
    strata, pilot + Neyman allocation, explicit tail bracket, per-stratum
    variance, rule-of-three on zero-fail sampled strata.
    Returns dict with p_any point, 95% CI, UB bracket, per-stratum table."""
    from evaluator_v1 import make_bposd
    from itertools import combinations
    from math import comb
    rng = np.random.default_rng(seed)
    dec = make_bposd(Hd, priors)
    M = len(priors)
    lam = float(np.sum(priors))
    # stratum-weight vector out to negligible suffix
    w_hi = 8
    while True:
        R = pb_suffix_table(priors, w_hi)
        if 1.0 - R[0].sum() < 1e-15 or w_hi >= M:
            break
        w_hi = min(2 * w_hi + 4, M)
    Pw = R[0]                                    # P(W=w), w=0..w_hi
    order = np.argsort(Pw)[::-1]
    strata, covered = [], 0.0
    for w in order:                               # greedy cover by mass (D7)
        strata.append(int(w)); covered += Pw[w]
        if 1.0 - covered <= 1e-12:
            break
    strata = sorted(strata)
    table = {}
    for w in list(strata):                        # enumeration (D6)
        if w == 0:
            table[w] = dict(kind="enum", n=1,
                            fails=_decode_set(dec, Hd, O, []), f=None)
            table[w]["f"] = float(table[w]["fails"])
            continue
        if comb(M, w) <= enum_cap and (Pw[w] >= enum_mass_floor
                                       or w <= force_enum_w):
            # D6 addendum (dated 2026-07-10, pre-run): enumerate only strata
            # that are BOTH cheap (comb <= enum_cap) and mass-relevant
            # (P(w) >= enum_mass_floor), or force-enumerated low strata
            # (w <= force_enum_w; used by the G2 row to resolve prior P6).
            # Rationale: at registered caps, w=2 (139k decodes) would be
            # enumerated at m=3/8 where it carries ~2e-4 mass -- pure waste.
            # exact f_w: enumeration must weight subsets by odds (the D4
            # conditional law applies to enumeration too)
            logodds = np.log(priors) - np.log1p(-priors)
            num = den = 0.0
            for cols in combinations(range(M), w):
                wgt = float(np.exp(np.sum(logodds[list(cols)])))
                num += wgt * _decode_set(dec, Hd, O, cols); den += wgt
            table[w] = dict(kind="enum", n=comb(M, w), fails=None, f=num / den)
    sampled = [w for w in strata if w not in table]
    pilots = {}
    for w in sampled:
        pilots[w] = sum(
            _decode_set(dec, Hd, O, cond_bernoulli_draw(priors, R, w, rng))
            for _ in range(pilot))
    rem = max(budget - pilot * len(sampled), 0)   # Neyman (efficiency only)
    def sig(w):
        f = max(pilots[w] / pilot, 1.0 / pilot)
        return Pw[w] * np.sqrt(f * (1 - f))
    tot = sum(sig(w) for w in sampled) or 1.0
    for w in sampled:
        extra = int(rem * sig(w) / tot)
        f = pilots[w] + sum(
            _decode_set(dec, Hd, O, cond_bernoulli_draw(priors, R, w, rng))
            for _ in range(extra))
        n = pilot + extra
        table[w] = dict(kind="mc", n=n, fails=f, f=f / n)
    point = var = ub_extra = 0.0
    for w in strata:
        t = table[w]
        fw = t["f"]
        if t["kind"] == "mc":
            if t["fails"] == 0:
                ub_extra += Pw[w] * 3.0 / t["n"]  # rule-of-three (landmine 11)
                vw = 0.0
            else:
                vw = fw * (1 - fw) / t["n"]
        else:
            vw = 0.0
        point += Pw[w] * fw
        var += Pw[w] ** 2 * vw
    tail = float(1.0 - sum(Pw[w] for w in strata))  # f<=1 bound (D7)
    se = float(np.sqrt(var))
    return dict(p_any=float(point), se=se,
                ci95=[float(max(point - 1.96 * se, 0.0)),
                      float(point + 1.96 * se)],
                ub_bracket=point + tail + ub_extra, tail=tail,
                zero_fail_ub=ub_extra, lam=lam, strata=strata,
                per_stratum={int(w): {kk: (round(vv, 10) if isinstance(vv, float)
                                           else vv)
                                      for kk, vv in table[w].items()}
                             for w in strata},
                tail_ok=bool(tail <= tail_frac * max(point, 1e-300)))

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
    # (6) Poisson-binomial DP vs 2^12 brute force -- exact to 1e-12
    rng = np.random.default_rng(0)
    pr = rng.uniform(0.01, 0.3, 12)
    R = pb_suffix_table(pr, 12)
    brute = np.zeros(13)
    for mask in range(1 << 12):
        w = bin(mask).count("1")
        prob = np.prod(np.where([(mask >> j) & 1 for j in range(12)], pr, 1 - pr))
        brute[w] += prob
    assert np.max(np.abs(R[0] - brute)) < 1e-12, "PB-DP drift vs brute force"
    out["pb_dp_vs_brute"] = "ok"
    # (7) conditional-Bernoulli law: empirical inclusion marginals vs exact
    # P(j in S | W=w) = p_j * [PB of others at w-1] / P(W=w), M=6, w=3, 20k draws
    pr6 = rng.uniform(0.05, 0.5, 6)
    R6 = pb_suffix_table(pr6, 6)
    exact = np.zeros(6)
    for j in range(6):
        others = np.delete(pr6, j)
        exact[j] = pr6[j] * pb_suffix_table(others, 6)[0][2] / R6[0][3]
    draws = 20000
    emp = np.zeros(6)
    for _ in range(draws):
        for j in cond_bernoulli_draw(pr6, R6, 3, rng):
            emp[j] += 1
    emp /= draws
    zmax = np.max(np.abs(emp - exact) / np.sqrt(exact * (1 - exact) / draws))
    assert zmax < 5, f"conditional-law drift zmax={zmax:.2f}"
    out["cond_law_zmax"] = round(float(zmax), 3)
    # (8) stratified end-to-end micro: rep-3 at m=8 vs plain-DEM, 5-sigma
    strat = stratified_estimate(Hd3, O3, pr3, seed=3, budget=4000, pilot=200,
                                enum_cap=5000)
    p_plain = g0_dem_sample(Hd3, O3, pr3, 4000, seed=4)
    se_c = np.sqrt(strat["se"] ** 2 + p_plain * (1 - p_plain) / 4000)
    zs = (strat["p_any"] - p_plain) / se_c if se_c > 0 else 0.0
    assert abs(zs) < 5, f"stratified micro z={zs:.2f}"
    assert strat["tail_ok"], "micro tail not controlled"
    out["strat_micro_z"] = round(float(zs), 3)
    print(json.dumps(out)); print(json.dumps({"selftest": "PASS"}))

# --------------------------------------------------------------- G1 gate ---
G1_BUDGETS = {3.0: dict(plain_shots=40000, seed_plain=30710, seed_strat=30711,
                        budget=30000, pilot=400, enum_cap=200000),
              8.0: dict(plain_shots=20000, seed_plain=30810, seed_strat=30811,
                        budget=30000, pilot=400, enum_cap=200000)}

def run_g1(quick=False):
    """G1 (PREREG section 4): stratified vs plain-DEM on rep2(x)eh8 at m=3 and
    m=8. PASS iff 95% CIs overlap at BOTH elevations AND the stratified point
    sits inside the plain estimator's 95% CI at m=3."""
    H, k = build_rep2eh8()
    cells = {}
    for m, cfg in G1_BUDGETS.items():
        plain_shots = 2000 if quick else cfg["plain_shots"]
        budget = 3000 if quick else cfg["budget"]
        pilot = 150 if quick else cfg["pilot"]
        enum_cap = 5000 if quick else cfg["enum_cap"]
        t0 = time.time()
        circ = referee_circuit(H, m)
        Hd, O, priors = dem_matrices(circ)
        strat = stratified_estimate(Hd, O, priors, cfg["seed_strat"],
                                    budget=budget, pilot=pilot,
                                    enum_cap=enum_cap)
        t1 = time.time()
        p_pl = g0_dem_sample(Hd, O, priors, plain_shots, cfg["seed_plain"])
        t2 = time.time()
        se_pl = np.sqrt(max(p_pl * (1 - p_pl), 1e-300) / plain_shots)
        ci_pl = [float(max(p_pl - 1.96 * se_pl, 0.0)), float(p_pl + 1.96 * se_pl)]
        overlap = bool(strat["ci95"][0] <= ci_pl[1] and ci_pl[0] <= strat["ci95"][1])
        inside = bool(ci_pl[0] <= strat["p_any"] <= ci_pl[1])
        cells[m] = dict(overlap=overlap, inside=inside)
        print(json.dumps(dict(
            stage="G1", code="rep2(x)eh8 [16,4,8]", m=m, quick=quick,
            strat_p_any=strat["p_any"], strat_ci95=strat["ci95"],
            strat_tail=strat["tail"], strat_zero_fail_ub=strat["zero_fail_ub"],
            strat_lam=round(float(strat["lam"]), 4), strata=strat["strata"],
            per_stratum=strat["per_stratum"], tail_ok=strat["tail_ok"],
            plain_p_any=p_pl, plain_ci95=ci_pl, plain_shots=plain_shots,
            ci_overlap=overlap, point_inside_plain=inside,
            t_strat_s=round(t1 - t0, 1), t_plain_s=round(t2 - t1, 1),
            seeds=dict(strat=cfg["seed_strat"], plain=cfg["seed_plain"]))))
    ok = cells[3.0]["overlap"] and cells[8.0]["overlap"] and cells[3.0]["inside"]
    label = ("G1 PASS" if ok else "G1 FAIL") + \
            (" (quick smoke -- NOT the gate)" if quick else "")
    print(json.dumps({"verdict": label}))

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


# --------------------------------------------------------------- G2 gate ---
# rep2(x)eh8 row anchors: direct-MC truth from s5_rankmap_data.json (F=75
# fails at SHOTS=200000, ROUNDS=8, k=4; re-verified by Code pre-commit at
# f78e376). Garwood exact Poisson 95% on F=75 -> counts [58.9923, 94.0131]
# -> p_any [2.9496e-4, 4.7007e-4] -> eps via the referee's own conventions.
# Bands computed offline (scipy not in the canonical venv) and hardcoded:
G2_REP2EH8 = dict(
    name="rep2(x)eh8 [16,4,8]", k=4, m=1.0,
    eps_truth=1.1721359996663683e-05,           # == G2_ANCHORS entry
    eps_band=[9.219154925688144e-06, 1.4693655943642803e-05],
    p_any_band=[0.00029496128850725725, 0.0004700657472441638])
G2_BUDGET = dict(seed_strat=110710, budget=400000, pilot=1000,
                 enum_cap=200000, force_enum_w=2, enum_mass_floor=0.01)

def eps_from_pany(p_any, k):
    """D9: conversion by the referee's own functions -- import, don't rederive."""
    from evaluator_v1 import per_round
    pk = 1 - (1 - p_any) ** (1.0 / k)
    return per_round(pk, ROUNDS)

def k1_evaluate(Pw_f_table):
    """K1 (PREREG section 5): strata carrying >=80% of sum P(w)*f_w all have
    f_w < 1e-3 => conditioning failed to enrich; design killed for regime."""
    contrib = [(w, t["pw"] * t["f"]) for w, t in Pw_f_table.items()
               if t["f"] and t["f"] > 0]
    total = sum(c for _, c in contrib)
    if total <= 0:
        return dict(k1_fired=None, note="no failing strata measured")
    contrib.sort(key=lambda x: -x[1])
    top, cum = [], 0.0
    for w, c in contrib:
        top.append(w); cum += c
        if cum >= 0.8 * total:
            break
    fmax = max(Pw_f_table[w]["f"] for w in top)
    return dict(k1_fired=bool(fmax < 1e-3), top_strata=top,
                f_max_at_top=float(fmax))

def run_g2_rep2eh8(quick=False):
    """G2 row 1 (PREREG section 4): the sampler vs the directly-measured m=1
    truth for rep2(x)eh8. PASS iff (a) rel 95% half-width (bracket-inflated)
    <= 25% -- else INCONCLUSIVE; (b) sampler interval intersects the MC band;
    (c) sampler point inside the MC band. force_enum_w=2 resolves prior P6."""
    cfg = dict(G2_BUDGET)
    if quick:
        cfg.update(budget=20000, pilot=300, enum_cap=5000, force_enum_w=1)
    H, k = build_rep2eh8()
    t0 = time.time()
    circ = referee_circuit(H, G2_REP2EH8["m"])
    Hd, O, priors = dem_matrices(circ)
    strat = stratified_estimate(Hd, O, priors, cfg["seed_strat"],
                                budget=cfg["budget"], pilot=cfg["pilot"],
                                enum_cap=cfg["enum_cap"],
                                enum_mass_floor=cfg["enum_mass_floor"],
                                force_enum_w=cfg["force_enum_w"])
    t1 = time.time()
    p = strat["p_any"]
    lo = strat["ci95"][0]
    hi = max(strat["ci95"][1], strat["ub_bracket"])   # bracket-inflated (D7/D8)
    rel = (hi - lo) / (hi + lo) if (hi + lo) > 0 else 1.0
    eps_pt, eps_lo, eps_hi = (eps_from_pany(x, k) for x in (p, lo, hi))
    band = G2_REP2EH8["eps_band"]
    conclusive = bool(rel <= 0.25)
    intersects = bool(eps_lo <= band[1] and band[0] <= eps_hi)
    inside = bool(band[0] <= eps_pt <= band[1])
    if not conclusive:
        cell = "INCONCLUSIVE"
    else:
        cell = "PASS" if (intersects and inside) else "FAIL"
    # K1 diagnostic from the measured profile
    prof = {}
    R = pb_suffix_table(priors, max(strat["strata"]))
    for w in strat["strata"]:
        t = strat["per_stratum"][w]
        prof[w] = dict(pw=float(R[0][w]), f=t.get("f"))
    k1 = k1_evaluate(prof)
    # P6 resolution: f_1, f_2 exact if enumerated
    p6 = {w: strat["per_stratum"].get(w, {}).get("f")
          for w in (1, 2)
          if strat["per_stratum"].get(w, {}).get("kind") == "enum"}
    print(json.dumps(dict(
        stage="G2", row=G2_REP2EH8["name"], m=1.0, quick=quick,
        p_any=p, p_any_ci95=strat["ci95"], ub_bracket=strat["ub_bracket"],
        tail=strat["tail"], zero_fail_ub=strat["zero_fail_ub"],
        lam=round(float(strat["lam"]), 4),
        eps=eps_pt, eps_interval=[eps_lo, eps_hi], rel_halfwidth=round(rel, 4),
        mc_band_eps=band, criterion_a_conclusive=conclusive,
        criterion_b_intersects=intersects, criterion_c_point_inside=inside,
        cell=cell + (" (quick smoke -- NOT the gate)" if quick else ""),
        k1=k1, p6_exact_f=p6, per_stratum=strat["per_stratum"],
        decode_budget=cfg["budget"], seeds=dict(strat=cfg["seed_strat"]),
        t_s=round(t1 - t0, 1))))
    print(json.dumps({"verdict": ("G2 rep2(x)eh8 " + cell) +
                      (" (quick smoke -- NOT the gate)" if quick else "")}))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--g0", action="store_true")
    ap.add_argument("--g1", action="store_true")
    ap.add_argument("--g2-rep2eh8", action="store_true")
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.g0:
        run_g0(quick=a.quick)
    elif a.g1:
        run_g1(quick=a.quick)
    elif a.g2_rep2eh8:
        run_g2_rep2eh8(quick=a.quick)
    else:
        ap.print_help()
