import json, os
from hl5 import PV_REAL, PV_OM, PV_KAPPA, crf, idc, R_GLOBAL
HERE = os.path.dirname(os.path.abspath(__file__))
PV_2025, PV_2016, PV_2010, GROUND_2025 = 43.51, 19.283, 3.605, 12.57
GROUND_ZONE = {'Sud-isole': 6.36, 'Centro-Sud': 1.83, 'Nord': 3.40}
ONS = {'E0': (13.6, 31.0, 34.0, 1600), 'E1': (6.0, 64.0, 71.0, 2400), 'E2': (10.0, 71.0, 80.0, 2100), 'E3': (15.0, 82.0, 92.0, 1800),
       'E4': (15.0, 96.0, 109.0, 1500), 'E5': (10.0, 118.0, 134.0, 1200)}
OFFS = {'O1': (2.0, 160.0, 2600), 'O2': (3.8, 172.5, 2900), 'O3': (6.0, 138.5, 3070), 'O4': (10.0, 112.5, 3150), 'O5': (25.0, 132.5, 2700)}
def ann_kW(c, r=None):
    """EUR/kW-yr of a technology record c = dict(capex_kW, life, build_y, om_kW): overnight capex x interest during construction x CRF + fixed O&M (same rule as nuclear)."""
    r = R_GLOBAL if r is None else r
    return c['capex_kW'] * (idc(r, c['build_y']) if c.get('build_y') else 1.0) * crf(r, c['life']) + c.get('om_kW', 0.0)
def life_factor(c):
    """Mean output over the life relative to year 1, for a linear degradation c['degr'] per year."""
    return 1.0 - c.get('degr', 0.0) * (c['life'] - 1) / 2.0
def pv_blocks(href_pv, curve='central', exist='post2016', cost_mult=1.0, exist_GW=None, v8=None):
    J = json.load(open(os.path.join(HERE, 'pv_land_blocks.json')))[curve]
    E = {'post2016': PV_2025 - PV_2016, 'post2010': PV_2025 - PV_2010, 'none': 0.0}[exist] if exist_GW is None else exist_GW
    g = GROUND_2025 / PV_2025; Eg = E * g; Er = E - Eg
    zsum = sum(GROUND_ZONE.values()); roof_tot = sum(b['gw_reali'] for b in J if b['tipo'].startswith('tetti'))
    out = []; exg = 0.0; exgr = 0.0; exr = 0.0; exrr = 0.0
    for b in J:
        ded = 0.0
        if b['tipo'] == 'terra': ded = Eg * GROUND_ZONE[b['zona']] / zsum; exg += ded; exgr += ded * b['rho']
        elif b['tipo'].startswith('tetti'): ded = Er * b['gw_reali'] / roof_tot; exr += ded; exrr += ded * b['rho']
        m = b['m']; cst = PV_REAL * (1 - PV_KAPPA + PV_KAPPA * m) * cost_mult; rho = b['rho']
        if v8 is not None:   # bottom-up: EUR/kW-yr by plant type, divided by the reference hours because the LP multiplies cost by yref
            c = v8['pv'][b['tipo'].replace('terra-pipeline', 'terra')]
            cst = ann_kW(c) * 1000.0 / href_pv * cost_mult; rho = b['rho'] * c.get('yield_mult', 1.0) * life_factor(c)
        out.append(dict(name=f"PV_{b['tipo']}_{b['zona']}", res='pv', cap=b['gw_reali'] - ded, cost=cst, yref=href_pv, rho=rho, own='new', thr=True))
    om_g = PV_OM; om_r = PV_OM; fg = fr = 1.0
    if v8 is not None:
        eg = v8['pv']['exist_terra']; er = v8['pv']['exist_tetti']
        om_g = eg['om_kW'] * 1000.0 / href_pv; om_r = er['om_kW'] * 1000.0 / href_pv; fg = eg.get('yield_mult', 1.0); fr = er.get('yield_mult', 1.0)
    if exg > 0: out.append(dict(name='PVex_terra', res='pv', cap=exg, cost=om_g, yref=href_pv, rho=exgr / exg * fg, own='existing', thr=False))
    if exr > 0: out.append(dict(name='PVex_tetti', res='pv', cap=exr, cost=om_r, yref=href_pv, rho=exrr / exr * fr, own='existing', thr=False))
    return out
def wind_blocks(href_on, case='A', on=('E0', 'E1', 'E2', 'E3', 'E4', 'E5'), off=('O1', 'O2', 'O3', 'O4', 'O5'), off_cost=None,
                cost_mult=1.0, e0_GW=None, e0_free_GW=None, v8=None):
    out = []; ci = 1 if case == 'A' else 2
    for k in on:
        cap, cA, cB, h = ONS[k]; cost = (cA, cB)[ci - 1] * (cost_mult if k != 'E0' else 1.0)
        if v8 is not None:   # bottom-up: the same EUR/kW-yr for every new block; blocks differ by hours. E0 (existing) pays fixed O&M only
            cost = (v8['on']['exist_om_kW'] if k == 'E0' else ann_kW(v8['on']) * cost_mult) * 1000.0 / h
        if k == 'E0':
            if e0_free_GW is not None:
                out.append(dict(name='E0', res='on', cap=e0_free_GW, cost=cost, yref=h, rho=h / href_on, own='existing', thr=False))
                out.append(dict(name='E0rep', res='on', cap=cap - e0_free_GW, cost=(ONS['E1'][1], ONS['E1'][2])[ci - 1] * cost_mult, yref=h, rho=h / href_on, own='new', thr=False))
                continue
            out.append(dict(name='E0', res='on', cap=cap, cost=cost, yref=h, rho=h / href_on, own='existing', thr=False))
        else:
            out.append(dict(name=k, res='on', cap=cap, cost=cost, yref=h, rho=h / href_on, own='new', thr=True))
    for k in off:
        cap, c, h = OFFS[k]
        if v8 is not None and v8.get('off'): c = ann_kW(v8['off'][v8['off']['blocks'][k]]) * 1000.0 / h
        out.append(dict(name=k, res='off', cap=cap, cost=(c if off_cost is None else off_cost) * cost_mult, yref=h, rho=1.0, own='new', thr=True))
    return out
