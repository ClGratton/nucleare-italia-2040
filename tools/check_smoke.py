#!/usr/bin/env python3
"""Compare a smoke-test run with the reference stored in tests/expected_smoke_h12.jsonl.
Usage: python tools/check_smoke.py results/smoke_runs.jsonl
The system cost must match within 0.02 EUR/MWh. Nuclear capacity may differ by a few tenths of GW between solver versions because the optimum is flat."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p): return {json.loads(l)['tag']: json.loads(l)['res'] for l in open(p) if l.strip()}
ref = load(os.path.join(ROOT, 'tests', 'expected_smoke_h12.jsonl')); new = load(sys.argv[1]); ok = True
for t, r in ref.items():
    if t not in new: print('MISSING', t); ok = False; continue
    dc = abs(new[t]['cost_new'] - r['cost_new']); dn = abs(new[t]['N_GW'] - r['N_GW'])
    flag = 'OK' if dc <= 0.02 else 'COST MISMATCH'
    if dc > 0.02: ok = False
    print(f"{t}: cost {new[t]['cost_new']} (ref {r['cost_new']}), N {new[t]['N_GW']} (ref {r['N_GW']}), status {new[t]['status']}: {flag}" + ('' if dn <= 0.5 else '  [N differs by more than 0.5 GW: report it]'))
print('SMOKE TEST PASSED' if ok else 'SMOKE TEST FAILED'); sys.exit(0 if ok else 1)
