#!/usr/bin/env python3
"""s8_truth.py -- S8 operating-point truth campaign (direct MC at cost).

Governed by expedition/PREREG_truth.md. Instrument: the FROZEN referee,
unchanged. Five rows at m=1 (winner rep3(x)eh8, frontier eh8(x)eh8, C3 find
from the committed artifact, rep-7, rep-13), staged budgets with hard caps
and wall-clock kills, 500k-shot chunks with per-chunk seeds, checkpointed
JSONL with byte-identical resume (re-running the same command skips
completed chunks). Exact Garwood 95% Poisson intervals via a pure-python
regularized-incomplete-gamma implementation (scipy absent from the
canonical venv), anchored in the selftest against scipy-computed reference
quantiles. stim is per-machine deterministic only (Entry 011): the record
run is the workbench's.

Usage:
  python -u s8_truth.py --selftest
  python -u s8_truth.py --run [--rows winner,frontier,c3,rep7,rep13]
  python -u s8_truth.py --status
Checkpoints: s8_checkpoints.jsonl (append-only). Verdicts: printed JSONL.
"""
import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, ".")
import numpy as np

GM = dict(nbar=11.0, k_ratio=1e-4, p_m=6e-3)
ROUNDS = 8
MODE = "xonly"
CHUNK = 500_000
CKPT = "s8_checkpoints.jsonl"
C3_ARTIFACT = "c3_find_H.json"
C3_HASH_ANCHOR = "f42569e3fb53016f"
G2_ANCHORS = {  # committed rankmap m=1 values, verbatim (landmark gate)
    "rep2(x)eh8 [16,4,8]":  1.1721359996663683e-05,
    "C3 find [34,6,12]":    2.074077687191922e-05,
    "rep3(x)eh8 [24,4,12]": 3.125018555039105e-07,
    "eh8(x)eh8 [64,16,16]": 7.812540891993791e-08,
}
# scipy reference quantiles (computed offline 2026-07-10) anchoring the
# pure-python chi2 ppf below: (q, df, value)
CHI2_ANCHORS = [
    (0.025, 150, 117.9845154029029),
    (0.975, 152, 188.02629889766553),
    (0.025, 2, 0.05063561596857975),
    (0.975, 4, 11.143286781877796),
    (0.025, 400, 346.48176536291464),
    (0.975, 402, 459.44396333089975),
    (0.975, 2, 7.377758908227871),
]

ROWS = dict(
    winner=dict(name="rep3(x)eh8 [24,4,12]", k=4, stage1=2_000_000,
                cap=20_000_000, wall_h=6.0, seed_base=810_000),
    frontier=dict(name="eh8(x)eh8 [64,16,16]", k=16, stage1=2_000_000,
                  cap=10_000_000, wall_h=6.0, seed_base=820_000),
    c3=dict(name="C3 find [34,6,12]", k=6, stage1=2_000_000,
            cap=4_000_000, wall_h=2.0, seed_base=830_000),
    rep7=dict(name="rep-7 [7,1,7]", k=1, stage1=2_000_000,
              cap=20_000_000, wall_h=3.0, seed_base=840_000),
    rep13=dict(name="rep-13 [13,1,13]", k=1, stage1=2_000_000,
               cap=20_000_000, wall_h=3.0, seed_base=850_000),
)
TARGET_EVENTS = 96          # ~±20% at 95%

# ------------------------------------------------ pure-python Garwood CI ---
def _gammainc_lower_reg(a, x):
    """Regularized lower incomplete gamma P(a,x); series for x < a+1,
    continued fraction otherwise (Numerical Recipes forms)."""
    if x <= 0:
        return 0.0
    lg = math.lgamma(a)
    if x < a + 1.0:
        term = 1.0 / a
        s = term
        n = a
        for _ in range(10000):
            n += 1.0
            term *= x / n
            s += term
            if abs(term) < abs(s) * 1e-16:
                break
        return s * math.exp(-x + a * math.log(x) - lg)
    # continued fraction for Q(a,x)
    tiny = 1e-300
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny: d = tiny
        c = b + an / c
        if abs(c) < tiny: c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-16:
            break
    q = math.exp(-x + a * math.log(x) - lg) * h
    return 1.0 - q

