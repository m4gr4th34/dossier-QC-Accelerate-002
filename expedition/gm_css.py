#!/usr/bin/env python3
"""gm_css.py -- Campaign 1 harness: GM-gate channel for ARBITRARY CSS outer codes.

Generalizes gm_corridor.py from repetition codes to any (Hx, Hz):
  - syndrome-extraction schedule by greedy edge-coloring of each Tanner graph
    (no data qubit or ancilla in two gates per slot; slot count reported);
  - GM CNOT channel per gate [Guillaud & Mirrahimi, PRX 9, 041053, Sec. VI;
    constants pending OPEN-7 byte-check]: the CONTROL carries the non-adiabatic
    term. X-checks: ancilla is control. Z-checks: DATA is control -- so Z-check
    extraction taxes data qubits directly, which is why extraction_mode
    "xonly" exists (bit floor at nbar=11 is ~1e-9, handled analytically;
    Ruiz's LDPC-cat architecture likewise measures phase checks only);
  - k logical observables tracked simultaneously; per-logical convention
    Pk = 1-(1-P_any)^(1/k) (Day-1 resolver.py convention);
  - BP-OSD on the circuit DEM (search-harness decoder), pymatching where the
    DEM is matchable (repetition regression only).

Cycle = 1 prep slot + (X-block colors) + (Z-block colors if mode=full) + 1
measurement slot; idle dephasing p = nbar*k1/k2 per slot on every idle qubit.
Regression gate: rep-d through THIS harness must reproduce gm_corridor.py.
"""
import math
import sys
sys.path.insert(0, ".")
import numpy as np
import stim
from evaluator_v1 import logical_rate, per_round, _kernel2, _rref2, _in_rowspace2

def gm_channel(nbar, k_ratio, nonadiabatic=True):
    na = 1.0 / (2 * math.pi * nbar) if nonadiabatic else 0.0
    return dict(idle=nbar * k_ratio,
                ctrl=nbar * k_ratio + na,
                tgt=nbar * k_ratio / 2, zz=nbar * k_ratio / 2,
                prep=nbar * k_ratio)

def edge_color(H):
    """Greedy proper edge coloring of the Tanner graph. Returns dict color ->
    list of (row, col) edges; no row or col repeats within a color."""
    H = np.atleast_2d(np.asarray(H, dtype=np.uint8))
    colors = []          # list of (rows_used, cols_used, edges)
    for i in range(H.shape[0]):
        for q in np.flatnonzero(H[i]):
            q = int(q)
            placed = False
            for rows, cols, edges in colors:
                if i not in rows and q not in cols:
                    rows.add(i); cols.add(q); edges.append((i, q)); placed = True
                    break
            if not placed:
                colors.append(({i}, {q}, [(i, q)]))
    return [edges for _, _, edges in colors]

def logical_basis(Hx, Hz, basis="X"):
    """All k logical representatives: kernel(A) reps independent mod rowspace(B)."""
    Hx = np.atleast_2d(np.asarray(Hx, dtype=np.uint8))
    Hz = np.atleast_2d(np.asarray(Hz, dtype=np.uint8))
    A, B = (Hz, Hx) if basis == "X" else (Hx, Hz)
    n = A.shape[1] if A.size else B.shape[1]
    B2 = B if (B.size and B.shape[0]) else np.zeros((0, n), dtype=np.uint8)
    stack = _rref2(B2) if B2.shape[0] else np.zeros((0, n), dtype=np.uint8)
    rank = stack.shape[0]
    logicals = []
    for v in _kernel2(A):
        cand = np.vstack([stack, v]) if stack.shape[0] else v[None, :]
        r = _rref2(cand).shape[0]
        if r > rank:
            logicals.append(v.copy()); stack = _rref2(cand); rank = r
    return logicals

