# v8 facts for the documents (13 November 2026)

Single source for the white paper (Italian) and the preprint (English). Every number in the documents must come from this file,
from `docs/results_v8.md` (generated from the runs), from `model/techs_v8.json` (inputs with sources) or from `docs/audit/*`.
Nothing from the v7 drafts may be reused without checking it here: the v7 numbers are superseded.

## 1. Question and answer in one paragraph

How much nuclear does the least-cost zero-direct-emission Italian power system contain, for a 2040 demand of 400 TWh?
With one cost rule for every technology, the Dukovany costs as notified by the Czech state to the European Commission, and a
system that does not lean on other countries, the 3-hour model gives 23.2 GW (44.5% of demand) when technologies without
commercial plants are at first-plant costs (PI), and 15.7 GW (30.5%) when they are at their makers' target costs (OB), at a
5% real cost of capital. At 7%: 15.6 GW (PI) and 11.1 GW (OB, all small modular reactors). The optimum is flat: in PI at 5%
every capacity between 16 and 28 GW costs within 1% of the minimum. About 15 GW is in or near the optimum in every case except
OB at 7% (11 GW), OB with nuclear at the top of the official cost bracket and no small reactors (8 GW), and the variants that rely on
foreign capacity in the critical weeks (7 to 12 GW).

## 2. Model (unchanged structure, corrected inputs)

- Linear capacity-expansion model, HiGHS, one node, zero direct emissions, one fleet for four weather years (2016-2019) optimised together, 3-hour step (11,688 steps); about 350,000 variables and 440,000 constraints per run.
- Demand 400 TWh in 2040: 338 base + 15 heat pumps + 47 electric vehicles; hourly Terna load of 2016-2019 paired with the same weather year (PECD capacity factors). Existing hydropower 15 GW, 43.4 TWh, is given; costs are per MWh of the remaining 356.6 TWh.
- Technologies as decision variables: PV (ground, agrivoltaic, industrial and other roofs, by zone, finite land), onshore and offshore wind (finite blocks), large nuclear, small modular reactors, batteries, hydrogen (electrolyser, underground storage, turbine), compressed air, 100-hour storage, pumped hydro, new hydro, geothermal, bioenergy, solar thermal (CSP), interruptible load, smart charging, interconnection.
- PI and OB: technologies without commercial plants (hydrogen chain, compressed air, CSP at scale, SMR, 100-hour storage, enhanced geothermal) have a first-plant cost (PI) and a makers' target cost (OB). 100-hour storage is off in PI (no observed cost). OB is a lower bound for nuclear: it assumes every alternative reaches its target.
- Adequacy: firm capacity at least 1.1 x peak load (76.9 GW from the 3-hour data, same at every time step).
- Trade (central rule): balanced annual swap, imports = exports in every year; imports cost 115.94 EUR/MWh (PUN 2025), exports earn 61.07 EUR/MWh (France 2025 average); export limited to 6,095/11,535 of import capacity (Terna limits); no imports and no capacity credit in the three weeks of each year with the highest residual load. Reason: the plan must work if every neighbour planned the same way; counting on foreign plants is a dependence choice, shown as a variant with its price.

## 3. One cost rule for every technology

annual cost = overnight capex (development and grid connection included; contingency, subsidies and grants excluded) x interest during construction (real rate, build time) x CRF(real rate, life) + fixed O&M.
Real 2025 euros; costs of plants contracted or built in 2024-2026; net capacity; realistic output. Auction prices are not used as costs: the FER-X PV price (56.82 EUR/MWh) can be combined with capital grants up to 40% and tax credits; the MACSE battery price (12,959 EUR/MWh-yr) relied on post-contract revenues according to analysts.

