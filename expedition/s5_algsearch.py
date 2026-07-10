#!/usr/bin/env python3
"""s5_algsearch.py -- Campaign 3 driver: algebraic-fitness closed loop.
PREREG_search3.md governs. Entry 005's decision implemented: fitness is
EXACT ALGEBRA from VERIFY -- it cannot saturate, floor, or lie. The simulated
referee is demoted to finalist verification (separate, later step).

FITNESS (maximize): qubit efficiency  eff = k / (n + r)
CONSTRAINTS (hard): d >= DMIN (=12, the Ch4 winner's protection), w <= 4,
                    n <= 64, 1 <= k <= KEXACT (exact d from classical_verify).
    HONESTY NOTE: logical_min_weight's randomized path returns an UPPER bound
    (it finds low-weight logicals; true d could be lower) -- it CANNOT certify
    d >= DMIN. So k > KEXACT candidates are logged as d_unverified WATCHLIST
    rows (H preserved for extended exact verification) but earn no fitness,
    no credit, and no frontier claim. The campaign proper is the exact-d region.
Constraint form is rate-proof: distance is a floor, not a divisor.

Runs learn (elitism + crossover + bandit; credit = relative frontier
improvement in eff) vs matched random control. No stim anywhere: full
validation possible on the numpy stack. Candidates clearing the frozen
landmark frontier are logged as frontier_events for finalist referee review.
"""
import sys, os, json, time, math, argparse
sys.path.insert(0, ".")
import numpy as np
import s5_proposer as sp                       # PROPOSE/LEARN reused verbatim
from hgp import classical_verify
from verify_code import rank2, rref2

DMIN, WCAP, NCAP = 12, 4, 64
KEXACT = 16
LMW_TRIES = 2000                               # watchlist screen effort

# frozen landmark frontier (PREREG_search3): best known eff at d>=DMIN, w<=WCAP
FRONTIER_BEST = 0.1250                          # eh8(x)eh8 [64,16,16]
WINNER_EFF = 0.0769                             # rep3(x)eh8 [24,4,12]

def evaluate(H, rng):
    """(ok, record). Exact d for k<=KEXACT; certified lower bound above.
    Deterministic: bound rng is seeded from the candidate hash."""
    n = H.shape[1]; r = H.shape[0]
    if n > NCAP:
        return False, dict(reason="n>cap", n=n)
    w = int(H.sum(axis=1).max()) if r else 0
    if w > WCAP:
        return False, dict(reason="w>cap", n=n)
    k = n - rank2(H)
    if k < 1:
        return False, dict(reason="k<1", n=n)
    if k > n - DMIN + 1:      # Singleton: d <= n-k+1, so d>=DMIN forces k <= n-DMIN+1
        return False, dict(reason="singleton", n=n, k=k)
    if k > KEXACT:
        # upper bound can't certify d>=DMIN: no fitness, no claim, ever.
        # The ~1s lmw screen is paid ONLY for candidates whose efficiency
        # would beat the frontier (the interesting fringe); the rest are
        # instant kills -- keeps the loop at algebraic speed.
        if k / (n + r) <= FRONTIER_BEST:
            return False, dict(reason="k>KEXACT_uninteresting", n=n, k=k)
        # NO in-loop screening (lmw at kernel-dim ~22 costs ~8s -- 100x the
        # loop's speed). Log-and-defer: the H rides in the watchlist row and
        # gets screened OFFLINE after the run. Honesty preserved, speed kept.
        return False, dict(reason="k>KEXACT_watchlist", n=n, k=k,
                           watchlist=True)
    _, _, d = classical_verify(H)
    if d is None or d < DMIN:
        return False, dict(reason=f"d<{DMIN}", n=n, k=k, d=d)
    eff = k / (n + r)
    return True, dict(n=n, k=k, d=int(d), dkind="exact", w=w, r=r, eff=eff)

def _bound_rng(H):
    h = int.from_bytes(sp.h_encode(H)["hash"].encode()[:8], "little")
    return np.random.default_rng(h % (2**63))

