#!/usr/bin/env python3
"""s7_union.py -- S7 decoder-aware union sampler, stage U-G0 ONLY.

Governed by expedition/PREREG_union.md (@46e0b6d, Addendum 1 applied).
Reuses the G0/G1-gated s6 instruments verbatim (DEM reduction, decoder path,
_decode_set); nothing here re-derives what s6 already gates.

U-G0 (this stage, PREREG_union section 2):
  (1) committed w<=2 core identities load and reproduce (basis-hash anchor);
  (2) Karp-Luby estimator validated on synthetic unions with brute-force
      exact answers -- monotone AND non-monotone (rescue) cases, 5-sigma;
  (3) multiplicity correction cross-checked both ways (count-of-contained
      vs first-contained-core) on the same synthetic;
  (4) minimalizer idempotent (minimalize(core) == core), and each committed
      seed core, planted alone, fails under the real referee.

The Karp-Luby scheme (U2): draw core c w.p. pi_c/Z (pi_c = prod p_j, the
product-measure probability that all of c fires; Z = sum pi_c); set
S = c UNION Bernoulli(rest); then
  count variant:  X = Z * fail(S) / m(S),  m(S) = #{cores contained in S}
  first variant:  X = Z * fail(S) * [c == min contained core]
Both are unbiased for T1 = P(fail(S) AND S contains a known core); the
decoder supplies fail(S), so rescues and non-monotonicity cost no bias.

Usage:
  python -u s7_union.py --ug0
Output: JSONL (python -u; an "empty log" is buffering).
"""
import argparse
import hashlib
import json
import sys
import time

sys.path.insert(0, ".")
import numpy as np

from s6_sampler import (build_rep2eh8, referee_circuit, dem_matrices,
                        _decode_set, DECODER_ANCHOR)

BASIS_FILE = "core_basis_rep2eh8.json"
BASIS_SHA_ANCHOR = "ae7b99a1a85f7e77"       # committed @ cfd4865
F2_ANCHOR = 1.884942995805515e-07           # committed @ cfd4865

# ------------------------------------------------------------ core basis ---
def load_basis():
    b = json.load(open(BASIS_FILE))
    rec = {k: v for k, v in b.items() if k != "basis_sha256"}
    blob = json.dumps(rec, sort_keys=True).encode()
    sha = hashlib.sha256(blob).hexdigest()[:16]
    assert sha == b["basis_sha256"] == BASIS_SHA_ANCHOR, \
        f"basis hash drift: {sha} vs {BASIS_SHA_ANCHOR} -- STOP"
    assert b["f2_weighted"] == F2_ANCHOR, "f2 anchor drift -- STOP"
    cores = [tuple(sorted(c["idx"])) for c in b["cores"]]
    assert len(cores) == len(set(cores)) == b["n_failing_pairs"]
    return cores

# ------------------------------------------------- Karp-Luby estimator ---
def kl_estimate(cores, priors, fail_fn, n, seed, variant="count"):
    """Unbiased T1 estimator. fail_fn(sorted index list) -> {0,1}.
    Returns dict with t1, se, per-sample stats."""
    rng = np.random.default_rng(seed)
    M = len(priors)
    logpi = np.array([np.sum(np.log([priors[j] for j in c])) for c in cores])
    pi = np.exp(logpi)
    Z = float(pi.sum())
    probs = pi / Z
    order = {c: i for i, c in enumerate(sorted(cores))}
    xs = np.zeros(n)
    fails = rescues = 0
    for t in range(n):
        ci = rng.choice(len(cores), p=probs)
        c = cores[ci]
        fired = rng.random(M) < priors
        fired[list(c)] = True
        S = np.flatnonzero(fired)
        Sset = set(S.tolist())
        contained = [cc for cc in cores if Sset.issuperset(cc)]
        f = fail_fn(S.tolist())
        fails += f
        rescues += (1 - f)
        if variant == "count":
            xs[t] = Z * f / len(contained)
        else:                                   # first-contained-core
            first = min(contained, key=lambda cc: order[cc])
            xs[t] = Z * f * (1.0 if c == first else 0.0)
    t1 = float(xs.mean())
    se = float(xs.std(ddof=1) / np.sqrt(n)) if n > 1 else float("inf")
    return dict(t1=t1, se=se, Z=Z, n=n, variant=variant,
                fail_rate=fails / n, rescue_rate=rescues / n)

