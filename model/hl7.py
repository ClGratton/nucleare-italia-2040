import sys, json, time, os, numpy as np, scipy.sparse as sp
import highspy
from hl5 import crf, idc, AV, BATT_REAL, PV_REAL, PV_KAPPA, build_data, load_inputs, real_cost
INF = np.inf
def load_techs(path):
    return json.load(open(path))
def _arr(v, T, mon=None):
    if v is None: return None
    a = np.asarray(v, dtype=float)
    if a.ndim == 0: return np.full(T, float(a))
    if len(a) == 12 and mon is not None: return a[mon]
    return a
def solve7(D, vre, disp=(), stor=(), dsm=(), dac=None, reserve=1.1, firm_MW=0.0, grid_thr=137.0, grid_x=0.0, emis_cap=0.0,
           band=0.0, band_units=(), N_fix=None, tl=None, excl_denominator=(), peak_load=None, extra_prof=None, verbose=False, want_x=False, solver=None, export=None):
    step = D['step']; Y = D['Y']; load = D['load'] - D['must']
    T = len(load); t = np.arange(T); mon = D['m12']; yr = D['yr']; Mm = mon + 12 * yr
    prof = {'pv': D['s'], 'on': D['w'], 'off': D['o']}
    if extra_prof: prof.update(extra_prof)
    disp = [dict(u) for u in disp if u.get('on', True)]; stor = [u for u in stor if u.get('on', True)]; dsm = [u for u in dsm if u.get('on', True)]
    for u in disp:
        if 'blocks' not in u: u['blocks'] = [dict(cap_lo=u.get('cap_lo', 0.0), cap_hi=u.get('cap_hi'), capex_yr=u.get('capex_yr', 0.0))]
    nc = [0]
    def col(k=1): i = nc[0]; nc[0] += k; return i
    cvre = [col() for _ in vre]; cX = col()
    cdisp = [[col() for _ in u['blocks']] for u in disp]
    cst = []
    for s in stor:
        d = {'E': col()}
        if s.get('dur') is None: d['Pc'] = col(); d['Pd'] = col()
        cst.append(d)
    cdsm = [col() if d.get('cap_cost') is not None else None for d in dsm]
    cdac = col() if dac else None
    pg = {p: col(T) for p in sorted({b['profile'] for b in vre})}
    sdisp = [None if u.get('flat') else col(T) for u in disp]
    sst = [dict(ch=col(T), dis=col(T), soc=col(T)) for _ in stor]
    sdsm = [dict(up=col(T), dn=col(T) if d.get('kind') != 'export' else None) for d in dsm]
    sdac = col(T) if dac else None
    sexp = col(T) if export else None
    nv = nc[0]
    cost = np.zeros(nv); lo = np.zeros(nv); hi = np.full(nv, INF)
    for j, b in enumerate(vre):
        cost[cvre[j]] = (b['cost'] * b['yref'] + b.get('grid', 0.0)) * Y; hi[cvre[j]] = b['cap'] * 1000; lo[cvre[j]] = b.get('lo', 0.0) * 1000
    cost[cX] = grid_x * 1000 * Y
    rows = []; rl = []; ru = []; nr = [0]
    def add(n, ent, l, h):
        rows.extend([(r + nr[0], c, v) for r, c, v in ent])
        rl.append(np.broadcast_to(np.asarray(l, dtype=float), (n,))); ru.append(np.broadcast_to(np.asarray(h, dtype=float), (n,))); nr[0] += n
    ones = np.ones(T)
    for p, c0 in pg.items():
        js = [j for j, b in enumerate(vre) if b['profile'] == p]
        ent = [(t, c0 + t, ones)] + [(t, np.full(T, cvre[j]), -prof[p] * vre[j]['rho']) for j in js]
        add(T, ent, -INF, 0.0)
    tj = [j for j, b in enumerate(vre) if b.get('thr')]
    add(1, [(np.zeros(len(tj) + 1, dtype=int), np.array([cvre[j] for j in tj] + [cX]), np.array([1.0] * len(tj) + [-1.0]))], -INF, grid_thr * 1000)
    av_of = lambda u: _arr(u.get('avail', 1.0), T, mon)
    peak = (load.max() if peak_load is None else peak_load) / step
    ipk = int(load.argmax())
    cred = []
    flat_sup = []
    spd = 24 // step; day = t // spd
    for k, u in enumerate(disp):
        cs = cdisp[k]; so = sdisp[k]; av = av_of(u)
        for c0, b in zip(cs, u['blocks']):
            lo[c0] = b.get('cap_lo', 0.0) * 1000; hi[c0] = INF if b.get('cap_hi') is None else b['cap_hi'] * 1000
            cost[c0] = b.get('capex_yr', 0.0) * Y
        caphi = sum((b['cap_hi'] if b.get('cap_hi') is not None else 1e6) for b in u['blocks'])
        if u.get('credit', 'av') is not None and u.get('credit_on', True):
            for c0 in cs:
                cr = av[ipk] if u.get('credit', 'av') == 'av' else float(u['credit'])
                cred.append((c0, -cr))
        if u.get('flat'):
            for c0 in cs: flat_sup.append((c0, av * step))
            continue
        cost[so:so + T] = _arr(u.get('var', 0.0), T, mon)
        add(T, [(t, so + t, ones)] + [(t, np.full(T, c0), -av * step) for c0 in cs], -INF, 0.0)
        if u.get('minload', 0.0) > 0: add(T, [(t, so + t, -ones)] + [(t, np.full(T, c0), u['minload'] * av * step) for c0 in cs], -INF, 0.0)
        EL = u.get('energy'); EL = [] if not EL else (EL if isinstance(EL, list) else [EL])
        for E in EL:
            if E['kind'] == 'annual':
                add(Y, [(yr, so + t, ones)], E['min'] if E.get('min') is not None else -INF, E['value'])
            elif E['kind'] == 'hours':
                add(Y, [(yr, so + t, ones)] + [(np.arange(Y), np.full(Y, c0), np.full(Y, -E['value'])) for c0 in cs], -INF, 0.0)
            elif E['kind'] == 'daily_yield':
                pr = prof[E['prof']]; fac = np.zeros(T // spd); Ty = T // Y
                for y_ in range(Y):
                    sl = slice(y_ * Ty, (y_ + 1) * Ty); tot = pr[sl].sum()
                    dd = np.add.reduceat(pr[sl], np.arange(0, Ty, spd)); fac[y_ * (Ty // spd):(y_ + 1) * (Ty // spd)] = dd / tot * E['value']
                nd = T // spd
                add(nd, [(day, so + t, ones)] + [(np.arange(nd), np.full(nd, c0), -fac) for c0 in cs], -INF, 0.0)
            else:
                mv = np.tile(np.asarray(E['value'], dtype=float), Y)
                add(12 * Y, [(Mm, so + t, ones)], mv if E['kind'] == 'monthly_eq' else -INF, mv)
                if u.get('floor', 0.0) > 0:
                    cnt = np.bincount(Mm, minlength=12 * Y); mean = mv[Mm] / cnt[Mm]
                    lo[so:so + T] = np.minimum(u['floor'] * mean, min(caphi, 1e6) * 1000 * step)
        if u.get('seq'):
            add(Y, [(yr, so + t, np.full(T, u['seq']['t_per_MWh']))], -INF, u['seq']['Mt_yr'] * 1e6)
    for k, s in enumerate(stor):
        d = cst[k]; z = sst[k]; cE = d['E']
        lo[cE] = s.get('E_lo', 0.0) * 1000; hi[cE] = INF if s.get('E_hi') is None else s['E_hi'] * 1000
        cost[cE] = s.get('E_cost', 0.0) * Y
        if s.get('dur') is not None:
            add(T, [(t, z['ch'] + t, ones), (t, np.full(T, cE), -step / s['dur'] * ones)], -INF, 0.0)
            add(T, [(t, z['dis'] + t, ones), (t, np.full(T, cE), -step / s['dur'] * ones)], -INF, 0.0)
            cred.append((cE, -s.get('credit_e', 1.0 / s['dur'])))
        else:
            for nm, sr in (('Pc', 'ch'), ('Pd', 'dis')):
                c1 = d[nm]; lo[c1] = s.get(nm + '_lo', 0.0) * 1000; hi[c1] = INF if s.get(nm + '_hi') is None else s[nm + '_hi'] * 1000
                cost[c1] = s.get(nm + '_cost', 0.0) * Y
                add(T, [(t, z[sr] + t, ones), (t, np.full(T, c1), -step * ones)], -INF, 0.0)
            cred.append((d['Pd'], -s.get('credit_p', 0.0)))
        if s.get('dis_max_base'):
            m = s['dis_max_base']; hi[z['dis']:z['dis'] + T] = m['share'] * np.asarray(D[m['key']], dtype=float)
        add(T, [(t, z['soc'] + t, ones), (t, np.full(T, cE), -ones)], -INF, 0.0)
        tn = (t + 1) % T
        add(T, [(t, z['soc'] + tn, ones), (t, z['soc'] + t, -(1.0 - s.get('loss', 0.0)) * ones), (t, z['ch'] + t, -s['eta_c'] * ones), (t, z['dis'] + t, ones / s['eta_d'])], 0.0, 0.0)
        cost[z['ch']:z['ch'] + T] = s.get('var_ch', 0.0); cost[z['dis']:z['dis'] + T] = s.get('var_dis', 0.0)
    for k, dv in enumerate(dsm):
        z = sdsm[k]; up = z['up']; dn = z['dn']; cc = cdsm[k]
        capMW = None if dv.get('cap_GW') is None else dv['cap_GW'] * 1000
        if cc is not None:
            lo[cc] = dv.get('cap_lo', 0.0) * 1000; hi[cc] = INF if dv.get('cap_hi') is None else dv['cap_hi'] * 1000; cost[cc] = dv['cap_cost'] * Y
            add(T, [(t, up + t, ones), (t, np.full(T, cc), -step * ones)], -INF, 0.0)
        elif capMW is not None:
            hi[up:up + T] = capMW * step
        if dn is not None and dv.get('base') is not None:
            hi[dn:dn + T] = dv['share'] * np.asarray(D[dv['base']], dtype=float)
        cost[up:up + T] = dv.get('var', 0.0)
        if dv.get('window'):
            w = (t + int(dv.get('window_off', 0))) // int(dv['window']); nw = int(w.max()) + 1
            add(nw, [(w, up + t, ones), (w, dn + t, -ones / dv.get('eta', 1.0))], 0.0, 0.0)
    if dac:
        lo[cdac] = 0.0; hi[cdac] = INF if dac.get('cap_hi') is None else dac['cap_hi']; cost[cdac] = dac['capex_yr'] * Y
        add(T, [(t, sdac + t, ones), (t, np.full(T, cdac), -step * ones)], -INF, 0.0)
        cost[sdac:sdac + T] = dac.get('var', 0.0)
    ent = []
    for c0 in pg.values(): ent.append((t, c0 + t, ones))
    for k in range(len(disp)):
        if sdisp[k] is not None: ent.append((t, sdisp[k] + t, ones))
    for c0, a in flat_sup: ent.append((t, np.full(T, c0), a))
    for k, s in enumerate(stor): ent += [(t, sst[k]['dis'] + t, ones), (t, sst[k]['ch'] + t, -ones)]
    for k, dv in enumerate(dsm):
        ent.append((t, sdsm[k]['up'] + t, -ones))
        if sdsm[k]['dn'] is not None: ent.append((t, sdsm[k]['dn'] + t, ones))
    if dac: ent.append((t, sdac + t, -dac['elec_MWh_per_t'] * ones))
    if export:
        ent.append((t, sexp + t, -ones))
    add(T, ent, load, load)
    if export:
        ki = next(k for k, u in enumerate(disp) if u['name'] == 'IMPORT')
        # export limit: by default the import capacity; with cap_frac, that fraction of it (Terna export NTC / import NTC)
        xf = float(export.get('cap_frac', 1.0))
        add(T, [(t, sexp + t, ones)] + [(t, np.full(T, c0), -step * xf * ones) for c0 in cdisp[ki]], -INF, 0.0)
        cost[sexp:sexp + T] = -float(export.get('price', 0.0))      # revenue per MWh exported (0 = pure sink)
        Dyr = float(D['load'].sum()) / Y
        if export.get('X') is not None:
            # annual balance per weather year: -X_exp * D <= imports - exports <= X * D  (X = X_exp = 0: a balanced energy swap, neither net importer nor net exporter)
            lo_ = -float(export['X_exp']) * Dyr if export.get('X_exp') is not None else -INF
            add(Y, [(yr, sdisp[ki] + t, ones), (yr, sexp + t, -ones)], lo_, float(export['X']) * Dyr)
    cr = [(c, v) for c, v in cred]
    add(1, [(np.zeros(len(cr), dtype=int), np.array([c for c, _ in cr]), np.array([v for _, v in cr]))], -INF, -(reserve * peak - firm_MW))
    ee = [(np.zeros(T, dtype=int), sdisp[k] + t, np.full(T, u['ef'])) for k, u in enumerate(disp) if u.get('ef') and sdisp[k] is not None]
    if dac: ee.append((np.zeros(T, dtype=int), sdac + t, -ones))
    if ee: add(1, ee, -INF, emis_cap)
    if N_fix is not None:
        for k, u in enumerate(disp):
            if u.get('grp') == 'nuclear':
                for c0 in cdisp[k]: lo[c0] = hi[c0] = N_fix * 1000
    A = sp.coo_matrix((np.concatenate([np.broadcast_to(v, np.shape(r)) if np.ndim(v) == 0 else v for r, c, v in rows]),
                       (np.concatenate([np.asarray(r) for r, c, v in rows]), np.concatenate([np.broadcast_to(c, np.shape(r)) if np.ndim(c) == 0 else c for r, c, v in rows]))),
                      shape=(nr[0], nv)).tocsc()
    rlo = np.concatenate(rl); rup = np.concatenate(ru)
    lp = highspy.HighsLp(); lp.num_col_ = nv; lp.num_row_ = A.shape[0]; lp.col_cost_ = cost; lp.col_lower_ = lo; lp.col_upper_ = hi
    lp.row_lower_ = rlo; lp.row_upper_ = rup; lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_ = A.indptr.astype(np.int32); lp.a_matrix_.index_ = A.indices.astype(np.int32); lp.a_matrix_.value_ = A.data
    nrows = A.shape[0]; del A, rows
    hs = highspy.Highs(); hs.setOptionValue('output_flag', False); hs.setOptionValue('threads', 1)
    if tl: hs.setOptionValue('time_limit', float(tl))
    if solver: hs.setOptionValue('solver', solver)
    t0 = time.time(); hs.passModel(lp); del lp; hs.run()
    sol = hs.getSolution(); x = np.array(sol.col_value); dual = np.array(sol.col_dual)
    fun = hs.getInfo().objective_function_value; st = hs.modelStatusToString(hs.getModelStatus())
    if verbose: print('solve', round(time.time() - t0, 1), st, 'cols', nv, 'rows', nrows, file=sys.stderr, flush=True)
    bandres = {}
    if band > 0 and band_units and st == 'Optimal':
        nz = np.nonzero(cost)[0]
        hs.addRow(-highspy.kHighsInf, fun * (1 + band), len(nz), nz.astype(np.int32), cost[nz])
        hs.changeColsCost(len(nz), nz.astype(np.int32), np.zeros(len(nz)))
        hs.setOptionValue('simplex_strategy', 4); b0 = hs.getBasis()
        bk = [k for k, u in enumerate(disp) if u['name'] in band_units]
        bcols = [c0 for k in bk for c0 in cdisp[k]]
        for sgn, ext in ((-1.0, 'max'), (1.0, 'min')):
            for cb in bcols: hs.changeColCost(cb, sgn)
            hs.setBasis(b0); hs.run(); xb = np.array(hs.getSolution().col_value)
            bandres['N_' + ext] = round(float(sum(xb[cb] for cb in bcols) / 1e3), 3)
            bandres['status_N' + ext] = hs.modelStatusToString(hs.getModelStatus())
            sh = sum(xb[sdisp[k]:sdisp[k] + T].sum() for k in bk)
            bandres['sh_at_N' + ext] = round(float(sh / D['load'].sum()), 4)
            bandres['pv_at_N' + ext] = round(float(sum(xb[cvre[j]] for j, b in enumerate(vre) if b['profile'] == 'pv') / 1e3), 2)
            bandres['on_at_N' + ext] = round(float(sum(xb[cvre[j]] for j, b in enumerate(vre) if b['profile'] == 'on') / 1e3), 2)
            for cb in bcols: hs.changeColCost(cb, 0.0)
    Dt = D['load'].sum(); Dnet = load.sum()
    def dispE(k):
        u = disp[k]
        if sdisp[k] is not None: return x[sdisp[k]:sdisp[k] + T].sum()
        av = av_of(u); return float((av * step).sum() * sum(x[c] for c in cdisp[k]))
    ex = sum(dispE(k) for k, u in enumerate(disp) if u['name'] in excl_denominator or u.get('excl'))
    newD = Dnet - ex
    units = {}
    for j, b in enumerate(vre):
        g = x[cvre[j]] / 1e3
        if g > 1e-6: units[b['name']] = dict(GW=round(g, 3), cap=round(b['cap'], 3), sat=bool(g >= b['cap'] - 1e-3 and b['cap'] < 1e3), grp=b.get('grp', b['profile']))
    for k, u in enumerate(disp):
        g = sum(x[c] for c in cdisp[k]) / 1e3; e = dispE(k) / Y / 1e6
        caphi = None if any(b.get('cap_hi') is None for b in u['blocks']) else sum(b['cap_hi'] for b in u['blocks'])
        EL = u.get('energy'); EL = [] if not EL else (EL if isinstance(EL, list) else [EL])
        lim = next((E['value'] / 1e6 for E in EL if E['kind'] == 'annual'), None)
        sat = bool((caphi is not None and g >= caphi - 1e-3 and caphi > 0 and sum(b.get('cap_lo', 0.0) for b in u['blocks']) < caphi) or (lim is not None and e >= lim - 1e-3))
        if g > 1e-6 or e > 1e-6:
            o = dict(GW=round(g, 3), TWh=round(e, 3), hours=round(e * 1e6 / (g * 1e3 + 1e-9), 0) if g > 1e-6 else 0, sat=sat, grp=u.get('grp'))
            if caphi is not None: o['cap_hi'] = round(caphi, 3)
            if lim is not None: o['TWh_limit'] = round(lim, 3)
            if len(u['blocks']) > 1: o['blocks_GW'] = [round(x[c] / 1e3, 3) for c in cdisp[k]]
            units[u['name']] = o
    for k, s in enumerate(stor):
        d = cst[k]; z = sst[k]; E = x[d['E']] / 1e3
        if E > 1e-6 or (s.get('E_hi') is not None and s.get('E_lo', 0) > 0):
            o = dict(GWh=round(E, 3), TWh_out=round(x[z['dis']:z['dis'] + T].sum() / Y / 1e6, 3), grp=s.get('grp'))
            if 'Pc' in d: o.update(Pc_GW=round(x[d['Pc']] / 1e3, 3), Pd_GW=round(x[d['Pd']] / 1e3, 3))
            if s.get('E_hi') is not None: o['sat'] = bool(E >= s['E_hi'] - 1e-3); o['E_hi_GWh'] = s['E_hi']
            units[s['name']] = o
        if s.get('probe'):
            units[s['name'] + '_probe'] = dict(GWh=round(E, 3), value_EUR_per_kWh_yr=round(float(-dual[d['E']] / Y / 1000.0), 4))
    for k, dv in enumerate(dsm):
        z = sdsm[k]; e = x[z['up']:z['up'] + T].sum() / Y / 1e6
        if e > 1e-6: units[dv['name']] = dict(TWh=round(e, 3), GW=round((x[cdsm[k]] / 1e3) if cdsm[k] is not None else 0.0, 3), grp=dv.get('grp'))
    if dac and x[cdac] > 1e-9: units['DAC'] = dict(MtCO2=round(x[sdac:sdac + T].sum() / Y / 1e6, 3), t_per_h=round(x[cdac], 1))
    if export: units['EXPORT'] = dict(TWh=round(x[sexp:sexp + T].sum() / Y / 1e6, 3))
    em = sum(u['ef'] * x[sdisp[k]:sdisp[k] + T].sum() for k, u in enumerate(disp) if u.get('ef') and sdisp[k] is not None) / Y / 1e6 if any(u.get('ef') for u in disp) else 0.0
    def grp_sum(g): return sum(sum(x[c] for c in cdisp[k]) for k, u in enumerate(disp) if u.get('grp') == g) / 1e3
    def grp_e(g): return sum(dispE(k) for k, u in enumerate(disp) if u.get('grp') == g)
    bal = {'demand_TWh': round(Dnet / Y / 1e6, 3), 'VRE': {}, 'gen_TWh': {}, 'stor': {}, 'dsm': {}, 'peak_GW': {}, 'cost_Meur_yr': {}, 'credit_GW': {}}
    sup = 0.0
    for p, c0 in pg.items():
        used = x[c0:c0 + T].sum() / Y / 1e6; av_ = sum(x[cvre[j]] * vre[j]['rho'] * prof[p].sum() for j, b in enumerate(vre) if b['profile'] == p) / Y / 1e6
        bal['VRE'][p] = dict(avail=round(av_, 3), used=round(used, 3), curt=round(av_ - used, 3)); sup += used
    for k, u in enumerate(disp):
        e = dispE(k) / Y / 1e6; bal['gen_TWh'][u['name']] = round(e, 3); sup += e
        capx = sum(cost[c] * x[c] for c in cdisp[k]); var = (cost[sdisp[k]:sdisp[k] + T] @ x[sdisp[k]:sdisp[k] + T]) if sdisp[k] is not None else 0.0
        bal['cost_Meur_yr'][u['name']] = dict(capex_om=round(capx / Y / 1e6, 2), energy=round(var / Y / 1e6, 2))
        if sdisp[k] is not None: bal['peak_GW'][u['name']] = round(x[sdisp[k]:sdisp[k] + T].max() / step / 1e3, 3)
        if u.get('credit', 'av') is not None and u.get('credit_on', True):
            cr_ = av_of(u)[ipk] if u.get('credit', 'av') == 'av' else float(u['credit']); bal['credit_GW'][u['name']] = round(cr_ * sum(x[c] for c in cdisp[k]) / 1e3, 3)
    for k, s in enumerate(stor):
        d = cst[k]; z = sst[k]; i_ = x[z['ch']:z['ch'] + T].sum() / Y / 1e6; o_ = x[z['dis']:z['dis'] + T].sum() / Y / 1e6; sup += o_ - i_
        bal['stor'][s['name']] = dict(in_TWh=round(i_, 3), out_TWh=round(o_, 3), loss_TWh=round(i_ - o_, 3))
        v = cost[d['E']] * x[d['E']] + cost[z['ch']:z['ch'] + T] @ x[z['ch']:z['ch'] + T] + cost[z['dis']:z['dis'] + T] @ x[z['dis']:z['dis'] + T]
        for nm in ('Pc', 'Pd'):
            if nm in d: v += cost[d[nm]] * x[d[nm]]
        bal['cost_Meur_yr'][s['name']] = dict(capex_om=round(v / Y / 1e6, 2), energy=0.0)
        bal['credit_GW'][s['name']] = round((s.get('credit_p', 0.0) * x[d['Pd']] if 'Pd' in d else s.get('credit_e', 1.0 / s['dur']) * x[d['E']]) / 1e3, 3)
    for k, dv in enumerate(dsm):
        z = sdsm[k]; u_ = x[z['up']:z['up'] + T].sum() / Y / 1e6; d_ = x[z['dn']:z['dn'] + T].sum() / Y / 1e6 if z['dn'] is not None else 0.0; sup += d_ - u_
        bal['dsm'][dv['name']] = dict(up_TWh=round(u_, 3), down_TWh=round(d_, 3))
    if dac: sup -= dac['elec_MWh_per_t'] * x[sdac:sdac + T].sum() / Y / 1e6
    gv = 0.0
    for j, b in enumerate(vre): gv += cost[cvre[j]] * x[cvre[j]]
    bal['cost_Meur_yr']['VRE_and_grid'] = dict(capex_om=round((gv + cost[cX] * x[cX]) / Y / 1e6, 2), energy=0.0)
    if dac: bal['cost_Meur_yr']['DAC'] = dict(capex_om=round((cost[cdac] * x[cdac] + cost[sdac:sdac + T] @ x[sdac:sdac + T]) / Y / 1e6, 2), energy=0.0)
    bal['supply_minus_demand_TWh'] = round(sup - Dnet / Y / 1e6, 4); bal['reserve_required_GW'] = round(reserve * peak / 1e3, 3)
    bal['total_cost_Meur_yr'] = round(fun / Y / 1e6, 2); bal['denominator_TWh'] = round(newD / Y / 1e6, 3)
    res = dict(cost_new=fun / newD, cost_all=fun / Dt, cost_net=fun / Dnet, N_GW=grp_sum('nuclear'), sh_nuc=grp_e('nuclear') / Dt,
               SMR_GW=grp_sum('smr'), sh_smr=grp_e('smr') / Dt, status=st, obj_EUR_yr=fun / Y,
               peak_GW=peak / 1e3, load_factor=float(Dnet / (T * step) / peak), thr_excess_GW=float(x[cX] / 1e3), emissions_MtCO2_gross=em,
               units=units, demand_TWh=Dt / Y / 1e6, diag=bal)
    cs = {}
    for j, b in enumerate(vre): cs[b.get('grp', b['profile'])] = cs.get(b.get('grp', b['profile']), 0) + cost[cvre[j]] * x[cvre[j]]
    cs['grid_over'] = cost[cX] * x[cX]
    for k, u in enumerate(disp):
        g = u.get('grp', u['name']); v = sum(cost[c] * x[c] for c in cdisp[k])
        if sdisp[k] is not None: v += cost[sdisp[k]:sdisp[k] + T] @ x[sdisp[k]:sdisp[k] + T]
        cs[g] = cs.get(g, 0) + v
    for k, s in enumerate(stor):
        d = cst[k]; z = sst[k]; v = cost[d['E']] * x[d['E']] + cost[z['ch']:z['ch'] + T] @ x[z['ch']:z['ch'] + T] + cost[z['dis']:z['dis'] + T] @ x[z['dis']:z['dis'] + T]
        for nm in ('Pc', 'Pd'):
            if nm in d: v += cost[d[nm]] * x[d[nm]]
        cs[s.get('grp', s['name'])] = cs.get(s.get('grp', s['name']), 0) + v
    for k, dv in enumerate(dsm):
        z = sdsm[k]; cs[dv.get('grp', dv['name'])] = cs.get(dv.get('grp', dv['name']), 0) + cost[z['up']:z['up'] + T] @ x[z['up']:z['up'] + T] + (cost[cdsm[k]] * x[cdsm[k]] if cdsm[k] is not None else 0)
    if dac: cs['dac'] = cost[cdac] * x[cdac] + cost[sdac:sdac + T] @ x[sdac:sdac + T]
    if export: cs['export_revenue'] = cost[sexp:sexp + T] @ x[sexp:sexp + T]
    res['comp'] = {k: round(v / newD, 2) for k, v in cs.items() if abs(v) > 1e-6}
    res.update(bandres)
    if export: res['export_TWh'] = x[sexp:sexp + T].sum() / Y / 1e6; res['import_TWh'] = dispE(ki) / Y / 1e6
    nk = [k for k, u in enumerate(disp) if u.get('grp') == 'nuclear']
    if nk and grp_sum('nuclear') > 1e-6: res['nuc_cf'] = float(grp_e('nuclear') / Y / (grp_sum('nuclear') * 1e3 * 8760))
    res['reserve_peak_GW'] = peak / 1e3
    r = {k: (round(float(v), 3) if isinstance(v, (float, np.floating)) else v) for k, v in res.items()}
    return (r, x) if want_x else r
def vre_blocks(blocks, allow=('n', 's', 'w', 'b'), grid_pv=13.0, grid_on=8.0, pv_ref_h=1066.0, on_ref_h=1709.0, grid_scale=1.0):
    vre = []
    for b in blocks:
        g = 0.0; cap = b['cap']
        if b['res'] == 'pv' and b['own'] == 'new': g = grid_pv * pv_ref_h * grid_scale
        if b['res'] == 'on' and b['own'] == 'new': g = grid_on * on_ref_h * grid_scale
        if b['own'] == 'new' and ((b['res'] == 'pv' and 's' not in allow) or (b['res'] in ('on', 'off') and 'w' not in allow)): cap = 0.0
        vre.append(dict(name=b['name'], profile=b['res'], cap=cap, cost=b['cost'], yref=b['yref'], rho=b['rho'], grid=g, thr=bool(b.get('thr')), grp=b['res']))
    return vre
def spec_v6(D, blocks, nuc_capex=7600, r=0.05, y=7, minload=0.5, avail=AV, allow=('n', 's', 'w', 'b'), batt=BATT_REAL, life=80,
            imp_GW=0.0, imp_price=80.0, eff=0.85, dur=6.6, reserve=1.1, hydro_GW=15.0, hydro_floor=0.37, ph_GW=7.3, ph_GWh=51.0, ph_eff=0.75,
            hydro_credit=1.0, ph_credit=1.0, batt_credit_dur=None, imp_credit=0.5, nuc_credit=None, om_fix=17.0, om_var=15.0, grid_nuc=2.0,
            grid_pv=13.0, grid_on=8.0, grid_thr=137.0, grid_x=None, pv_ref_h=1066.0, on_ref_h=1709.0, N_fix=None, ld_cost=1486.0, ld_dur=100.0,
            ld_eff=0.5, band=0.0, tl=None, **ignored):
    vre = vre_blocks(blocks, allow, grid_pv, grid_on, pv_ref_h, on_ref_h)
    if grid_x is None: grid_x = 0.5 * (grid_pv * pv_ref_h + grid_on * on_ref_h) / 1000.0
    av = np.array(avail, dtype=float)[D['m12']] if np.ndim(avail) else np.full(len(D['load']), float(avail)); avm = float(av.mean())
    fixN = nuc_capex * 1000 * idc(r, y) * crf(r, life) + om_fix * 0.9 * 8760 + grid_nuc * avm * 8760
    hm = D['hb'][:12]
    disp = [dict(name='NUC', grp='nuclear', cap_lo=0.0, cap_hi=(None if 'n' in allow else 0.0), capex_yr=fixN, var=om_var, avail=list(avail) if np.ndim(avail) else float(avail),
                 minload=minload, credit=('av' if nuc_credit is None else nuc_credit)),
            dict(name='HYDRO', grp='hydro', cap_lo=hydro_GW, cap_hi=hydro_GW, capex_yr=0.0, var=0.0, avail=1.0, energy=dict(kind='monthly_eq', value=list(hm)),
                 floor=hydro_floor, credit=hydro_credit, excl=True)]
    if imp_GW > 0: disp.append(dict(name='IMPORT', grp='import', cap_lo=imp_GW, cap_hi=imp_GW, capex_yr=0.0, var=imp_price, avail=1.0, credit=imp_credit))
    stor = [dict(name='BATT', grp='battery', dur=dur, E_cost=batt, E_hi=(None if 'b' in allow else 0.0), eta_c=eff, eta_d=1.0,
                 credit_e=1.0 / (dur if batt_credit_dur is None else batt_credit_dur)),
            dict(name='PUMPED', grp='pumped', Pc_lo=ph_GW, Pc_hi=ph_GW, Pd_lo=ph_GW, Pd_hi=ph_GW, E_lo=ph_GWh, E_hi=ph_GWh, eta_c=ph_eff, eta_d=1.0, credit_p=ph_credit)]
    if 'l' in allow: stor.append(dict(name='LDES', grp='ldes', dur=ld_dur, E_cost=ld_cost, eta_c=ld_eff, eta_d=1.0, credit_e=1.0 / ld_dur))
    return dict(vre=vre, disp=disp, stor=stor, reserve=reserve, grid_thr=grid_thr, grid_x=grid_x, band=band, band_units=('NUC',), N_fix=N_fix, tl=tl)
