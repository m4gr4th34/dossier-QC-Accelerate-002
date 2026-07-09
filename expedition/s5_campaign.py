#!/usr/bin/env python3
"""s5_campaign.py -- Ch5 Campaign 2 driver: the closed AI loop, run for hours.
PREREG_search2.md governs (frozen fdd8de5); method pin at 3383286.

Runs TWO campaigns under ONE referee, matched compute, SEQUENTIAL:
  learn   -- elitism + crossover + per-compute operator bandit
  random  -- matched-compute pure-random control (no learning)
Best triage-FOM per generation, learn vs random, is Q1's evidence.

Two ratios, never conflated (method pin, NOTEBOOK Day 3):
  triage FOM  -- pilot-depth eps via analytic-fit sort key; STEERING ONLY,
                 never enters the leaderboard.
  scoreboard  -- same_instrument_ratio: candidate vs its D6 strict-rep
                 comparator, BOTH simulated through the same referee at the
                 same deep depth; resolves Q2/Q3/Q4; elites only.

Reuses s5_proposer for ALL proposer/verify/score/learn logic. This file adds
only: the deep same-instrument scoreboard leg, the generational governor,
JSONL logging, and checkpoint/resume.

Referee is LAZY (via s5_proposer.score). --dry-run swaps a deterministic numpy
surrogate so the loop / governor / checkpoint / resume validate WITHOUT
stim/ldpc; real numbers come only from the canonical stack.
"""
import sys, os, json, time, argparse
sys.path.insert(0, ".")
import numpy as np
import s5_proposer as sp

def _rep_H(n):
    """[n,1,n] repetition parity check -- identical to s2_seeds.rep_H, defined
    locally so the numpy-only dry-run path never imports the stim-bearing
    s2_seeds. Not referee logic; the referee itself stays fully reused."""
    H = np.zeros((n - 1, n), dtype=np.uint8)
    for i in range(n - 1):
        H[i, i] = H[i, i + 1] = 1
    return H

PILOT_UNIT = sp.PILOT["shots"]
DEEP_UNITS = sp.DEEP["shots"] / sp.PILOT["shots"]   # deep cost in pilot-units

def _strict_comparator(qlog):
    """D6 strict comparator -- identical to s2_arena.strict_comparator; defined
    locally (pure function) so neither the dry-run nor the real path imports the
    stim-bearing s2_arena. Smallest odd d with 2d-1 >= qlog."""
    d = 3
    while 2 * d - 1 < qlog:
        d += 2
    return d

# =============================================================================
# scoreboard resolver (the only number that reaches the leaderboard)
# =============================================================================
def _per_round(eps_R, R):
    """Exact copy of evaluator_v1.per_round (saturation-aware); inlined so the
    numpy-only dry-run path needs no stim-bearing import."""
    x = max(1.0 - 2.0 * eps_R, 1e-12)
    return 0.5 * (1.0 - x ** (1.0 / R))

def _floor_eps_ub(k, rounds, shots):
    """Per-round per-logical eps for a zero-fail run: rule-of-three 95% upper
    bound p_any <= 3/shots, mapped through the k-th root and the saturation-aware
    per-round conversion. The most a floored side's true rate could be."""
    p_any_ub = 3.0 / shots
    eps_R = 1.0 - (1.0 - p_any_ub) ** (1.0 / k)
    return _per_round(eps_R, rounds)

def same_instrument_ratio(H, n, k, rounds, shots, seed, score_fn):
    """Candidate vs D6 strict-rep comparator, both through the SAME referee at
    the SAME deep depth (same-instrument, depth-matched, per E8). GM optimism
    cancels.

    Zero-fail flooring is handled by rule-of-three (Ch4 convention: zero-fail
    runs publish as 95% bounds, never as point values). Returns
    (ratio, kind, dstar, eps_c, eps_r), kind one of:
      point                    -- both sides > 0; ratio is a point value.
      lower_bound_rep_floored  -- rep floored (0 fails); ratio is a LOWER bound
                                  (candidate >= this many x worse), using rep's
                                  3/shots upper bound as the denominator.
      upper_bound_cand_floored -- candidate floored; ratio is an UPPER bound
                                  (candidate <= this; a bounded win).
      both_floored_unresolved  -- both floored; ratio None, defer to the 2e6
                                  finalist depth (STOP-condition re-check)."""
    qlog = (n + H.shape[0]) / k
    dstar = _strict_comparator(qlog)
    eps_c, _ = score_fn(H, k, rounds, shots, seed)
    eps_r, _ = score_fn(_rep_H(dstar), 1, rounds, shots, seed)
    if eps_c > 0 and eps_r > 0:
        return eps_c / eps_r, "point", dstar, eps_c, eps_r
    if eps_c > 0 and eps_r == 0:                       # rep floored -> lower bound
        return (eps_c / _floor_eps_ub(1, rounds, shots),
                "lower_bound_rep_floored", dstar, eps_c, eps_r)
    if eps_c == 0 and eps_r > 0:                       # candidate floored -> upper bound
        return (_floor_eps_ub(k, rounds, shots) / eps_r,
                "upper_bound_cand_floored", dstar, eps_c, eps_r)
    return None, "both_floored_unresolved", dstar, eps_c, eps_r

