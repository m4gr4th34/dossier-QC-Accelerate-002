#!/usr/bin/env python3
"""
evaluator_v1.py -- SANDBOX PROTOTYPE of the v1 circuit-level finite-bias evaluator.

Noise model: DERIV-ocelot-noise-v1.md (author-approved structure, decisions D1-D4):
  Gamma_Z = nbar*kappa_1 = 3.333e4 /s   [DERIVED, 3-point consistency-checked]
  Gamma_X_active = 1250 /s              [DERIVED from CX^2-cycle 3.5e-3 / 2.8us]
  Gamma_X_idle   = 1000 /s              [conservative floor from '>1 ms']
  t_cycle = 2.8e-6 s [QUOTED]           t_cx = 500e-9 s nominal [QUOTED range 292-552ns]
  nbar PINNED at 2 (D3). Correlated ZZ omitted (D4, limitation L1).
  Ancilla modes (D1): 'transmon' -- ancilla physics folded into measurement flip p_m
                      (FITTED later against Ocelot d=5; d=3 held out);
                      'cat'      -- ancilla is a cat qubit: time-driven biased Pauli
                      errors during its CX window (hooks propagate via stim), plus
                      the same p_m readout flip (stated assumption A1).
Errors are TIME-DRIVEN: each CX applies Z/X error at the derived rates over t_cx on
its participants; end-of-round residual tops every data qubit up to exactly t_cycle.
So total per-round data dephasing = 1-exp(-Gamma_Z*t_cycle) independent of gate
count (licensed by derivation Step 3: idle-dominated, CX excess bounded ~0.007).

Prototype-grade: sandbox stack py3.12.3/numpy2.5.1/stim1.16.0/ldpc2.4.1/pymatching2.4.0.
Canonical numbers happen on Code's pinned venv at repo-formalization.
"""
import math
import numpy as np
import stim

# ---- anchor parameters (see DERIV doc for provenance) ----
GAMMA_Z = 3.333e4          # /s
GAMMA_X_ACTIVE = 1250.0    # /s
GAMMA_X_IDLE = 1000.0      # /s
T_CYCLE = 2.8e-6           # s
T_CX = 500e-9              # s

def p_of(rate, t):
    return 1.0 - math.exp(-rate * t)

class Noise:
    def __init__(self, mode="cat", p_m=0.0, lam=1.0,
                 gamma_z=GAMMA_Z, gamma_x=GAMMA_X_ACTIVE,
                 t_cycle=T_CYCLE, t_cx=T_CX):
        assert mode in ("cat", "transmon")
        self.mode, self.p_m, self.lam = mode, p_m, lam
        self.gz, self.gx = lam * gamma_z, gamma_x   # lambda scales Z (bias severity knob)
        self.t_cycle, self.t_cx = t_cycle, t_cx
        self.pz_cx = p_of(self.gz, t_cx)
        self.px_cx = p_of(self.gx, t_cx)

    def resid(self, t):
        return p_of(self.gz, t), p_of(self.gx, t)

