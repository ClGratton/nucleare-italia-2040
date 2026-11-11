# Capacity expansion model v6, zero-emission Italian power system 2040, single node, 3-hour step, solved with highspy.
# (see repo/v6/hl5.py for the full header)
import sys, json, time, os, numpy as np, scipy.sparse as sp
import highspy
DBG = bool(os.environ.get('V6DEBUG'))

HYD_2023 = [2171, 1590, 1721, 1643, 4598, 5176, 4477, 3913, 3621, 3388, 4270, 3381]   # GWh, Terna
HYD_2024 = [3117, 2702, 4094, 4871, 5964, 6483, 6151, 4188, 3876, 5282, 3162, 2186]
AV = [0.97, 0.97, 0.87, 0.87, 0.87, 0.97, 0.97, 0.97, 0.87, 0.87, 0.87, 0.97]      # nuclear availability by month (assumption, mean 0.92)

import os
R_GLOBAL = float(os.environ.get('V7_R', '0.05'))
def crf(r, n): return r * (1 + r) ** n / ((1 + r) ** n - 1)

def real_cost_parts(price, indexed, contract=20, life=30, r=R_GLOBAL, infl=0.02, opex=0.2):
    # price-based technologies: capital part computed at the base rate 5%, then scaled by CRF(r,life)/CRF(5%,life); O&M part unchanged
    rb = 0.05
    d = [(1 + rb) ** -t for t in range(1, contract + 1)]
    real = price * sum((indexed + (1 - indexed) * (1 + infl) ** -t) * x for t, x in enumerate(d, 1)) / sum(d)
    return real * (1 - opex) * crf(rb, life) / crf(rb, contract) * crf(r, life) / crf(rb, life), real * opex

def real_cost(price, indexed, **k):
    a, b = real_cost_parts(price, indexed, **k); return a + b

PV_AUCTION, WIND_REF, BATT_AUCTION = 56.82, 85.0, 12959.0   # FER X Dec 2025, MACSE Sep 2025 (nominal)
PV_CAP, PV_OM = real_cost_parts(PV_AUCTION, 0.2)             # EUR/MWh real
PV_REAL = PV_CAP + PV_OM
WIND_REAL = real_cost(WIND_REF, 0.2)
BATT_REAL = real_cost(BATT_AUCTION, 0.1, contract=15, life=15)
PV_KAPPA = PV_CAP / PV_REAL                                   # capital share of the real PV cost (0.764)
def idc(r, y): return sum((1 + r) ** (y - k - 0.5) for k in range(y)) / y

def load_inputs(path='inputs_v6.npz'):
    z = np.load(path); return {k: z[k] for k in z.files}

HP_SHAPE_H = np.array([0.6] * 6 + [1.8] * 3 + [1.0] * 9 + [2.0] * 4 + [0.8] * 2)       # local hour of day, relative weights (declared assumption)
HP_SHAPE_H = HP_SHAPE_H / HP_SHAPE_H.sum()
def ev_shape(mode):
    e = np.zeros(24)
    if mode == 'evening': e[18:24] = 0.7 / 6; e += 0.3 / 24      # 70% of daily energy 18:00-24:00 local, 30% spread over 24 h
    elif mode == 'evening100': e[18:24] = 1 / 6
    elif mode == 'flat': e += 1 / 24
    elif mode == 'day': e[9:16] = 0.5 / 7; e[18:24] += 0.3 / 6; e += 0.2 / 24
    elif mode == 'mix': e[18:24] = 0.4 / 6; e[0:6] += 0.3 / 6; e += 0.3 / 24
    elif mode == 'night':  e[0:6] = 0.7 / 6; e += 0.3 / 24
    return e

