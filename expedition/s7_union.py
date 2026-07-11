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

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ug0", action="store_true")
    a = ap.parse_args()
    if a.ug0:
        run_ug0()
    else:
        ap.print_help()
