#!/usr/bin/env python3
"""Rerun every job with the corrected inputs (21 Nov 2026).

Usage (from the repository folder):
    python tools/rerun_all.py --workers 8

What it does:
1. Moves the result files of the runs made before the input corrections to results/legacy/before_input_corrections/
   (only the first time; later calls resume).
2. Runs the smoke test at 12 hours and stops if it does not match tests/expected_smoke_h12.jsonl.
3. Runs every 3-hour and 6-hour batch into the result files the report reads. run_jobs.py skips runs already in
   the output file, so the script can be stopped and started again.

Each 3-hour run takes about 1.3 GB of memory and one core, 20 to 60 minutes. Choose --workers so that
workers x 1.5 GB fits in free memory and workers <= physical cores.
"""
import argparse, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, 'results')
LEG = os.path.join(R, 'legacy', 'before_input_corrections')
OLD = ['v8_runs.jsonl', 'v8_runs_h6.jsonl', 'v8_runs_review.jsonl']

# batch file -> output file (all in results/)
BATCHES = [
    ('batch2_optimum_h3.json', 'v8_runs.jsonl'),
    ('batch1_value_curve_h3.json', 'v8_runs.jsonl'),
    ('batch5_ob_without_smr_h3.json', 'v8_runs.jsonl'),
    ('batch3_variants_h3.json', 'v8_runs.jsonl'),
    ('batch6_review_checks_h3.json', 'v8_runs_review.jsonl'),
    ('batch8_comparison_h3.json', 'v8_runs_extra.jsonl'),
    ('batch9_sensitivity_h3.json', 'v8_runs_extra.jsonl'),
    ('batch4_value_curve_h6.json', 'v8_runs_h6.jsonl'),
]


def run(args):
    print('>', ' '.join(args), flush=True)
    return subprocess.call([sys.executable] + args, cwd=ROOT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) // 2))
    a = ap.parse_args()

    os.makedirs(LEG, exist_ok=True)
    for f in OLD:
        src, dst = os.path.join(R, f), os.path.join(LEG, f)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.move(src, dst); print('moved', f, 'to', os.path.relpath(LEG, ROOT))

    smoke = os.path.join(R, 'smoke_runs.jsonl')
    if os.path.exists(smoke): os.remove(smoke)
    if run(['tools/run_jobs.py', 'jobs/smoke_h12.json', '--workers', str(min(a.workers, 4)), '--out', smoke]) != 0 or \
       run(['tools/check_smoke.py', smoke]) != 0:
        sys.exit('Smoke test failed: stop and report the output.')

    for jobs, out in BATCHES:
        if run(['tools/run_jobs.py', os.path.join('jobs', jobs), '--workers', str(a.workers), '--out', os.path.join(R, out)]) != 0:
            sys.exit(f'{jobs} did not finish; run the same command again to resume.')
    for out in ('v8_runs.jsonl', 'v8_runs_h6.jsonl', 'v8_runs_review.jsonl', 'v8_runs_extra.jsonl'):
        run(['tools/check_results.py', os.path.join(R, out)])
    print('All runs done. Commit results/ and push.')


if __name__ == '__main__':
    main()