def build_data(inp, years=(2016, 2017, 2018, 2019), wyears=None, step=3, D_total=400e6, hp=15e6, ev=47e6, h2=0.0, grow=1.0,
               bio=8e6, geo=5.3e6, hyd_total=43.4e6, hyd='avg', ev_mode='evening', hp_mode='hdd', ev_scale=1.0, prof='pecd', h_pv=1066.0, h_on=1709.0):
    wyears = list(years) if wyears is None else list(wyears)
    py = list(inp['pecd_years'])
    mon = inp['month']; Y = len(years)
    base_tot = D_total - hp * grow - ev * grow * ev_scale - h2
    assert base_tot > 0
    L = []; S = []; W = []; O = []; M = []; YR = []; EVL = []; HPL = []
    es = ev_shape(ev_mode)
    for k, (ly, wy) in enumerate(zip(years, wyears)):
        i = ly - 2016; j = py.index(wy)
        ld = inp['load'][i]; hl = inp['hour_local'][i]
        b = ld / ld.sum() * base_tot
        if hp_mode == 'hdd': mw = inp['hdd'][i][mon]
        else: mw = np.ones(8760)
        w = HP_SHAPE_H[hl]; norm = np.bincount(mon, weights=w, minlength=12)[mon]
        hpv = mw * w / norm; hpv = hpv / hpv.sum() * hp * grow
        evv = es[hl]; evv = evv / evv.sum() * ev * grow * ev_scale
        tot = b + hpv + evv + h2 / 8760.0
        must = np.full(8760, (bio + geo) / 8760.0)
        agg = lambda a: a.reshape(-1, step).sum(1)
        L.append(agg(tot)); M.append(agg(must)); EVL.append(agg(evv)); HPL.append(agg(hpv))
        if prof == 'pecd': S.append(agg(inp['pecd_pv'][j])); W.append(agg(inp['pecd_on'][j]))
        else:
            a = agg(inp['pv_opsd'][i]); S.append(a / a.sum() * h_pv); a = agg(inp['wind_opsd'][i]); W.append(a / a.sum() * h_on)
        O.append(agg(inp['pecd_off'][j]))
        mm = mon.reshape(-1, step)[:, 0]; YR.append(np.full(len(mm), k)); L[-1] = L[-1]
        if k == 0: mon_s = mm
    base4 = [py.index(y) for y in (2016, 2017, 2018, 2019)]
    href = dict(pv=float(inp['pecd_pv'][base4].sum(1).mean()) if prof == 'pecd' else h_pv, on=float(inp['pecd_on'][base4].sum(1).mean()) if prof == 'pecd' else h_on,
                off=float(inp['pecd_off'][base4].sum(1).mean()))
    h23 = np.array(HYD_2023) * 1e3; h24 = np.array(HYD_2024) * 1e3
    if hyd == 'avg': hm = (h23 + h24) / 2; hm = hm / hm.sum() * hyd_total if hyd_total else hm
    elif hyd == 'dry': hm = h23
    elif hyd == 'wet': hm = h24
    else: hm = np.zeros(12)
    d = dict(ev=np.concatenate(EVL), hp=np.concatenate(HPL), load=np.concatenate(L), must=np.concatenate(M), s=np.concatenate(S), w=np.concatenate(W), o=np.concatenate(O),
             m12=np.tile(mon_s, Y), yr=np.concatenate(YR), hb=np.tile(hm, Y), step=step, Y=Y, href=href)
    d['demand_TWh'] = float(d['load'].sum() / Y / 1e6)
    return d

