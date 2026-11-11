#!/usr/bin/env python3
"""Run a list of model jobs in parallel and append each result to a JSON-lines file.

Usage:  python tools/run_jobs.py jobs/<file>.json [--workers N] [--out results/v8_runs.jsonl] [--only SUBSTR]

A job file is a JSON list of objects {"tag": "...", "spec": {...}, "R": 0.07 (optional real discount rate)}.
Each job is one process (model/run7.py). Jobs whose tag is already in the output file are skipped, so the
command can be stopped and restarted at any time. One line is appended per finished job.
"""
import argparse, json, os, subprocess, sys, time, threading
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
LOCK = threading.Lock()

def done(out):
    d = set()
    if os.path.exists(out):
        for l in open(out):
            try: d.add(json.loads(l)['tag'])
            except Exception: pass
    return d

def run_one(job, out):
    tag = job['tag']; spec = dict(job['spec'], tag=tag); t0 = time.time()
    env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    if job.get('R'): env['V7_R'] = str(job['R'])
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'model', 'run7.py'), json.dumps(spec)], capture_output=True, text=True, env=env)
    line = [l for l in p.stdout.strip().split('\n') if l.startswith('{')]
    if p.returncode != 0 or not line:
        with LOCK: print(f"FAILED {tag}: {p.stderr[-600:]}", flush=True)
        return
    j = json.loads(line[-1]); j['sec'] = round(time.time() - t0); j['spec'] = spec; j['R'] = job.get('R')
    r = j['res']
    with LOCK:
        with open(out, 'a') as f: f.write(json.dumps(j) + '\n')
        print(f"{tag}  cost {r['cost_new']}  N {r['N_GW']} GW  share {r['sh_nuc']}  {r['status']}  {j['sec']} s", flush=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('jobs'); ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) // 2))
    ap.add_argument('--out', default=os.path.join(ROOT, 'results', 'v8_runs.jsonl')); ap.add_argument('--only', default=None)
    a = ap.parse_args()
    jobs = json.load(open(a.jobs)); d = done(a.out)
    todo = [j for j in jobs if j['tag'] not in d and (a.only is None or a.only in j['tag'])]
    print(f"{len(jobs)} jobs in file, {len(jobs) - len(todo)} already done or filtered, {len(todo)} to run with {a.workers} workers", flush=True)
    it = iter(todo); lk = threading.Lock()
    def worker():
        while True:
            with lk: job = next(it, None)
            if job is None: return
            run_one(job, a.out)
    th = [threading.Thread(target=worker) for _ in range(a.workers)]
    [t.start() for t in th]; [t.join() for t in th]
    print('all done', flush=True)

if __name__ == '__main__': main()