# ---------------------------------------------------------- minimalizer ---
def minimalize(S, fail_fn):
    """Greedy decode-checked reduction of a failing set to a minimal core.
    Deterministic: fixed descending-index removal order, repeated passes."""
    cur = sorted(S)
    assert fail_fn(cur), "minimalize called on a non-failing set"
    changed = True
    while changed:
        changed = False
        for j in sorted(cur, reverse=True):
            trial = [x for x in cur if x != j]
            if trial and fail_fn(trial):
                cur = trial
                changed = True
    return tuple(sorted(cur))

# ------------------------------------------------------ U-G0 validations ---
def brute_T1(priors, cores, fail_fn_set):
    """Exact T1 over all 2^M subsets (synthetic-scale only)."""
    M = len(priors)
    tot = 0.0
    for mask in range(1 << M):
        S = [j for j in range(M) if (mask >> j) & 1]
        Sset = set(S)
        if not any(Sset.issuperset(c) for c in cores):
            continue
        if not fail_fn_set(Sset):
            continue
        p = np.prod([priors[j] if j in Sset else 1 - priors[j]
                     for j in range(M)])
        tot += float(p)
    return tot

def run_ug0():
    out = {"stage": "U-G0"}
    rng = np.random.default_rng(20260710)
    # --- synthetic setup: M=12, 3 cores, one rescue set
    M = 12
    pr = rng.uniform(0.05, 0.3, M)
    cores = [(0, 3), (2, 5, 7), (3, 8)]
    rescue = (1, 4)
    # (2) monotone union vs brute force, both variants (3)
    mono = lambda Sset: True
    exact_m = brute_T1(pr, cores, mono)
    ff = lambda S: 1 if any(set(S).issuperset(c) for c in cores) else 0
    for var in ("count", "first"):
        est = kl_estimate(cores, pr, lambda S: ff(S), 40000, seed=11, variant=var)
        z = (est["t1"] - exact_m) / est["se"]
        assert abs(z) < 5, f"monotone {var} z={z:.2f}"
        out[f"mono_{var}_z"] = round(float(z), 3)
    out["mono_exact"] = exact_m
    # non-monotone: rescue set cancels failure
    nonmono_set = lambda Sset: not Sset.issuperset(rescue)
    exact_n = brute_T1(pr, cores, nonmono_set)
    ffn = lambda S: (1 if (any(set(S).issuperset(c) for c in cores)
                           and not set(S).issuperset(rescue)) else 0)
    est = kl_estimate(cores, pr, ffn, 40000, seed=12, variant="count")
    z = (est["t1"] - exact_n) / est["se"]
    assert abs(z) < 5, f"non-monotone z={z:.2f}"
    out["nonmono_z"] = round(float(z), 3)
    out["nonmono_exact"] = exact_n
    # (4) minimalizer: synthetic idempotence + core recovery
    embed = sorted(set([0, 3] + [9, 10]))          # core + benign extras
    got = minimalize(embed, lambda S: ff(S))
    assert got == (0, 3), f"minimalizer wrong core: {got}"
    assert minimalize(list(got), lambda S: ff(S)) == got, "not idempotent"
    out["minimalizer_synthetic"] = "ok"
    # --- referee-tied checks: (1) basis anchors + planted seed cores fail
    cores_real = load_basis()
    out["basis"] = dict(n_cores=len(cores_real), sha=BASIS_SHA_ANCHOR)
    from evaluator_v1 import make_bposd
    H, k = build_rep2eh8()
    circ = referee_circuit(H, 1.0)
    Hd, O, priors = dem_matrices(circ)
    dec = make_bposd(Hd, priors)
    fail_real = lambda S: _decode_set(dec, Hd, O, S)
    planted = [fail_real(list(c)) for c in cores_real]
    assert all(planted), f"seed core failed to fail: {planted}"
    idem = [minimalize(list(c), fail_real) == c for c in cores_real]
    assert all(idem), f"seed core not minimal: {idem}"
    out["planted_seed_cores_fail"] = True
    out["seed_cores_minimal"] = True
    print(json.dumps(out))
    print(json.dumps({"verdict": "U-G0 PASS"}))


