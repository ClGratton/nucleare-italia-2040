# nucleare-italia-2040

Least-cost zero-direct-emission Italian power system for a 2040 demand of 400 TWh, and the nuclear capacity it contains.
Linear capacity-expansion model (HiGHS), one node, four weather years optimised together, steps of 3, 6 or 12 hours.

**Status (11 November 2026): model and inputs corrected after a full audit; the v8 results are being recomputed.**
The numbers in the white paper and preprint drafts under `docs/drafts/` are those of v7 and are superseded.

## What changed in v8

An independent audit of the code, of every cost input and of the data (`docs/audit/audit_v8_findings.md`) found errors in both directions.
The full history of the project's errors and of the headline number is in `docs/audit/audit_history.md`.

One rule now applies to every technology, nuclear included:

    annual cost = overnight capex (development and grid connection included, contingency and subsidies excluded)
                  x interest during construction (real rate, build time)
                  x capital recovery factor (real rate, technical life)
                  + fixed O&M

in real 2025 euros, with costs of plants contracted or built in 2024-2026, net capacity and realistic output.
Auction prices (FER-X, MACSE) are no longer used as costs. Sources with URLs: `docs/audit/v8_symmetric_costs.md` and the `src` fields of `model/techs_v8.json`.

| Item | v7 | v8 |
|---|---|---|
| Nuclear central case | 8,540 EUR/kW (gross MW, fuel deducted), 7 y, 80 y, O&M 32 EUR/MWh, availability 0.92 | 10,200 EUR/kW net (EPC + owner's costs, EC decision SA.117794), 9 y, 60 y, OPEX 40 EUR/MWh, availability 0.90 |
| Nuclear fixed cost | 670 EUR/kW-yr at 5% | 911 at 5%, 1,239 at 7% |
| Ground PV | FER-X price x 1,375 h = 58 EUR/kW-yr (implied 681 EUR/kW) | 950 EUR/kWp, O&M 20, 25 y, degradation 0.5%/yr = 89 EUR/kWp-yr |
| Agrivoltaic PV | implied 908 EUR/kW | 1,200 EUR/kWp |
| Onshore wind | about 150 EUR/kW-yr | 1,600 EUR/kW, O&M 40 = 159 EUR/kW-yr |
| Offshore wind | 2040-2050 estimates with learning | today's estimates: 3,400 (fixed), 4,750 (floating) EUR/kW |
| Batteries | MACSE award price, 11,466 EUR/MWh-yr | ARERA 332/2026 reference, 168.6 EUR/kWh usable, 21,547 EUR/MWh-yr |
| Electrolyser (first plant) | 1,819 EUR/kW | 2,056 EUR/kW (IEA 2025) |
| Interest during construction, fixed O&M | nuclear and gas CCS only | every technology |
| 100-hour storage in the first-plant case | maker's target | off (no observed cost) |
| Grid threshold 137 GW | counted new plants only (bug) | total wind + PV stock |
| 7% runs | wind and grid charge not scaled (bug) | every capital cost follows the rate |
| Reserve requirement | peak of the step-averaged load (changes with the step) | peak of the 3-hour data at every step |
| Trade | imports at 115.94, exports earn 0, exports up to import capacity, critical weeks by low PV+wind | balanced annual swap, imports 115.94, exports 61.07, Terna export limit, no imports in the 3 highest residual-load weeks per year |
| Existing PV output | 1,304 h | scaled to the observed fleet (1,117 h, GSE 2025) |

With the v7 settings the modified code reproduces a stored v7 result exactly (`ss0_PI_670_h12`: 86.167 EUR/MWh, 17.756 GW).

## Layout

    model/      hl7.py (LP), spec7.py (technology data -> LP units), hl5.py (demand and profiles), blocks_v6.py (PV and wind supply curves),
                run7.py (one run), techs_v8.json (inputs with sources), techs_v7.json (superseded inputs, kept for regression)
    data/       inputs_main.npz (load 2016-2019, PECD capacity factors for 8 weather years, heating degree days; 3-hour resolution)
    jobs/       job lists (JSON), written by tools/make_jobs.py
    tools/      run_jobs.py (parallel, resumable), check_smoke.py, check_results.py, make_jobs.py
    results/    v8_runs.jsonl (one JSON line per run), legacy/v7_results.jsonl
    tests/      expected_smoke_h12.jsonl
    docs/       RUNBOOK.md, audit/, drafts/

## Run

    python -m venv .venv && . .venv/bin/activate        (Windows: .venv\Scripts\activate)
    pip install -r requirements.txt
    python tools/run_jobs.py jobs/smoke_h12.json --workers 2 --out results/smoke_runs.jsonl
    python tools/check_smoke.py results/smoke_runs.jsonl
    python tools/run_jobs.py jobs/batch2_optimum_h3.json --workers 4

`run_jobs.py` skips the tags already present in the output file, so it can be stopped and restarted.
One 3-hour run takes about 1.3 GB of memory and one core; the 8-weather-year runs about twice as much.

## Method in one paragraph

The result is not one number but a function. Runs with nuclear capacity fixed at N give the system cost C(N); for any nuclear
fixed cost f' the cost is C(N) + (f' - f) N, so the optimal capacity for every cost case (Dukovany, Barakah, Vogtle, ...) is read
from the same runs, together with how flat the optimum is. In v7 the optimum was flat: at the central cost, capacities between
about 13 and 28 GW were within 1% of the minimum system cost, which is why small corrections moved the headline number by many GW.

## Known limits (see docs/audit)

One node; four weather years (2016-2019) with an eight-year stress variant; 3-hour data (hourly rebuild pending); hydro with the same
monthly budget every year; neighbours are not simulated; build times of several minor technologies are assumptions; distribution-grid
reinforcement is not costed; existing wind is kept at O&M cost although it will be beyond its life in 2040.