| Technology | Capex | O&M | Life, build | Annual cost at 5% | Source |
|---|---|---|---|---|---|
| Nuclear, large (central) | 10,200 EUR/kW net | OPEX 40 EUR/MWh (27.75 fixed + 12.25 variable) | 60 y, 9 y | fixN 911 EUR/kW-yr (1,239 at 7%) | EC decision SA.117794 on Dukovany, OJ C/2026/2825 |
| PV ground, tracker | 950 EUR/kWp | 20 EUR/kWp-yr | 25 y, 1 y; degradation 0.5%/yr | 89 EUR/kWp-yr | PoliMi Renewable Energy Report 2025; Italia Solare Oct 2025; GSE for ARERA 239/2025 |
| PV agrivoltaic | 1,200 EUR/kWp | 20 | 25 y, 1 y | 107 | PoliMi 2025 |
| PV industrial roofs | 950 EUR/kWp | 20 | 25 y, 1 y | 89 | mean of GSE (850) and PoliMi (1,000-1,100) |
| PV other roofs | 1,250 EUR/kWp | 20 | 25 y, 1 y | 111 | mean of GSE (1,100) and IEA PVPS Italy 2024 (1,400) |
| Onshore wind | 1,600 EUR/kW | 40 EUR/kW-yr | 25 y, 2 y | 159 EUR/kW-yr | PoliMi 2025; GSE for ARERA 239/2025 |
| Offshore wind, floating | 4,750 EUR/kW | 100 | 25 y, 3 y | 463 | PoliMi 2025; Sapienza/ANEV 2026 (none built in Italy) |
| Batteries, 4 h | 168.6 EUR per usable kWh | 4.486 EUR/kWh-yr | 15 y, 2 y; 85% round trip | 21,547 EUR/MWh-yr | ARERA 332/2026/R/eel (150.5 x 1.12 oversizing) |
| Electrolyser (PI) | 2,056 EUR/kW | 3%/yr | 20 y, 2 y | | IEA Global Hydrogen Review 2025 |
| Hydrogen storage | 113 EUR per MWh of working capacity per year | | | | Hystories D8.6, depleted gas field (desk study) |
| SMR | 17,200 (PI), 11,700 (OB) EUR/kW | as large nuclear | 60 y, 5 y | 1,264 (PI), 934 (OB) EUR/kW-yr at 5%; 1,231 (OB) at 7% | Darlington BWRX-300: unit 1 and four-unit programme |

Full list with URLs: `docs/audit/v8_symmetric_costs.md`; every input and its source: `model/techs_v8.json`.
Implied changes against v7: ground PV from 58 to 89 EUR/kWp-yr (+54%), batteries from 11,466 to 21,547 EUR/MWh-yr (+88%), onshore wind from about 150 to 159, nuclear fixed cost from 670 to 911 EUR/kW-yr (+36%).

## 4. Nuclear cost: the central case and the others

Dukovany 5-6 (two APR1000), from the European Commission's opening decision on the Czech state aid (SA.117794, published 27 May 2026):
- EPC contract 407 bn CZK (KHNP, June 2025); the fuel contract is separate (15-20 bn CZK, about ten years) and is NOT inside the 407 bn. v7 had deducted fuel from the price: wrong.
- State preparation and owner's costs 85 bn CZK (CT24, 13 Oct 2025; inside the Commission's development capex bracket of EUR 3.0-5.0 bn).
- Capacity "up to 976 MWe each" sellable (1,055 MWe is gross); 15.4 TWh a year = 90% load factor.
- (407 + 85) bn CZK / 24.688 CZK/EUR (ECB 2025 average) / 1,952 MW = 10,210 EUR/kW net, rounded 10,200. The Commission's overnight bracket of EUR 20-25 bn (EPC, fuel, owner's costs, contingency; 2024 prices) gives 9,890-12,450 EUR/kW net without fuel: the central value is at the floor of the official bracket (no contingency spent = "built properly"); the top is 12,700 EUR/kW in 2025 euros.
- Czech financial model: 9-year construction phase, 60-year operation, OPEX 35-45 EUR/MWh (fixed O&M, lifecycle investment, fuel, waste account, decommissioning): midpoint 40 used.
- The two-unit aid package is under in-depth investigation by the Commission, not approved.
- fixN = 10,200 x idc(5%, 9 y) x CRF(5%, 60 y) + 27.75 x 0.9 x 8.76 + grid = 676 + 219 + 16 = 911 EUR/kW-yr; 1,239 at 7%. idc(r, y) = (1/y) sum_{k=0}^{y-1} (1+r)^(y-k-0.5).

Other cost cases, read on the value curve with the same O&M, life and availability (fixN at 5%): Dukovany in 7 years 877; top of the official bracket (12,700) 1,077; Barakah 5,500 EUR/kW, 8 y: 590 (Dec 2009 contract of 20.4 bn USD revalued; a floor: final cost not public); Saeul/Shin Hanul budget 2,965 EUR/kW, 8 y: 426 (a budget, not final cost); median of Flamanville 3, Olkiluoto 3, Mochovce 3-4, Vogtle 3-4: 9,680 EUR/kW, 15 y: 988; Vogtle 13,400 EUR/kW, 10 y: 1,147 (v7 had 15,540: interest counted twice).
Net/gross caveat: Barakah, Saeul, Flamanville and Mochovce figures are per gross kW (understated by about 4-7%).

## 5. Results

All numbers: `docs/results_v8.md` (sections 1-5). Key ones:

Central (3 h): PI 5% 23.2 GW, 44.5% of demand, system cost 114.42 against 127.77 EUR/MWh without nuclear, saving 13.35 EUR/MWh = 4.8 bn EUR/yr. PI 7%: 15.6 GW, 29.9%, saving 8.59. OB 5%: 15.7 GW, 30.5%, 107.53 against 114.39, saving 6.86 = 2.4 bn EUR/yr. OB 7%: 11.1 GW, all SMR, 21.6%, saving 2.62.

Value curve (EUR/kW-yr at which a block of capacity is worth building; independent of the cost of nuclear). PI 5%: 0-4 GW 1,318; 4-8 1,220; 8-12 1,149; 12-16 1,074; 16-20 973; 20-24 921; 24-28 868; 28-32 755; 32-36 672; 36-40 462. PI 7%: 1,582; 1,467; 1,387; 1,286; 1,162; 1,098; 1,028; 898; 800; 545. OB 5% with SMRs available: 0-4 GW 1,459, then 934, 934, 927 (the cost of SMRs at target, which replace large reactors), 877, 812, 717. OB 7% with SMRs: 1,465; 1,231; 1,228; 1,148; 1,054; 981; 858.
OB without SMRs (value of nuclear as a whole; batch 5, 20 runs): at 5%: 0-4 GW 1,145; 4-8 1,087; 8-12 1,058; 12-16 965; 16-20 877; 20-24 812; 24-28 717; 28-32 663; 32-36 616. At 7%: 1,360; 1,301; 1,262; 1,148; 1,054; 981; 858; 801; 740. Free optimum without SMRs: 15.65 GW at 5% (same as with SMRs available: none is built), 11.0 GW of large reactors at 7% (cost 131.43 against 131.16 with SMRs). From 12-16 GW upward the two OB curves coincide. Cost cases on the OB 5% curve without SMRs (best N; within 1%): Dukovany official 16 (12-20), saving 6.85; 7 years 20 (12-24); top of bracket 8 (0-12), saving 0.88; risk median 12 (8-16); Vogtle 0 (0-8). At 7%: Dukovany official 12 (4-16), saving 2.30; top of bracket 0.

Flat optimum (range of N on the 4-GW grid within 1% of the minimum cost, central cost): PI 5% 16-28 GW; PI 7% 12-20; OB 5% 12-20 (4-20 on the curve where SMRs fill the gap); OB 7% 4-16.

Cost cases on the PI 5% curve (best N on the 4-GW grid; range within 1% of the minimum): Dukovany official 24 (16-28); 7 years 24 (20-28); top of bracket 12 (8-20); risk median 16 (12-24); Vogtle: see results_v8.md; Barakah 36; Saeul budget 40 (36-40). See results_v8.md section 3 for every curve.
The first 4 GW are worth 1,318 EUR/kW-yr in PI at 5%, more than nuclear at Vogtle cost (1,147); in OB without SMRs they are worth 1,145, equal to the Vogtle cost (the 1,459 of the OB curve with SMRs available measures large reactors against a system already filled with SMRs and is not the value of nuclear).

Systems (3 h, 5%). PI with nuclear: 76 GW PV, 33.4 GW onshore wind, 23.2 GW nuclear, 129 GWh batteries, 2.1 TWh hydrogen storage, 17.7 TWh swapped with neighbours each way, nuclear load factor 87.5%. PI without nuclear: 193 GW PV, 59.6 GW onshore (every block), 2.6 GW offshore, 281 GWh batteries, 14.8 TWh hydrogen storage, 27.7 TWh swapped. OB with nuclear: 85 GW PV, 44.6 GW onshore, 15.7 GW nuclear, 10 GW CSP, 214 GWh compressed air. OB without: 161 GW PV, 59.6 GW onshore, 10 GW CSP, 152 GWh batteries, 8.7 TWh hydrogen storage.

Variants (5%, one assumption changed; nuclear GW PI / OB; saving PI): central 23.2 / 15.7 (13.35); exports earn nothing 25.4 / 18.3 (15.26); exports earn the import price 18.0 / 14.1 (11.86); net imports up to 10% of demand 23.4 / 12.6 (11.81); net exports allowed 22.8 / 15.8; critical weeks by low PV+wind 18.2 / 14.5 (10.45); v7 import rule (38% foreign capacity credit, no exports) 11.9 / 7.2 (5.96); batteries at the MACSE price 18.1 / 14.0 (11.38); eight weather years including the four worst 27.1 / 15.5 (17.49); 7-year build 26.7 / 18.2; top of the cost bracket 14.0 / 14.4 (OB: SMR); v7 nuclear inputs (fixN 670) 33.6 / 28.4.
Reading: under self-sufficiency nuclear is 14-27 GW in PI and 12-18 GW in OB in every variant; the import rule is the largest lever (counting on foreign capacity in critical weeks halves nuclear); the 10% net-import allowance saves 0.31 EUR/MWh with nuclear in PI (114.42 -> 114.11) and 1.85 without (127.77 -> 125.92).

