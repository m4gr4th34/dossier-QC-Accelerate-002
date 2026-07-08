#!/usr/bin/env python3
"""refit_bitflip.py -- amplitude-free bit-flip refit of the Ocelot repetition-code data.

REQUIRES THE OCELOT DATASET, WHICH IS NOT IN THIS REPO AND NOT IN CI.
  Data: H. Putterman et al., Nature 638, 927 (2025), dataset DOI
  10.5281/zenodo.14257632 -> data_upload.zip. Download and extract locally:
    mkdir -p ~/ocelot-data && cd ~/ocelot-data
    curl -L -o data_upload.zip "https://zenodo.org/records/14257632/files/data_upload.zip?download=1"
    unzip -o data_upload.zip -d extracted
  This script reads ~/ocelot-data/extracted/data_upload/{first_d3,second_d3,d5}_bit_flip.
  The dataset is deliberately kept OUT of the repo (145 MB) and off CI; the numbers
  this script prints are cited in NOTEBOOK.md Day-2 and the DERIV v1.1 addendum, and
  are reproduced by re-running against a local extraction.

FIT CONVENTION (the paper's own, ledger E3): the storage correlator is fit with a
FREE amplitude,
    corr(C) = A * exp(-C / tau),    corr(C) = 1 - 2 * P_flip(C),
so a C=0 SPAM/readout offset lands in A rather than biasing tau low. Then
    T_Z = tau * T_cycle  (T_cycle = 2.8 us),   eps_bit = 1 / (2 * tau).
P_flip is symmetrized over the two logical eigenstate preparations (+Z: |alpha>^n,
-Z: |-alpha>^n): P_flip = 0.5*(P(logical=1|+Z) + P(logical=0|-Z)).

SCHEMA ADAPTATIONS (discovered from the released parquet, not assumed):
  - Initial-state INDEX LEVEL is discovered by name-match ('initial'), because the
    two d3 sections index their storages differently: first_d3 uses S1/S2/S3 while
    second_d3 uses S3/S4/S5 (it is physically the other half of the d5 chip). d5
    uses S1..S5. Hardcoding 'S1_initial_state' fails on second_d3.
  - (Sibling note, for the phase first-look decoder not shipped here: the same
    sections also relabel ancillas -- first_d3 A1/A2 vs second_d3 A3/A4 -- so
    ancilla columns must likewise be discovered, not hardcoded.)
  - Per-cat bit-flip times are NOT extractable from this dataset: readout
    symmetrizations leave individual storage marginals at 0.50, so only the n-cat
    logical XOR observable is well-defined (see NOTEBOOK Day-2, closure C2).

Run on the off-repo analysis environment (canonical stack + pandas/pyarrow/scipy):
    python refit_bitflip.py
"""
import pandas as pd, numpy as np, os
from scipy.optimize import curve_fit
base=os.path.expanduser("~/ocelot-data/extracted/data_upload")
T_CYCLE=2.8e-6

def flip_curve(section):
    """symmetrized logical-flip prob vs num_cycles, per nbar. returns dict nbar->(t,p)."""
    df=pd.read_parquet(os.path.join(base,section))
    init_lvl=[n for n in df.index.names if 'initial' in n][0]   # schema adaptation
    out={}
    for nb in sorted(df.index.get_level_values('nbar').unique()):
        sub=df.xs(nb, level='nbar')
        recs=[]
        for cyc,g in sub.groupby(level='num_cycles'):
            ist=g.index.get_level_values(init_lvl); log=g['logical_state'].values
            p_plus=log[ist=='+Z'].mean(); p_minus=1.0-log[ist=='-Z'].mean()
            recs.append((cyc,0.5*(p_plus+p_minus)))
        recs.sort()
        out[nb]=(np.array([r[0] for r in recs],float),np.array([r[1] for r in recs],float))
    return out

def refit(section):
    """corr(C)=A*exp(-C/tau); A free. returns nbar->(A,tau,T_Z,eps_bit)."""
    fc=flip_curve(section); res={}
    for nb,(t,p) in fc.items():
        corr=1.0-2.0*p
        model=lambda C,A,tau:A*np.exp(-C/tau)
        popt,_=curve_fit(model,t,corr,p0=[0.9,max(t)/3],maxfev=40000,
                         bounds=([0.1,1.0],[1.0,1e7]))
        A,tau=popt
        res[nb]=(A,tau,tau*T_CYCLE,1.0/(2.0*tau))
    return res