def chi2_ppf(q, df):
    """Inverse chi2 CDF by bisection on P(df/2, x/2). Exact to ~1e-10 rel."""
    a = df / 2.0
    lo, hi = 0.0, max(4.0 * df, 50.0)
    while _gammainc_lower_reg(a, hi / 2.0) < q:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _gammainc_lower_reg(a, mid / 2.0) < q:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

def garwood(fails):
    lo = 0.5 * chi2_ppf(0.025, 2 * fails) if fails > 0 else 0.0
    hi = 0.5 * chi2_ppf(0.975, 2 * fails + 2)
    return lo, hi

# ------------------------------------------------------------------ rows ---
def build_H(row_key):
    from s2_seeds import product_code, rep_H, ext_hamming8
    if row_key == "winner":
        return product_code(rep_H(3), ext_hamming8())
    if row_key == "frontier":
        return product_code(ext_hamming8(), ext_hamming8())
    if row_key == "c3":
        from s5_proposer import h_decode
        import hashlib
        b = json.load(open(C3_ARTIFACT))
        assert b["hash"] == C3_HASH_ANCHOR, "C3 artifact hash drift -- STOP"
        return h_decode(b)
    if row_key == "rep7":
        return rep_H(7)
    if row_key == "rep13":
        return rep_H(13)
    raise KeyError(row_key)

def chunk_fails(H, k, shots, seed):
    from gm_css import fom
    Hz = np.zeros((0, H.shape[1]), dtype=np.uint8)
    _, p_any, _, _ = fom(H, Hz, k, ROUNDS, GM["p_m"], GM["nbar"],
                         GM["k_ratio"] * 1.0, MODE, shots, seed=seed)
    f = p_any * shots
    fi = round(f)
    assert abs(f - fi) < 1e-6, f"non-integer fail count {f} -- convention drift"
    return int(fi)

def load_ckpt():
    done = {}
    if os.path.exists(CKPT):
        for line in open(CKPT):
            r = json.loads(line)
            done[(r["row"], r["chunk"])] = r
    return done

def eps_from_pany(p_any, k):
    from evaluator_v1 import per_round
    pk = 1 - (1 - p_any) ** (1.0 / k)
    return per_round(pk, ROUNDS)

