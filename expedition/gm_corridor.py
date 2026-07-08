#!/usr/bin/env python3
"""gm_corridor.py -- OPEN-6 prototype: Ruiz comparability corridor.

Repetition-code (phase) memory under the Guillaud-Mirrahimi dissipative-gate
cat channel, at Ruiz's operating point (kappa_1/kappa_2 = 1e-4, nbar = 11,
every operation of duration T = 1/kappa_2 [QUOTED, Ruiz Nat. Commun. 16, 1040]).

CNOT channel [Guillaud & Mirrahimi, PRX 9, 041053 (2019), Sec. VI; fetched
2026-07-07, constants pending PDF byte-check]:
    p_Z(control)   = nbar*k1*T + 1/(2*pi*nbar*k2*T)
    p_Z(target)    = nbar*k1*T/2
    p_Z1Z2 (corr.) = nbar*k1*T/2
Idle for one op-slot: p_Z = nbar*k1*T.  Prep |+>: p_Z = nbar*k1*T (order-level).
Measurement flip p_m: NOT verified from primary -> swept over a decade; the
corridor verdict must hold across the sweep (robustness, not tuning).

Target curve [QUOTED, Ruiz Fig. 3 caption]:
    eps_zL = 0.07 * (486 * k1/k2)^(0.94 * floor((d+1)/2))
Evaluated IN CODE from the quoted form (ledger E5: a fetch-summarizer evaluation
of this formula was arithmetically wrong -- exponent 0.94 instead of 1.88 at d=3;
caught by computing from the quoted formula rather than trusting derived numbers).

Corridor grade: SAME-ORDER agreement (factor ~3), per DERIV. Their model is
master-equation-derived and differs in gate-level detail; this is a corridor
check, not a reproduction.
"""
import math
import sys
sys.path.insert(0, ".")
import numpy as np
import stim
from evaluator_v1 import logical_rate, per_round

NBAR = 11.0
K_RATIO = 1e-4
# per-op-slot (T = 1/kappa_2) probabilities
P_IDLE = NBAR * K_RATIO                        # 1.1e-3
P_CX_CTRL = NBAR * K_RATIO + 1.0 / (2 * math.pi * NBAR)   # 1.1e-3 + 1.447e-2
P_CX_TGT = NBAR * K_RATIO / 2                  # 5.5e-4
P_CX_ZZ = NBAR * K_RATIO / 2                   # 5.5e-4
P_PREP = NBAR * K_RATIO

def ruiz_fit(d, k_ratio=K_RATIO):
    return 0.07 * (486 * k_ratio) ** (0.94 * ((d + 1) // 2))

def rep_gm_circuit(d, rounds, p_m):
    """Phase-flip repetition code (XX checks), cat ancillas, GM gate channel.
    Cycle = 4 op-slots: prep | CX(anc->left) | CX(anc->right) | measure.
    Data qubits idle-dephase in every slot they are not a CX target."""
    n = d
    anc = list(range(n, n + n - 1))
    data = list(range(n))
    c = stim.Circuit()
    c.append("RX", data)
    mcount = 0
    meas = {}
    for r in range(rounds):
        slots_used = np.zeros(n)
        # slot 0: ancilla prep (data idle)
        c.append("RX", anc)
        c.append("Z_ERROR", anc, P_PREP)
        # slots 1,2: CX(anc -> data i), CX(anc -> data i+1); GM channel per gate
        for step in (0, 1):
            for i in range(n - 1):
                tgt = i + step
                c.append("CX", [anc[i], tgt])
                c.append("Z_ERROR", [anc[i]], P_CX_CTRL)
                c.append("Z_ERROR", [tgt], P_CX_TGT)
                c.append("E", [stim.target_z(anc[i]), stim.target_z(tgt)], P_CX_ZZ)
                slots_used[tgt] += 1
        # slot 3: ancilla measure (data idle)
        for i in range(n - 1):
            if p_m > 0:
                c.append("Z_ERROR", [anc[i]], p_m)
            c.append("MX", [anc[i]])
            meas[(r, i)] = mcount; mcount += 1
        # data idle top-up: 4 slots total minus CX-target slots
        for q in data:
            idle_slots = 4 - slots_used[q]
            if idle_slots > 0:
                c.append("Z_ERROR", [q], 1 - (1 - P_IDLE) ** idle_slots)
        for i in range(n - 1):
            cur = meas[(r, i)]
            if r == 0:
                c.append("DETECTOR", [stim.target_rec(cur - mcount)])
            else:
                c.append("DETECTOR", [stim.target_rec(cur - mcount),
                                      stim.target_rec(meas[(r - 1, i)] - mcount)])
    c.append("MX", data)
    dpos = {q: mcount + j for j, q in enumerate(data)}
    mcount += n
    for i in range(n - 1):
        c.append("DETECTOR", [stim.target_rec(dpos[i] - mcount),
                              stim.target_rec(dpos[i + 1] - mcount),
                              stim.target_rec(meas[(rounds - 1, i)] - mcount)])
    c.append("OBSERVABLE_INCLUDE", [stim.target_rec(dpos[0] - mcount)], 0)
    return c

def channel(nbar, k_ratio):
    return dict(p_idle=nbar * k_ratio,
                p_ctrl=nbar * k_ratio + 1.0 / (2 * math.pi * nbar),
                p_tgt=nbar * k_ratio / 2, p_zz=nbar * k_ratio / 2,
                p_prep=nbar * k_ratio)

if __name__ == "__main__":
    for k_ratio in (1e-4, 1e-3):
        ch = channel(NBAR, k_ratio)
        globals().update(P_IDLE=ch["p_idle"], P_CX_CTRL=ch["p_ctrl"],
                         P_CX_TGT=ch["p_tgt"], P_CX_ZZ=ch["p_zz"], P_PREP=ch["p_prep"])
        print(f"k1/k2={k_ratio:.0e}: p_idle={P_IDLE:.2e} p_cx_ctrl={P_CX_CTRL:.2e} "
              f"p_cx_tgt={P_CX_TGT:.2e} p_zz={P_CX_ZZ:.2e}")
        for d, shots in ((3, 200000), (5, 2000000 if k_ratio == 1e-4 else 200000)):
            tgt = ruiz_fit(d, k_ratio)
            rounds = 2 * d
            print(f"  d={d}: Ruiz fit target = {tgt:.3e}  (rounds={rounds}, shots={shots})")
            for p_m in (2e-3, 6e-3, 2e-2):
                c = rep_gm_circuit(d, rounds, p_m)
                rr = logical_rate(c, shots, seed=71, decoder="pymatching")
                r = per_round(rr, rounds)
                ratio = r / tgt if tgt > 0 else float("inf")
                print(f"    p_m={p_m:.0e}: eps_zL/cycle = {r:.3e} "
                      f"(fails={int(round(rr*shots))})  ratio to fit = {ratio:5.2f}")
