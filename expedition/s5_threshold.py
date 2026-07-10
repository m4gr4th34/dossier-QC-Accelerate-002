#!/usr/bin/env python3
"""s5_threshold.py -- threshold-crossing evaluator (ruler attempt #3, Entry 003).

DEAD RULERS (see CH5_WORKING.md):
  #1 direct-MC eps at GM point (Entry 002): strong codes floor below shot noise.
  #2 noise-sweep slope (Entry 003): measurable-window curvature confound --
     strong codes sample flat near-threshold, better codes get flatter slopes.

THIS RULER: find the noise multiplier m* where each code's eps crosses ONE
FIXED common target (TARGET=0.1). Rank by m*: higher = tolerates more noise =
better. Every code is measured at the SAME observable, so the curvature
confound cannot arise -- there is no slope to fit. Frozen referee; the probe
schedule is a root-find, not an instrument change.

PROOF BURDEN (unmet until measured): must pass the two-code gate AND the
4-code x 3-seed hardening ladder (the bar Entry 003 set after the slope ruler
passed the easy gate and failed the hard one).
"""
import sys, math
sys.path.insert(0, ".")
import numpy as np

GM = dict(nbar=11.0, k_ratio=1e-4, p_m=6e-3)
TARGET = 0.1                 # the common eps every code is measured at
PHYS_CEIL = 0.4              # nbar*k_ratio*m must stay below this
M_MIN, M_MAX = 1.0, 360.0    # search range (M_MAX just under ceiling/nbar/kr)
SHOTS = 20000
ROUNDS = 8
MAX_EVALS = 14
TOL = 1.15                   # stop when bracket ratio m_hi/m_lo < TOL

def _real_score(H, k, m, shots, seed):
    from gm_css import fom
    Hz = np.zeros((0, H.shape[1]), dtype=np.uint8)
    pk, _, _, _ = fom(H, Hz, k, ROUNDS, GM["p_m"], GM["nbar"],
                      GM["k_ratio"] * m, "xonly", shots, seed=seed)
    return pk

def m_star(H, k, seed=7, shots=SHOTS, score_fn=_real_score):
    """Root-find the multiplier where eps crosses TARGET. Geometric bisection
    with a coarse bracket pass; log-linear interpolation at the end.
    Returns dict(ok, m_star, n_evals, reason, probes)."""
    probes = {}
    def probe(m):
        m = round(float(m), 6)
        if m in probes:
            return probes[m]
        if len(probes) >= MAX_EVALS or GM["nbar"] * GM["k_ratio"] * m >= PHYS_CEIL:
            return None
        try:
            probes[m] = score_fn(H, k, m, shots, seed)
        except Exception:
            probes[m] = None
        return probes[m]

    # coarse geometric pass to bracket the crossing
    lo = hi = None
    m = M_MIN
    while m <= M_MAX and len(probes) < MAX_EVALS:
        e = probe(m)
        if e is not None:
            if e < TARGET:
                lo = m
            elif e >= TARGET:
                hi = m
                break
        m *= 3.0
    if lo is None or hi is None:
        which = "never reached TARGET (code too strong for range)" if hi is None \
                else "already above TARGET at M_MIN (code too weak)"
        return dict(ok=False, m_star=None, n_evals=len(probes),
                    reason=which, probes=dict(probes))
    # geometric bisection
    while hi / lo > TOL and len(probes) < MAX_EVALS:
        mid = math.sqrt(lo * hi)
        e = probe(mid)
        if e is None:
            break
        if e < TARGET:
            lo = mid
        else:
            hi = mid
    # log-linear interpolation between the final bracket
    el, eh = probes[round(lo, 6)], probes[round(hi, 6)]
    el = max(el, 1e-9)
    t = (math.log10(TARGET) - math.log10(el)) / \
        (math.log10(eh) - math.log10(el)) if eh > el else 0.5
    ms = 10 ** (math.log10(lo) + t * (math.log10(hi) - math.log10(lo)))
    return dict(ok=True, m_star=float(ms), n_evals=len(probes),
                reason=None, probes=dict(probes))

def rank_key(res):
    """Lower = better convention kept: negate m* (higher threshold = better)."""
    return -res["m_star"] if res["ok"] else float("inf")

