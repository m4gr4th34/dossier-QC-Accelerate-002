#!/usr/bin/env python3
"""s5_sweep.py -- noise-sweep evaluator (the replacement ruler, Entry 002).

WHY: Entry 002 proved direct Monte-Carlo eps at the fixed GM point cannot rank
strong codes (both floor below shot noise; 2e6 shots gave an inverted order).
FIX: read the SAME frozen referee at noise levels where failures are COMMON,
fit log(eps) vs log(noise), rank by the suppression slope. Better codes
suppress faster toward the operating point -- measurable with real statistics
at pilot cost. Not a moving instrument: circuit/decoder/calibration frozen;
the sweep is a fixed ladder of operating points read through them.

FOM: rank by SLOPE of log(eps) vs log(noise). eps grows with noise, so slope>0;
the BETTER code has the STEEPER slope (faster suppression toward the operating
point). rank_key = (-slope, extrapolated GM eps); lower key = better.

PROOF BURDEN (unmet until measured): must pass the Entry-001 known-ordering
diagnostic -- winner [24,4,12] vs weaker [9,1,9], correct order, with margin --
before any loop steers on it. Run --gate on the canonical stack.
"""
import sys, math
sys.path.insert(0, ".")
import numpy as np

GM = dict(nbar=11.0, k_ratio=1e-4, p_m=6e-3)
LADDER = (3.0, 10.0, 30.0, 100.0, 300.0)  # coarse probe (k_ratio mult only)
PHYS_CEIL = 0.4                        # nbar*k_ratio*m must stay below this
MIN_PTS = 3                            # in-window points needed for a fit
MAX_EVALS = 12                         # hard budget per code (probe+refine)
WINDOW = (5e-4, 0.25)                          # keep points w/ measurable eps
SHOTS = 20000                                  # per ladder point
ROUNDS = 8

def _real_score(H, k, m, shots, seed):
    """Frozen referee, ONE knob swept: k_ratio*m. p_m held at GM so log(m)
    means one physical thing and the slope is interpretable."""
    from gm_css import fom
    Hz = np.zeros((0, H.shape[1]), dtype=np.uint8)
    pk, _, _, _ = fom(H, Hz, k, ROUNDS, GM["p_m"], GM["nbar"],
                      GM["k_ratio"] * m, "xonly", shots, seed=seed)
    return pk

def sweep(H, k, seed=7, shots=SHOTS, ladder=LADDER, score_fn=_real_score):
    """Probe the ladder, keep measurable points, fit log(eps) ~ a + b*log(m).
    Returns dict(slope, eps_at_gm_log, n_points, points, ok, reason).
    slope b: more negative = faster suppression = better code.
    eps_at_gm_log: fitted intercept at m=1 (log10) -- extrapolated GM-point eps."""
    pts, skipped, evals = [], [], {}
    def probe(m):
        """One rung: physical-ceiling drop, per-rung try/except, window filter.
        ADAPTIVE: strong codes rise steeply through the window (the steeper the
        suppression -- the signal itself -- the fewer fixed rungs land in it),
        so the ladder refines itself per code instead of being tuned to any one
        strength. Returns eps or None."""
        m = round(float(m), 6)
        if m in evals or len(evals) >= MAX_EVALS:
            return evals.get(m)
        if GM["nbar"] * GM["k_ratio"] * m >= PHYS_CEIL:
            skipped.append((m, "unphysical: nbar*k_ratio*m >= ceiling"))
            evals[m] = None; return None
        try:
            eps = score_fn(H, k, m, shots, seed)
        except Exception as exc:
            skipped.append((m, f"{type(exc).__name__}: {str(exc)[:80]}"))
            evals[m] = None; return None
        evals[m] = eps
        if WINDOW[0] <= eps <= WINDOW[1]:
            pts.append((math.log10(m), math.log10(eps)))
        return eps
    # coarse pass
    for m in ladder:
        probe(m)
    # adaptive refinement: bisect (geometrically) every adjacent probed pair
    # that brackets or crosses the window, until MIN_PTS or budget exhausted
    while len(pts) < MIN_PTS and len(evals) < MAX_EVALS:
        ms = sorted(m for m, e in evals.items() if e is not None)
        cands = []
        for lo, hi in zip(ms, ms[1:]):
            el, eh = evals[lo], evals[hi]
            spans = (el < WINDOW[0] and eh > WINDOW[0]) or                     (el < WINDOW[1] and eh > WINDOW[1]) or                     (WINDOW[0] <= el <= WINDOW[1]) or                     (WINDOW[0] <= eh <= WINDOW[1])
            if spans and hi / lo > 1.25:
                cands.append(math.sqrt(lo * hi))   # geometric midpoint
        if not cands:
            break
        for c in cands:
            if len(pts) >= MIN_PTS or len(evals) >= MAX_EVALS:
                break
            probe(c)
    pts.sort()
    if len(pts) < 2:
        return dict(ok=False, reason=f"only {len(pts)} measurable points",
                    slope=None, eps_at_gm_log=None, n_points=len(pts),
                    points=pts, skipped=skipped)
    x = np.array([p[0] for p in pts]); y = np.array([p[1] for p in pts])
    b, a = np.polyfit(x, y, 1)          # y = a + b*x
    return dict(ok=True, reason=None, slope=float(b), eps_at_gm_log=float(a),
                n_points=len(pts), points=pts, skipped=skipped)

