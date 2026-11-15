# v8 facts for the documents (13 November 2026)

Single source for the white paper (Italian) and the preprint (English). Every number in the documents must come from this file,
from `docs/results_v8.md` (generated from the runs), from `model/techs_v8.json` (inputs with sources) or from `docs/audit/*`.
Nothing from the v7 drafts may be reused without checking it here: the v7 numbers are superseded.

## 1. Question and answer in one paragraph

How much nuclear does the least-cost zero-direct-emission Italian power system contain, for a 2040 demand of 400 TWh?
With one cost rule for every technology, the Dukovany contract price in the European Commission decision plus the owner's costs (10,200 EUR/kW net, the bottom of the 10,090-12,706 bracket the Commission reports), and a
system that does not lean on other countries, the 3-hour model gives 23.2 GW (44.5% of demand) when technologies without
commercial plants are at first-plant costs (PI), and 15.7 GW (30.5%) when they are at their makers' target costs (OB), at a
5% real cost of capital. At 7%: 15.6 GW (PI) and 11.1 GW (OB, all small modular reactors). The optimum is flat: in PI at 5%
every capacity between 16 and 28 GW costs within 1% of the minimum. About 15 GW is in or near the optimum at 5% with nuclear between the contract cost and the midpoint of the official bracket
(midpoint, 11,400 EUR/kW: 16 GW in PI, 12 GW in OB), and at 7% in PI at contract cost. It is not when two unfavourable conditions combine:
OB at 7% (11 GW); OB at the top of the bracket without small reactors (8 GW, 0-12 within 1%); 7% with the top of the bracket (PI 4 GW, 0-12 within 1%; OB 0);
7% with the risk median (PI 8, OB 0); OB at Vogtle cost (0, 0-8 within 1%); and the v7 trade rule, which counts on foreign capacity in the critical weeks
and on net imports of 52-71 TWh a year, about today's level (7 to 12 GW).

## 2. Model (unchanged structure, corrected inputs)

- Linear capacity-expansion model, HiGHS, one node, zero direct emissions, one fleet for four weather years (2016-2019) optimised together, 3-hour step (11,680 steps); 315,000 to 390,000 variables and 365,000 to 475,000 constraints (about twice with eight weather years) per run.
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

Central (3 h): PI 5% 23.2 GW, 44.5% of demand, system cost 114.42 against 127.77 EUR/MWh without nuclear, saving 13.35 EUR/MWh = 4.8 bn EUR/yr. PI 7%: 15.6 GW, 29.9%, saving 8.59. OB 5%: 15.7 GW, 30.5%, 107.53 against 114.39, saving 6.86 = 2.4 bn EUR/yr. OB 7%: 11.1 GW, all SMR, 21.6%, saving 2.63.

Value curve (EUR/kW-yr at which a block of capacity is worth building; independent of the cost of nuclear). PI 5%: 0-4 GW 1,318; 4-8 1,220; 8-12 1,149; 12-16 1,074; 16-20 973; 20-24 921; 24-28 868; 28-32 755; 32-36 672; 36-40 462. PI 7%: 1,582; 1,467; 1,387; 1,286; 1,162; 1,098; 1,028; 898; 800; 545. OB 5% with SMRs available: 0-4 GW 1,459, then 934, 934, 927 (the cost of SMRs at target, which replace large reactors), 877, 812, 717. OB 7% with SMRs: 1,465; 1,231; 1,228; 1,148; 1,054; 981; 858.
OB without SMRs (value of nuclear as a whole; batch 5, 20 runs): at 5%: 0-4 GW 1,145; 4-8 1,087; 8-12 1,058; 12-16 965; 16-20 877; 20-24 812; 24-28 717; 28-32 663; 32-36 616. At 7%: 1,360; 1,301; 1,262; 1,148; 1,054; 981; 858; 802; 740. Free optimum without SMRs: 15.65 GW at 5% (same as with SMRs available: none is built), 11.0 GW of large reactors at 7% (cost 131.43 against 131.16 with SMRs). The two OB curves coincide from 16 GW at 5% and from 12 GW at 7%. Cost cases on the OB 5% curve without SMRs (best N; within 1%): Dukovany contract 16 (12-20), saving 6.85; 7 years 20 (12-24); midpoint of bracket 12 (8-16), saving 3.57; top of bracket 8 (0-12), saving 0.88; risk median 12 (8-16); Vogtle 0 (0-8). At 7%: Dukovany contract 12 (4-16), saving 2.30; midpoint of bracket 4 (0-8), saving 0.03; top of bracket 0. PI at 7%: midpoint 12 (8-16), saving 4.09; top of bracket 4 (0-12), saving 1.10; risk median 8 (4-12); Vogtle 0.

