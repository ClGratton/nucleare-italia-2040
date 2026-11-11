# Audit v8 (2026-11-11): findings of the independent audits

Rule set by the owner: every correction applied to one source must be checked for all the others (no subsidised PV price if nuclear is costed at full official cost; same treatment of owner's costs, net capacity, interest during construction, life, O&M, realistic output).

## A. Nuclear cost inputs (verified by me on EC decision SA.117794, OJ C/2026/2825, 27 May 2026: https://eur-lex.europa.eu/eli/C/2026/2825/oj/eng/pdf)

A1. Fuel is NOT inside the 407 bn CZK EPC price. The Nuclear Fuel Contract is separate (signed 17 Jun 2025; CT24 18 Jul 2025: 407 + 15 bn = 422; oEnergetice 4 Jun 2025: 15-20 bn CZK for almost ten years). The deduction of 382 EUR/kW was wrong.
A2. Official overnight cost (recital 93): EUR [20-25] bn for both units, covering EPC, fuel contract, owner's costs and contingencies; EPC EUR [15-20] bn; development CAPEX EUR [3.0-5.0] bn, construction CAPEX EUR [15-20] bn, 2024 real terms (recital 94). The study's 8,540 x 2.11 GW = 17.9 bn is below the official floor.
A3. Capacity: "up to 976 MWe each", 15.4 TWh/yr (recitals 40-41) = 90% on 2 x 976: 976 is the sellable capacity, 1,055 is gross. EPC per net kW: 407e9/24.688/1.952e6 = 8,446 EUR/kW (not 7,850). EPC + owner's costs (85 bn CZK, public figure): 19.93 bn EUR = 10,209 EUR/kW net. EC bracket excluding fuel (0.7 bn): 9,890-12,450 EUR/kW net (2024 EUR), x1.021 = 10,095-12,710 (2025 EUR).
A4. Financial model (recital 89): 9-year construction phase, 60-year operation; works 2029; first sync Dec 2036 (U5), Dec 2037 (U6); construction start by April 2030 / April 2031 (recital 60). Development capex is spent 2025-2029.
A5. OPEX (recital 95): [35-45] EUR/MWh including fixed O&M (35-45% of OPEX), lifecycle investment (15-25%), fuel (15-25%), nuclear account, decommissioning. Study: 17 fixed + 15 variable = 32. NEI US fleet 2023: 29.9 EUR/MWh.
A6. Strike price [85-105] EUR/MWh (2024 prices) with a preferential state loan; target RoE [6-8]%. The two-unit aid package is under in-depth investigation, not approved (the text said "approved").
A7. Vogtle overstated about 14%: owners' 31 bn USD is capital AND financing (AP 25 May 2023); only Georgia Power's financing had been removed. Corrected 13,100-13,700 EUR/kW, fixN about 1,030 (was 1,172).
A8. Barakah: 20.4 bn USD is a Dec 2009 contract; if in 2010 USD the CPI factor is 1.476 not 1.255: about 5,500 EUR/kW (4,670 is a floor); net MW +4%.
A9. Saeul label: the reference gives a Shin Hanul budget (6.5 trillion won per 1.4 GW unit), not Saeul 3-4 actuals.
A10. Risk case: Flamanville 13.2 bn (2015) excludes complementary costs; Mochovce 6.7 bn is cost of completion; Hinkley excluded (with it the median is about 10,300).
A11. Price base of the 407 bn: "current prices" July 2024 / June 2025, with escalation clauses: 0 to +2.5%.
A12. Cost of capital: Sizewell C RAB 6.73% real in construction (NAO 2026); Dukovany loan 0% until licence then state cost + 1%.
A13. Net vs gross is inconsistent across cases (Vogtle net; Barakah, Saeul, Flamanville, Mochovce gross).
Verified correct: all fixN arithmetic, ECB rate 24.688, WNA fuel cost, INL 12.57%, Barakah 24.4 bn = financing.

Corrected central candidates (fixN, EUR/kW-yr; F = 150.14 at 5%):
- 10,200 EUR/kW net, 9 y, 80 y: 803.6 (5%), 1,142 (7%); with 60 y: 826.6, 1,155; with 7 y, 80 y: 770.5, 1,072.
- EC bracket top 12,500: 951 (9 y, 80 y, 5%).
- OPEX at the EC floor (35 instead of 32): +24 EUR/kW-yr; at the midpoint 40: +63.

## B. Non-nuclear cost inputs

B1. PV cost from the FER-X auction price (56.82 nominal -> 42.18 real EUR/MWh) is multiplied by 1,375 h (PECD mean): 58.0 EUR/kW-yr, implied ground capex 681 EUR/kW + 13.7 O&M. Agrivoltaic 908, industrial roofs 852, other roofs 1,065 EUR/kW, below the paper's own stated values (1,000; 1,500-2,300). Agrivoltaic is the marginal PV block. If winners yield more than 1,375 h the EUR/kW is understated.
B2. LDES (iron-air) in the first-plant case uses the maker's 2021 target (20 USD/kWh), no O&M, not flagged novel.
B3. BUG: grid threshold 137 GW is defined on total wind+PV stock (43 existing + 94 enabled) but the code counts only new blocks (37.8 GW existing exempt): threshold for new should be about 99 GW. No-nuclear +1.5 EUR/MWh. Grid cost 245 EUR/kW is transmission only.
B4. Hydrogen storage: depleted gas field desk study (Hystories D8.6, 3.76 EUR/kg, range 2.06-14.95), not a first plant; compression energy, losses, pipelines, IDC not modelled. White paper monthly section uses 37.6 EUR/kg (inconsistent).
B5. CSP target = IRENA 2024 world average (China-driven), 10 GW cap unsourced, credit 0.97, table cites the wrong source.
B6. Interest during construction and fixed O&M not uniform: nuclear and gas CCS get idc; CSP, H2 turbine, CAES, new pumped hydro, geothermal, interconnectors none; CAES, pumped, LDES, cables zero O&M.
B7. Wind is bottom-up (1,320 EUR/kW, 5.2%?, 25 y, O&M) and not as described in the paper; stricter than PV.
B8. Politecnico RER 2025 LCOE: PV and wind 17-24% above the model.
B9. Batteries: MACSE 12,959 EUR/MWh-yr -> implied 95 EUR/kWh; ARERA reference 150.5 EUR/kWh + 4.486/yr -> 19.0 EUR/kWh-yr (+66%).
B10. CAES target from an Energy Dome CO2-battery claim.
Asymmetries: capacity credit (batteries, LDES full power; hydro 15 GW at 1.0; CSP 0.97; H2 0.95; PV, wind 0); existing roofs at 1,262 h vs fleet 1,066 h; 119.7 GW agrivoltaic cap is the authors' choice and binds; no-nuclear builds 200 GW PV (Terna-Snam 2040: 114-137) and 53 GW onshore wind (29-39).
Verified: FER-X 56.82 (PV), 72.85 (wind); MACSE 12,959, 6.6 h; PUN 115.94; ACER H2 turbine data; arithmetic of all annualisations.

## C. Data and structural assumptions

C1. Import rule asymmetric: import at 115.94 (Italian PUN; GME 2025 border prices: France 61.07, Slovenia 104.64, Switzerland about 102), export at 0. Fee 10.31 (no nuclear) vs 5.93 (nuclear) EUR/MWh = 4.38 of the 9.00 gap. Critical weeks (3 lowest solar+wind) are not the scarce weeks: 7 of 12 outside the top-3 residual-load weeks. Exports capped by import capacity (11.5-18.9 GW) instead of Terna export NTC (about 6.1 GW). Effect on N: credit rule 14.15 GW -> imp0 19.68 -> X=0 20.45.
C2. Nuclear load factor 88-89% of nameplate (96% of the assumed 92% availability), helped by the export sink; France 2024: 67%.
C3. Four weather years decide the result: worst years give 30.8 (PI) / 24.3 (OB) GW vs 20.5 / 18.4. The npz has 8 PECD years only.
C4. Reserve requirement depends on the step: peak 64.69 (12 h), 66.98 (6 h), 76.88 (3 h), 82.11 GW (1 h shapes); the step correction is partly this artefact; Richardson to 1 h has no basis. Hourly data exist in OPSD/PECD (the "1 h impossible" claim holds only for the shipped payload).
C5. Single node with the lowest plausible grid cost (23 bn / 94 GW; the Terna plan says up to about 40 bn; distribution excluded).
C6. PV yield: PECD 1,375 h vs GSE fleet 1,066 h; existing plants credited 1,262-1,407 h; December-January share 10.1% vs 8.8% observed.
C7. Hydro: same hydrology every year (dry years missing), credit 1.0 on 15 + 7.3 GW.
C8. Demand 400 TWh consistent with DDS 2024 (404-439); heat pumps without cold spells; EV shifting limited.
C9. repo/it1519.csv is synthetic while the README presents it as OPSD.
Verified: load is real hourly data paired with the same weather year; totals; PECD hours; 11,535 MW import capacity.

## D. Model code (independent audit, six 12 h test runs)

D1. BUG: wind block costs and the VRE grid charge were not scaled at 7% (PV, nuclear grid and grid_x were). Understated cost at 7%: 845 + 543 M EUR/yr with nuclear, 1,232 + 795 without. Test (7%, fixN 923, 12 h): N 7.83 -> 11.40 GW. Penalised nuclear in every 7% run. H2 store annual cost also unscaled.
D2. BUG: grid threshold counts new blocks only (effective threshold 174.8 GW instead of 137). Missing charge 521 M EUR/yr (1.46 EUR/MWh) in every no-nuclear case and from fixN 750 up. PI 750, PI 800 and 7% 923 sit exactly on the kink (new VRE 137.0 GW): their N (about 12 and 11.4 GW) is set by this constant. Penalised nuclear.
D3. Reserve peak depends on the step: 64.69 / 66.98 / 76.88 GW at 12 / 6 / 3 h; 82.11 with hourly EV and heat-pump shapes. Test (12 h, peak 82.11): cost +3.44 EUR/MWh, N 17.76 -> 17.50, batteries 117 -> 260 GWh: shifts cost level, not N.
D4. Export capped by built import capacity (11.5-18.9 GW) rather than Terna's export limit (about 6.1 GW). Test (12 h): N 17.76 -> 17.99.
D5. Minor: EV window offset truncates 9 h to 6 h at step 6 (EV_SMART inactive at 12 h); a named variant on a novel unit skipped the default case (CSP 'c3' alone in PI would use target capex; not hit in central runs).
D6. Critical weeks: the PV+wind index picks autumn weeks; 5 of 12 rank 8th-16th by residual load. Test with the 3 highest residual-load weeks: N 17.76 -> 18.81, cost +0.82.
D7. Auction conversion: maths right; all PV blocks use yref 1,375 h; implied capex ground 682, agrivoltaic 909, industrial roofs 852, other roofs 1,065 EUR/kW, O&M 13.7; wind E1 about 1,800 EUR/kW; battery 95 EUR/kWh + 2.3/yr. The 20->30 year stretch (x0.811) is exact only if bidders value years 21-30 at zero.
D8. Flat optimum: at fixN 670 (6 h, PI) N = 12.1 GW costs +1.16%, 17.8 +0.12%, 23.6 +0.14%, 27.5 +0.67%: about 13 to 28 GW lies within 1% of the minimum cost. This is why the result swings.
D9. IDC only for nuclear, SMR, gas CCS; fixed O&M absent for existing hydro and pumped storage, import cables, new pumped hydro, CAES.
Verified correct: units of every coefficient and row; time aggregation (sums); crf, idc, fixed part 150.144 / 154.771; PI/OB plumbing as documented; stored results internally consistent (components sum to total, imports = exports, reserve binding with nuclear, nuclear at 95.5% of availability); cost_new denominator 356.6 TWh; sh_nuc includes exported energy (44.7% of demand = 42.2% of generation at 3 h).

Regression after the v8 code changes (v7 settings): ss0_PI_670_h12 reproduced exactly (86.167 EUR/MWh, 17.756 GW).