def css_memory_circuit(Hx, Hz, rounds, noise, basis="X"):
    """Memory experiment for a CSS outer code, all-cat data qubits.
    basis='X': prepare |+..+>, protect against Z (phase-flip memory; observable X_L).
    basis='Z': prepare |0..0>, protect against X (bit-flip memory; observable Z_L).
    Ancillas: one per stabilizer row, reused each round."""
    Hx = np.atleast_2d(np.asarray(Hx, dtype=np.uint8))
    Hz = np.atleast_2d(np.asarray(Hz, dtype=np.uint8))
    n = Hx.shape[1] if Hx.size else Hz.shape[1]
    nx, nz = (Hx.shape[0] if Hx.size else 0), (Hz.shape[0] if Hz.size else 0)
    ax = list(range(n, n + nx))            # X-stab ancillas
    az = list(range(n + nx, n + nx + nz))  # Z-stab ancillas
    data = list(range(n))
    c = stim.Circuit()
    c.append("RX" if basis == "X" else "R", data)

    meas_index = {}   # (round, 'x'/'z', row) -> measurement record position
    mcount = 0

    def step_err(qubits, pz, px):
        if pz > 0: c.append("Z_ERROR", qubits, pz)
        if px > 0: c.append("X_ERROR", qubits, px)

    for r in range(rounds):
        used_time = np.zeros(n)
        # X stabilizers: ancilla |+>, CX(anc -> data), MX
        for i in range(nx):
            c.append("RX", [ax[i]])
        for i in range(nx):
            sup = np.flatnonzero(Hx[i])
            for q in sup:
                c.append("CX", [ax[i], int(q)])
                if noise.mode == "cat":
                    step_err([ax[i], int(q)], noise.pz_cx, noise.px_cx)
                else:
                    step_err([int(q)], noise.pz_cx, noise.px_cx)
                used_time[q] += noise.t_cx
        for i in range(nx):
            if noise.p_m > 0: c.append("Z_ERROR", [ax[i]], noise.p_m)  # flips MX outcome
            c.append("MX", [ax[i]])
            meas_index[(r, 'x', i)] = mcount; mcount += 1
        # Z stabilizers: ancilla |0>, CX(data -> anc), MZ
        for i in range(nz):
            c.append("R", [az[i]])
        for i in range(nz):
            sup = np.flatnonzero(Hz[i])
            for q in sup:
                c.append("CX", [int(q), az[i]])
                if noise.mode == "cat":
                    step_err([az[i], int(q)], noise.pz_cx, noise.px_cx)
                else:
                    step_err([int(q)], noise.pz_cx, noise.px_cx)
                used_time[q] += noise.t_cx
        for i in range(nz):
            if noise.p_m > 0: c.append("X_ERROR", [az[i]], noise.p_m)  # flips MZ outcome
            c.append("M", [az[i]])
            meas_index[(r, 'z', i)] = mcount; mcount += 1
        # residual idle on data: top up to exactly t_cycle
        for q in data:
            t_res = max(noise.t_cycle - used_time[q], 0.0)
            pz, px = noise.resid(t_res)
            step_err([q], pz, px)
        # detectors: same-stabilizer consecutive-round comparisons (first-round
        # detector only for the family that is deterministic in the prepared basis)
        for kind, cnt in (('x', nx), ('z', nz)):
            deterministic_first = (kind == 'x' and basis == "X") or (kind == 'z' and basis == "Z")
            for i in range(cnt):
                cur = meas_index[(r, kind, i)]
                if r == 0:
                    if deterministic_first:
                        c.append("DETECTOR", [stim.target_rec(cur - mcount)])
                else:
                    prev = meas_index[(r - 1, kind, i)]
                    c.append("DETECTOR", [stim.target_rec(cur - mcount),
                                          stim.target_rec(prev - mcount)])
    # final transversal data measurement + reconstructed stabilizers + observable
    c.append("MX" if basis == "X" else "M", data)
    dpos = {q: mcount + j for j, q in enumerate(data)}
    mcount += n
    H_final, kind = (Hx, 'x') if basis == "X" else (Hz, 'z')
    for i in range(H_final.shape[0] if H_final.size else 0):
        sup = np.flatnonzero(H_final[i])
        last = meas_index[(rounds - 1, kind, i)]
        targs = [stim.target_rec(dpos[int(q)] - mcount) for q in sup]
        targs.append(stim.target_rec(last - mcount))
        c.append("DETECTOR", targs)
    # logical observable: X_L (basis X) / Z_L (basis Z) -- first logical rep
    L = logical_op(Hx, Hz, basis)
    c.append("OBSERVABLE_INCLUDE",
             [stim.target_rec(dpos[int(q)] - mcount) for q in np.flatnonzero(L)], 0)
    return c

def _rref2(A):
    A = A.copy() % 2; r = 0
    for col in range(A.shape[1]):
        piv = np.flatnonzero(A[r:, col]) + r
        if len(piv) == 0: continue
        A[[r, piv[0]]] = A[[piv[0], r]]
        for j in np.flatnonzero(A[:, col]):
            if j != r: A[j] ^= A[r]
        r += 1
        if r == A.shape[0]: break
    return A[:r]