def gm_css_circuit(Hx, Hz, rounds, p_m, nbar, k_ratio, mode="full", basis="X",
                   nonadiabatic=True):
    ch = gm_channel(nbar, k_ratio, nonadiabatic)
    Hx = np.atleast_2d(np.asarray(Hx, dtype=np.uint8))
    Hz = np.atleast_2d(np.asarray(Hz, dtype=np.uint8))
    n = Hx.shape[1] if Hx.size else Hz.shape[1]
    nx = Hx.shape[0] if Hx.size else 0
    nz = Hz.shape[0] if (Hz.size and mode == "full") else 0
    ax = list(range(n, n + nx)); az = list(range(n + nx, n + nx + nz))
    all_q = list(range(n + nx + nz))
    colX = edge_color(Hx) if nx else []
    colZ = edge_color(Hz) if nz else []
    c = stim.Circuit()
    c.append("RX" if basis == "X" else "R", list(range(n)))
    mcount = 0; meas = {}

    def slot(active_pairs, gates):
        """One slot: gates (list of (ctrl,tgt)), then GM channel + idle on rest."""
        busy = set()
        for ct, tg in gates:
            c.append("CX", [ct, tg])
            c.append("Z_ERROR", [ct], ch["ctrl"])
            c.append("Z_ERROR", [tg], ch["tgt"])
            c.append("E", [stim.target_z(ct), stim.target_z(tg)], ch["zz"])
            busy.add(ct); busy.add(tg)
        idle = [q for q in all_q if q not in busy]
        if idle:
            c.append("Z_ERROR", idle, ch["idle"])

    for r in range(rounds):
        # prep slot
        if nx: c.append("RX", ax); c.append("Z_ERROR", ax, ch["prep"])
        if nz: c.append("R", az); c.append("X_ERROR", az, ch["prep"])
        c.append("Z_ERROR", list(range(n)), ch["idle"])
        # X block: ancilla ax[i] is CONTROL, data q target
        for edges in colX:
            slot(None, [(ax[i], int(q)) for i, q in edges])
        # Z block: data q is CONTROL, ancilla az[j] target
        for edges in colZ:
            slot(None, [(int(q), az[j]) for j, q in edges])
        # measurement slot
        for i in range(nx):
            if p_m > 0: c.append("Z_ERROR", [ax[i]], p_m)
            c.append("MX", [ax[i]]); meas[(r, 'x', i)] = mcount; mcount += 1
        for j in range(nz):
            if p_m > 0: c.append("X_ERROR", [az[j]], p_m)
            c.append("M", [az[j]]); meas[(r, 'z', j)] = mcount; mcount += 1
        c.append("Z_ERROR", list(range(n)), ch["idle"])
        for kind, cnt in (('x', nx), ('z', nz)):
            det_first = (kind == 'x') == (basis == "X")
            for i in range(cnt):
                cur = meas[(r, kind, i)]
                if r == 0:
                    if det_first:
                        c.append("DETECTOR", [stim.target_rec(cur - mcount)])
                else:
                    c.append("DETECTOR", [stim.target_rec(cur - mcount),
                                          stim.target_rec(meas[(r - 1, kind, i)] - mcount)])
    c.append("MX" if basis == "X" else "M", list(range(n)))
    dpos = {q: mcount + j for j, q in enumerate(range(n))}
    mcount += n
    Hf, kind = (Hx, 'x') if basis == "X" else (Hz, 'z')
    for i in range(Hf.shape[0] if Hf.size else 0):
        if kind == 'z' and mode != "full": break
        targs = [stim.target_rec(dpos[int(q)] - mcount) for q in np.flatnonzero(Hf[i])]
        targs.append(stim.target_rec(meas[(rounds - 1, kind, i)] - mcount))
        c.append("DETECTOR", targs)
    for li, L in enumerate(logical_basis(Hx, Hz, basis)):
        c.append("OBSERVABLE_INCLUDE",
                 [stim.target_rec(dpos[int(q)] - mcount) for q in np.flatnonzero(L)], li)
    return c, len(colX), len(colZ)

def fom(Hx, Hz, k, rounds, p_m, nbar, k_ratio, mode, shots, seed, decoder="bposd",
        nonadiabatic=True):
    circ, cx_slots, cz_slots = gm_css_circuit(Hx, Hz, rounds, p_m, nbar, k_ratio, mode,
                                              nonadiabatic=nonadiabatic)
    p_any = logical_rate(circ, shots, seed=seed, decoder=decoder)
    pk_R = 1 - (1 - p_any) ** (1.0 / k)
    return per_round(pk_R, rounds), p_any, cx_slots, cz_slots
