#!/usr/bin/env python3
"""Figures of version 8 restored from version 7, redrawn with the v8 runs. Writes docs/figures/fig_{months,systems,nuccost,saving}_{it,en}.{png,pdf}.

Usage: python tools/make_figures_v8.py

Reads only repository files:
- data/monthly_pv_wind_2024_it.csv              monthly PV and wind output in Italy, 2024 (GSE, Terna)
- results/v8_runs.jsonl                          3-hour runs (central systems, fixed-N runs of the value curves)
- docs/results_v8.md                             cost cases (section 3) and check values (sections 1, 3, 5)
- model/techs_v8.json                            nuclear inputs (O&M, availability, variable cost, life)
Every plotted number is checked against docs/results_v8.md; the script stops if one differs.

1. fig_months:  monthly output of PV and wind in 2024 as a share of each source's annual output.
2. fig_systems: installed capacity and system cost of the four central systems (3 h, 5%), composition as in results_v8.md section 5.
3. fig_nuccost: cost of a nuclear MWh against construction cost, cost rule of model/spec7.py, availability 90%, with the cost cases.
4. fig_saving:  saving (cost without nuclear minus cost with nuclear) against fixN, read on the value curves at 5% and 7%.
The v7 figure of the monthly cost per useful MWh is not redrawn: the v8 runs store no monthly results.
"""
import csv, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from value_curve import fixN, crf, idc   # same formula as model/spec7.py
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator

FD = os.path.join(ROOT, 'docs', 'figures'); os.makedirs(FD, exist_ok=True)
E = 356.6   # TWh: demand not met by existing hydro, denominator of the system cost

# ---------------------------------------------------------------- inputs
R = {}
for l in open(os.path.join(ROOT, 'results', 'v8_runs.jsonl')):
    try: j = json.loads(l); R[j['tag']] = j
    except Exception: pass
def cost(t): return R[t]['res']['obj_EUR_yr'] / 356.6e6

def md_tables(path):
    """{'<section>|<bold title>': rows} for every table of results_v8.md."""
    out = {}; sec = ''; title = ''; cur = None
    for line in open(path, encoding='utf-8').read().split('\n'):
        if line.startswith('## '): sec = line[3:].split('.')[0].strip(); title = ''; cur = None
        elif line.startswith('**'): title = line.split('**')[1].strip(); cur = None
        elif line.startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if set(''.join(cells)) <= set('-: '): continue
            key = sec + '|' + title
            if cur != key: cur = key; out[key] = []
            out[key].append(cells)
        else: cur = None
    return out
MD = md_tables(os.path.join(ROOT, 'docs', 'results_v8.md'))
num = lambda s: float(s.replace(',', ''))
def check(a, b, tol, what):
    if abs(a - b) > tol: sys.exit(f'mismatch with docs/results_v8.md: {what}: computed {a}, report {b}')

NUC = next(u for u in json.load(open(os.path.join(ROOT, 'model', 'techs_v8.json')))['disp'] if u['name'] == 'NUC')

# ---------------------------------------------------------------- style (as tools/report_v8.py)
INK = '#1f2933'; MUT = '#6b7785'; GRID = '#e3e7ec'; BLUE = '#2a6fb0'; ORA = '#c8621a'
plt.rcParams.update({'font.size': 8.5, 'axes.edgecolor': MUT, 'axes.labelcolor': INK, 'xtick.color': MUT, 'ytick.color': MUT, 'axes.spines.top': False,
                     'axes.spines.right': False, 'font.family': 'DejaVu Sans', 'axes.linewidth': 0.6})
def fmt(v, lang, dec=0):
    s = f"{v:,.{dec}f}"
    return s.replace(',', 'X').replace('.', ',').replace('X', '.') if lang == 'it' else s
