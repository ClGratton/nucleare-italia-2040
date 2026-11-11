import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hl5, hl7, blocks_v6, spec7
def run(a, inp=None):
    a = dict(a); tag = a.pop('tag', ''); inp = inp or hl5.load_inputs(a.pop('inputs', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'inputs_main.npz')))
    step = a.pop('step', 3); dk = dict(step=step)
    for k in ('years', 'wyears'):
        if k in a: dk[k] = tuple(a.pop(k))
    if a.pop('v6reg', False):
        D = hl5.build_data(inp, **dk); hp = D['href']
        blocks = blocks_v6.pv_blocks(hp['pv']) + blocks_v6.wind_blocks(hp['on'])
        sp = hl7.spec_v6(D, blocks, **{k: (tuple(v) if k == 'allow' else v) for k, v in a.items() if k in ('band', 'allow', 'nuc_capex', 'r', 'y')}); info = {}
    else:
        bm = a.pop('bio_must', 0.0); gm = a.pop('geo_must', 0.0)
        D = hl5.build_data(inp, bio=bm, geo=gm, **dk); hp = D['href']
        J = hl7.load_techs(os.path.join(os.path.dirname(os.path.abspath(__file__)), a.pop('techs', 'techs_v7.json')))
        v8 = J.get('vre')    # bottom-up PV and wind costs (v8); absent in techs_v7.json
        blocks = blocks_v6.pv_blocks(hp['pv'], v8=v8) + blocks_v6.wind_blocks(hp['on'], v8=v8)
        G = J.get('global', {})
        if G.get('grid_thr_total_GW'):   # the threshold is defined on the total wind + PV stock: subtract the existing fleet kept in the model
            a.setdefault('grid_thr', G['grid_thr_total_GW'] - sum(b['cap'] for b in blocks if b['own'] == 'existing'))
        pk = a.pop('peak_ref_step', G.get('peak_ref_step'))
        if pk:   # reserve requirement on the peak of the finest data (same value at every time step)
            D0 = D if pk == step else hl5.build_data(inp, bio=bm, geo=gm, **dict(dk, step=pk))
            a['_peak_load'] = float((D0['load'] - D0['must']).max()) / pk * step
        kw = {k: a.pop(k) for k in ('mode', 'nuc', 'cases', 'default_novel', 'off', 'variants', 'allow', 'band', 'N_fix', 'reserve', 'grid_thr') if k in a}
        if 'allow' in kw: kw['allow'] = tuple(kw['allow'])
        sp, info = spec7.build(D, blocks, J, **kw)
        pr = a.pop('probe', None)
        if pr:
            if pr['type'] == 'carnot': sp['stor'].append(dict(name='CARNOT', grp='probe', probe=True, E_hi=0.1, eta_c=pr['eta'], eta_d=1.0, credit_p=0.0))
            else: sp['stor'].append(dict(name='HPTANK', grp='probe', probe=True, dur=pr['dur'], E_hi=pr['GWh'], eta_c=1.0, eta_d=1.0, credit_e=0.0, dis_max_base=dict(key='hp', share=1.0)))
    if 'export_X' in a: sp['export'] = dict(X=a.pop('export_X'))
    if 'export' in a: sp['export'] = a.pop('export')      # dict(X=..., cap_frac=..., price=...)
    if '_peak_load' in a: sp['peak_load'] = a.pop('_peak_load')
    res = hl7.solve7(D, **sp, solver=a.get('solver'), verbose=bool(os.environ.get('V7DEBUG')))
    res['hours_ref'] = {k: round(v, 1) for k, v in hp.items()}
    return tag, res, info
if __name__ == '__main__':
    tag, res, info = run(json.loads(sys.argv[1]))
    print(json.dumps({'tag': tag, 'res': res, 'info': info}))
