#!/usr/bin/env python3
"""Value curve of nuclear from the runs with nuclear capacity fixed at N GW.

Usage: python tools/value_curve.py results/v8_runs_h6.jsonl [--step 6] [--rate r5]

For each case (PI, OB) it prints:
- the system cost C(N) in EUR per MWh of demand not met by existing hydro;
- the marginal value of nuclear capacity between consecutive N, in EUR/kW-yr: the annual fixed cost at which the system is
  indifferent between N1 and N2. It does not depend on any assumption about the cost of nuclear:
      v(N1,N2) = f0 - [C(N2) - C(N1)] * E / (N2 - N1)
  with f0 the fixed cost used in the runs and E the energy denominator;
- for a list of cost cases, the optimal capacity (on the grid of N), its cost, the saving against no nuclear, and the range of
  capacities whose system cost is within 1% of the minimum.
"""
import argparse, json, re, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'model'))

def crf(r, n): return r * (1 + r) ** n / ((1 + r) ** n - 1)
def idc(r, y): return sum((1 + r) ** (y - k - 0.5) for k in range(y)) / y
def fixN(capex, r, y, life=60, om_fix_MWh=27.75, grid=2.0, av=0.90):
    """Annual fixed cost of nuclear, EUR/kW-yr (same formula as model/spec7.py)."""
    return capex * idc(r, y) * crf(r, life) + om_fix_MWh * 0.9 * 8.76 + grid * av * 8.76 * crf(r, 40) / crf(0.05, 40)

CASES = [  # name, overnight capex EUR/kW, construction years
    ('Dukovany contract, central', 10200, 9), ('Dukovany, 7 years', 10200, 7), ('Dukovany, midpoint of EC bracket', 11400, 9), ('Dukovany, top of EC bracket', 12700, 9),
    ('v7 central capex', 8540, 7), ('Barakah', 5500, 8), ('Saeul budget', 2965, 8), ('Risk median', 9680, 15), ('Vogtle', 13400, 10)]

def load(path, step, rate, infix=''):
    C = {}; f0 = {}; E = {}
    for l in open(path):
        try: j = json.loads(l)
        except Exception: continue
        m = re.match(rf'v8_(PI|OB)_{rate}_{infix}N(\d+)_h{step}$', j['tag']) or (infix and re.match(rf'v8_(PI|OB)_{rate}_N(00)_h{step}$', j['tag']))
        if not m: continue
        cs, N = m.group(1), int(m.group(2)); r = j['res']
        C.setdefault(cs, {})[N] = r['cost_new']; E[cs] = r['obj_EUR_yr'] / r['cost_new'] / 1e6
        if N > 0: f0[cs] = j['info']['NUC_capex_yr_kW']
    return C, f0, E

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('path'); ap.add_argument('--step', type=int, default=6); ap.add_argument('--rate', default='r5'); ap.add_argument('--infix', default='', help="e.g. nosmr_ for the runs without small modular reactors")
    a = ap.parse_args(); r = 0.05 if a.rate == 'r5' else 0.07
    C, f0, E = load(a.path, a.step, a.rate, a.infix)
    for cs in sorted(C):
        if cs not in f0: continue
        Ns = sorted(C[cs]); c = C[cs]; e = E[cs]; f = f0[cs]
        print(f"\n== {cs}, {a.rate}, {a.step} h; runs made at fixN {f:.1f} EUR/kW-yr; energy {e:.1f} TWh ==")
        print("N GW   cost EUR/MWh   marginal value of the next block, EUR/kW-yr")
        for i, N in enumerate(Ns):
            v = '' if i == len(Ns) - 1 else f"{f - (c[Ns[i + 1]] - c[N]) * e / (Ns[i + 1] - N):8.0f}  ({N}-{Ns[i + 1]} GW)"
            print(f"{N:4d}   {c[N]:8.3f}      {v}")
        print("\ncase                              capex   y   fixN   best N   cost    saving vs N=0   within 1% of minimum")
        for name, k, y in CASES:
            fx = fixN(k, r, y); cc = {N: c[N] + (fx - f) * N / e for N in Ns}; nb = min(cc, key=cc.get)
            near = [N for N in Ns if cc[N] <= cc[nb] * 1.01]
            print(f"{name:32s} {k:6d} {y:3d} {fx:6.0f} {nb:6d}   {cc[nb]:7.2f}   {cc[0] - cc[nb]:6.2f}          {min(near)}-{max(near)} GW")

if __name__ == '__main__': main()