def _kernel2(A):
    """Basis of null space of A over GF(2)."""
    A = np.atleast_2d(np.asarray(A, dtype=np.uint8))
    m, n = A.shape
    if m == 0: return np.eye(n, dtype=np.uint8)
    R = _rref2(A)
    pivots = []
    for row in R:
        nz = np.flatnonzero(row)
        if len(nz): pivots.append(nz[0])
    free = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free:
        v = np.zeros(n, dtype=np.uint8); v[f] = 1
        for i, row in enumerate(R):
            nz = np.flatnonzero(row)
            if len(nz) and f in nz[1:]: v[nz[0]] = 1
        basis.append(v)
    return np.array(basis, dtype=np.uint8) if basis else np.zeros((0, n), dtype=np.uint8)

def _in_rowspace2(v, A):
    A = np.atleast_2d(np.asarray(A, dtype=np.uint8))
    if A.size == 0 or A.shape[0] == 0: return not v.any()
    R = _rref2(np.vstack([A, v]))
    return len(_rref2(A)) == len(R)

def logical_op(Hx, Hz, basis):
    """One representative logical: X-type (commutes w/ Hz, not in rowspace(Hx)) for
    basis='X'; Z-type analog for basis='Z'."""
    Hx = np.atleast_2d(np.asarray(Hx, dtype=np.uint8))
    Hz = np.atleast_2d(np.asarray(Hz, dtype=np.uint8))
    A, B = (Hz, Hx) if basis == "X" else (Hx, Hz)
    for v in _kernel2(A):
        if v.any() and not _in_rowspace2(v, B):
            return v
    raise ValueError("no logical operator found (k=0?)")

# ---- DEM -> matrices -> BP-OSD ----
def dem_to_matrices(dem):
    rows_h, rows_o, priors = [], [], []
    ndet, nobs = dem.num_detectors, dem.num_observables
    for inst in dem.flattened():
        if inst.type != "error": continue
        p = inst.args_copy()[0]
        dets, obs = [], []
        for t in inst.targets_copy():
            if t.is_relative_detector_id(): dets.append(t.val)
            elif t.is_logical_observable_id(): obs.append(t.val)
        rows_h.append(dets); rows_o.append(obs); priors.append(p)
    H = np.zeros((ndet, len(priors)), dtype=np.uint8)
    O = np.zeros((nobs, len(priors)), dtype=np.uint8)
    for j, (ds, os_) in enumerate(zip(rows_h, rows_o)):
        for d in ds: H[d, j] ^= 1
        for o in os_: O[o, j] ^= 1
    return H, O, np.array(priors)

def make_bposd(H, priors):
    from ldpc import BpOsdDecoder
    try:
        return BpOsdDecoder(H, error_channel=list(priors), bp_method="ms",
                            max_iter=30, osd_method="osd_e", osd_order=4)
    except TypeError:
        return BpOsdDecoder(H, channel_probs=list(priors), bp_method="ms",
                            max_iter=30, osd_method="osd_e", osd_order=4)

def logical_rate(circuit, shots, seed, decoder="bposd"):
    dem = circuit.detector_error_model(decompose_errors=False, flatten_loops=True)
    H, O, priors = dem_to_matrices(dem)
    sampler = circuit.compile_detector_sampler(seed=seed)
    dets, obs = sampler.sample(shots, separate_observables=True)
    if decoder == "pymatching":
        import pymatching
        m = pymatching.Matching.from_detector_error_model(
            circuit.detector_error_model(decompose_errors=True, flatten_loops=True))
        pred = m.decode_batch(dets)
        fails = int(np.sum(np.any(pred.astype(np.uint8) != obs.astype(np.uint8), axis=1)))
    else:
        dec = make_bposd(H, priors)
        fails = 0
        for s in range(shots):
            e_hat = dec.decode(dets[s].astype(np.uint8))
            pred = (O @ e_hat.astype(np.uint8)) % 2
            fails += int(np.any(pred != obs[s].astype(np.uint8)))
    return fails / shots

def per_round(eps_R, R):
    """Convert R-round failure prob to per-round, accounting for 0.5 saturation."""
    x = max(1.0 - 2.0 * eps_R, 1e-12)
    return 0.5 * (1.0 - x ** (1.0 / R))

def phase_rep(n):
    Hx = np.zeros((n - 1, n), dtype=np.uint8)
    for i in range(n - 1): Hx[i, i] = Hx[i, i + 1] = 1
    return Hx, np.zeros((0, n), dtype=np.uint8)