def run_row(key, done):
    cfg = ROWS[key]
    H = build_H(key)
    t0 = time.time()
    shots_done = sum(r["shots"] for (rk, _), r in done.items() if rk == key)
    fails = sum(r["fails"] for (rk, _), r in done.items() if rk == key)
    chunk_idx = sum(1 for (rk, _) in done if rk == key)
    killed = None
    def target_shots():
        if shots_done < cfg["stage1"]:
            return cfg["stage1"]
        p_hat = fails / shots_done if shots_done else 0.0
        if fails >= TARGET_EVENTS:
            return shots_done                     # done
        if p_hat <= 0:
            return cfg["cap"]                     # floor-hunting to cap
        return min(cfg["cap"], int(TARGET_EVENTS / p_hat))
    while shots_done < target_shots():
        if (time.time() - t0) / 3600.0 > cfg["wall_h"]:
            killed = "KT1 wall-clock"
            break
        n = min(CHUNK, target_shots() - shots_done)
        seed = cfg["seed_base"] + chunk_idx
        f = chunk_fails(H, cfg["k"], n, seed)
        rec = dict(row=key, chunk=chunk_idx, seed=seed, shots=n, fails=f,
                   cum_shots=shots_done + n, cum_fails=fails + f,
                   t=round(time.time() - t0, 1))
        with open(CKPT, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(json.dumps(rec))
        done[(key, chunk_idx)] = rec
        shots_done += n
        fails += f
        chunk_idx += 1
    # verdict
    p_hat = fails / shots_done if shots_done else 0.0
    lo_c, hi_c = garwood(fails)
    eps = eps_from_pany(p_hat, cfg["k"]) if fails else 0.0
    eps_lo = eps_from_pany(lo_c / shots_done, cfg["k"]) if shots_done else 0.0
    eps_hi = eps_from_pany(hi_c / shots_done, cfg["k"]) if shots_done else 0.0
    kind = "measurement" if fails >= 10 else \
           ("floor" if fails == 0 else "event-starved interval")
    print(json.dumps(dict(
        stage="S8-row", row=cfg["name"], key=key, m=1.0,
        shots=shots_done, fails=fails, p_any=p_hat,
        eps=eps, eps_ci95=[eps_lo, eps_hi],
        floor_eps_ub=(eps_from_pany(3.0 / shots_done, cfg["k"])
                      if fails == 0 and shots_done else None),
        scoreboard_kind=kind, capped=killed,
        wall_s=round(time.time() - t0, 1))))

def run_selftest():
    out = {"stage": "selftest"}
    for q, df, ref in CHI2_ANCHORS:
        got = chi2_ppf(q, df)
        assert abs(got - ref) / ref < 1e-9, f"chi2 anchor drift {q},{df}"
    out["chi2_anchors"] = "ok"
    d = json.load(open("s5_rankmap_data.json"))
    lookup = {"rep2(x)eh8 [16,4,8]": "rep2(x)eh8 [16,4,8]",
              "C3 find [34,6,12]": "C3 find [34,6,12]",
              "rep3(x)eh8 [24,4,12]": "rep3(x)eh8 [24,4,12] (Ch4 winner)",
              "eh8(x)eh8 [64,16,16]": "eh8(x)eh8 [64,16,16] (frontier)"}
    for k, kk in lookup.items():
        assert d[kk]["1.0"] == G2_ANCHORS[k], f"anchor drift: {k}"
    out["g2_anchors"] = "ok"
    import hashlib, inspect
    import evaluator_v1
    src = inspect.getsource(evaluator_v1.make_bposd)
    for tok in ('bp_method="ms"', "max_iter=30", 'osd_method="osd_e"',
                "osd_order=4"):
        assert tok in src, f"decoder drift: {tok}"
    out["decoder_anchor"] = "ok"
    b = json.load(open(C3_ARTIFACT))
    assert b["hash"] == C3_HASH_ANCHOR
    out["c3_hash"] = "ok"
    # structural: all five rows build with expected (n, k)
    from hgp import classical_verify
    expect = dict(winner=(24, 4, 12), frontier=(64, 16, 16), c3=(34, 6, 12),
                  rep7=(7, 1, 7), rep13=(13, 1, 13))
    for key, (n, k, dd) in expect.items():
        H = build_H(key)
        got = classical_verify(H)
        assert got == (n, k, dd), f"{key}: {got}"
    out["rows_structural"] = "ok"
    print(json.dumps(out))
    print(json.dumps({"selftest": "PASS"}))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--rows", default="c3,rep7,rep13,winner,frontier")
    a = ap.parse_args()
    if a.selftest:
        run_selftest()
    elif a.status:
        done = load_ckpt()
        for key in ROWS:
            s = sum(r["shots"] for (rk, _), r in done.items() if rk == key)
            f = sum(r["fails"] for (rk, _), r in done.items() if rk == key)
            print(json.dumps(dict(row=key, shots=s, fails=f)))
    elif a.run:
        done = load_ckpt()
        for key in a.rows.split(","):
            run_row(key.strip(), done)
        print(json.dumps({"verdict": "S8 campaign sweep complete "
                          "(rows may be capped/floored -- see rows)"}))
    else:
        ap.print_help()
