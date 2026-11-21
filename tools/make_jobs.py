#!/usr/bin/env python3
"""Write the v8 job lists into jobs/. Run from the repository root:  python tools/make_jobs.py

Naming: v8_<case>_<rate>_<what>_h<step>, with case PI (first-plant costs for technologies without commercial plants) or
OB (target costs), rate r5 or r7 (real cost of capital for every technology).
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Y4 = [2016, 2017, 2018, 2019]
AV = 0.90 / 0.92                       # nuclear availability: mean 0.90 (Czech model) on the monthly shape of the model (mean 0.92)
NUC = dict(capex=10300, y=9, av_scale=AV)   # central nuclear case (life, O&M and variable cost come from model/techs_v8.json)
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

def ob_without_smr(step=3, Ns=(4, 8, 12, 16, 20, 24, 28, 32, 36), rates=(0.05, 0.07)):
    """OB value curve with small modular reactors switched off. In the OB case SMRs at target cost (11,700 EUR/kW, 5-year build) cost almost
    the same per kW-year as large reactors (934 against 911 at 5%; 1,231 against 1,239 at 7%), so in the fixed-N runs of batch 1 the model fills
    the gap with SMRs and the curve is flat at the SMR cost. These runs give the value of nuclear capacity as a whole. N = 0 is the same as batch 1."""
    out = []
    for r in rates:
        for N in Ns:
            sp = base('OB', step, r); sp['off'] = sp['off'] + ['SMR']; sp['N_fix'] = float(N)
            out.append(job(f"v8_OB_{rt(r)}_nosmr_N{N:02d}_h{step}", sp, r))
        sp = base('OB', step, r); sp['off'] = sp['off'] + ['SMR']
        out.append(job(f"v8_OB_{rt(r)}_nosmr_opt_h{step}", sp, r))
    return out

def review_checks(step=3):
    """Two checks asked by the independent review of 14 November, free nuclear, 5%.
    credit38: the central trade rule with ONE change, foreign plants count for 38% in the critical weeks (credit and availability), to separate
    that effect from the other four changes bundled in the v7 trade rule.
    grid350: base grid charge scaled by 350/245 (about 340 EUR/kW on every new PV and onshore wind kW instead of about 238) and second charge (13.77 EUR/kW-yr, unchanged) above 108 GW of wind+PV instead of 137 GW (model/techs_v8_grid350.json)."""
    out = []
    for cs in ('PI', 'OB'):
        sp = base(cs, step); sp['cases'] = {'IMPORT': 'credit38'}; out.append(job(f"v8_{cs}_r5_credit38_opt_h{step}", sp))
    for cs in ('PI', 'OB'):
        sp = base(cs, step); sp['techs'] = 'techs_v8_grid350.json'; out.append(job(f"v8_{cs}_r5_grid350_opt_h{step}", sp))
    return out

def comparison_runs(step=3):
    """Runs for the comparison with other studies, free nuclear, 5%.
    nz: net-zero mode, gas with and without capture and direct air capture allowed (as in net-zero energy-system models), with and without nuclear.
    island: no imports and no exports at all, with and without nuclear.
    barakah_opt: nuclear at 5,500 EUR/kW and 8 years as a free optimum (the value curve stops at 36 GW).
    csp3300 (OB): concentrated solar at a yield of 3,300 h, with and without nuclear."""
    out = []
    for cs in ('PI', 'OB'):
        for nuc in (True, False):
            tail = 'opt' if nuc else 'N00'
            sp = base(cs, step, nuc=nuc); sp['mode'] = 'NZ'; out.append(job(f"v8_{cs}_r5_nz_{tail}_h{step}", sp))
            sp = base(cs, step, nuc=nuc); sp.pop('export', None); sp['off'] = sp['off'] + ['IMPORT']; out.append(job(f"v8_{cs}_r5_island_{tail}_h{step}", sp))
        sp = base(cs, step); sp['nuc'] = dict(NUC, capex=5500, y=8, r=0.05); out.append(job(f"v8_{cs}_r5_barakah_opt_h{step}", sp))
    for nuc in (True, False):
        sp = base('OB', step, nuc=nuc); sp['cases'] = {'CSP': 'y3300'}; out.append(job(f"v8_OB_r5_csp3300_{'opt' if nuc else 'N00'}_h{step}", sp))
    return out

def sensitivity_runs(step=3):
    """Sensitivities named in the documents (each changes one assumption of the central case), 5% unless stated, free nuclear and without nuclear."""
    out = []
    def both(name, cs, ch, nuc_only=False, r=0.05):
        for nuc in ((True,) if nuc_only else (True, False)):
            sp = base(cs, step, r, nuc=nuc)
            for k, v in ch.items():
                if k == 'cases': sp['cases'] = dict(sp.get('cases', {}), **v)
                elif k == 'nuc': sp['nuc'] = dict(sp['nuc'], **v)
                elif k == 'off+': sp['off'] = sp['off'] + v
                elif v is None: sp.pop(k, None)
                else: sp[k] = v
            out.append(job(f"v8_{cs}_{rt(r)}_{name}_{'opt' if nuc else 'N00'}_h{step}", sp, r))
    for cs in ('PI', 'OB'):
        both('x05', cs, dict(export=dict(EXP, X=0.05)))                       # net imports up to 5% of demand
        both('ximp', cs, dict(export=dict(EXP, X=None)))                      # net imports without limit (critical-week rule kept)
        both('d385', cs, dict(D_total=385e6)); both('d439', cs, dict(D_total=439e6))     # demand 385 and 439 TWh
        for ev in ('flat', 'night', 'day'): both(f'ev{ev}', cs, dict(ev_mode=ev))        # electric-vehicle charging profile
        both('hpflat', cs, dict(hp_mode='flat'))                              # heat pumps without the heating-degree-day shape
        both('vre075', cs, dict(vre_cap_scale=0.75)); both('vre150', cs, dict(vre_cap_scale=1.5))   # new PV and wind supply 75% and 150%
        both('hdry', cs, dict(hyd='dry')); both('hwet', cs, dict(hyd='wet'))  # dry (2023) and wet (2024) hydro years
        both('av84', cs, dict(nuc=dict(av_scale=0.84 / 0.92)), nuc_only=True)  # mean nuclear availability 84%
        both('avflat', cs, dict(nuc=dict(av_flat=True)), nuc_only=True)        # same availability in every month
        both('minl0', cs, dict(nuc=dict(minload=0.0)), nuc_only=True)          # no minimum load for nuclear
        both('ncredlow', cs, dict(nuc=dict(credit=0.851)), nuc_only=True)   # nuclear adequacy credit at the lowest monthly availability
        both('res100', cs, dict(reserve=1.0)); both('hcred10', cs, dict(cases={'HYDRO': 'credit10'}))   # reserve margin 0; hydro counted as 10 GW
        for nm, ch in (('noh2', {'off+': ['H2']}), ('nobio', {'off+': ['BIO_GAS', 'BIO_SOL']}), ('nogeo', {'off+': ['GEO_G1', 'GEO_G2', 'GEO_EGS']}),
                       ('nonewlines', {'cases': {'IMPORT': 'nonew'}})):
            sp = base(cs, step, nuc=False)
            for k, v in ch.items():
                if k == 'off+': sp['off'] = sp['off'] + v
                else: sp['cases'] = dict(sp.get('cases', {}), **v)
            out.append(job(f"v8_{cs}_r5_{nm}_N00_h{step}", sp))
        for r in (0.05, 0.07):                                                # Mastrantuono et al.: 4,000 USD2022/kW = 3,575 EUR/kW, 10 years
            sp = base(cs, step, r); sp['nuc'] = dict(NUC, capex=3575, y=10, r=r); out.append(job(f"v8_{cs}_{rt(r)}_mastr_opt_h{step}", sp, r))
        both('island', cs, dict(export=None, **{'off+': ['IMPORT']}), r=0.07)   # no trade at 7%
    for c in ('c3', 'c20'): both(f'csp{c}', 'OB', dict(cases={'CSP': c}))   # CSP ceilings 3 and 20 GW
    return out

def write(name, jobs):
    p = os.path.join(ROOT, 'jobs', name); json.dump(jobs, open(p, 'w'), indent=1); print(name, len(jobs), 'jobs')

if __name__ == '__main__':
    write('smoke_h12.json', free_optimum(step=12, rates=(0.05,)) + [job('v8_PI_r5_N00_h12', base('PI', 12, nuc=False)), job('v8_PI_r5_N12_h12', dict(base('PI', 12), N_fix=12.0))])
    write('batch1_value_curve_h3.json', value_curve(3))
    write('batch2_optimum_h3.json', free_optimum(3))
    write('batch3_variants_h3.json', variants(3))
    write('batch4_value_curve_h6.json', value_curve(6, rates=(0.05,)) + free_optimum(6, rates=(0.05,)))
    write('batch5_ob_without_smr_h3.json', ob_without_smr(3))
    write('batch6_review_checks_h3.json', review_checks(3))
    write('smoke6_h12.json', review_checks(12))
    write('batch8_comparison_h3.json', comparison_runs(3))
    write('batch9_sensitivity_h3.json', sensitivity_runs(3))
    write('smoke9_h12.json', comparison_runs(12) + sensitivity_runs(12))