Time step: the same model at 6 h gives 21.7 GW (PI) and 13.7 GW (OB) at 5% (`results/v8_runs_h6.jsonl`); 3 h raises the optimum by about 2 GW. Hourly data were not rebuilt: the 3-hour results may still understate nuclear slightly; direction known from 12 -> 6 -> 3 h, size unknown.

## 6. Why the number moved across versions (trajectory)

First PDF 74% (34 GW, hourly model of one year optimised per year, nuclear 7,600 EUR/kW) -> v2 33% (renewables at real lifetime cost) -> v3/v4 36% -> v5 45% (PV land limit) -> v6 59% (2040 demand, no imports) -> v7 29% (imports with foreign capacity credit, all technologies, owner's costs) -> v7 with self-sufficiency 45% -> v8 44% PI / 31% OB.
The v8 value is close to the previous one by coincidence of two large opposite corrections: nuclear fixed cost +36% (official Dukovany figures) and renewables and batteries at full bottom-up cost (PV +54%, batteries +88%). With the v7 nuclear cost and v8 renewable costs the model would give 33.6 GW; with v8 nuclear cost and the v7 import rule 11.9 GW.
Structural reason for the swings: the optimum is flat (16-28 GW within 1% of cost in PI), so small cost changes move the optimum by many GW while the system cost barely changes.
Error register: 98 entries (`docs/audit/audit_history.md`): cost inputs 15, citations 9, code 5, data 7, method 23, wording or claims 34, document build 5. Audit of 11 November 2026: `docs/audit/audit_v8_findings.md` (nuclear costs, other costs, data and assumptions, code). Two code bugs fixed (grid threshold on new plants only; wind and grid charge not scaled at 7%), both had penalised nuclear.

## 7. Limits still open (state them; direction on nuclear in brackets)

One node, grid cost 245 EUR/kW transmission only, distribution not costed (understates nuclear); four weather years, eight-year stress variant (27.1 GW in PI); 3-hour data; hydro with the same monthly budget every year, no dry years; neighbours not simulated, export price is an annual average (favours the system that exports more = without nuclear); OPEX 40 is the midpoint of an official range (35 would lower fixN by about 39 EUR/kW-yr, 45 raise it by 39); capacity credits are assumptions (batteries at power x 4/6.6, hydro 15 GW at 1.0); build times of minor technologies assumed; existing wind kept at O&M although beyond its life in 2040; perfect foresight; nuclear load factor 87.5-89% results from the optimisation with availability 90% and may be optimistic against fleets that modulate (France 2024: 67%); hydrogen storage cost from a desk study; the monthly cost analysis and the comparison with other studies of the v7 white paper were not re-verified and are left out of v8.

## 8. Recommendation (one, with the condition that changes it)

Plan a nuclear fleet of about 15 GW (about 15 APR1000 units of 976 MW net, about 30% of 2040 demand) as the part that is justified in nearly every case: it is the optimum with alternatives at target cost (OB 5%: 15.7 GW), with capital at 7% and first-plant costs (PI 7%: 15.6 GW), and with nuclear at the top of the official cost bracket in PI (14.0 GW); and keep the option to grow to about 23 GW if hydrogen, compressed air and solar thermal do not reach their target costs (PI 5%: 23.2 GW; 16-28 GW within 1% of the minimum cost).
Conditions: built as at Dukovany (about 10,200 EUR/kW net including owner's costs, 9 years, capital near 5% real) and a system that does not rely on foreign capacity in the critical weeks.
What changes it: capital at 7% together with alternatives at target cost (11 GW, as small reactors); or accepting dependence on foreign capacity in the critical weeks (7-12 GW).
Where the 15 GW does not hold: in OB with nuclear at the top of the cost bracket the optimum is 14.4 GW only as small reactors at their target cost; with large reactors alone it is 8 GW, and any capacity between 0 and 12 GW is within 1% of the minimum (saving 0.88 EUR/MWh). In PI the first 4 GW are worth building in every cost case examined at 5%, Vogtle included.

## 9. Style rules

Italian: no long or medium dashes; plain words; no question headings; no filler; compare only homogeneous quantities; every number with its unit and step; say "nostro calcolo" for derived values. Label every claim that comes from an assumption as an assumption. Do not write that the Commission approved the Dukovany two-unit aid. Do not use the words "robust" or "robusto" without the range that supports it.
