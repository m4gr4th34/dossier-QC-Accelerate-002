#!/usr/bin/env python3
"""s5_proposer.py -- Ch5 Campaign 2: the automated proposer (a closed AI loop).
PREREG_search2.md governs (frozen fdd8de5).

REUSE, DON'T REBUILD: the referee is s2_arena's circuit-level GM instrument,
untouched. This module is ONLY the front-end (PROPOSE) and the LEARN station.

The loop, unattended:
  PROPOSE -> VERIFY (classical_verify + caps) -> SCORE (pilot -> deep, elites)
  -> LEARN (elitism + crossover + per-compute operator bandit) -> PROPOSE ...

Two campaigns run under identical referee/triage/budget:
  * the learning loop (elitism + crossover + bandit)
  * a matched-compute pure-random control (no learning)
Best-FOM-per-generation, loop vs control, is Q1's evidence.

X-only extraction: a candidate IS a classical parity-check matrix H used as the
phase (Z) checks; bit logicals weight-1 (analytic floor). Scoring mirrors
s2_arena.run_leg EXACTLY:
    fom(H, empty_Hz, k, rounds, p_m, nbar, k_ratio, "xonly", shots, seed)

VERIFY tractability (pre-run harness parameter, physics-neutral -- see PREREG
addendum): exact classical_verify enumerates 2^k codewords, so it is the cheap
gate only for k <= KMAX. Candidates with k > KMAX are KILLED and LOGGED
(reason "k>KMAX"); they are the few-check/high-k/low-d corner (junk at d>=3),
never the low-k usable codes the campaign targets.

Determinism: master seed; every candidate appended to JSONL; per-generation
checkpoint. A re-run from the seed reproduces the leaderboard (PREREG
determinism gate) or the result is not reported.

Heavy referee imports (stim/ldpc via gm_css, evaluator_v1) are LAZY -- inside
score() -- so PROPOSE/VERIFY/LEARN/logging/checkpoint (--selftest) run on the
numpy-only stack; real numbers come only from the canonical stack.
"""
import sys, json, time, base64, hashlib
sys.path.insert(0, ".")
import numpy as np
from hgp import classical_verify                 # numpy-only (exact n,k,d)
from verify_code import rank2, rref2             # numpy-only

# ---- frozen from Ch4 (s2_arena), NOT re-tuned -------------------------------
GM = dict(nbar=11.0, k_ratio=1e-4, p_m=6e-3)
CAPS = dict(w=4, n=40, kmin=1, dmin=3)
KMAX = 16                                          # exact-distance tractability
PILOT = dict(shots=20000, rounds=8)
DEEP = dict(shots=400000, rounds=16)               # elites; top finalist -> 2e6

# =============================================================================
# PROPOSE
# =============================================================================
def random_sparse_H(rng, n=None):
    n = int(n if n is not None else rng.integers(5, CAPS["n"] + 1))
    r = int(rng.integers(2, n))
    H = np.zeros((r, n), dtype=np.uint8)
    for i in range(r):
        w = int(rng.integers(2, CAPS["w"] + 1))
        H[i, rng.choice(n, size=w, replace=False)] = 1
    return H

def mutate(H, rng):
    """Single-bit flip, reverted if it breaks the [2, w] row-weight window."""
    if H.shape[0] == 0:
        return H
    H = H.copy()
    i, j = int(rng.integers(H.shape[0])), int(rng.integers(H.shape[1]))
    H[i, j] ^= 1
    s = int(H[i].sum())
    if s > CAPS["w"] or s < 2:
        H[i, j] ^= 1
    return H

def crossover(Ha, Hb, rng):
    """Recombine two elite phase-check matrices: restrict to the shared column
    range, keep a random subset of each parent's cap-legal rows. Crude by design
    -- a proposal, not a guarantee; VERIFY is the referee (Day-1 doctrine)."""
    n = min(Ha.shape[1], Hb.shape[1])
    rows = []
    for M in (Ha[:, :n], Hb[:, :n]):
        for row in M:
            if 2 <= int(row.sum()) <= CAPS["w"] and rng.random() < 0.5:
                rows.append(row)
    if not rows:
        return Ha[:, :n].copy()
    return np.array(rows, dtype=np.uint8)

OPS = ("mutate", "crossover", "random")

def propose(op, elites, rng):
    if op == "random" or not elites:
        return random_sparse_H(rng)
    if op == "crossover" and len(elites) >= 2:
        a, b = (elites[int(rng.integers(len(elites)))] for _ in range(2))
        return crossover(a, b, rng)
    return mutate(elites[int(rng.integers(len(elites)))], rng)

# =============================================================================
# VERIFY
# =============================================================================
def verify_caps(H):
    """(ok, (n,k,d), reason). Exact only for k<=KMAX; physics-neutral cost gate."""
    n = H.shape[1]
    k = n - rank2(H)
    if k < CAPS["kmin"]:
        return False, (n, k, None), "k<kmin"
    if n > CAPS["n"]:
        return False, (n, k, None), "n>ncap"
    w = int(H.sum(axis=1).max()) if H.shape[0] else 0
    if w > CAPS["w"]:
        return False, (n, k, None), "w>wcap"
    if k > KMAX:
        return False, (n, k, None), "k>KMAX"
    _, _, d = classical_verify(H)
    if d is None or d < CAPS["dmin"]:
        return False, (n, k, d), "d<dmin"
    return True, (n, k, d), None

