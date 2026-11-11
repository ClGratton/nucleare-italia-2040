# Runbook for the machine that computes the v8 results

Goal: run the job lists in `jobs/` and push the result file. Do not change anything under `model/`, `data/`, `jobs/` or `tools/`.
If something looks wrong, write it in `results/NOTES.md`, push it and stop: the model owner fixes it on the other side.

## 1. Set up

1. Python 3.11 or newer. Create a virtual environment in `.venv` and install `requirements.txt` (numpy, scipy, highspy).
2. Check the machine: number of physical cores and free memory. Workers = physical cores minus one, and no more than free memory in GB divided by 3.

## 2. Smoke test (about 5 minutes)

    python tools/run_jobs.py jobs/smoke_h12.json --workers 2 --out results/smoke_runs.jsonl
    python tools/check_smoke.py results/smoke_runs.jsonl

It must print `SMOKE TEST PASSED`. If it does not, write the full output in `results/NOTES.md`, commit, push and stop.

## 3. Batches, in this order

    python tools/run_jobs.py jobs/batch2_optimum_h3.json --workers W        (4 runs: the central results)
    python tools/run_jobs.py jobs/batch1_value_curve_h3.json --workers W    (48 runs: cost with nuclear fixed at 0-48 GW, 5% and 7%)
    python tools/run_jobs.py jobs/batch3_variants_h3.json --workers W       (38 runs: one assumption changed at a time; the wx8 runs need twice the memory)

All of them append to `results/v8_runs.jsonl`. A run that is already in that file is skipped, so a batch can be interrupted and restarted with the same command.
Expected time per run at the 3-hour step: 15 to 60 minutes on one core.

After each batch:

    python tools/check_results.py results/v8_runs.jsonl
    git add results/v8_runs.jsonl results/NOTES.md
    git commit -m "v8 runs: <batch name>, <number> runs"
    git pull --rebase origin main
    git push origin main

Also commit and push after every 10 finished runs of the long batches, so partial results are available early.
Write in `results/NOTES.md`: machine (CPU, cores, RAM, OS), Python and highspy versions, workers used, time per batch, any `FAILED` line printed by `run_jobs.py`
and any problem reported by `check_results.py`. A failed run is not retried more than once; report it and go on with the others.

## 4. When all three batches are pushed

Check `jobs/` after a `git pull`: if new job files have appeared (for example `batch5_*.json`), run them the same way. Otherwise stop and report.
