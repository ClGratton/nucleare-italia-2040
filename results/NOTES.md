# Run notes

## Machine
- CPU: AMD Ryzen 7 9700X, 8 physical cores
- RAM: 16 GB installed (15.06 GB visible to Windows)
- OS: Windows 11 Home 10.0.22631
- Python 3.12.4, numpy 2.5.4, scipy 1.18.1, highspy 1.16.0

## Smoke test
- `jobs/smoke_h12.json`, 2 workers, 183 s: `SMOKE TEST PASSED` (all four values equal to the reference).

## batch2_optimum_h3 (4 runs)
- Started with 1 worker (free memory 3 GB at the time, so floor(3/3) = 1).
- `v8_PI_r5_opt_h3` finished in 1347 s.
- The machine went to sleep during the night, so `v8_OB_r5_opt_h3` stopped for hours. The batch was stopped and restarted with the same command and 3 workers, after memory was freed (9.3 GB available, so floor(9.3/3) = 3). The finished run was skipped; the interrupted run started again from scratch.
- Run times: PI_r7 2182 s, OB_r7 2726 s, OB_r5 2748 s (3 runs in parallel).
- All 4 runs Optimal, no `FAILED` lines. `check_results.py`: 4 runs checked, 0 problems.
- Observation, not a judgement: `v8_OB_r7_opt_h3` has N = 0.0 GW (no nuclear at the optimum with r = 7%).
- Batch time on the clock: about 1 h of computing (the pause during sleep is not counted).

## batch1_value_curve_h3 (48 runs)
- Started with 2 workers (8.66 GB available).
- 10 runs done at 13:33 (PI r5, N00 to N36), all Optimal, 1095-1652 s each, no `FAILED` lines. `check_results.py`: 14 runs checked, 0 problems.
- After the runbook change (924a421, free memory / 2), restarted at 13:36 with 4 workers (8.29 GB available); the 2 interrupted runs start again.
- Restarted again at 14:33 to re-apply the rule: 8.42 GB free after stopping, so floor(8.42/2) = 4 workers (same number). 14 runs done; the 4 interrupted runs start again.
- 20 runs done at 16:24, all Optimal, no `FAILED` lines. With 4 workers each OB run takes 3092-3539 s (PI runs took 1095-1652 s with 2 workers; different run types, so not a like-for-like comparison). `check_results.py`: 24 runs checked, 0 problems.
- 30 runs done at 17:52, all Optimal, no `FAILED` lines (PI r7 runs: 2165-2728 s with 4 workers). `check_results.py`: 34 runs checked, 0 problems.
- Restarted at 17:53 with 6 workers at the operator's request (8.05 GB free after stopping; the runbook rule would give floor(8.05/2) = 4). 30 runs done and skipped; the 4 interrupted runs (PI r7 N24-N36, 1-13 min in) start again.
- From about 19:40 an Android emulator (about 1.7 GB) ran on the same machine; available memory fell to 0.25-0.5 GB and Windows paged heavily. The OB r7 runs took 5895-7278 s instead of about 3000 s; no run failed.
- 40 runs done at 20:33, all Optimal, no `FAILED` lines. `check_results.py`: 44 runs checked, 0 problems.
- Batch finished at about 21:55: 48/48 runs, all Optimal, no `FAILED` lines. Last OB r7 runs: 2720-7643 s (slowed by the memory shortage above). `check_results.py`: 52 runs checked, 0 problems.
- Batch time on the clock: about 10 h 15 min (11:40 to 21:55, including the restarts).

## batch3_variants_h3 (38 runs)
- Run one variant group at a time with `--only <group>` (same command otherwise), so that the 4 `wx8` runs get their own worker count: free memory / 2 for the other groups, free memory / 3 for `wx8`, measured before each group.
- Workers per group so far: exp0 1 (an Android emulator was using memory), exppar 3, x10 2, xfree 2, v7imp 4, vreweek 4, macse 4, nuc 3, wx8 2 (free memory / 3).
- 10 runs done at 01:19 (exp0, exppar, x10 PI opt), all Optimal, no `FAILED` lines. `check_results.py`: 62 runs checked, 0 problems.
- 20 runs done at 03:39 (up to v7imp), all Optimal, no `FAILED` lines. `check_results.py`: 72 runs checked, 0 problems.
- 30 runs done at 05:59 (up to nuc), all Optimal, no `FAILED` lines. `check_results.py`: 82 runs checked, 0 problems.
- Batch finished at about 12:20: 38/38 runs, all Optimal, no `FAILED` lines. The wx8 runs are the slowest: PI 5635 and 7812 s, OB 12496 and 13949 s (2 in parallel). `check_results.py`: 90 runs checked, 0 problems.
- Batch time on the clock: about 14 h 20 min (22:00 to 12:20).

## After the three batches
- `git pull` after batch 3: the new job file is `jobs/batch5_ob_without_smr_h3.json` (commit 2fd26c3). `batch4_value_curve_h6.json` was already there at the start and its results are already in `results/v8_runs_h6.jsonl`, so it is not run here.

## batch5_ob_without_smr_h3 (20 runs)
- Started at 12:25 with 3 workers (7.25 GB available).
- At about 13:35 `run_jobs.py` printed `FAILED v8_OB_r5_nosmr_N20_h3:` with an empty stderr tail (so run7.py ended without a result line and without an error message). Available memory at that moment: 5.0 GB; no memory event in the Windows System log. It will be retried once, after the rest of the batch, with the same command.
- Observation for the model owner, not checked further: the nosmr runs at N = 16, 24, 28, 32, 36 GW give exactly the same cost as the batch-1 OB r5 runs at the same N (107.532, 109.024, 111.202, 113.98, 117.292), while N = 4, 8, 12 differ (e.g. N04: 111.76 here, 108.239 in batch 1). This would happen if batch-1 runs used no SMRs from 16 GW up; I have not checked the capacity mix.
- The machine rebooted without a clean shutdown in the afternoon (Windows Kernel-Power event 41 at 15:33; event 6008 dates the unexpected stop at 14:23). 8 runs had finished; the runs in progress were lost. Restarted at 18:5x with the same command; this restart also counts as the single retry of `v8_OB_r5_nosmr_N20_h3`. Only 2.91 GB were free after the reboot (a Gradle build and other programs were running), so 1 worker.
- The retry of `v8_OB_r5_nosmr_N20_h3` succeeded: Optimal, 1491 s. Its cost (107.911) and that of `v8_OB_r5_nosmr_opt_h3` (107.53, N 15.65 GW) are again identical to batch 1 OB r5 N20 and batch 2 OB r5 opt.
- 10 runs done at 19:47. `check_results.py`: 100 runs checked, 0 problems. Restarted with 2 workers (4.59 GB free); the run started 1 minute earlier starts again.
- Batch finished at about 23:35: 20/20 runs, all Optimal; one `FAILED` (N20 r5, see above) that succeeded on its single retry. `check_results.py`: 110 runs checked, 0 problems.
- The r7 nosmr runs show the same pattern as r5: from 12 GW up the cost equals batch 1 OB r7 (131.491, 132.516, 134.598, 137.5, 141.778, 146.689, 152.289), at 4 and 8 GW it is higher (132.436 and 131.744 against 131.261 and 131.359).
- `v8_OB_r7_nosmr_opt_h3`: cost 131.434, N 11.044 GW, against batch 2 `v8_OB_r7_opt_h3` cost 131.164, N 0.0 GW (with SMRs available).
- `v8_OB_r7_nosmr_N20_h3` took 6771 s, about three times the neighbouring runs; no error.