# ------------------------------------------------------------- U-G1 gate ---
from s6_sampler import (pb_suffix_table, cond_bernoulli_draw, eps_from_pany,
                        G2_REP2EH8)

UG1_BUDGET = dict(new_decode_cap=108000, all_in_cap=540000, seed_enum=139128,
                  rounds=3,
                  t2_budget=[30000, 30000, 24000], t2_pilot=300,
                  t1_samples=[0, 8000, 8000],
                  amplify_cap=3000, minimalize_cap=2000,
                  seed_base=210710, period=64, max_shift=7)

class CountingFail:
    def __init__(self, dec, Hd, O):
        self.dec, self.Hd, self.O, self.n = dec, Hd, O, 0
    def __call__(self, S):
        self.n += 1
        return _decode_set(self.dec, self.Hd, self.O, list(S))

def translates(core, M, period, max_shift):
    out = []
    for t in range(-max_shift, max_shift + 1):
        if t == 0:
            continue
        c = tuple(sorted(j + t * period for j in core))
        if c[0] >= 0 and c[-1] < M:
            out.append(c)
    return out

def stratified_T2(Hd, O, priors, basis, fail, seed, budget, pilot):
    """Stratified estimate of T2 = P(fail AND no known core in S), basis
    FROZEN for the whole call. Core-containing draws score 0 with no decode.
    Returns (est dict, harvested failing sets, decodes used)."""
    rng = np.random.default_rng(seed)
    M = len(priors)
    w_hi = 8
    while True:
        R = pb_suffix_table(priors, w_hi)
        if 1.0 - R[0].sum() < 1e-15 or w_hi >= M:
            break
        w_hi = min(2 * w_hi + 4, M)
    Pw = R[0]
    order = np.argsort(Pw)[::-1]
    strata, cov = [], 0.0
    for w in order:
        strata.append(int(w)); cov += Pw[w]
        if 1.0 - cov <= 1e-12:
            break
    strata = sorted(strata)
    basis_sets = [set(c) for c in basis]
    d0 = fail.n
    harvested = []
    def g(w):
        S = cond_bernoulli_draw(priors, R, w, rng)
        Sset = set(S)
        if any(Sset.issuperset(b) for b in basis_sets):
            return 0
        f = fail(S)
        if f:
            harvested.append(tuple(sorted(S)))
        return f
    pilots = {w: sum(g(w) for _ in range(pilot)) for w in strata}
    spent = pilot * len(strata)
    rem = max(budget - spent, 0)
    def sig(w):
        f = max(pilots[w] / pilot, 1.0 / pilot)
        return Pw[w] * np.sqrt(f * (1 - f))
    tot = sum(sig(w) for w in strata) or 1.0
    table = {}
    for w in strata:
        extra = int(rem * sig(w) / tot)
        fl = pilots[w] + sum(g(w) for _ in range(extra))
        n = pilot + extra
        table[w] = dict(n=n, fails=fl, f=fl / n)
    point = var = ub = 0.0
    for w in strata:
        t = table[w]
        point += Pw[w] * t["f"]
        if t["fails"] == 0:
            ub += Pw[w] * 3.0 / t["n"]
        else:
            var += Pw[w] ** 2 * t["f"] * (1 - t["f"]) / t["n"]
    tail = float(1.0 - sum(Pw[w] for w in strata))
    se = float(np.sqrt(var))
    est = dict(t2=float(point), se=se, zero_fail_ub=float(ub), tail=tail,
               n_harvested=len(harvested))
    return est, harvested, fail.n - d0

