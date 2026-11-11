#!/usr/bin/env python3
"""Consistency checks on a results file. Usage: python tools/check_results.py results/v8_runs.jsonl
1. Every run is Optimal. 2. Balanced trade where required. 3. Value curve: the cost with fixed nuclear capacity N must be convex in N
(an LP property); a violation means a solver or bookkeeping error. 4. The free optimum must not cost more than any fixed-N run of the same case."""
import json, re, sys
R = {}
for l in open(sys.argv[1]):
    try: j = json.loads(l); R[j['tag']] = j
    except Exception: pass
bad = 0
for t, j in R.items():
    r = j['res']
    if r['status'] != 'Optimal': print('NOT OPTIMAL', t, r['status']); bad += 1
    ex = j['spec'].get('export') or {}
    if ex.get('X') == 0.0 and ex.get('X_exp') == 0.0 and abs(r.get('import_TWh', 0) - r.get('export_TWh', 0)) > 0.01: print('TRADE NOT BALANCED', t); bad += 1
groups = {}
for t, j in R.items():
    m = re.match(r'(v8_(?:PI|OB)_r\d)_N(\d+)_(h\d+)$', t)
    if m: groups.setdefault((m.group(1), m.group(3)), []).append((int(m.group(2)), j['res']['obj_EUR_yr']))
for k, pts in groups.items():
    pts.sort()
    for (n0, c0), (n1, c1), (n2, c2) in zip(pts, pts[1:], pts[2:]):
        s1 = (c1 - c0) / (n1 - n0); s2 = (c2 - c1) / (n2 - n1)
        if s2 < s1 - 1e-4 * abs(c1) / max(n1, 1): print('NOT CONVEX', k, n0, n1, n2, round(s1 / 1e6, 2), round(s2 / 1e6, 2)); bad += 1
    o = R.get(f"{k[0]}_opt_{k[1]}")
    if o and any(o['res']['obj_EUR_yr'] > c * (1 + 1e-6) for _, c in pts): print('OPTIMUM ABOVE A FIXED-N RUN', k); bad += 1
print(len(R), 'runs checked,', bad, 'problems'); sys.exit(1 if bad else 0)