def run(mode, seed, budget_s, outdir, pop, max_gens=10**9):
    os.makedirs(outdir, exist_ok=True)
    jsonl = open(os.path.join(outdir, "candidates.jsonl"), "a")
    def log(**kw): jsonl.write(json.dumps(kw, sort_keys=True) + "\n"); jsonl.flush()
    rng = np.random.default_rng(seed)
    bandit = sp.OperatorBandit(sp.OPS, rng) if mode == "learn" else None
    elites, gen_best, best = [], [], 0.0
    t0 = time.time()
    for gen in range(max_gens):
        if time.time() - t0 >= budget_s: break
        surv = []
        for _ in range(pop):
            op = bandit.pick() if bandit else "random"
            H = sp.propose(op, elites, rng)
            ok, rec = evaluate(H, _bound_rng(H))
            if not ok:
                if rec.get("watchlist"):        # k>KEXACT, screen not below DMIN
                    enc = sp.h_encode(H)
                    log(gen=gen, mode=mode, stage="watchlist", op=op,
                        hash=enc["hash"], b64=enc["b64"], **rec)
                if bandit: bandit.update(op, 0.0)
                continue
            enc = sp.h_encode(H)
            row = dict(gen=gen, mode=mode, stage="fit", op=op,
                       hash=enc["hash"], **rec)
            if rec["eff"] > best:                    # NEW RUNNING-BEST: full H
                row["running_best"] = True           # (Entry 006 fix: the top
                row["b64"] = enc["b64"]              # find must live in the log,
                row["shape"] = enc["shape"]          #  not be replay-only;
            if rec["eff"] > FRONTIER_BEST:          #  shape needed by h_decode)
                row["frontier_event"] = True
                row["b64"] = enc["b64"]
                row["shape"] = enc["shape"]
            log(**row)
            surv.append((rec["eff"], H))
            if bandit:
                credit = max(0.0, (rec["eff"] - best) / max(best, 1e-9))
                bandit.update(op, min(credit, 1.0))
            best = max(best, rec["eff"])
        gen_best.append(max((e for e, _ in surv), default=None))
        if mode == "learn" and surv:
            pool = sorted(elites_scored(elites) + surv, key=lambda t: -t[0])
            elites = [H for _, H in pool[:8]]
        elif mode == "random":
            elites = []
    jsonl.close()
    summ = dict(mode=mode, seed=seed, generations=len(gen_best),
                best_eff=best, gen_best=gen_best[-20:],
                frontier_best_known=FRONTIER_BEST, winner_eff=WINNER_EFF,
                bandit=(bandit.snapshot() if bandit else None),
                elapsed_s=time.time() - t0)
    with open(os.path.join(outdir, "summary.json"), "w") as f:
        json.dump(summ, f, indent=2)
    return summ

def elites_scored(elites):
    out = []
    for H in elites:
        ok, rec = evaluate(H, _bound_rng(H))
        if ok: out.append((rec["eff"], H))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget-min", type=float, default=15.0)
    ap.add_argument("--seed", type=int, default=20260710)
    ap.add_argument("--out", default="s5_run3")
    ap.add_argument("--pop", type=int, default=200)
    ap.add_argument("--max-gens", type=int, default=10**9)
    a = ap.parse_args()
    for mode in ("learn", "random"):
        print(f"=== {mode} ({a.budget_min} min) ===")
        s = run(mode, a.seed, a.budget_min * 60,
                os.path.join(a.out, mode, str(a.seed)), a.pop, a.max_gens)
        print(f"  gens={s['generations']} best_eff={s['best_eff']:.4f} "
              f"(frontier {FRONTIER_BEST}, winner {WINNER_EFF})"
              + (f" bandit={s['bandit']}" if s["bandit"] else ""))
    print("\nP-readouts: learn-vs-random best_eff + trajectories in summary.json;"
          " frontier_events (if any) carry full H for finalist referee review.")

if __name__ == "__main__":
    main()
