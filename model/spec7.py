import numpy as np
from hl5 import crf, idc, AV, BATT_REAL, real_cost, R_GLOBAL
import hl7, blocks_v6
DAYS = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], dtype=float)
def json_copy(o):
    import json; return json.loads(json.dumps(o))
def _apply(u, case_names, novel_default):
    u = json_copy(u); cs = u.get('cases', {})
    names = case_names if isinstance(case_names, list) else ([case_names] if case_names else [])
    if u.get('novel') and not any(n in ('first', 'target') for n in names): names = [novel_default] + names   # default first, then the named variants on top (v7 skipped the default when a variant was named)
    for n in names:
        if n in cs:
            for k, v in cs[n].items(): u[k] = v
    miss = [k for k in ('capex_kW', 'capture', 'eur_t', 'eur_kWh', 'dur') if k in u and u[k] is None and u.get('name') != 'BATT']
    if miss: raise ValueError('MISSING DATA: %s %s' % (u.get('name'), miss))
    return u
def _ann(capex_kW, life, r, build_y=None, om_kW=0.0):
    """Annual cost in EUR/MW-yr: overnight capex x interest during construction (if build_y) x CRF + fixed O&M. Same rule for every technology."""
    k = capex_kW * 1000 * crf(r, life)
    if build_y: k *= idc(r, build_y)
    return k + om_kW * 1000
def critical_mask(D, T, n_frac=0.05, rank='vre', ref_pv_GW=100.0, ref_on_GW=40.0):
    """Boolean mask of the critical weeks of each year (default 5% of weeks = 3 per year).
    rank='vre': lowest mean of normalised PV and onshore profiles (v7). rank='residual': highest mean residual load (load minus PV and wind of a reference mix)."""
    spd = 24 // D['step']; wk = 7 * spd; Y_ = D['Y']; Ty = T // Y_; nw = Ty // wk; mask = np.zeros(T, bool)
    if rank == 'residual':
        idx = -(np.asarray(D['load']) - ref_pv_GW * 1000 * np.asarray(D['s']) - ref_on_GW * 1000 * np.asarray(D['w']))
    else:
        idx = 0.5 * (np.asarray(D['s']) / np.mean(D['s']) + np.asarray(D['w']) / np.mean(D['w']))
    for y_ in range(Y_):
        wm = idx[y_ * Ty:y_ * Ty + nw * wk].reshape(nw, wk).mean(1)
        for w_ in np.argsort(wm)[:max(1, int(round(n_frac * nw)))]: mask[y_ * Ty + w_ * wk:y_ * Ty + (w_ + 1) * wk] = True
    return mask
