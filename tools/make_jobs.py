#!/usr/bin/env python3
"""Write the v8 job lists into jobs/. Run from the repository root:  python tools/make_jobs.py

Naming: v8_<case>_<rate>_<what>_h<step>, with case PI (first-plant costs for technologies without commercial plants) or
OB (target costs), rate r5 or r7 (real cost of capital for every technology).
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Y4 = [2016, 2017, 2018, 2019]
AV = 0.90 / 0.92                       # nuclear availability: mean 0.90 (Czech model) on the monthly shape of the model (mean 0.92)
NUC = dict(capex=10200, y=9, av_scale=AV)   # central nuclear case (life, O&M and variable cost come from model/techs_v8.json)
EXP = dict(X=0.0, X_exp=0.0, cap_frac=round(6095 / 11535, 4), price=61.07)   # balanced annual swap (imports = exports), Terna export limit; imports cost 115.94, exports earn 61.07 (France 2025 average)
OFF = {'PI': ['WAVE', 'LDES'], 'OB': ['WAVE']}

def base(cs, step=3, r=0.05, nuc=True, export=EXP, years=Y4, **kw):
    sp = dict(techs='techs_v8.json', mode='ZD', default_novel='first' if cs == 'PI' else 'target', step=step, years=years, off=list(OFF[cs]), export=dict(export))
    if nuc: sp['nuc'] = dict(NUC, r=r)
    else: sp['allow'] = ['s', 'w', 'b']
    sp.update(kw)
    return sp

def job(tag, sp, r=0.05):
    j = dict(tag=tag, spec=sp)
    if abs(r - 0.05) > 1e-9: j['R'] = r
    return j

def rt(r): return 'r5' if abs(r - 0.05) < 1e-9 else 'r7'

def value_curve(step=3, Ns=(0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 48), rates=(0.05, 0.07)):
    """System cost with nuclear capacity FIXED at N GW. From these runs the cost at any nuclear fixed cost f' follows exactly:
    C(N; f') = C(N; f) + (f' - f) x N, so the optimal capacity for every cost case is read from one set of runs."""
    out = []
    for r in rates:
        for cs in ('PI', 'OB'):
            for N in Ns:
                sp = base(cs, step, r, nuc=(N > 0))
                if N > 0: sp['N_fix'] = float(N)
                out.append(job(f"v8_{cs}_{rt(r)}_N{N:02d}_h{step}", sp, r))
    return out

def free_optimum(step=3, rates=(0.05, 0.07)):
    return [job(f"v8_{cs}_{rt(r)}_opt_h{step}", base(cs, step, r), r) for r in rates for cs in ('PI', 'OB')]

def variants(step=3):
    """Each variant changes ONE assumption of the central case; run with free nuclear and without nuclear, PI and OB, 5%."""
    V = {
        'exp0':    dict(export=dict(EXP, price=0.0)),                       # exports earn nothing (v7 rule)
        'exppar':  dict(export=dict(EXP, price=115.94)),                    # exports earn the import price
        'x10':     dict(export=dict(EXP, X=0.10)),                          # net imports allowed up to 10% of demand
        'xfree':   dict(export=dict(EXP, X_exp=None)),                      # net exports allowed (only imports <= exports)
        'v7imp':   dict(export=None, cases={'IMPORT': 'v7credit'}),         # v7 rule: imports with 38% credit, no exports
        'vreweek': dict(cases={'IMPORT': 'vre_weeks'}),                     # critical weeks chosen as in v7
        'macse':   dict(cases={'BATT': 'macse'}),                           # batteries at the MACSE award price (v7)
        'wx8':     dict(years=Y4 + Y4, wyears=Y4 + [1994, 1998, 2014, 2015]),   # eight weather years, four of them the worst of the record
    }
    out = []
    for name, ch in V.items():
        for cs in ('PI', 'OB'):
            for nuc in (True, False):
                sp = base(cs, step, 0.05, nuc=nuc)
                for k, v in ch.items():
                    if k == 'cases': sp['cases'] = dict(sp.get('cases', {}), **v)
                    elif v is None: sp.pop(k, None)
                    else: sp[k] = v
                out.append(job(f"v8_{cs}_r5_{name}_{'opt' if nuc else 'N00'}_h{step}", sp))
    # nuclear cost variants on the free optimum: v7 inputs, 7-year build, top of the official bracket
    for cs in ('PI', 'OB'):
        for name, nd, cases in (('nucv7', dict(capex=8540, y=7, r=0.05), {'NUC': 'v7'}),      # superseded v7 inputs (8,540 EUR/kW gross, 7 y, 80 y, O&M 32, availability 0.92)
                                ('nuc7y', dict(NUC, y=7, r=0.05), None),                       # seven years of construction
                                ('nuctop', dict(NUC, capex=12700, r=0.05), None)):             # top of the official cost bracket
            sp = base(cs, step); sp['nuc'] = nd
            if cases: sp['cases'] = cases
            out.append(job(f"v8_{cs}_r5_{name}_opt_h{step}", sp))
    return out

def write(name, jobs):
    p = os.path.join(ROOT, 'jobs', name); json.dump(jobs, open(p, 'w'), indent=1); print(name, len(jobs), 'jobs')

if __name__ == '__main__':
    write('smoke_h12.json', free_optimum(step=12, rates=(0.05,)) + [job('v8_PI_r5_N00_h12', base('PI', 12, nuc=False)), job('v8_PI_r5_N12_h12', dict(base('PI', 12), N_fix=12.0))])
    write('batch1_value_curve_h3.json', value_curve(3))
    write('batch2_optimum_h3.json', free_optimum(3))
    write('batch3_variants_h3.json', variants(3))
    write('batch4_value_curve_h6.json', value_curve(6, rates=(0.05,)) + free_optimum(6, rates=(0.05,)))
