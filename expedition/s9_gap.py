#!/usr/bin/env python3
"""s9_gap.py -- S9 decoder-gap share measurement (Entry 013).

Governed by expedition/PREREG_gapshare.md. Frozen referee; gated S6
machinery reused verbatim (numpy paths -- cross-machine exact). Measures,
per code, the fraction Q of operating-point logical failures that are
DECODER-CREATED: failing shots whose fault set flips no logical observable
(truth = 0). Q is a hard lower bound on the decoder-induced share.

Usage:
  python -u s9_gap.py --selftest
  python -u s9_gap.py --run [--codes rep2eh8,winner,frontier,c3,rep7]
Output: JSONL (python -u).
"""
import argparse
import json
import sys
import time

sys.path.insert(0, ".")
import numpy as np

from s6_sampler import (build_rep2eh8, referee_circuit, dem_matrices,
                        pb_suffix_table, cond_bernoulli_draw, G2_ANCHORS)

C3_HASH_ANCHOR = "f42569e3fb53016f"
PILOT = 300
WALL_KILL_H = 2.5
BOOT = 1000

CODES = dict(
    rep2eh8=dict(name="rep2(x)eh8 [16,4,8]", k=4, seed=910000, budget=250000),
    winner=dict(name="rep3(x)eh8 [24,4,12]", k=4, seed=910001, budget=3000000),
    frontier=dict(name="eh8(x)eh8 [64,16,16]", k=16, seed=910002,
                  budget=1500000),
    c3=dict(name="C3 find [34,6,12]", k=6, seed=910003, budget=250000),
    rep7=dict(name="rep-7 [7,1,7]", k=1, seed=910004, budget=3000000),
)

def build_H(key):
    from s2_seeds import product_code, rep_H, ext_hamming8
    if key == "rep2eh8":
        return build_rep2eh8()[0]
    if key == "winner":
        return product_code(rep_H(3), ext_hamming8())
    if key == "frontier":
        return product_code(ext_hamming8(), ext_hamming8())
    if key == "c3":
        from s5_proposer import h_decode
        b = json.load(open("c3_find_H.json"))
        assert b["hash"] == C3_HASH_ANCHOR, "C3 artifact hash drift -- STOP"
        return h_decode(b)
    if key == "rep7":
        return rep_H(7)
    raise KeyError(key)

def classify_draw(dec, Hd, O, S):
    """Decode fault set S. Returns (fail, benign): fail=1 if pred != truth;
    benign=1 if additionally truth == 0 (decoder-created logical error)."""
    dets = np.zeros(Hd.shape[0], dtype=np.uint8)
    truth = np.zeros(O.shape[0], dtype=np.uint8)
    for j in S:
        dets ^= Hd[:, j]; truth ^= O[:, j]
    e_hat = dec.decode(dets)
    pred = (O @ e_hat.astype(np.uint8)) % 2
    fail = int(np.any(pred != truth))
    benign = int(fail and not np.any(truth))
    missed = int(fail and np.any(truth) and not np.any(pred))
    return fail, benign, missed