Flat optimum (range of N on the 4-GW grid within 1% of the minimum cost, central cost): PI 5% 16-28 GW; PI 7% 12-20; OB 5% 12-20 (4-20 on the curve where SMRs fill the gap); OB 7% 4-16.

Cost cases on the PI 5% curve (best N on the 4-GW grid; range within 1% of the minimum): Dukovany contract 24 (16-28); 7 years 24 (20-28); midpoint of bracket (11,400 EUR/kW, fixN 991) 16 (12-24), saving 8.95; top of bracket 12 (8-20); risk median 16 (12-24); Vogtle: see results_v8.md; Barakah 36; Saeul budget 40 (36-40). See results_v8.md section 3 for every curve.
The first 4 GW are worth 1,318 EUR/kW-yr in PI at 5%, more than nuclear at Vogtle cost (1,147); in OB without SMRs they are worth 1,145, equal to the Vogtle cost (the 1,459 of the OB curve with SMRs available is not the value of the first 4 GW: the point at 0 GW has no nuclear of any kind, the point at 4 GW has 4 GW of large reactors plus the small reactors the model adds by itself, so the step credits the benefit of those small reactors to the 4 GW).

Systems (3 h, 5%). PI with nuclear: 76 GW PV, 33.4 GW onshore wind, 23.2 GW nuclear, 129 GWh batteries, 2.1 TWh hydrogen storage, 17.7 TWh swapped with neighbours each way, nuclear load factor 87.5%. PI without nuclear: 193 GW PV, 59.6 GW onshore (every block except the worst, 10 GW at 1,200 hours: 69.6 GW are available), every ground and agrivoltaic PV block at its cap, and two of the three industrial-roof blocks (the northern one is not built), 2.6 GW offshore, 281 GWh batteries, 14.8 TWh hydrogen storage, 27.7 TWh swapped. OB with nuclear: 85 GW PV, 44.6 GW onshore, 15.7 GW nuclear, 10 GW CSP, 214 GWh compressed air. OB without: 161 GW PV, 59.6 GW onshore, 10 GW CSP, 152 GWh batteries, 8.7 TWh hydrogen storage.

Variants (5%, one assumption changed; nuclear GW PI / OB; saving PI): central 23.2 / 15.7 (13.35); exports earn nothing 25.4 / 18.3 (15.26); exports earn the import price 18.0 / 14.1 (11.86); net imports up to 10% of demand 23.4 / 12.6 (11.81); net exports allowed 22.8 / 15.8; critical weeks by low PV+wind 18.2 / 14.5 (10.45); v7 trade rule, a bundle of five changes (38% foreign capacity credit and 38% availability in the critical weeks, weeks chosen by low PV+wind, import price x1.17 in those weeks, no exports, no annual balance) 11.9 / 7.2 (5.96); batteries at the MACSE price 18.1 / 14.0 (11.38); eight weather years including the four worst 27.1 / 15.5 (17.49); 7-year build 26.7 / 18.2; top of the cost bracket 14.0 / 14.4 (OB: SMR); v7 nuclear inputs, also a bundle (8,540 EUR/kW, 7 years, 80-year life, O&M 32, availability 92%; fixN 670) 33.6 / 28.4.
Reading: with the annual balance and no foreign capacity in the critical weeks, nuclear is 14.0-27.1 GW in PI and 14.0-18.3 GW in OB in every variant (OB at the top of the bracket: 14.4 GW of small reactors; with large reactors only 8 GW, 0-12 within 1%); with net imports up to 10% of demand it is 23.4 (PI) and 12.6 (OB). Among the system rules the trade rule moves the result most; the cost of nuclear moves it more (cost cases span 0-40 GW).
The v7 trade rule halves nuclear, but it is five changes at once. Taken one at a time: net imports up to 10% of demand 23.4 / 12.6; critical weeks chosen by low PV+wind 18.2 / 14.5; the whole bundle 11.9 / 7.2. The 38% foreign capacity credit alone, annual balance kept (3-hour runs, results/v8_runs_review.jsonl): 17.9 GW in PI (cost 110.52) and 14.1 GW in OB (cost 104.81). It is the largest single change in PI, about half of the drop, and only 1.6 GW in OB. No single change explains the halving. The halving comes from the combination: foreign plants available in the critical weeks AND no annual balance, so imports become a firm source all year (52-71 TWh).
Price of self-sufficiency (v8 rule against the v7 trade rule, 5%): system cost with nuclear 114.42 against 109.99 in PI (+4.44 EUR/MWh, 1.6 bn EUR/yr) and 107.53 against 103.38 in OB (+4.15, 1.5 bn); without nuclear 127.77 against 115.95 in PI (+11.82, 4.2 bn) and 114.39 against 105.52 in OB (+8.87, 3.2 bn). Under the v7 rule Italy imports 52.0 TWh/yr (PI with nuclear), 57.7 (PI without), 56.0 (OB with), 70.7 (OB without) and exports nothing; in 2025 it imported 55.2 TWh and exported 7.4 (net 47.8). So the v7 rule is about today's dependence, and the v8 central case is a choice to end it. The rule favours nuclear and must be stated as such among the limits.
The eight-year variant repeats the 2016-2019 load with the weather of 1994, 1998, 2014, 2015 for the added four years (load and weather are not from the same year there). the 10% net-import allowance saves 0.31 EUR/MWh with nuclear in PI (114.42 -> 114.11) and 1.85 without (127.77 -> 125.92).