# =============================================================================
# SCORE  (lazy heavy imports; mirrors s2_arena.run_leg byte-for-byte)
# =============================================================================
def score(H, k, rounds, shots, seed):
    from gm_css import fom
    Hz = np.zeros((0, H.shape[1]), dtype=np.uint8)
    pk, p_any, _, _ = fom(H, Hz, k, rounds, GM["p_m"], GM["nbar"], GM["k_ratio"],
                          "xonly", shots, seed=seed)
    return pk, p_any

def ratio_to_comparator(H, n, k, pk):
    from s2_arena import strict_comparator
    from gm_corridor import ruiz_fit
    qlog = (n + H.shape[0]) / k
    dstar = strict_comparator(qlog)
    er = ruiz_fit(dstar)
    return (pk / er if er else float("inf")), dstar, er

# =============================================================================
# LEARN
# =============================================================================
class OperatorBandit:
    """Reward-weighted selection over proposal operators. Credit = PER-COMPUTE
    frontier improvement: max(0, parent_best_fom - child_fom) / compute_spent,
    where compute is the shots the child actually consumed before dying
    (VERIFY-killed ~ 0 -> undefined credit, skipped; pilot -> PILOT shots; deep
    -> DEEP shots). Rewards operators whose offspring improve the frontier
    CHEAPLY. Raw (non-per-compute) improvement is logged alongside for the
    chapter's legible story."""
    def __init__(self, ops, rng, lr=0.15, floor=0.05):
        self.ops, self.rng, self.lr, self.floor = list(ops), rng, lr, floor
        self.w = {o: 1.0 for o in self.ops}

    def pick(self):
        tot = sum(self.w.values())
        r = self.rng.random() * tot
        c = 0.0
        for o in self.ops:
            c += self.w[o]
            if r <= c:
                return o
        return self.ops[-1]

    def update(self, op, credit):
        self.w[op] *= (1.0 + self.lr * max(credit, 0.0))
        tot = sum(self.w.values()); m = len(self.ops)
        for o in self.ops:
            self.w[o] = self.floor / m + (1.0 - self.floor) * self.w[o] / tot

    def snapshot(self):
        return {o: round(v, 5) for o, v in self.w.items()}

# =============================================================================
# logging / determinism helpers
# =============================================================================
def h_encode(H):
    b = np.ascontiguousarray(H, dtype=np.uint8).tobytes()
    return dict(shape=list(H.shape),
                b64=base64.b64encode(b).decode(),
                hash=hashlib.sha256(b + str(H.shape).encode()).hexdigest()[:16])

def h_decode(rec):
    b = base64.b64decode(rec["b64"])
    return np.frombuffer(b, dtype=np.uint8).reshape(rec["shape"]).copy()

def row_equiv(Ha, Hb):
    """True iff Ha, Hb (same n) have equal row spans -- exact GF(2) test."""
    if Ha.shape[1] != Hb.shape[1]:
        return False
    return np.array_equal(rref2(Ha.copy())[0], rref2(Hb.copy())[0])

# =============================================================================
# --selftest : numpy-only; proves the loop closes + reproduces (no referee)
# =============================================================================
def _selftest():
    def run(seed):
        rng = np.random.default_rng(seed)
        bandit = OperatorBandit(OPS, rng)
        elites, hashes, kills = [], [], 0
        for _ in range(600):
            op = bandit.pick()
            H = propose(op, elites, rng)
            ok, (n, k, d), reason = verify_caps(H)
            if not ok:
                kills += 1
                bandit.update(op, 0.0)
                continue
            fom_proxy = (n + H.shape[0]) / (k * d)   # cheap stand-in for referee
            hashes.append(h_encode(H)["hash"])
            elites.append(H)
            elites = sorted(elites, key=lambda M: len(M))[:6]
            bandit.update(op, 1.0 / fom_proxy)
        return hashes, kills, bandit.snapshot()

    h1, kills, snap = run(20260708)
    h2, _, _ = run(20260708)
    assert h1 == h2, "DETERMINISM FAIL: identical seeds diverged"
    assert kills > 0, "expected VERIFY kills in the broad space"
    # round-trip
    rng = np.random.default_rng(1)
    H = random_sparse_H(rng)
    assert np.array_equal(H, h_decode(h_encode(H))), "encode/decode round-trip fail"
    # row-equivalence sanity
    A = np.array([[1, 1, 0], [0, 1, 1]], np.uint8)
    assert row_equiv(A, A[::-1].copy()), "row_equiv should ignore row order"
    assert not row_equiv(A, np.array([[1, 0, 0], [0, 1, 0]], np.uint8))
    print(f"SELFTEST PASS  candidates_kept={len(h1)} verify_kills={kills}")
    print(f"  determinism: {len(h1)} hashes identical across two seeded runs")
    print(f"  bandit weights (per-compute credit): {snap}")
    print(f"  KMAX={KMAX} CAPS={CAPS}")

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print("usage: python3 s5_proposer.py --selftest    "
              "(campaign driver added in block 3, after referee smoke)")