def run_code(key):
    cfg = CODES[key]
    from evaluator_v1 import make_bposd
    H = build_H(key)
    circ = referee_circuit(H, 1.0)
    Hd, O, priors = dem_matrices(circ)
    dec = make_bposd(Hd, priors)
    rng = np.random.default_rng(cfg["seed"])
    t0 = time.time()
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
    stats = {w: dict(n=0, fails=0, benign=0, missed=0) for w in strata}
    def draw(w):
        S = cond_bernoulli_draw(priors, R, w, rng)
        f, b, mi = classify_draw(dec, Hd, O, S)
        st = stats[w]
        st["n"] += 1; st["fails"] += f; st["benign"] += b; st["missed"] += mi
    for w in strata:
        for _ in range(PILOT):
            draw(w)
    spent = PILOT * len(strata)
    rem = max(cfg["budget"] - spent, 0)
    def sig(w):
        # contribution allocation: pour budget where the failure MASS lives
        # (P(w)*f_w), which is what determines Q's variance -- not sqrt(f(1-f))
        f = max(stats[w]["fails"] / max(stats[w]["n"], 1), 0.25 / PILOT)
        return Pw[w] * f
    tot = sum(sig(w) for w in strata) or 1.0
    killed = None
    for w in strata:
        for _ in range(int(rem * sig(w) / tot)):
            if (time.time() - t0) / 3600.0 > WALL_KILL_H:
                killed = "KS2 wall-clock"
                break
            draw(w)
        if killed:
            break
    # weighted share + deterministic bootstrap
    def share(resample=None):
        num = den = 0.0
        for w in strata:
            st = stats[w]
            if st["n"] == 0:
                continue
            if resample is None:
                fl, bn = st["fails"], st["benign"]
            else:
                # resample failure count binomially, benign among fails
                fl = resample.binomial(st["n"], st["fails"] / st["n"])
                bn = (resample.binomial(fl, st["benign"] / st["fails"])
                      if st["fails"] > 0 and fl > 0 else 0)
            num += Pw[w] * bn / st["n"]
            den += Pw[w] * fl / st["n"]
        return (num / den) if den > 0 else float("nan"), den
    q, p_fail_weighted = share()
    brng = np.random.default_rng(cfg["seed"] + 500000)
    boots = sorted(share(brng)[0] for _ in range(BOOT))
    lo, hi = boots[int(0.025 * BOOT)], boots[int(0.975 * BOOT)]
    tot_fails = sum(st["fails"] for st in stats.values())
    tot_benign = sum(st["benign"] for st in stats.values())
    tot_missed = sum(st["missed"] for st in stats.values())
    kind = "measurement" if tot_fails >= 30 else "insufficient events (KS1)"
    print(json.dumps(dict(
        stage="S9", code=cfg["name"], key=key, m=1.0,
        decodes=sum(st["n"] for st in stats.values()),
        raw_fails=tot_fails, raw_benign=tot_benign, raw_missed=tot_missed,
        Q_decoder_created_share=round(float(q), 4),
        Q_ci95=[round(float(lo), 4), round(float(hi), 4)],
        weighted_p_fail=float(p_fail_weighted),
        scoreboard_kind=kind, capped=killed, seed=cfg["seed"],
        t_s=round(time.time() - t0, 1))))
    return q, kind

def run_selftest():
    out = {"stage": "selftest"}
    d = json.load(open("s5_rankmap_data.json"))
    lookup = {"rep2(x)eh8 [16,4,8]": "rep2(x)eh8 [16,4,8]",
              "C3 find [34,6,12]": "C3 find [34,6,12]",
              "rep3(x)eh8 [24,4,12]": "rep3(x)eh8 [24,4,12] (Ch4 winner)",
              "eh8(x)eh8 [64,16,16]": "eh8(x)eh8 [64,16,16] (frontier)"}
    for k, kk in lookup.items():
        assert d[kk]["1.0"] == G2_ANCHORS[k], f"anchor drift: {k}"
    out["g2_anchors"] = "ok"
    import inspect
    import evaluator_v1
    src = inspect.getsource(evaluator_v1.make_bposd)
    for tok in ('bp_method="ms"', "max_iter=30", 'osd_method="osd_e"',
                "osd_order=4"):
        assert tok in src, f"decoder drift: {tok}"
    out["decoder_anchor"] = "ok"
    b = json.load(open("c3_find_H.json"))
    assert b["hash"] == C3_HASH_ANCHOR
    out["c3_hash"] = "ok"
    # synthetic classification check on the committed trap basis:
    # a known trap pair must classify as (fail=1, benign=1); a single fault
    # must classify as (fail=0, benign=0)
    from evaluator_v1 import make_bposd
    basis = json.load(open("core_basis_rep2eh8.json"))
    trap = basis["cores"][0]["idx"]
    H = build_rep2eh8()[0] if False else build_H("rep2eh8")
    circ = referee_circuit(H, 1.0)
    Hd, O, priors = dem_matrices(circ)
    dec = make_bposd(Hd, priors)
    f, bn, mi = classify_draw(dec, Hd, O, trap)
    assert (f, bn) == (1, 1), f"trap pair misclassified: {(f, bn)}"
    f2, bn2, _ = classify_draw(dec, Hd, O, [trap[0]])
    assert (f2, bn2) == (0, 0), "single fault misclassified"
    out["classification_check"] = "ok"
    print(json.dumps(out))
    print(json.dumps({"selftest": "PASS"}))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--codes", default="rep2eh8,winner,frontier,c3,rep7")
    a = ap.parse_args()
    if a.selftest:
        run_selftest()
    elif a.run:
        for key in a.codes.split(","):
            run_code(key.strip())
        print(json.dumps({"verdict": "S9 gap-share campaign complete"}))
    else:
        ap.print_help()
