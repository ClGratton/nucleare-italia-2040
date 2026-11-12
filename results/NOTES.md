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
