# nucleare-italia-2040

How much nuclear capacity the least-cost Italian power system with zero direct emissions contains for a 2040 demand of 400 TWh.
Linear capacity-expansion model (HiGHS), one node, four weather years (2016-2019) optimised together, 3-hour step.

Author: Claudio Gratton. Version 8, November 2026.

## Documents

- `docs/white_paper/white_paper_nucleare_italia_v8.pdf`: white paper in Italian (source: `content.py`, `build.py`).
- `docs/preprint/preprint_nuclear_italy_v8.pdf`: preprint in English (LaTeX sources in the same folder).
- `docs/results_v8.md`: every table of results, generated from the runs by `tools/report_v8.py`.
- `docs/v8_facts.md`: derivations and decisions behind the numbers in the documents.
- `docs/audit/`: audit of code and inputs, sources with URLs, and the register of every error found in the project.

## Central results (3-hour step, 5% real cost of capital)

| Case | Nuclear | Share of demand | Saving against no nuclear |
|---|---|---|---|
| PI: technologies without commercial plants at first-plant cost | 23.2 GW | 44.5% | 13.35 EUR/MWh |
| OB: the same technologies at their target cost | 15.7 GW | 30.5% | 6.86 EUR/MWh |

At 7%: 15.6 GW (PI) and 11.1 GW (OB, all small modular reactors). The optimum is flat: in PI at 5% every capacity between 16 and 28 GW
costs within 1% of the minimum. The recommendation in the documents is about 15 GW, with the option to grow to about 23 GW.

## Method

One cost rule for every technology, nuclear included, at today's prices:

    annual cost = overnight capex (development and grid connection included, contingency and subsidies excluded)
                  x interest during construction (real rate, build time)
                  x capital recovery factor (real rate, technical life)
                  + fixed O&M

Real 2025 euros, net capacity. Central nuclear cost: Dukovany contract plus owner's costs, 10,200 EUR/kW net, 9-year build, 60-year life.
Trade: balanced annual swap with neighbours, no foreign capacity in the three critical weeks of each year.

The result is a value curve. Runs with nuclear capacity fixed at N give the system cost C(N); for any nuclear fixed cost f' the cost is
C(N) + (f' - f) N / E, so the optimal capacity for every nuclear cost case is read from the same runs (`tools/value_curve.py`).

## Layout

    model/      hl7.py (LP), spec7.py (technology data to LP units), hl5.py (demand and profiles), blocks_v6.py (PV and wind supply curves),
                run7.py (one run), techs_v8.json (inputs with sources), techs_v8_grid350.json (grid-charge check), techs_v7.json (previous inputs)
    data/       inputs_main.npz (load 2016-2019, PECD capacity factors for 8 weather years, heating degree days)
    jobs/       job lists, written by tools/make_jobs.py
    tools/      run_jobs.py (parallel, resumable), check_smoke.py, check_results.py, make_jobs.py, value_curve.py, report_v8.py
    results/    v8_runs.jsonl (3-hour runs), v8_runs_h6.jsonl (6-hour runs), v8_runs_review.jsonl (check runs), legacy/v7_results.jsonl
    tests/      expected_smoke_h12.jsonl
    docs/       documents, results, audit

## Run

    python -m venv .venv && . .venv/bin/activate        (Windows: .venv\Scripts\activate)
    pip install -r requirements.txt
    python tools/run_jobs.py jobs/smoke_h12.json --workers 2 --out results/smoke_runs.jsonl
    python tools/check_smoke.py results/smoke_runs.jsonl
    python tools/run_jobs.py jobs/batch2_optimum_h3.json --workers 4
    python tools/report_v8.py

`run_jobs.py` skips runs already in the output file, so it can be stopped and restarted.
One 3-hour run takes about 1.3 GB of memory, one core and 20 to 60 minutes.