# =============================================================================
# dry-run surrogate referee (numpy-only; deterministic in (seed, H))
# =============================================================================
def _surrogate_score(H, k, rounds, shots, seed):
    _, _, d = sp.classical_verify(H)
    rng = np.random.default_rng(np.frombuffer(
        __import__("hashlib").sha256(H.tobytes() + str(seed).encode()).digest()[:8],
        dtype=np.uint64))
    eps = 1e-3 * float(np.exp(-(d or 1))) * (1.0 + 0.05 * rng.standard_normal())
    eps = max(eps, 1e-12)
    return eps, eps

# =============================================================================
# checkpoint / resume
# =============================================================================
def _save_ckpt(path, gen, elites, bandit, rng, elapsed, best_fom, gen_best):
    ck = dict(gen=gen, elapsed=elapsed, best_fom=best_fom, gen_best=gen_best,
              elites=[sp.h_encode(H) for H in elites],
              bandit=(dict(bandit.w) if bandit else None),   # RAW weights (no round)
              rng_state=rng.bit_generator.state)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(ck, f)
    os.replace(tmp, path)

def _load_ckpt(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        ck = json.load(f)
    ck["elites"] = [sp.h_decode(e) for e in ck["elites"]]
    return ck

# =============================================================================
# one campaign
# =============================================================================
def run_campaign(mode, seed, budget_s, outdir, pilot_pop, deep_promote,
                 score_fn, max_gens=10**9):
    os.makedirs(outdir, exist_ok=True)
    jsonl = open(os.path.join(outdir, "candidates.jsonl"), "a")
    ckpt = os.path.join(outdir, "checkpoint.json")

    rng = np.random.default_rng(seed)
    bandit = sp.OperatorBandit(sp.OPS, rng) if mode == "learn" else None
    elites, gen0, elapsed0 = [], 0, 0.0
    best_fom = float("inf")
    gen_best = []

    ck = _load_ckpt(ckpt)
    if ck:
        elites = ck["elites"]; gen0 = ck["gen"] + 1; elapsed0 = ck["elapsed"]
        best_fom = ck["best_fom"]; gen_best = list(ck["gen_best"])
        rng.bit_generator.state = ck["rng_state"]
        if bandit and ck["bandit"]:
            bandit.w = dict(ck["bandit"])
        print(f"  [resume] {mode}: gen {gen0}, {len(elites)} elites, "
              f"{elapsed0/3600:.2f} h elapsed")

    def log(**kw):
        jsonl.write(json.dumps(kw, sort_keys=True) + "\n"); jsonl.flush()

    t0 = time.time()
    for gen in range(gen0, max_gens):
        if elapsed0 + (time.time() - t0) >= budget_s:
            break
        survivors = []
        for _ in range(pilot_pop):
            op = bandit.pick() if bandit else "random"
            H = sp.propose(op, elites, rng)
            ok, (n, k, d), reason = sp.verify_caps(H)
            enc = sp.h_encode(H)
            if not ok:
                log(gen=gen, mode=mode, stage="verify", kept=False,
                    reason=reason, n=n, k=k, hash=enc["hash"])
                if bandit:
                    bandit.update(op, 0.0)      # verify-kill ~ 0 compute, 0 credit
                continue
            # score + credit, guarded so no single candidate can kill the run
            try:
                eps, _ = score_fn(H, k, sp.PILOT["rounds"], sp.PILOT["shots"], seed)
                tri = eps                   # STEERING ONLY = raw pilot eps
                log(gen=gen, mode=mode, stage="pilot", kept=True, n=n, k=k, d=d,
                    w=int(H.sum(axis=1).max()), triage_eps=eps, triage_fom=tri,
                    op=op, hash=enc["hash"], b64=enc["b64"])
                survivors.append((tri, eps, H, n, k, d, op))
                # per-compute credit: RELATIVE frontier improvement / compute
                # (pilot = 1 unit). Both operands clipped at the pilot shot-noise
                # floor 1/shots -- a rate below that is unmeasurable (same
                # rule-of-three honesty as the deep scoreboard), so a floored
                # pilot earns proportionate credit, never a spurious 1.0, and the
                # denominator is never zero.
                ef = 1.0 / sp.PILOT["shots"]
                be, te = max(best_fom, ef), max(tri, ef)
                credit = max(0.0, (be - te) / be) if np.isfinite(be) else 0.0
                best_fom = min(best_fom, tri)
            except Exception as exc:
                log(gen=gen, mode=mode, stage="error", kept=False,
                    reason=f"{type(exc).__name__}: {str(exc)[:200]}",
                    n=n, k=k, d=d, hash=enc["hash"], b64=enc["b64"])
                credit = 0.0                 # errored candidate: no credit, deterministic
            if bandit:
                bandit.update(op, credit)
        if not survivors:
            gen_best.append(None)
            _save_ckpt(ckpt, gen, elites, bandit, rng, elapsed0 + time.time() - t0, best_fom, gen_best)
            continue

        survivors.sort(key=lambda t: t[0])
        gen_best.append(survivors[0][0])

        # deep scoreboard leg -- elites only (the honest cost story)
        for (tri, eps, H, n, k, d, op) in survivors[:deep_promote]:
            enc = sp.h_encode(H)
            try:
                ratio, kind, dstar, ec, er = same_instrument_ratio(
                    H, n, k, sp.DEEP["rounds"], sp.DEEP["shots"], seed, score_fn)
                log(gen=gen, mode=mode, stage="deep", kept=True, n=n, k=k, d=d,
                    w=int(H.sum(axis=1).max()), qlog=(n + H.shape[0]) / k,
                    scoreboard_ratio=ratio, scoreboard_kind=kind,
                    needs_finalist=(kind == "both_floored_unresolved"),
                    rep_dstar=dstar, eps_cand=ec, eps_rep=er,
                    op=op, hash=enc["hash"], b64=enc["b64"])
            except Exception as exc:
                log(gen=gen, mode=mode, stage="error_deep", kept=False,
                    reason=f"{type(exc).__name__}: {str(exc)[:200]}",
                    n=n, k=k, d=d, hash=enc["hash"], b64=enc["b64"])
            # no bandit credit here: deep is the scoreboard leg, not steering
            # (the op was already credited once at pilot; deep would double-count)

        # LEARN: elitism (top-E by triage FOM = pilot eps; carried + this gen)
        if mode == "learn":
            pool = [(_peek_eps(H, seed, score_fn), H) for H in elites]
            pool += [(t[0], t[2]) for t in survivors]
            pool.sort(key=lambda x: x[0])
            elites = [H for _, H in pool[:6]]
        else:
            elites = []   # random control carries nothing

        _save_ckpt(ckpt, gen, elites, bandit, rng, elapsed0 + time.time() - t0, best_fom, gen_best)
        print(f"  {mode} gen {gen}: best triage-FOM "
              f"{gen_best[-1]:.3e}  (survivors {len(survivors)}/{pilot_pop}, "
              f"{(elapsed0+time.time()-t0)/3600:.2f} h)"
              + (f"  bandit {bandit.snapshot()}" if bandit else ""))

    jsonl.close()
    summary = dict(mode=mode, seed=seed, generations=len(gen_best),
                   gen_best_triage_fom=gen_best,
                   final_bandit=(bandit.snapshot() if bandit else None),
                   elapsed_h=(elapsed0 + time.time() - t0) / 3600)
    with open(os.path.join(outdir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    return summary

def _peek_eps(H, seed, score_fn):
    """Cheap re-score of a carried elite for elitism ranking (pilot depth)."""
    k = H.shape[1] - sp.rank2(H)
    eps, _ = score_fn(H, max(k, 1), sp.PILOT["rounds"], sp.PILOT["shots"], seed)
    return eps

# =============================================================================
# main -- sequential learn then random, matched compute
# =============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget-hours", type=float, default=8.0)
    ap.add_argument("--seed", type=int, default=20260708)
    ap.add_argument("--out", default="s5_run")
    ap.add_argument("--pilot-pop", type=int, default=40)
    ap.add_argument("--deep-promote", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-gens", type=int, default=10**9)
    a = ap.parse_args()

    score_fn = _surrogate_score if a.dry_run else sp.score
    per_mode_s = a.budget_hours * 3600 / 2.0    # sequential, matched wall-clock
    print(f"Ch5 Campaign 2 | dry_run={a.dry_run} | {a.budget_hours}h "
          f"({per_mode_s/3600:.2f}h/mode) | pilot_pop={a.pilot_pop} "
          f"deep_promote={a.deep_promote} | seed={a.seed}")

    for mode in ("learn", "random"):
        print(f"\n=== {mode} ===")
        s = run_campaign(mode, a.seed, per_mode_s,
                         os.path.join(a.out, mode, str(a.seed)),
                         a.pilot_pop, a.deep_promote, score_fn, a.max_gens)
        print(f"  {mode} done: {s['generations']} gens, {s['elapsed_h']:.2f} h")

    # Q1 headline: learn vs random best triage-FOM trajectory
    def _best(mode):
        p = os.path.join(a.out, mode, str(a.seed), "summary.json")
        v = [x for x in json.load(open(p))["gen_best_triage_fom"] if x is not None]
        return min(v) if v else None
    bl, br = _best("learn"), _best("random")
    print(f"\nQ1 readout: learn best-triage-FOM {bl} vs random {br} "
          f"(lower is better; CI-clear separation adjudicated in strategy room)")

if __name__ == "__main__":
    main()