# ---------------------------------------------------------------- solver
def solve(D, blocks, nuc_capex=7600, r=0.05, y=7, minload=0.5, avail=AV, allow=('n', 's', 'w', 'b'), batt=BATT_REAL, life=80,
          imp_GW=0.0, imp_price=80.0, eff=0.85, dur=6.6, reserve=1.1,
          hydro_on=True, hydro_GW=15.0, hydro_floor=0.37, ph_GW=7.3, ph_GWh=51.0, ph_eff=0.75,
          hydro_credit=1.0, ph_credit=1.0, batt_credit_dur=None, imp_credit=0.5, nuc_credit=None,
          om_fix=17.0, om_var=15.0, grid_nuc=2.0, grid_basis='cap', grid_pv=13.0, grid_on=8.0, grid_thr=137.0, grid_x=None,
          pv_ref_h=1066.0, on_ref_h=1709.0, N_fix=None, ld_cost=1486.0, ld_dur=100.0, ld_eff=0.5, band=0.0, band_solver='primal', tl=None, presolve=None, h2=None):
    step = D['step']; Y = D['Y']; load = D['load'] - D['must']; s = D['s']; w = D['w']; o = D['o']
    T = len(load); t = np.arange(T); Mm = D['m12'] + 12 * D['yr']
    hb = D['hb']
    av = np.array(avail, dtype=float)[D['m12']] if np.ndim(avail) else np.full(T, float(avail)); avm = float(av.mean())
    fixN = nuc_capex * 1000 * idc(r, y) * crf(r, life) + om_fix * 0.9 * 8760 + grid_nuc * avm * 8760
    nb = len(blocks)
    iN, iE = 0, 1; ib = [2 + j for j in range(nb)]; iX = 2 + nb; iL = iX + 1
    LD = 'l' in allow; HY = ('h' in allow) and h2 is not None; iH = iL + (1 if LD else 0); nfix = iH + (3 if HY else 0)
    K = 12; tv = lambda k: nfix + k * T; lv = lambda k: nfix + K * T + k * T
    nv = nfix + K * T + (3 * T if LD else 0) + (3 * T if HY else 0)
    hv = lambda k: nfix + K * T + (3 * T if LD else 0) + k * T
    n_, ps_, pw_, po_, ch_, dis_, soc_, h_, pc_, pd_, psoc_, im_ = range(12)
    if grid_x is None: grid_x = 0.5 * (grid_pv * pv_ref_h + grid_on * on_ref_h) / 1000.0      # kEUR/MW-yr, one more unit of grid charge
    c = np.zeros(nv); c[iN] = fixN * Y; c[iE] = batt * Y
    for j, b in enumerate(blocks):
        g = 0.0
        if b['res'] == 'pv' and b['own'] == 'new' and grid_basis == 'cap': g = grid_pv * pv_ref_h
        if b['res'] == 'on' and b['own'] == 'new' and grid_basis == 'cap': g = grid_on * on_ref_h
        c[ib[j]] = (b['cost'] * b['yref'] + g) * Y
    c[iX] = grid_x * 1000 * Y
    c[tv(n_):tv(n_ + 1)] = om_var; c[tv(im_):tv(im_ + 1)] = imp_price
    if grid_basis == 'used': c[tv(ps_):tv(ps_ + 1)] = grid_pv; c[tv(pw_):tv(pw_ + 1)] = grid_on
    if LD: c[iL] = ld_cost * Y
    if HY: c[iH] = h2['el_cost'] * Y; c[iH + 1] = h2['sto_cost'] * Y; c[iH + 2] = h2['t_cost'] * Y; c[hv(1):hv(2)] = h2['t_vom']
    A = []; bb = []
    def blk(entries, ub):
        R = []; C = []; V = []
        for ci, vi in entries:
            R.append(t); C.append(np.broadcast_to(ci, (T,))); V.append(np.broadcast_to(vi, (T,)).astype(float))
        A.append(sp.csr_matrix((np.concatenate(V), (np.concatenate(R), np.concatenate(C))), shape=(T, nv)))
        bb.append(np.broadcast_to(ub, (T,)).astype(float))
    pvj = [j for j, b in enumerate(blocks) if b['res'] == 'pv']; onj = [j for j, b in enumerate(blocks) if b['res'] == 'on']; ofj = [j for j, b in enumerate(blocks) if b['res'] == 'off']
    blk([(tv(n_) + t, 1), (iN, -av * step)], 0)
    blk([(tv(n_) + t, -1), (iN, minload * av * step)], 0)
    blk([(tv(ps_) + t, 1)] + [(ib[j], -s * blocks[j]['rho']) for j in pvj], 0)
    blk([(tv(pw_) + t, 1)] + [(ib[j], -w * blocks[j]['rho']) for j in onj], 0)
    blk([(tv(po_) + t, 1)] + [(ib[j], -o * blocks[j]['rho']) for j in ofj], 0)
    blk([(tv(ch_) + t, 1), (iE, -step / dur)], 0)
    blk([(tv(dis_) + t, 1), (iE, -step / dur)], 0)
    blk([(tv(soc_) + t, 1), (iE, -1)], 0)
    if LD:
        blk([(lv(0) + t, 1), (iL, -step / ld_dur)], 0); blk([(lv(1) + t, 1), (iL, -step / ld_dur)], 0); blk([(lv(2) + t, 1), (iL, -1)], 0)
    if HY:   # electrolyser power, turbine power, store content bounded by their capacities
        blk([(hv(0) + t, 1), (iH, -step)], 0); blk([(hv(1) + t, 1), (iH + 2, -step)], 0); blk([(hv(2) + t, 1), (iH + 1, -1)], 0)
    Aub = sp.vstack(A).tocsr(); bub = np.concatenate(bb); del A, bb
    # firm capacity reserve (MW): credit x capacity >= reserve x peak of the net load
    peak = load.max() / step; avp = float(av[int(load.argmax())]); nc = avp if nuc_credit is None else nuc_credit
    bc = dur if batt_credit_dur is None else batt_credit_dur
    rc = [iN, iE] + ([iL] if LD else []) + ([iH + 2] if HY else []); rv = [-nc, -1.0 / bc] + ([-1.0 / ld_dur] if LD else []) + ([-h2['t_credit']] if HY else [])
    Ares = sp.csr_matrix((rv, ([0] * len(rc), rc)), shape=(1, nv))
    firm = (hydro_GW * hydro_credit + ph_GW * ph_credit) * 1000 if hydro_on else 0.0
    bres = np.array([-(reserve * peak - firm - imp_GW * imp_credit * 1000)])
    # grid threshold: capacity of new PV and wind blocks above grid_thr (GW) pays the extra charge X
    thr_cols = [ib[j] for j, b in enumerate(blocks) if b.get('thr')] + [iX]; thr_vals = [1.0] * (len(thr_cols) - 1) + [-1.0]
    Athr = sp.csr_matrix((thr_vals, ([0] * len(thr_cols), thr_cols)), shape=(1, nv)); bthr = np.array([grid_thr * 1000])
    Aub = sp.vstack([Aub, Ares, Athr]).tocsr(); bub = np.concatenate([bub, bres, bthr])
    R = []; C = []; V = []
    for k, sg in ((n_, 1), (ps_, 1), (pw_, 1), (po_, 1), (ch_, -1), (dis_, 1), (h_, 1), (pc_, -1), (pd_, 1), (im_, 1)):
        R.append(t); C.append(tv(k) + t); V.append(np.full(T, float(sg)))
    if LD:
        R += [t, t]; C += [lv(0) + t, lv(1) + t]; V += [np.full(T, -1.0), np.full(T, 1.0)]
    if HY: R += [t, t]; C += [hv(0) + t, hv(1) + t]; V += [np.full(T, -1.0), np.full(T, 1.0)]
    Abal = sp.csr_matrix((np.concatenate(V), (np.concatenate(R), np.concatenate(C))), shape=(T, nv))
    tn = (t + 1) % T
    def dyn(sock, inn, out, e):
        return sp.csr_matrix((np.concatenate([np.ones(T), -np.ones(T), np.full(T, -e), np.ones(T)]),
                              (np.concatenate([t, t, t, t]), np.concatenate([sock + tn, sock + t, inn + t, out + t]))), shape=(T, nv))
    Asoc = dyn(tv(soc_), tv(ch_), tv(dis_), eff)
    Aph = dyn(tv(psoc_), tv(pc_), tv(pd_), ph_eff)
    Ald = dyn(lv(2), lv(0), lv(1), ld_eff) if LD else None
    Ah = sp.csr_matrix((np.concatenate([np.ones(T), -np.ones(T), np.full(T, -h2['eta_el']), np.full(T, 1.0 / h2['eta_t'])]),
                        (np.concatenate([t, t, t, t]), np.concatenate([hv(2) + tn, hv(2) + t, hv(0) + t, hv(1) + t]))), shape=(T, nv)) if HY else None   # store: +eta_el x electrolyser input - turbine output / eta_t, cyclic
    nm = 12 * Y
    Ahyd = sp.csr_matrix((np.ones(T), (Mm, tv(h_) + t)), shape=(nm, nv))
    Aeq = sp.vstack([Abal, Asoc, Aph] + ([Ald] if LD else []) + [Ahyd] + ([Ah] if HY else [])).tocsr()
    beq = np.concatenate([load, np.zeros(T), np.zeros(T)] + ([np.zeros(T)] if LD else []) + [hb] + ([np.zeros(T)] if HY else []))
    del Abal, Asoc, Aph, Ald, Ahyd
    lo = np.zeros(nv); hi = np.full(nv, np.inf)
    if 'n' not in allow: hi[iN] = 0
    if 'b' not in allow: hi[iE] = 0
    cnt = np.bincount(Mm, minlength=nm); mean = hb[Mm] / cnt[Mm]
    hcap = hydro_GW * 1000 * step
    lo[tv(h_):tv(h_ + 1)] = np.minimum(hydro_floor * mean, hcap); hi[tv(h_):tv(h_ + 1)] = hcap if hydro_on else 0
    phc = ph_GW * 1000 * step if hydro_on else 0
    hi[tv(pc_):tv(pc_ + 1)] = phc; hi[tv(pd_):tv(pd_ + 1)] = phc; hi[tv(psoc_):tv(psoc_ + 1)] = ph_GWh * 1000 if hydro_on else 0
    hi[tv(im_):tv(im_ + 1)] = imp_GW * 1000 * step
    for j, b in enumerate(blocks):
        hi[ib[j]] = b['cap'] * 1000
        if (b['own'] == 'new') and ((b['res'] == 'pv' and 's' not in allow) or (b['res'] in ('on', 'off') and 'w' not in allow)): hi[ib[j]] = 0
    if N_fix is not None: lo[iN] = hi[iN] = N_fix * 1000
    Aall = sp.vstack([Aub, Aeq]).tocsc(); rl = np.concatenate([np.full(len(bub), -np.inf), beq]); ru = np.concatenate([bub, beq])
    del Aub, Aeq
    lp = highspy.HighsLp(); lp.num_col_ = nv; lp.num_row_ = Aall.shape[0]; lp.col_cost_ = c; lp.col_lower_ = lo; lp.col_upper_ = hi
    lp.row_lower_ = rl; lp.row_upper_ = ru; lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_ = Aall.indptr.astype(np.int32); lp.a_matrix_.index_ = Aall.indices.astype(np.int32); lp.a_matrix_.value_ = Aall.data
    del Aall
    hs = highspy.Highs(); hs.setOptionValue('output_flag', False); hs.setOptionValue('threads', 1)
    if tl: hs.setOptionValue('time_limit', float(tl))
    if presolve: hs.setOptionValue('presolve', presolve)
    t0_ = time.time(); hs.passModel(lp); del lp; hs.run()
    if DBG: print('main solve', round(time.time() - t0_, 1), hs.getInfo().simplex_iteration_count, file=sys.stderr, flush=True)
    x = np.array(hs.getSolution().col_value); fun = hs.getInfo().objective_function_value
    st = hs.modelStatusToString(hs.getModelStatus())
    sl = lambda k: x[tv(k):tv(k + 1)]
    bandres = {}
    if band > 0 and hi[iN] > 0 and st == 'Optimal':
        # near-optimal band: min and max nuclear capacity among systems costing at most (1+band) x the optimum (primal simplex from the optimal basis)
        nz = np.nonzero(c)[0]
        hs.addRow(-highspy.kHighsInf, fun * (1 + band), len(nz), nz.astype(np.int32), c[nz])
        hs.changeColsCost(len(nz), nz.astype(np.int32), np.zeros(len(nz)))
        if band_solver == 'primal': hs.setOptionValue('simplex_strategy', 4)
        b0 = hs.getBasis(); tot_load = load.sum()
        for sgn, ext in ((-1.0, 'max'), (1.0, 'min')):
            hs.changeColCost(iN, sgn); hs.setBasis(b0); t1_ = time.time(); hs.run(); xb = np.array(hs.getSolution().col_value)
            if DBG: print('band', ext, round(time.time() - t1_, 1), hs.getInfo().simplex_iteration_count, hs.modelStatusToString(hs.getModelStatus()), file=sys.stderr, flush=True)
            bandres['N_' + ext] = round(float(xb[iN] / 1e3), 3)
            bandres['sh_at_N' + ext] = round(float(xb[tv(n_):tv(n_ + 1)].sum() / tot_load), 4)
            bandres['pv_at_N' + ext] = round(float(sum(xb[ib[j]] for j in pvj) / 1e3), 2)
            bandres['on_at_N' + ext] = round(float(sum(xb[ib[j]] for j in onj) / 1e3), 2)
            bandres['E_at_N' + ext] = round(float(xb[iE] / 1e6), 2)
            bandres['status_N' + ext] = hs.modelStatusToString(hs.getModelStatus())
    n = sl(n_); ps = sl(ps_); pw = sl(pw_); po = sl(po_); dis = sl(dis_); ch = sl(ch_); hy = sl(h_); pdd = sl(pd_); im = sl(im_)
    N = x[iN]; E = x[iE]
    gb = {b['name']: float(x[ib[j]] / 1e3) for j, b in enumerate(blocks)}
    capx = lambda js: sum(x[ib[j]] for j in js)
    pv_pot = sum(x[ib[j]] * blocks[j]['rho'] for j in pvj) * s.sum(); on_pot = sum(x[ib[j]] * blocks[j]['rho'] for j in onj) * w.sum(); of_pot = sum(x[ib[j]] * blocks[j]['rho'] for j in ofj) * o.sum()
    Dt = D['load'].sum(); Dnet = load.sum(); newD = Dnet - hy.sum()
    mon = D['m12']
    cfm = [round(float(n[mon == k].sum() / (N * step * (mon == k).sum())), 2) if N > 0 else 0 for k in range(12)]
    spd = 24 // step; nd = T // spd; nn = n[:nd * spd].reshape(nd, spd)
    daily_cf = nn.sum(1) / (N * step * spd) if N > 0 else np.zeros(nd)
    comp = dict(nuc=float(c[iN] * N + c[tv(n_):tv(n_ + 1)] @ n) / newD, batt=float(c[iE] * E) / newD,
                pv=float(sum(c[ib[j]] * x[ib[j]] for j in pvj)) / newD, on=float(sum(c[ib[j]] * x[ib[j]] for j in onj)) / newD,
                off=float(sum(c[ib[j]] * x[ib[j]] for j in ofj)) / newD, gridx=float(c[iX] * x[iX]) / newD, imp=float(c[tv(im_):tv(im_ + 1)] @ im) / newD,
                ld=float(c[iL] * x[iL]) / newD if LD else 0.0, gridvar=float(c[tv(ps_):tv(ps_ + 1)] @ ps + c[tv(pw_):tv(pw_ + 1)] @ pw) / newD)
    out = dict(cost_new=fun / newD, cost_all=fun / Dt, cost_net=fun / Dnet, N_GW=N / 1e3,
               PV_GW=capx(pvj) / 1e3, ON_GW=capx(onj) / 1e3, OFF_GW=capx(ofj) / 1e3,
               PVnew_GW=sum(x[ib[j]] for j in pvj if blocks[j]['own'] == 'new') / 1e3, ONnew_GW=sum(x[ib[j]] for j in onj if blocks[j]['own'] == 'new') / 1e3,
               E_GWh=E / 1e3, sh_nuc=n.sum() / Dt, sh_nuc_net=n.sum() / Dnet, sh_pv=ps.sum() / Dt, sh_on=pw.sum() / Dt, sh_off=po.sum() / Dt, sh_h=hy.sum() / Dt,
               sh_ph=pdd.sum() / Dt, sh_imp=im.sum() / Dt, sh_must=D['must'].sum() / Dt,
               nuc_cf=(n.sum() / (N * T * step) if N > 0 else 0), curt_pv=(1 - ps.sum() / pv_pot if pv_pot > 0 else 0),
               curt_on=(1 - pw.sum() / on_pot if on_pot > 0 else 0), curt_off=(1 - po.sum() / of_pot if of_pot > 0 else 0),
               batt=dis.sum() / Dt, fixN=fixN / 1000, peak_GW=peak / 1e3, demand_TWh=Dt / Y / 1e6, net_TWh=Dnet / Y / 1e6,
               load_factor=float(Dnet / (T * step) / peak), thr_excess_GW=float(x[iX] / 1e3),
               ld_GWh=x[iL] / 1e3 if LD else 0, sh_ld=(x[lv(1):lv(2)].sum() / Dt if LD else 0), nuc_swing=float((nn.max(1) - nn.min(1)).mean() / (N * step)) if N > 0 else 0,
               daily_cf_p10=float(np.percentile(daily_cf, 10)), daily_cf_p90=float(np.percentile(daily_cf, 90)), cf_month=cfm)
    if HY:
        el = x[hv(0):hv(1)]; tb = x[hv(1):hv(2)]
        out.update(h2_el_GW=x[iH] / 1e3, h2_sto_TWh=x[iH + 1] / 1e6, h2_t_GW=x[iH + 2] / 1e3, h2_t_hours=(tb.sum() / Y / x[iH + 2] if x[iH + 2] > 1e-6 else 0),
                   h2_el_hours=(el.sum() / Y / x[iH] if x[iH] > 1e-6 else 0), sh_h2=tb.sum() / Dt)
        comp['h2'] = float(c[iH] * x[iH] + c[iH + 1] * x[iH + 1] + c[iH + 2] * x[iH + 2] + c[hv(1):hv(2)] @ tb) / newD
    r_ = {k: (round(float(v), 3) if not isinstance(v, list) else v) for k, v in out.items()}
    r_['blocks_GW'] = {k: round(v, 3) for k, v in gb.items() if v > 1e-6}
    r_['comp'] = {k: round(v, 2) for k, v in comp.items()}
    r_.update(bandres); r_['status'] = st
    return r_