def build(D, blocks, J, mode='ZD', nuc=None, cases=None, default_novel='first', off=(), variants=(), allow=('s', 'w', 'b', 'n'), reserve=1.1,
          band=0.0, N_fix=None, tl=None, extra=None, grid_thr=137.0):
    r0 = R_GLOBAL; cases = cases or {}; nuc = nuc or {}
    rn = nuc.get('r', r0)
    G = J.get('global', {})
    # v8: the grid charge is a 40-year annuity, so it follows the discount rate like every other capital cost (v7 left it at the 5% value)
    gs = (crf(R_GLOBAL, 40) / crf(0.05, 40)) if G.get('scale_grid_with_rate') else 1.0
    vre = hl7.vre_blocks(blocks, allow, grid_pv=G.get('grid_pv', 13.0), grid_on=G.get('grid_on', 8.0), grid_scale=gs)
    grid_x = 0.5 * (13.0 * 1066.0 + 8.0 * 1709.0) / 1000.0 * (crf(R_GLOBAL, 40) / crf(0.05, 40))
    T = len(D['load']); mon = D['m12']
    AVn = np.minimum(1.0, np.array(AV, dtype=float) * float(nuc.get('av_scale', 1.0)))   # nuclear availability by month (v8: av_scale sets the mean)
    av = AVn[mon]; avm = float(av.mean())
    hm = np.asarray(D['hb'][:12], dtype=float)
    disp = []; info = {}
    for u0 in J['disp']:
        nm = u0['name']
        if not u0.get('on', True) or nm in off: continue
        if u0.get('mode') and mode not in u0['mode']: continue
        if u0.get('variant_only') and nm not in variants: continue
        if nm in ('NUC', 'SMR') and 'n' not in allow: continue
        u = _apply(u0, cases.get(nm), default_novel)
        if nm == 'NUC' and 'capex' in nuc: u['capex_kW'] = nuc['capex']
        if nm == 'NUC':
            for k_ in ('life', 'om_fix_MWh', 'var', 'minload', 'om_cf'):
                if k_ in nuc: u[k_] = nuc[k_]
        d = dict(name=nm, grp=u.get('grp'))
        if u.get('builtin') == 'hydro':
            d.update(blocks=[dict(cap_lo=u['cap_GW'], cap_hi=u['cap_GW'])], var=0.0, avail=1.0, energy=dict(kind='monthly_eq', value=list(hm)), floor=u['floor'], credit=u['credit'], excl=True)
        elif 'om_fix_MWh' in u:
            ru = rn; y = nuc.get('y', u['build_y']) if nm == 'NUC' else u['build_y']
            fix = u['capex_kW'] * 1000 * idc(ru, y) * crf(ru, u['life']) + u['om_fix_MWh'] * u['om_cf'] * 8760 + u['grid_MWh'] * avm * 8760 * (crf(R_GLOBAL, 40) / crf(0.05, 40))
            d.update(blocks=[dict(cap_lo=0.0, cap_hi=None, capex_yr=fix)], var=u['var'], avail=AVn.tolist(), minload=u['minload'], credit=u['credit'])
            info[nm + '_capex_yr_kW'] = round(fix / 1000, 1)
        elif nm == 'IMPORT':
            sc = u.get('capex_scale', 1.0)
            bl = [dict(cap_lo=0.0, cap_hi=b['cap_hi'], capex_yr=_ann(b['capex_kW'], u['life'], r0, u.get('build_y'), b['capex_kW'] * u.get('om_frac', 0.0)) * sc) for b in u['blocks']]
            sc_av = u.get('scarcity_avail', 1.0); avl = np.ones(T); avl_mask = np.zeros(T, bool)
            if sc_av < 1.0 or u.get('scarcity_price_mult', 1.0) != 1.0:
                avl_mask = critical_mask(D, T, 0.05, u.get('scarcity_rank', 'vre')); avl[avl_mask] = sc_av
            pv_ = np.full(T, float(u.get('price', u['var']))); pm_ = u.get('scarcity_price_mult', 1.0)
            if pm_ != 1.0: pv_[avl_mask] = pv_[avl_mask] * pm_
            d.update(blocks=bl, var=pv_, avail=avl.tolist(), credit=u['credit'])
            if u.get('energy_cap_TWh'): d['energy'] = dict(kind='annual', value=u['energy_cap_TWh'] * 1e6)
        elif nm == 'INTERR':
            sc = u.get('scale', 1.0)
            d.update(blocks=[dict(cap_lo=0.0, cap_hi=b['cap_hi'], capex_yr=b['capex_yr_kW'] * 1000 * sc) for b in u['blocks']], var=u['var'], avail=1.0, credit=u['credit'],
                     energy=dict(kind='hours', value=float(u['hours_yr'])))
        elif u.get('flat'):
            bl = []
            for b in u['blocks']:
                if 'lcoe' in u: cy = u['lcoe'] * u['avail'] * 8760
                elif b.get('capex_kW') is not None: cy = _ann(b['capex_kW'], b['life'], r0, u.get('build_y'), b.get('om_fix_kW', 0))
                else: cy = b.get('om_fix_kW', 0) * 1000
                if 'lcoe' not in u and (u.get('capex_kW') is not None or u.get('om_fix_kW') is not None):
                    ck = u.get('capex_kW', b.get('capex_kW')); om = u.get('om_fix_kW', b.get('om_fix_kW', 0))
                    cy = (_ann(ck, b['life'], r0, u.get('build_y')) if ck is not None else 0.0) + om * 1000
                bl.append(dict(cap_lo=b.get('cap_lo', 0.0), cap_hi=b['cap_hi'], capex_yr=cy))
            if nm == 'GEO_EX': a = u['TWh'] * 1e6 / (u['blocks'][0]['cap_hi'] * 1000 * 8760)
            elif 'hours' in u and u.get('monthly_shape') == 'hydro': a = np.minimum(hm / hm.mean() * u['hours'] / 8760, 1.0).tolist()
            elif 'hours' in u: a = u['hours'] / 8760
            else: a = u['avail']
            d.update(blocks=bl, flat=True, avail=a, credit=u['credit'])
        elif 'TWh_el' in u:
            e = u['TWh_el'] * 1e6
            om = u['om_frac'] * u['capex_kW'] * 1000
            bl = [dict(cap_lo=u['cap_exist_GW'], cap_hi=u['cap_exist_GW'], capex_yr=om)]
            if not u.get('no_new'): bl.append(dict(cap_lo=0.0, cap_hi=u['cap_exist_GW'], capex_yr=_ann(u['capex_kW'], u['life'], r0, u.get('build_y')) + om))
            tol = u.get('monthly_flat_tol', 0.07); mv = (e * (1 + tol) * DAYS / 365.0).tolist()
            en = [dict(kind='annual', value=e, min=(e if u.get('must') else None)), dict(kind='monthly_le', value=mv)]
            d.update(blocks=bl, var=u['fuel_th'] / u['eff'], avail=1.0, credit=u['credit'], energy=en)
        elif nm == 'CSP':
            bl = []
            for b in u['blocks']:
                if b.get('exist'): bl.append(dict(cap_lo=b['cap_hi'], cap_hi=b['cap_hi'], capex_yr=u.get('om_fix_kW', b['om_fix_kW']) * 1000))
                else: bl.append(dict(cap_lo=0.0, cap_hi=u.get('cap_new_GW', b['cap_hi']), capex_yr=_ann(u.get('capex_kW', b['capex_kW']), b['life'], r0, u.get('build_y'), u.get('om_fix_kW', b['om_fix_kW']))))
            cr = u['credit']
            if cr == 'profile':
                spd = 24 // D['step']; Y_ = D['Y']; Ty = T // Y_; s_ = np.asarray(D['s']); ld = np.asarray(D['load']); H = float(u.get('credit_hours', 4.0))
                B = np.zeros(T)
                for y_ in range(Y_):
                    sl = slice(y_ * Ty, (y_ + 1) * Ty); dd = np.add.reduceat(s_[sl], np.arange(0, Ty, spd)); dd = dd / s_[sl].sum() * float(u['daily_MWh_per_MW'])
                    B[sl] = np.repeat(dd, spd)[:Ty]
                top = np.argsort(ld)[-max(4, int(round(0.01 * T))):]
                cr = float(np.mean(np.minimum(1.0, B[top] / H)))
                info['CSP_credit'] = dict(credit=round(cr, 3), top_steps=len(top), H=H, B_MWh_per_MW_mean=round(float(B[top].mean()), 2), B_min=round(float(B[top].min()), 2))
            d.update(blocks=bl, var=0.0, avail=1.0, credit=cr, energy=dict(kind='daily_yield', prof='pv', value=float(u['daily_MWh_per_MW'])))
        elif nm in ('GAS_CCS', 'GAS_NOCCS'):
            cap = u['capture']; eff = u['eff']; co2 = u['co2_per_MWh_th'] / eff
            fix = u['capex_kW'] * 1000 * idc(r0, u['build_y']) * crf(r0, u['life']) + u['om_fix_kW'] * 1000
            captured = cap * co2; gas = cases.get('_gas_price', u['gas_eur_MWh'])
            var = u['om_var'] + gas / eff + u.get('ts_eur_t', 0.0) * captured
            d.update(blocks=[dict(cap_lo=0.0, cap_hi=None, capex_yr=fix)], var=var, avail=1.0, credit=u['credit'], ef=(1 - cap) * co2 + u['upstream_t_MWh'])
            if u.get('seq_Mt_yr') and cap > 0: d['seq'] = dict(t_per_MWh=captured, Mt_yr=u['seq_Mt_yr'])
            info[nm] = dict(var_EUR_MWh=round(var, 1), ef_t_MWh=round(d['ef'], 4), captured_t_MWh=round(captured, 4), fix_kEUR_MW_yr=round(fix / 1000, 1))
        else:
            raise ValueError('unknown disp unit ' + nm)
        disp.append(d)
    stor = []
    for s0 in J['stor']:
        nm = s0['name']
        if not s0.get('on', True) or nm in off: continue
        s = _apply(s0, cases.get(nm), default_novel); d = dict(name=nm, grp=s.get('grp'))
        if nm == 'BATT':
            prem = s.get('macse_prem'); ec = real_cost(prem, 0.1, contract=15, life=15) if prem else BATT_REAL
            if s.get('eur_kWh') is not None:    # v8: bottom-up, same rule as every other technology (EUR/kWh of energy capacity, power included)
                ec = _ann(s['eur_kWh'], s['life'], r0, s.get('build_y'), s.get('om_kWh', 0.0))
            d.update(dur=s['dur'], E_cost=ec, E_hi=(None if 'b' in allow else 0.0), eta_c=s['eff'], eta_d=1.0, credit_e=1.0 / max(s['dur'], s.get('credit_dur', s['dur'])))
        elif nm == 'PUMPED':
            d.update(Pc_lo=s['GW'], Pc_hi=s['GW'], Pd_lo=s['GW'], Pd_hi=s['GW'], E_lo=s['GWh'], E_hi=s['GWh'], eta_c=s['eff'], eta_d=1.0, credit_p=s['credit_p'])
        elif nm in ('PUMPED_NEW', 'CAES'):
            d.update(dur=s['dur'], E_cost=_ann(s['eur_kWh'], s['life'], r0, s.get('build_y'), s['eur_kWh'] * s.get('om_frac', 0.0)), E_hi=s.get('GWh_hi'), eta_c=s['eff'], eta_d=1.0, credit_e=1.0 / s['dur'])
        elif s.get('h2'):
            d.update(Pc_cost=s['el_capex'] * 1000 * (crf(R_GLOBAL, s.get('el_life', 20)) * (idc(R_GLOBAL, s['el_build_y']) if s.get('el_build_y') else 1.0) + s.get('el_om_frac', 0.03)),
                     Pd_cost=_ann(s['t_capex'], s['t_life'], R_GLOBAL, s.get('t_build_y'), s['t_fom']), E_cost=s['sto'] * ((1 - s.get('sto_cap_share', 0.0)) + s.get('sto_cap_share', 0.0) * crf(R_GLOBAL, 30) / crf(0.05, 30)),
                     eta_c=s['eta_el'], eta_d=s['eta_t'], var_dis=s['t_vom'], credit_p=0.95)
        elif nm == 'LDES':
            fL = 1.0 if abs(R_GLOBAL - 0.05) < 1e-9 else ((1 - s.get('opex_share', 0.2)) * crf(R_GLOBAL, s.get('life', 20)) / crf(0.05, s.get('life', 20)) + s.get('opex_share', 0.2))
            ecL = s['E_cost'] * fL
            if s.get('eur_kWh') is not None: ecL = _ann(s['eur_kWh'], s.get('life', 20), r0, s.get('build_y'), s.get('om_kWh', 0.0))
            d.update(dur=s['dur'], E_cost=ecL, eta_c=s['eta'], eta_d=1.0, credit_e=s.get('credit_frac', 1.0) / s['dur'])
        else:
            raise ValueError('unknown stor unit ' + nm)
        stor.append(d)
    dsm = []
    for v0 in J['dsm']:
        if not v0.get('on', True) or v0['name'] in off: continue
        v = _apply(v0, cases.get(v0['name']), default_novel)
        dsm.append(dict(name=v['name'], grp=v.get('grp'), kind=v['kind'], base=v['base'], share=v['share'], window=max(1, v['window'] * 3 // D['step']), window_off=v['window_off'] * 3 // D['step'], var=v['var']))
    dac = None
    if mode == 'NZ' and J['dac'].get('on', True) and 'DAC' not in off:
        c = _apply(J['dac'], cases.get('DAC'), default_novel)
        el = c['elec_MWh_per_t'] + (c['heat_MWh_per_t'] if c.get('heat_as_elec') else 0.0)
        dac = dict(capex_yr=c['eur_t'] * 8760.0, var=0.0, elec_MWh_per_t=el)
    out = dict(vre=vre, disp=disp, stor=stor, dsm=dsm, dac=dac, reserve=reserve, grid_thr=grid_thr, grid_x=grid_x, emis_cap=0.0, band=band,
               band_units=('NUC',), N_fix=N_fix, tl=tl)
    return out, info