def axfmt(axis, lang, dec=0): axis.set_major_formatter(FuncFormatter(lambda v, _: fmt(v, lang, dec)))
def save(fig, name, lang, tight=True):
    if tight: fig.tight_layout()
    fig.savefig(os.path.join(FD, f'{name}_{lang}.png'), dpi=220); fig.savefig(os.path.join(FD, f'{name}_{lang}.pdf')); plt.close(fig)
EUR = {'it': '€', 'en': 'EUR'}

# ---------------------------------------------------------------- 1. monthly output 2024
rows = [r for r in csv.reader(l for l in open(os.path.join(ROOT, 'data', 'monthly_pv_wind_2024_it.csv')) if not l.startswith('#'))][1:]
PV = [float(r[1]) for r in rows]; WD = [float(r[2]) for r in rows]
MONTHS = {'it': ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic'],
          'en': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']}
def fig_months(lang):
    t = dict(it=dict(pv='Fotovoltaico', wd='Eolico', flat='Domanda costante (1/12)', y='Quota della produzione annua (%)'),
             en=dict(pv='Solar PV', wd='Wind', flat='Flat demand (1/12)', y='Share of annual output (%)'))[lang]
    fig, ax = plt.subplots(figsize=(6.0, 2.9))
    ax.plot(range(12), [x / sum(PV) * 100 for x in PV], color=ORA, lw=1.6, marker='o', ms=3.5, label=t['pv'])
    ax.plot(range(12), [x / sum(WD) * 100 for x in WD], color=BLUE, lw=1.6, marker='s', ms=3.5, label=t['wd'])
    ax.axhline(100 / 12, color=MUT, lw=0.9, ls=(0, (4, 3)), label=t['flat'])
    ax.set_xticks(range(12)); ax.set_xticklabels(MONTHS[lang]); ax.set_ylabel(t['y']); ax.set_ylim(0, 14); axfmt(ax.yaxis, lang)
    ax.grid(axis='y', color=GRID, lw=0.5); ax.set_axisbelow(True); ax.legend(frameon=False, fontsize=7, ncol=3, loc='upper center', bbox_to_anchor=(0.5, 1.12))
    save(fig, 'fig_months', lang)

# ---------------------------------------------------------------- 2. central systems
SYS = [('v8_PI_r5_opt_h3', 'PI with nuclear'), ('v8_PI_r5_N00_h3', 'PI without'), ('v8_OB_r5_opt_h3', 'OB with nuclear'), ('v8_OB_r5_N00_h3', 'OB without')]
def mix(t):   # same aggregation as tools/report_v8.py, section 5
    u = R[t]['res']['units']; g = lambda p: sum((v.get('GW') or 0) for k, v in u.items() if k.startswith(p)); e = lambda k: (u.get(k, {}).get('GWh') or 0)
    nuc = sum((u[k].get('GW') or 0) for k in ('NUC', 'SMR') if k in u)
    return dict(pv=g('PV'), on=sum((v.get('GW') or 0) for k, v in u.items() if re.match(r'E\d', k)), off=sum((v.get('GW') or 0) for k, v in u.items() if re.match(r'O\d', k)),
                nuc=nuc, csp=g('CSP'), imp=u.get('IMPORT', {}).get('GW') or 0, batt=e('BATT'), h2=e('H2'), caes=e('CAES'), ldes=e('LDES'), cost=cost(t))
S5 = {r[0]: r for r in MD['5|'][1:]}
S1 = {(r[0], r[1]): r for r in MD['1|'][1:]}
MIX = {}
for t, lab in SYS:
    m = MIX[t] = mix(t); r = S5[lab]
    for k, j, d in (('pv', 1, 0), ('on', 2, 1), ('off', 3, 1), ('nuc', 4, 1), ('csp', 5, 1), ('batt', 6, 0), ('h2', 7, 0), ('caes', 8, 0), ('ldes', 9, 0), ('imp', 10, 1)):
        check(round(m[k], d), num(r[j]), 1e-9, f'{lab} {k}')
    cs = lab[:2]; check(round(m['cost'], 2), num(S1[(cs, '5%')][5 if 'with nuclear' in lab else 6]), 1e-9, f'{lab} cost')
def fig_systems(lang):
    it = lang == 'it'
    lab = {'v8_PI_r5_opt_h3': 'PI con nucleare' if it else 'PI with nuclear', 'v8_PI_r5_N00_h3': 'PI senza nucleare' if it else 'PI without nuclear',
           'v8_OB_r5_opt_h3': 'OB con nucleare' if it else 'OB with nuclear', 'v8_OB_r5_N00_h3': 'OB senza nucleare' if it else 'OB without nuclear'}
    cats = [('nuc', 'Nucleare' if it else 'Nuclear', BLUE), ('pv', 'Fotovoltaico' if it else 'Solar PV', '#e0a526'), ('on', 'Eolico a terra' if it else 'Onshore wind', '#3a9a6e'),
            ('off', 'Eolico in mare' if it else 'Offshore wind', '#93cbb3'), ('csp', 'Solare termodinamico' if it else 'Solar thermal (CSP)', ORA),
            ('imp', 'Interconnessione' if it else 'Interconnection', '#9a8bb8')]
    sto = [('batt', 'batterie' if it else 'batteries'), ('h2', 'idrogeno' if it else 'hydrogen'), ('caes', 'aria compressa' if it else 'compressed air'), ('ldes', 'accumulo 100 h' if it else '100-hour')]
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    for i, (t, _) in enumerate(SYS):
        y = len(SYS) - 1 - i; m = MIX[t]; x0 = 0
        for k, name, col in cats:
            w = m[k]
            if w <= 0: continue
            ax.barh(y, w, left=x0, height=0.6, color=col, edgecolor='white', lw=0.5, label=name if i == 0 or (k in ('off',) and i == 1) else None)
            if w >= 12: ax.text(x0 + w / 2, y, fmt(w, lang), ha='center', va='center', fontsize=6.6, color='white' if k in ('nuc', 'on', 'csp', 'imp') else INK)
            x0 += w
        st = []
        for k, name in sto:
            v = m[k]
            if round(v) <= 0: continue
            st.append(f"{name} {fmt(v / 1000, lang, 1)} TWh" if k == 'h2' else f"{name} {fmt(v, lang)} GWh")
        lines = [st[:2], st[2:]] if len(st) > 2 else [st]
        ax.text(x0 + 4, y + 0.2, f"{fmt(m['cost'], lang, 2)} {EUR[lang]}/MWh", va='center', fontsize=7, color=INK, fontweight='bold')
        for n_, ln in enumerate(lines):
            ax.text(x0 + 4, y - 0.04 - 0.22 * n_, (('accumuli: ' if it else 'storage: ') if n_ == 0 else '') + ', '.join(ln) + (',' if n_ == 0 and len(lines) > 1 else ''), va='center', fontsize=6.3, color=MUT)
    ax.set_yticks(range(len(SYS))); ax.set_yticklabels([lab[t] for t, _ in SYS][::-1]); ax.tick_params(axis='y', length=0)
    ax.set_xlim(0, 410); ax.set_xticks(range(0, 301, 50)); ax.spines['bottom'].set_bounds(0, 300); ax.spines['left'].set_visible(False)
    ax.set_xlabel('Potenza installata (GW)' if it else 'Installed capacity (GW)', x=300 / 410 / 2); axfmt(ax.xaxis, lang)
    ax.grid(axis='x', color=GRID, lw=0.5); ax.set_axisbelow(True)
    h, l = ax.get_legend_handles_labels(); order = [l.index(n) for _, n, _ in cats if n in l]
    ax.legend([h[o] for o in order], [l[o] for o in order], frameon=False, fontsize=6.8, ncol=6, loc='upper center', bbox_to_anchor=(0.45, -0.2), handlelength=1.2, columnspacing=1.0)
    save(fig, 'fig_systems', lang)

# ---------------------------------------------------------------- cost cases (results_v8.md section 3)
CASES = [(r[0], num(r[1]), int(r[2]), num(r[3])) for r in MD['3|PI 5%'][1:]]
FIX7 = {r[0]: num(r[3]) for r in MD['3|PI 7%'][1:]}
for name, k, y, f5 in CASES:
    check(round(fixN(k, 0.05, y)), f5, 0, f'fixN {name} 5%'); check(round(fixN(k, 0.07, y)), FIX7[name], 0, f'fixN {name} 7%')
for k_, v_ in (('om_fix_MWh', 27.75), ('om_cf', 0.9), ('grid_MWh', 2.0), ('life', 60)):
    assert NUC[k_] == v_, f'techs_v8.json NUC {k_} differs from the fixN formula of tools/value_curve.py'
AV = 0.90; VAR = NUC['var']
def mwh(capex, r, y): return fixN(capex, r, y, life=NUC['life'], om_fix_MWh=NUC['om_fix_MWh'], grid=NUC['grid_MWh'], av=AV) / (AV * 8.76) + VAR

# ---------------------------------------------------------------- 3. cost of a nuclear MWh
CN = {'it': {'Dukovany contract, central': 'Dukovany', 'Dukovany, midpoint of EC bracket': 'punto medio intervallo', 'Dukovany, top of EC bracket': 'massimo intervallo',
             'v7 central capex': 'versione 7', 'Barakah': 'Barakah', 'Saeul budget': 'Shin Hanul', 'Risk median': 'mediana cantieri', 'Vogtle': 'Vogtle'},
      'en': {'Dukovany contract, central': 'Dukovany', 'Dukovany, midpoint of EC bracket': 'EC bracket midpoint', 'Dukovany, top of EC bracket': 'EC bracket top',
             'v7 central capex': 'v7 capex', 'Barakah': 'Barakah', 'Saeul budget': 'Shin Hanul', 'Risk median': 'risk median', 'Vogtle': 'Vogtle'}}
def fig_nuccost(lang):
    it = lang == 'it'; yrs = 'anni' if it else 'years'
    fig, ax = plt.subplots(figsize=(6.6, 3.4)); xs = list(range(2000, 14601, 100))
    for r, y, col, ls, lw in ((0.05, 9, BLUE, '-', 1.6), (0.05, 7, BLUE, (0, (5, 2)), 1.1), (0.05, 15, BLUE, ':', 1.3), (0.07, 9, ORA, '-', 1.6)):
        ax.plot(xs, [mwh(x, r, y) for x in xs], color=col, ls=ls, lw=lw, label=f"{fmt(r * 100, lang)}%, {y} {yrs}")
    done = set()
    for name, k, y, _ in CASES:
        p5, p7 = mwh(k, 0.05, y), mwh(k, 0.07, y)
        ax.plot([k], [p5], 'o', color=INK, ms=3.6, zorder=5); ax.plot([k], [p7], 'o', mfc='white', mec=INK, mew=0.9, ms=3.6, zorder=5)
        if k in done: continue
        done.add(k); ax.axvline(k, color=MUT, lw=0.5, ls=(0, (2, 2)), zorder=0)
        ax.text(k - 60, 4, CN[lang][name], rotation=90, ha='right', va='bottom', fontsize=6.5, color=MUT)
    ax.plot([], [], 'o', color=INK, ms=3.6, label=('casi di costo al 5%' if it else 'cost cases at 5%') + (' (cantiere proprio)' if it else ' (own build time)'))
    ax.plot([], [], 'o', mfc='white', mec=INK, mew=0.9, ms=3.6, label='casi di costo al 7%' if it else 'cost cases at 7%')
    ax.set_xlim(2000, 14600); ax.set_ylim(0, 240); ax.xaxis.set_major_locator(MultipleLocator(2000)); axfmt(ax.xaxis, lang); axfmt(ax.yaxis, lang)
    ax.set_xlabel('Costo di costruzione (€/kW)' if it else 'Overnight construction cost (EUR/kW)'); ax.set_ylabel('Costo del MWh nucleare (€/MWh)' if it else 'Cost of a nuclear MWh (EUR/MWh)')
    ax.grid(axis='y', color=GRID, lw=0.5); ax.set_axisbelow(True); ax.legend(frameon=True, framealpha=0.92, edgecolor='none', fontsize=6.8, loc='upper left')
    save(fig, 'fig_nuccost', lang)

# ---------------------------------------------------------------- 4. saving against fixN (value curves, same rules as tools/report_v8.py)
def curve(cs, rate, infix=''):
    c = {}; f0 = None
    for t, j in R.items():
        m = re.match(rf'v8_{cs}_{rate}_{infix}N(\d+)_h3$', t)
        if m:
            c[int(m.group(1))] = cost(t)
            if int(m.group(1)) > 0: f0 = j['info'].get('NUC_capex_yr_kW', f0)
    if infix and f'v8_{cs}_{rate}_N00_h3' in R: c[0] = cost(f'v8_{cs}_{rate}_N00_h3')
    if cs == 'OB' and not infix:   # N = 0 with SMRs available: the system with SMRs only
        so = [cost(t) for t in (f'v8_OB_{rate}_opt_h3', f'v8_OB_{rate}_nuctop_opt_h3') if t in R and R[t]['res']['N_GW'] < 1e-6]
        if so: c[0] = min(c[0], min(so))
    return dict(sorted(c.items())), f0
def best(c, f0, fx):
    cc = {N: c[N] + (fx - f0) * N / E for N in c}; nb = min(cc, key=cc.get); return nb, cc[nb]
CUR = {}
for cs, rt, infix, lab in (('PI', 'r5', '', 'PI 5%'), ('OB', 'r5', '', 'OB 5%, SMR available'), ('OB', 'r5', 'nosmr_', 'OB 5%, no SMR'),
                           ('PI', 'r7', '', 'PI 7%'), ('OB', 'r7', '', 'OB 7%, SMR available'), ('OB', 'r7', 'nosmr_', 'OB 7%, no SMR')):
    c, f0 = curve(cs, rt, infix); none = cost(f'v8_{cs}_{rt}_N00_h3'); CUR[lab] = (c, f0, none)
    for row in MD['3|' + lab][1:]:   # every cost case of section 3 must be reproduced
        nb, cb = best(c, f0, fixN(num(row[1]), 0.05 if rt == 'r5' else 0.07, int(row[2])))
        check(nb, int(row[4]), 0, f'{lab} {row[0]} best N'); check(round(none - cb, 2), num(row[6]), 1e-9, f'{lab} {row[0]} saving')
def saving(lab, fx): c, f0, none = CUR[lab]; return none - best(c, f0, fx)[1]
CENTRAL = {}
for rt in ('r5', 'r7'):
    for cs in ('PI', 'OB'):
        a, b = f'v8_{cs}_{rt}_opt_h3', f'v8_{cs}_{rt}_N00_h3'; sv = cost(b) - cost(a)
        check(round(sv, 2), num(S1[(cs, rt[1] + '%')][7]), 1e-9, f'central saving {cs} {rt}'); CENTRAL[(cs, rt)] = (R[a]['info']['NUC_capex_yr_kW'], sv)
check(CENTRAL[('PI', 'r5')][0], 911.0, 1e-9, 'central fixN at 5%')
def fig_saving(lang):
    it = lang == 'it'
    t = dict(pi='Primo impianto (PI)' if it else 'First plant (PI)', ob='Obiettivo (OB), senza piccoli reattori' if it else 'Target (OB), no SMRs',
             obs='Obiettivo (OB), con piccoli reattori disponibili' if it else 'Target (OB), SMRs available', opt='ottimo libero' if it else 'free optimum')
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.6), sharey=True)
    for ax, rt, r, ttl in ((axs[0], 'r5', 0.05, 'capitale al 5%' if it else '5% cost of capital'), (axs[1], 'r7', 0.07, 'capitale al 7%' if it else '7% cost of capital')):
        lo, hi = (380, 1400) if rt == 'r5' else (480, 1700); xs = list(range(lo, hi + 1, 2))
        for lab, col, ls, name in ((f'PI {rt[1]}%', BLUE, '-', t['pi']), (f'OB {rt[1]}%, no SMR', ORA, '-', t['ob']), (f'OB {rt[1]}%, SMR available', ORA, ':', t['obs'])):
            ax.plot(xs, [saving(lab, x) for x in xs], color=col, ls=ls, lw=1.6 if ls == '-' else 1.1, label=name)
        for name, key in (('Dukovany contract, central', 'cen'), ('Dukovany, top of EC bracket', 'top'), ('Vogtle', 'vog'), ('Barakah', 'bar')):
            k, y = next((c[1], c[2]) for c in CASES if c[0] == name); fx = fixN(k, r, y)
            ax.axvline(fx, color=INK if key == 'cen' else MUT, lw=0.9 if key == 'cen' else 0.5, ls='-' if key == 'cen' else (0, (4, 3)), zorder=0)
            txt = {'cen': 'Dukovany, contratto' if it else 'Dukovany contract', 'top': 'massimo intervallo ufficiale' if it else 'top of EC bracket', 'vog': 'Vogtle', 'bar': 'Barakah'}[key]
            ax.text(fx + 12, 57, f"{txt} {fmt(fx, lang)}", rotation=90, ha='left', va='top', fontsize=6.5, color=INK if key == 'cen' else MUT)
        for cs, mk, col in (('PI', 'D', BLUE), ('OB', 's', ORA)):
            fx, sv = CENTRAL[(cs, rt)]
            ax.plot([fx], [sv], mk, color=col, mec='white', mew=0.6, ms=5.5, zorder=6)
            ax.text(fx - 14, sv + (1.6 if cs == 'PI' else -1.6), f"{cs} {fmt(sv, lang, 2)}", ha='right', va='center', fontsize=6.8, color=col,
                    bbox=dict(fc='white', ec='none', pad=0.3, alpha=0.85))
        ax.set_title(ttl, fontsize=8.5, color=INK, loc='left'); ax.set_xlim(lo, hi); ax.set_ylim(0, 58); axfmt(ax.xaxis, lang)
        ax.set_xlabel('Costo fisso annuo del nucleare (€/kW all\'anno)' if it else 'Nuclear annual fixed cost fixN (EUR/kW-yr)'); ax.grid(axis='y', color=GRID, lw=0.5); ax.set_axisbelow(True)
    axs[0].set_ylabel('Risparmio (€/MWh)' if it else 'Saving (EUR/MWh)'); axfmt(axs[0].yaxis, lang)
    h, l = axs[0].get_legend_handles_labels()
    h += [plt.Line2D([], [], marker='D', color=MUT, ls='none', ms=4.5)]; l += [t['opt']]
    fig.legend(h, l, frameon=False, fontsize=6.8, ncol=4, loc='lower center', bbox_to_anchor=(0.5, 0.0), handlelength=1.8, columnspacing=1.2)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, 'fig_saving', lang, tight=False)

for lang in ('it', 'en'): fig_months(lang); fig_systems(lang); fig_nuccost(lang); fig_saving(lang)
print('figures written to', FD)
print('cost of a nuclear MWh at 90% availability (EUR/MWh):', {n: (round(mwh(k, 0.05, y), 1), round(mwh(k, 0.07, y), 1)) for n, k, y, _ in CASES})
print('central saving:', {f'{k[0]} {k[1]}': (v[0], round(v[1], 2)) for k, v in CENTRAL.items()})