sections=["first_d3_bit_flip","second_d3_bit_flip","d5_bit_flip"]
NDATA={"first_d3_bit_flip":3,"second_d3_bit_flip":3,"d5_bit_flip":5}
REF={}
print("=== R-F: amplitude-free refit  corr(C)=A*exp(-C/tau) ===")
print(f"{'section':20s} {'nbar':>4s} {'A':>6s} {'tau_cyc':>9s} {'T_Z(us)':>8s} {'eps_bit':>9s}")
for sec in sections:
    REF[sec]=refit(sec)
    for nb,(A,tau,TZ,eb) in REF[sec].items():
        print(f"{sec:20s} {nb:4.1f} {A:6.3f} {tau:9.1f} {TZ*1e6:8.1f} {eb:9.4f}")
    print()

# C1: eps_bit(d5,nbar=1) ~ 4%; d3 sections ~ 2%
print("=== C1 closure: eps_bit vs paper Fig-5 statements ===")
eb_d5_1=REF['d5_bit_flip'][1.0][3]
eb_d3a_1=REF['first_d3_bit_flip'][1.0][3]
eb_d3b_1=REF['second_d3_bit_flip'][1.0][3]
def rel(x,r): return (x-r)/r
print(f"  eps_bit(d5,nbar=1)={eb_d5_1:.4f} vs paper ~0.04  rel={rel(eb_d5_1,0.04):+.1%}  [{'PASS' if abs(rel(eb_d5_1,0.04))<=0.30 else 'FAIL'}]")
print(f"  eps_bit(first_d3,nbar=1)={eb_d3a_1:.4f} vs paper ~0.02  rel={rel(eb_d3a_1,0.02):+.1%}  [{'PASS' if abs(rel(eb_d3a_1,0.02))<=0.30 else 'FAIL'}]")
print(f"  eps_bit(second_d3,nbar=1)={eb_d3b_1:.4f} vs paper ~0.02  rel={rel(eb_d3b_1,0.02):+.1%}  [{'PASS' if abs(rel(eb_d3b_1,0.02))<=0.30 else 'FAIL'}]")

# C3 (ledger E4): the observable is an n-cat logical XOR, so the amplitude compounds
# as A ~ (1 - 2*p_ro)^n; the readout corridor must be applied to A^(1/n), NOT raw A.
print("\n=== C3 closure: per-cat readout from A^(1/n) vs ~7% erasure scale ===")
for sec in sections:
    n=NDATA[sec]
    Am=np.mean([REF[sec][nb][0] for nb in REF[sec]])
    per_cat=Am**(1.0/n); p_ro=(1.0-per_cat)/2.0
    print(f"  {sec:20s} n={n} meanA={Am:.3f} -> per-cat corr={per_cat:.3f} -> p_ro~{p_ro*100:.1f}%  "
          f"[{'PASS' if 0.03<=p_ro<=0.09 else 'CHECK'}]")

# A3: refit exponential scale k over nbar<=3
print("\n=== A3: exponential scale k on REFIT T_Z (nbar<=3), T_Z=T0*exp(k*nbar) ===")
for sec in sections:
    nbs=np.array([n for n in sorted(REF[sec]) if n<=3.0])
    TZ=np.array([REF[sec][n][2] for n in nbs])
    k,logT0=np.polyfit(nbs,np.log(TZ),1)
    print(f"  {sec:20s} k={k:.3f}/nbar (x{np.exp(k):.2f}/nbar) T0={np.exp(logT0)*1e6:.2f}us")

# save for the downstream p_m fit arithmetic (off-repo)
import json
dump={s:{str(nb):list(map(float,REF[s][nb])) for nb in REF[s]} for s in sections}
json.dump(dump, open(os.path.expanduser("~/ocelot-data/refit.json"),"w"))
print("\n(refit results saved to ~/ocelot-data/refit.json)")
