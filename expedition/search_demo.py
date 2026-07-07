#!/usr/bin/env python3
"""
search_demo.py — the loop, closed (micro-scale demo).

decide: evolutionary proposal (mutate/crossover sparse Hx/Hz under wmax<=6)
make:   candidate CSS matrices at fixed n=12, k==1 (apples-to-apples vs baselines)
verify: verify_code.verify() gates EVERYTHING (valid CSS, k==1) — nothing unverified scores
measure: FOM = logical error rate at p=0.01, eta=30 (the mixed regime the calibration exposed)
learn:  selection + elitism steer the next generation

Baselines in the arena: phase-rep-12, shor 3x4, shor 2x6.
Honest outcomes ranked equally: (a) beat baselines, (b) rediscover them, (c) lose — all
are loop-demo successes; only the FOM decides. Search-grade shots are small (rankable,
noisy); finalists re-scored at higher shots with a fresh seed.
"""
import numpy as np, time
from verify_code import verify
from fom import phase_rep, shor_ML, logical_error_rate

N, WMAX, P, ETA = 12, 6, 0.01, 30
POP, GENS, SEED = 22, 8, 11
SHOTS_SEARCH, SHOTS_FINAL = 3000, 24000
rng = np.random.default_rng(SEED)

def random_code():
    rx, rz = rng.integers(2, 6), rng.integers(4, 9)
    def rows(r):
        M = np.zeros((r, N), dtype=np.uint8)
        for i in range(r):
            w = rng.integers(2, WMAX + 1)
            M[i, rng.choice(N, size=w, replace=False)] = 1
        return M
    return rows(rx), rows(rz)

def mutate(Hx, Hz):
    Hx, Hz = Hx.copy(), Hz.copy()
    M = Hx if rng.random() < 0.5 and Hx.shape[0] else Hz
    if M.shape[0]:
        i, j = rng.integers(M.shape[0]), rng.integers(N)
        M[i, j] ^= 1
        if M[i].sum() > WMAX or M[i].sum() < 2:
            M[i, j] ^= 1
    return Hx, Hz

def gate(Hx, Hz):
    v = verify(Hx, Hz)
    return v if (v["valid"] and v["k"] == 1 and v["wmax"] <= WMAX) else None

def fom(Hx, Hz, shots, seed):
    return logical_error_rate(Hx, Hz, P, ETA, shots=shots, seed=seed)

if __name__ == "__main__":
    t0 = time.time()
    baselines = {"phase-rep-12": phase_rep(12), "shor3x4": shor_ML(3, 4),
                 "shor2x6": shor_ML(2, 6)}   # shor4x3/6x2 excluded: check weight > WMAX (the constraint prunes hand designs too)
    print(f"ARENA n={N} k=1 wmax<={WMAX} | p={P} eta={ETA} | baselines:")
    base_scores = {}
    for nm, (Hx, Hz) in baselines.items():
        v = gate(Hx, Hz); assert v, nm
        base_scores[nm] = fom(Hx, Hz, SHOTS_FINAL, seed=999)
        print(f"  {nm:14s} dx={v['dx']} dz={v['dz']} wmax={v['wmax']}  FOM={base_scores[nm]:.5f}")
    best_base = min(base_scores.values())

    # seed population: baselines + random valid codes
    pop = []
    for nm, (Hx, Hz) in baselines.items():
        pop.append((Hx, Hz))
    tries = 0
    while len(pop) < POP and tries < 4000:
        Hx, Hz = random_code(); tries += 1
        if gate(Hx, Hz): pop.append((Hx, Hz))
    print(f"\nseeded {len(pop)} verified candidates ({tries} random draws)")

    verified_total, gen_best = len(pop), []
    for g in range(GENS):
        scored = []
        for (Hx, Hz) in pop:
            scored.append((fom(Hx, Hz, SHOTS_SEARCH, seed=100 + g), Hx, Hz))
        scored.sort(key=lambda t: t[0])
        gen_best.append(scored[0][0])
        elites = scored[:6]
        nxt = [(Hx, Hz) for _, Hx, Hz in elites]
        while len(nxt) < POP:
            _, Hx, Hz = elites[rng.integers(len(elites))]
            cHx, cHz = mutate(Hx, Hz)
            if gate(cHx, cHz):
                nxt.append((cHx, cHz)); verified_total += 1
        pop = nxt
        print(f"  gen {g}: best search-FOM {gen_best[-1]:.5f}  (verified so far: {verified_total})")

    # finalists re-scored fresh
    finals = []
    for (Hx, Hz) in pop[:6]:
        v = gate(Hx, Hz)
        finals.append((fom(Hx, Hz, SHOTS_FINAL, seed=2027), v, Hx, Hz))
    finals.sort(key=lambda t: t[0])
    print("\nFINALISTS (re-scored, fresh seed, 24k shots):")
    for f, v, Hx, Hz in finals[:3]:
        print(f"  FOM={f:.5f}  [[{v['n']},{v['k']}]] dx={v['dx']} dz={v['dz']} wmax={v['wmax']}")
    champ = finals[0]
    print(f"\nbest baseline FOM={best_base:.5f} | search champion FOM={champ[0]:.5f}")
    verdict = ("SEARCH BEAT THE BASELINES" if champ[0] < best_base * 0.85 else
               "SEARCH MATCHED THE BASELINES (rediscovery-grade)" if champ[0] < best_base * 1.15 else
               "SEARCH LOST TO THE BASELINES — kept negative")
    print("VERDICT:", verdict)
    print(f"loop ran unattended: {GENS} generations, {verified_total} verifier-gated candidates, "
          f"{time.time()-t0:.0f}s")
    # print champion matrices for the record
    print("\nchampion Hx:\n", champ[2], "\nchampion Hz:\n", champ[3])
