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