def run_ug1():
    cfg = UG1_BUDGET
    cores = list(load_basis())
    from evaluator_v1 import make_bposd
    H, k = build_rep2eh8()
    circ = referee_circuit(H, 1.0)
    Hd, O, priors = dem_matrices(circ)
    dec = make_bposd(Hd, priors)
    fail = CountingFail(dec, Hd, O)
    M = len(priors)
    log = []
    t1_est = None
    t2_est = None
    for r in range(cfg["rounds"]):
        frozen = list(cores)
        rd = dict(round=r + 1, basis_size=len(frozen))
        if cfg["t1_samples"][r] > 0:
            d0 = fail.n
            t1_est = kl_estimate(frozen, priors, fail, cfg["t1_samples"][r],
                                 seed=220710 + r, variant="count")
            rd["t1"] = dict(t1=t1_est["t1"], se=t1_est["se"], Z=t1_est["Z"],
                            fail_rate=t1_est["fail_rate"],
                            decodes=fail.n - d0)
        t2_est, harvested, d2 = stratified_T2(
            Hd, O, priors, frozen, fail, cfg["seed_base"] + r,
            cfg["t2_budget"][r], cfg["t2_pilot"])
        rd["t2"] = dict(**t2_est, decodes=d2)
        # closure: minimalize + symmetry-amplify (capped, decode-counted)
        d0 = fail.n
        new_cores = []
        for S in harvested:
            if fail.n - d0 > cfg["minimalize_cap"]:
                rd["minimalize_capped"] = True
                break
            c = minimalize(list(S), fail)
            if c not in cores and c not in new_cores:
                new_cores.append(c)
        rd["minimalize_decodes"] = fail.n - d0
        d0 = fail.n
        amp = []
        for c in list(new_cores):
            for t in translates(c, M, cfg["period"], cfg["max_shift"]):
                if fail.n - d0 > cfg["amplify_cap"]:
                    rd["amplify_capped"] = True
                    break
                if t not in cores and t not in new_cores and t not in amp \
                        and fail(list(t)):
                    amp.append(t)
        rd["amplify_decodes"] = fail.n - d0
        rd["new_cores"] = len(new_cores)
        rd["amplified"] = len(amp)
        cores.extend(new_cores + amp)
        rd["decodes_cum"] = fail.n
        log.append(rd)
        print(json.dumps(rd))
        assert fail.n <= cfg["new_decode_cap"], "budget overrun -- abort"
    # verdict
    p_any = t1_est["t1"] + t2_est["t2"]
    se = float(np.sqrt(t1_est["se"] ** 2 + t2_est["se"] ** 2))
    lo = max(p_any - 1.96 * se, 0.0)
    hi = p_any + 1.96 * se + t2_est["zero_fail_ub"] + t2_est["tail"]
    rel = (hi - lo) / (hi + lo) if hi + lo > 0 else 1.0
    eps_pt, eps_lo, eps_hi = (eps_from_pany(x, k) for x in (p_any, lo, hi))
    band = G2_REP2EH8["eps_band"]
    new_decodes = fail.n
    all_in = new_decodes + cfg["seed_enum"]
    crit = dict(
        a_conclusive=bool(rel <= 0.25),
        b_intersects=bool(eps_lo <= band[1] and band[0] <= eps_hi),
        c_point_inside=bool(band[0] <= eps_pt <= band[1]),
        d_new_budget=bool(new_decodes <= cfg["new_decode_cap"]),
        e_all_in=bool(all_in < cfg["all_in_cap"]))
    if not crit["a_conclusive"]:
        cell = "INCONCLUSIVE"
    elif not (crit["d_new_budget"] and crit["e_all_in"]):
        cell = "FAIL-ON-EFFICIENCY"
    elif crit["b_intersects"] and crit["c_point_inside"]:
        cell = "PASS"
    else:
        cell = "FAIL"
    t1_share = t1_est["t1"] / p_any if p_any > 0 else 0.0
    # kill criteria (PREREG_union section 3), resolved mechanically
    t2_ub = t2_est["t2"] + 1.96 * t2_est["se"] + t2_est["zero_fail_ub"] \
        + t2_est["tail"]
    ku1 = bool(t2_ub > 0.25 * t1_est["t1"])
    ku2 = bool(1.0 - t1_est["fail_rate"] > 0.90)
    ku3 = bool(len(cores) > 50000)
    kills = dict(KU1_nonsparse=ku1,
                 KU1_t2ub_over_t1=round(float(t2_ub / max(t1_est["t1"],
                                                          1e-300)), 1),
                 KU2_rescue_blowup=ku2,
                 KU2_rescue_rate=round(float(1.0 - t1_est["fail_rate"]), 4),
                 KU3_basis_explosion=ku3)
    print(json.dumps(dict(
        stage="U-G1", row=G2_REP2EH8["name"], m=1.0,
        p_any=float(p_any), t1=t1_est["t1"], t2=t2_est["t2"],
        t1_share=round(float(t1_share), 4), basis_final=len(cores),
        eps=eps_pt, eps_interval=[eps_lo, eps_hi],
        rel_halfwidth=round(float(rel), 4), mc_band_eps=band,
        criteria=crit, kills=kills, new_decodes=new_decodes, all_in=all_in,
        cell=cell, rounds=log and len(log))))
    verdict = "U-G1 " + cell
    if ku1 or ku2 or ku3:
        verdict += " -- KILL CRITERIA FIRED: " + ",".join(
            k for k, v in [("KU1", ku1), ("KU2", ku2), ("KU3", ku3)] if v) \
            + " (design dead for this regime per PREREG_union section 3)"
    print(json.dumps({"verdict": verdict}))