Time step: the same model at 6 h gives 21.7 GW (PI) and 13.7 GW (OB) at 5% (`results/v8_runs_h6.jsonl`); 3 h raises the optimum by 1.6 GW (PI, 23.22 against 21.66) and 1.9 GW (OB, 15.65 against 13.73). Hourly data were not rebuilt: the 3-hour results may still understate nuclear slightly; direction known from 12 -> 6 -> 3 h, size unknown.

## 6. Why the number moved across versions (trajectory)

First PDF 74% (34 GW, 3-hour model with each year optimised on its own, nuclear 7,600 EUR/kW) -> v2 33% (renewables at real lifetime cost) -> v3/v4 36% -> v5 45% (PV land limit) -> v6 59% (2040 demand, no imports) -> v7 29% (imports with foreign capacity credit, all technologies, owner's costs) -> v7 with self-sufficiency 45% -> v8 44% PI / 31% OB.
The v8 value is close to the previous one by coincidence of two large opposite corrections: nuclear fixed cost +36% (official Dukovany figures) and renewables and batteries at full bottom-up cost (PV +54%, batteries +88%). With the v7 nuclear cost and v8 renewable costs the model would give 33.6 GW; with v8 nuclear cost and the v7 import rule 11.9 GW.
Structural reason for the swings: the optimum is flat (16-28 GW within 1% of cost in PI), so small cost changes move the optimum by many GW while the system cost barely changes.
Error register: 98 entries (`docs/audit/audit_history.md`): cost inputs 15, citations 7, code 6, data 7, method 26, wording or claims 33, document build 4. Audit of 11 November 2026: `docs/audit/audit_v8_findings.md` (nuclear costs, other costs, data and assumptions, code). Two code bugs fixed (grid threshold on new plants only; wind and grid charge not scaled at 7%), both had penalised nuclear.

## 7. Limits still open (state them; direction on nuclear in brackets)

One node, grid cost 245 EUR/kW transmission only, distribution not costed (understates nuclear); four weather years, eight-year stress variant (27.1 GW in PI); 3-hour data; hydro with the same monthly budget every year, no dry years; neighbours not simulated, export price is an annual average (favours the system that exports more = without nuclear); OPEX 40 is the midpoint of an official range (35 would lower fixN by about 39 EUR/kW-yr, 45 raise it by 39); capacity credits are assumptions (batteries at power x 4/6.6, hydro 15 GW at 1.0); build times of minor technologies assumed; existing wind kept at O&M although beyond its life in 2040; perfect foresight; nuclear load factor 87.5-89% results from the optimisation with availability 90% and may be optimistic against fleets that modulate (France 2024: 67%); hydrogen storage cost from a desk study; the monthly cost analysis and the comparison with other studies of the v7 white paper were not re-verified and are left out of v8.

## 8. Recommendation (one, with the condition that changes it)

Plan a nuclear fleet of about 15 GW (about 15 APR1000 units of 976 MW net, about 30% of 2040 demand) as the part that is justified in nearly every case: it is the optimum with alternatives at target cost (OB 5%: 15.7 GW), with capital at 7% and first-plant costs (PI 7%: 15.6 GW), and with nuclear at the top of the official cost bracket in PI (14.0 GW); and keep the option to grow to about 23 GW if hydrogen, compressed air and solar thermal do not reach their target costs (PI 5%: 23.2 GW; 16-28 GW within 1% of the minimum cost).
Conditions: built as at Dukovany (about 10,200 EUR/kW net including owner's costs, 9 years, capital near 5% real) and a system that does not rely on foreign capacity in the critical weeks.
What changes it: capital at 7% together with alternatives at target cost (11 GW, as small reactors); or accepting dependence on foreign capacity in the critical weeks (7-12 GW).
Where the 15 GW does not hold: in OB with nuclear at the top of the cost bracket the optimum is 14.4 GW only as small reactors at their target cost; with large reactors alone it is 8 GW, and any capacity between 0 and 12 GW is within 1% of the minimum (saving 0.88 EUR/MWh). In PI the first 4 GW are worth building in every cost case examined at 5%, Vogtle included.

## 9. Style rules

Italian: no long or medium dashes; plain words; no question headings; no filler; compare only homogeneous quantities; every number with its unit and step; say "nostro calcolo" for derived values. Label every claim that comes from an assumption as an assumption. Do not write that the Commission approved the Dukovany two-unit aid. Do not use the words "robust" or "robusto" without the range that supports it.

## 10. Corrections after the independent review of 14 November (they override anything above that disagrees)

- "Dukovany official" is renamed "Dukovany contract": 10,200 EUR/kW net is our sum of the EPC contract in the Commission decision (407 bn CZK) and the owner's costs (85 bn CZK, a public figure from Czech television, not in the decision). The decision gives only a bracket for the overnight cost, 20-25 bn EUR: 10,090-12,706 EUR/kW net in 2025 euros without fuel. Our figure sits at the bottom of the bracket. The midpoint (11,400 EUR/kW, fixN 991 at 5% and 1,357 at 7%) is a cost case on every curve: PI 5% 16 GW (12-24), OB 5% without SMRs 12 GW (8-16), PI 7% 12 GW (8-16), OB 7% 4 GW (0-8).
- OB is not a lower bound for nuclear: it lowers the cost of non-nuclear technologies without commercial plants but also of SMRs, so with expensive large reactors it can contain more nuclear than PI; it keeps PV, wind and batteries at 2024-2026 costs. Several variants give less nuclear than OB central.
- Limits that favour nuclear, to be stated with their direction: no cost decline to 2040 for PV, wind and batteries (nuclear is also at today's cost, but the observed trend of the first three is downward); the caps on ground and agrivoltaic PV are our choice and every such block is at its cap in the PI system without nuclear; demand flexibility is limited to smart charging of 25% of electric cars; no common-mode outages of the nuclear fleet; nuclear capex at the bottom of the official bracket; the trade rule (above). Limits that favour the system without nuclear: existing wind kept at O&M cost only; perfect foresight over the weather years.
- Between "v7 with self-sufficiency" and v8 more than two things changed: nuclear cost, PV, wind and battery costs, the export price (0 to 61.07), the criterion for critical weeks (low PV+wind to residual load), nuclear availability (92% to 90%), and two code fixes (grid threshold on total stock, wind and grid charge scaled with the rate).
- FER-X: the price can be combined with capital grants up to 40%, and in that case the tariff is cut by up to 35%. MACSE: 95 EUR/kWh refers to batteries of about 6.6 hours, 150.5 to 4 hours; they are not the same product.
- Arithmetic: 8,540 EUR/kW x 2.11 GW = 18.0 bn EUR. First PDF: 74% (not 68%).
- WAVE is off in all 110 runs and must not be listed as an active input.
- Grid charge: 245 EUR/kW above 137 GW of wind+PV is an assumption of the authors, NOT a Terna figure (94 GW and 137 GW are not in the Terna plan). The Terna 2025 plan gives over 23 bn EUR and +65 GW of renewables by 2030 on 43 GW installed in 2023: up to about 350 EUR/kW above 108 GW, an upper bound because the plan also serves security and demand. In the model the existing fleet kept is 37.8 GW, so the charge starts at 99.2 GW of new plants. Our value is lower than that bound: it favours the system without nuclear. Check runs with 350 EUR/kW above 108 GW (3 h, results/v8_runs_review.jsonl): nuclear 26.7 GW in PI (cost 115.44) and 19.1 GW in OB (cost 108.94), against 23.2 and 15.7 central.
- Do not write "as notified" or "official" for 10,200, and do not write that every input comes from official or regulatory sources or from plants of 2024-2026: some come from PoliMi, Italia Solare, trade press, and solar thermal (Andasol, 2008) and Barakah (2009 contract) are older.
- Offshore wind: one fixed-bottom plant exists in Italy (Beleolico, Taranto, 30 MW, 2022); no floating plant has been built.
- Barakah 5,500 EUR/kW includes owner's costs at 12.57% of the overnight cost, i.e. x1.1438 on the revalued contract (about 4,800 without: 20.4 bn USD / 5.6 GW x 1.476 / 1.1188 = 4,806). The risk median excludes Hinkley Point C (about 10,300 with it).
- 15 GW against the cost cases: on the 4-GW grid, 16 GW is within 1% of the minimum in 11 of the 20 cells of five cost cases above the contract cost x four curves. "Justified in nearly every case" is too strong: write "in most cases" and give the count.
- "Annual energy matters little" (10% net imports) holds in PI (23.2 to 23.4 GW) and not in OB (15.7 to 12.6 GW, saving 6.86 to 4.09).
- OB against PI: at the top of the bracket OB has more nuclear than PI (14.4 against 14.0 GW) because OB also puts small reactors at target cost.
- The flat optimum explains the movements of a few GW, not the whole 74%-29% swing: 36 GW costs 4.3% more than the optimum in PI; the large swings came from changed rules, costs and demand.
- Time steps: 4 years x 365 days x 8 = 11,680 steps at 3 hours.

## 11. Trade rule framing (15 November, overrides "favours nuclear" anywhere above)
- The central rule (no foreign capacity in the critical weeks) is NOT described as a choice that favours nuclear. Reason: the critical weeks (central rule, ranked by residual load) all fall in November-February (2016: Jan, Nov, Dec; 2017: Jan, Feb, Nov; 2018: Jan, Feb, Nov; 2019: Jan, Nov, Dec); the August week belongs to the v7 ranking by low PV+wind; in 2024 85% of Italy's imports came from Switzerland (43.1%) and France (41.6%) (Il Sole 24 Ore); in winter France has its peak and its firm capacity is nuclear; Switzerland was a net importer almost every day of winter 2025/26 with Goesgen offline (economiesuisse); France was a net importer in 2022 when reactors were stopped (Banque de France). Relying on imports in those weeks means relying largely on foreign nuclear; a system without Italian nuclear built that way imports nuclear.
- The v7 trade rule stays as a variant with its price. Its direction as a limit is uncertain (depends on free foreign winter capacity in 2040); the partial case is the 38% credit with balance kept: 17.9 GW PI, 14.1 GW OB.

## 12. Third review (15 November; the 11 November audit was the first, the 14 November review the second); overrides anything above
- Grid charge as the code applies it: every new PV and onshore wind kW pays 13 EUR/MWh x 1,066 h (PV) or 8 EUR/MWh x 1,709 h (wind), about 240 EUR/kW over 40 years; new kW above a total wind+PV stock of 137 GW pay a second charge of 13.77 EUR/kW-yr (about 236 EUR/kW). Offshore wind pays no per-MWh charge but counts toward the 137 GW threshold and pays the second charge; nuclear 2 EUR/MWh. In the PI system without nuclear 118 GW pay the second charge (4.57 EUR/MWh) and the average over all new PV and wind, offshore included, is about 363 EUR/kW. The Terna plan implies about 350 EUR/kW on average for the 2030 additions. Direction of our charge against that: NOT established; do not write that it favours the system without nuclear. The grid350 check (about 340 EUR/kW on every new kW plus the second charge above 108 GW) gives 26.7 GW (PI) and 19.1 GW (OB).
- "OB 0" in the lists of cases where 15 GW does not hold refers to large reactors only. With SMRs available, OB at 7% is 11.1 GW of SMRs whenever large reactors cost at least the contract price, and OB at Vogtle cost at 5% is about 14.4 GW of SMRs. Label these cells "large reactors only" or give the SMR values.
- Nuclear financed at a higher rate than everything else (read on the 5% curves, no new runs): nuclear at 7% with everything else at 5% (fixN 1,239): PI 4 GW (0-12 within 1%), saving 0.88 EUR/MWh; OB without SMRs 0 (0-4); SMRs at 7% (1,231) would not enter either. Nuclear at 6%, rest at 5% (fixN 1,066): PI 16 GW (8-20), saving 5.55; OB without SMRs 8 GW (0-12), saving 1.11. So the recommendation needs nuclear financed at about the same rate as the alternatives (state loan, contract for difference, as for Dukovany and as FER-X does for renewables). This is a condition of the recommendation and must be stated next to the 5% condition.
- The nuclear capex at contract price is NOT a limit favouring nuclear: it is the same rule as every other technology (contract price, no contingency). Remove it from the list of limits favouring nuclear; keep the bracket cases as cost cases.
- Model simplifications with known direction make the result cautious for nuclear: 3 h against 6 h raises nuclear (+1.6/+1.9 GW), eight weather years raise PI to 27.1, one node and the same hydro every year favour the system with more PV. Present them as "make the result cautious", not as weaknesses.
- Limits that remain and favour nuclear: costs of PV, wind, batteries and electrolysers frozen at today's level to 2040 (2040-cost variant being prepared); no common-mode outages; availability shape with 95% in peak months; PV land caps; limited demand flexibility. Limits that favour the system without nuclear also include hydrogen storage at 3.76 EUR/kg (low part of 2.06-14.95) and electrolysers at target cost in OB.
- v7-rule overlap: the residual and PV+wind rankings share 4 of 12 weeks (8 of 12 differ).
- "Five cost cases from the contract cost upward" (the contract included); four above it.
- The 14.0-27.1 GW range of the variants excludes the v7 nuclear-inputs bundle (33.6 GW).
- Value curve: the 462 EUR/kW-yr block is 36-40 GW.

## 13. Costs to 2040 (15 November); overrides section 12 where it disagrees
- Decision: no 2040 cost projection is used for any technology. Reason: the decision is taken now; nuclear is contracted now at today's prices (about ten years from decision to operation), and the alternatives must be compared at what can be contracted today (PV and batteries take one or two years; hydrogen is the last piece before fossil plants close). Future costs for the alternatives only would compare a contract with a forecast; for all, two forecasts. Projections for PV, batteries and nuclear series (and others) all point down and none is an observed cost; using them for some technologies and not for others would break the one-cost-rule symmetry. All technologies stay at today's costs (OB target costs aside). In the limits this item has unknown direction, not "favours nuclear". The batch-7 variant was withdrawn before running.
- Battery cost: the 3-hour variant with batteries at the MACSE price (about 95 EUR/kWh, 6.6 h) gives 18.1 GW (PI) and 14.0 GW (OB) against 23.2 and 15.7: it moves the optimum but keeps it at or above about 15 GW in PI and near it in OB. A 12-hour test cannot show battery effects (4-hour batteries inside 12-hour steps) and must not be quoted.

## 14. Nuclear-only financing cases (15 November, round 5); overrides section 12
- When only nuclear pays a higher rate, the grid charge in fixN stays at the system rate (5%), as for every other technology: fixN 1,064 at 6% and 1,235 at 7%; SMRs at 7% under the same rule 1,226. PI 6%: 16 GW (8-20), saving 5.65; OB without SMRs 6%: 8 GW (4-12), saving 1.16. PI 7%: 4 GW (0-12), saving 0.93; OB without SMRs 7%: 0 (0-4).
- Barakah: owner's costs are 12.57% of the overnight cost, i.e. x1.1438 on the contract; about 4,800 EUR/kW without them.
- Conditions of the recommendation (three, everywhere): built at the Dukovany contract cost; nuclear financed at about the alternatives' rate (5% for all in the central case; with 7% for all, 15 GW holds only with first-plant costs for the alternatives); no foreign capacity in the critical weeks. "Midpoint still holds 15 GW" is at 5%.

## 15. OB curve with SMRs available (15 November, round 10); overrides earlier sections
- On this curve N counts large reactors and N = 0 is the system with SMRs only (108.50 EUR/MWh at 5%, 14.4 GW of SMRs; 131.16 at 7%, 11.1 GW), not the system with no nuclear. The first block is worth 934 (5%) and 1,231 (7%); the 1,459 and 1,465 of earlier drafts were an artefact of using the no-nuclear system as N = 0.
- Ranges within 1% on this curve: 0-20 GW at 5%, 0-12 GW at 7%. Cost cases: midpoint, risk median, top of bracket and Vogtle give 0 large reactors at 5% (saving 5.89 against no nuclear, from the SMRs); at 7% every case from the contract up gives 0 large reactors (saving 2.63). Savings are against the system with no nuclear.
- The OB curves without SMRs (value of nuclear as a whole) and the "11 of 20" count are unchanged.