# ---------------------------------------------------------------------------
def _selftest():
    """Numpy-only. Includes the CURVED (saturating) synthetic that mimics the
    exact near-threshold flattening that broke the slope ruler -- this FOM must
    rank it correctly anyway."""
    def curved(m50, sharp):
        # eps(m) = 0.5 * (m/m50)^sharp / (1 + (m/m50)^sharp): saturates at 0.5,
        # crosses 0.1 at m = m50 * (0.25)^(1/sharp). Higher m50 = stronger code.
        def f(H, k, m, shots, seed):
            x = (m / m50) ** sharp
            rng = np.random.default_rng(seed * 7919 + int(m * 1e3))
            return 0.5 * x / (1 + x) * (1 + 0.03 * rng.standard_normal())
        return f
    H = np.zeros((2, 5), np.uint8)
    strong = m_star(H, 1, score_fn=curved(m50=120.0, sharp=4.0))
    mid    = m_star(H, 1, score_fn=curved(m50=40.0,  sharp=3.0))
    weak   = m_star(H, 1, score_fn=curved(m50=12.0,  sharp=2.0))
    assert all(r["ok"] for r in (strong, mid, weak)), "root-find failed"
    ks = [rank_key(strong), rank_key(mid), rank_key(weak)]
    assert ks == sorted(ks), f"ordering wrong on curved data: {ks}"
    # analytic crossings: m50*(0.25)^(1/sharp) = 84.9, 25.2, 6.0
    for r, want in ((strong, 84.9), (mid, 25.2), (weak, 6.0)):
        assert abs(r["m_star"] - want) / want < 0.15, \
            f"m* recovery off: got {r['m_star']:.1f} want {want}"
    d1 = m_star(H, 1, score_fn=curved(50, 3)); d2 = m_star(H, 1, score_fn=curved(50, 3))
    assert d1 == d2, "determinism fail"
    print(f"SELFTEST PASS  m* recovery on SATURATING (slope-ruler-breaking) curves: "
          f"strong={strong['m_star']:.1f} (want 84.9) mid={mid['m_star']:.1f} (25.2) "
          f"weak={weak['m_star']:.1f} (6.0); ordering + determinism OK; "
          f"evals per code <= {max(r['n_evals'] for r in (strong,mid,weak))}")

def _gate():
    from s2_seeds import product_code, rep_H, ext_hamming8
    winner = product_code(rep_H(3), ext_hamming8())
    weaker = product_code(rep_H(3), rep_H(3))
    rw, rk = m_star(winner, 4), m_star(weaker, 1)
    for name, r in (("winner [24,4,12]", rw), ("weaker [9,1,9] ", rk)):
        print(f"{name}: ok={r['ok']} m*="
              f"{r['m_star']:.1f}" if r["ok"] else f"{name}: UNRESOLVED {r['reason']}",
              f" evals={r['n_evals']}" if r["ok"] else "")
    if rw["ok"] and rk["ok"]:
        ok = rank_key(rw) < rank_key(rk)
        print(f"\nGATE {'PASS' if ok else 'FAIL'}: winner m*={rw['m_star']:.1f} "
              f"vs weaker m*={rk['m_star']:.1f} (margin {rw['m_star']/rk['m_star']:.2f}x)")
    else:
        print("\nGATE INCONCLUSIVE -- widen M range or fix; do not proceed.")

def _harden():
    from s2_seeds import product_code, rep_H, ext_hamming8
    ladder = [
        ("rep4(x)eh8 [32,4,16]", product_code(rep_H(4), ext_hamming8()), 4),
        ("rep3(x)eh8 [24,4,12]", product_code(rep_H(3), ext_hamming8()), 4),
        ("rep2(x)eh8 [16,4,8] ", product_code(rep_H(2), ext_hamming8()), 4),
        ("rep3(x)rep3 [9,1,9] ", product_code(rep_H(3), rep_H(3)),       1),
    ]
    print("HARDENING: known order top-to-bottom (d16 > d12 > d8 > weak), 3 seeds")
    all_pass = True
    for seed in (7, 101, 2026):
        rows = [(nm, m_star(H, k, seed=seed)) for nm, H, k in ladder]
        keys = [rank_key(r) for _, r in rows]
        ok = all(r["ok"] for _, r in rows) and keys == sorted(keys)
        all_pass &= ok
        print(f"\nseed={seed}  ordering {'CORRECT' if ok else 'WRONG/UNRESOLVED'}")
        for nm, r in rows:
            print(f"  {nm}  " + (f"m*={r['m_star']:7.1f}  evals={r['n_evals']}"
                                 if r["ok"] else f"UNRESOLVED: {r['reason']}"))
    print(f"\nHARDENING {'PASS' if all_pass else 'FAIL'}")

if __name__ == "__main__":
    if "--selftest" in sys.argv: _selftest()
    elif "--gate" in sys.argv:   _gate()
    elif "--harden" in sys.argv: _harden()
    else: print("usage: python3 s5_threshold.py --selftest | --gate | --harden")