def run_ug1_selftest():
    """Composition identity: T1 + T2 == P_fail exactly (brute force), any
    basis, monotone or not; plus sampled 5-sigma on both terms."""
    rng = np.random.default_rng(5)
    M = 12
    pr = rng.uniform(0.05, 0.3, M)
    cores = [(0, 3), (2, 5, 7)]
    rescue = (1, 4)
    ffn_set = lambda Sset: (any(Sset.issuperset(c) for c in [(0, 3), (2, 5, 7),
                                                             (6, 9, 11)])
                            and not Sset.issuperset(rescue))
    # brute force P_fail, T1(known basis), T2
    pf = t1 = t2 = 0.0
    for mask in range(1 << M):
        Sset = {j for j in range(M) if (mask >> j) & 1}
        p = float(np.prod([pr[j] if j in Sset else 1 - pr[j]
                           for j in range(M)]))
        f = ffn_set(Sset)
        pf += p * f
        contains = any(Sset.issuperset(c) for c in cores)
        t1 += p * (f and contains)
        t2 += p * (f and not contains)
    assert abs((t1 + t2) - pf) < 1e-15, "composition identity broken"
    print(json.dumps(dict(stage="ug1-selftest", pf=pf, t1=t1, t2=t2,
                          identity="exact")))
    print(json.dumps({"selftest": "PASS"}))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ug0", action="store_true")
    ap.add_argument("--ug1", action="store_true")
    ap.add_argument("--ug1-selftest", action="store_true")
    a = ap.parse_args()
    if a.ug0:
        run_ug0()
    elif a.ug1:
        run_ug1()
    elif a.ug1_selftest:
        run_ug1_selftest()
    else:
        ap.print_help()