def rank_key(res):
    """Sort key: lower = better. Real codes: eps GROWS with noise m, so slope>0
    and the BETTER code has the STEEPER slope (suppresses faster as noise falls
    toward the operating point). Primary: -slope (steeper first). Secondary:
    extrapolated GM-point eps (lower first)."""
    if not res["ok"]:
        return (float("inf"), float("inf"))
    return (-res["slope"], res["eps_at_gm_log"])

# ---------------------------------------------------------------------------
# --selftest: numpy-only; validates fit + ranking on synthetic codes
# ---------------------------------------------------------------------------
def _selftest():
    # synthetic referee: eps(m) = C * m^s  (power law), deterministic noise
    def fake(s_true, C):
        def f(H, k, m, shots, seed):
            rng = np.random.default_rng(seed * 1000 + int(m))
            return C * m ** s_true * (1 + 0.03 * rng.standard_normal())
        return f
    H = np.zeros((2, 5), np.uint8)
    strong = sweep(H, 1, score_fn=fake(3.0, 1e-9))   # steep suppression
    weak   = sweep(H, 1, score_fn=fake(1.5, 1e-6))   # shallow suppression
    assert strong["ok"] and weak["ok"], "fit failed on synthetic power laws"
    assert abs(strong["slope"] - 3.0) < 0.15, f"slope recovery off: {strong['slope']}"
    assert abs(weak["slope"] - 1.5) < 0.15, f"slope recovery off: {weak['slope']}"
    # steeper slope (faster suppression) must rank BETTER (smaller key):
    assert rank_key(strong) < rank_key(weak), "rank_key must prefer steeper slope"
    d1 = sweep(H, 1, score_fn=fake(2.0, 1e-8)); d2 = sweep(H, 1, score_fn=fake(2.0, 1e-8))
    assert d1 == d2, "determinism fail"
    print(f"SELFTEST PASS  slope recovery strong={strong['slope']:.3f} (want 3.0) "
          f"weak={weak['slope']:.3f} (want 1.5); ranking + determinism OK")

# ---------------------------------------------------------------------------
# --gate: the Entry-001/002 known-ordering diagnostic through THIS evaluator
# ---------------------------------------------------------------------------
def _gate():
    from s2_seeds import product_code, rep_H, ext_hamming8
    winner = product_code(rep_H(3), ext_hamming8())   # [24,4,12]
    weaker = product_code(rep_H(3), rep_H(3))         # [9,1,9]
    rw = sweep(winner, 4); rk = sweep(weaker, 1)
    print("code      ok  n_pts  slope      eps_at_gm(log10)")
    print(f"winner    {rw['ok']}  {rw['n_points']}     "
          f"{rw['slope'] if rw['ok'] else '--':>8}   {rw['eps_at_gm_log'] if rw['ok'] else rw['reason']}")
    print(f"weaker    {rk['ok']}  {rk['n_points']}     "
          f"{rk['slope'] if rk['ok'] else '--':>8}   {rk['eps_at_gm_log'] if rk['ok'] else rk['reason']}")
    if rw["ok"] and rk["ok"]:
        resolved = rank_key(rw) < rank_key(rk)
        margin = (rw["slope"] - rk["slope"])
        print(f"\nGATE {'PASS' if resolved else 'FAIL'}: winner ranked "
              f"{'better' if resolved else 'WORSE'} (slope margin {margin:+.3f})")
        print("(pass = correct known ordering with margin; the old ruler failed this)")
    else:
        print("\nGATE INCONCLUSIVE: a code lacked measurable ladder points -- "
              "widen LADDER/WINDOW and re-run; do NOT build a loop on this.")

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    elif "--gate" in sys.argv:
        _gate()
    else:
        print("usage: python3 s5_sweep.py --selftest | --gate")
