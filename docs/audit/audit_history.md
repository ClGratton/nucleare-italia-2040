# Audit history: optimal nuclear share for Italy 2040

Compiled on 11 Nov 2026 from the project records only: facts files v2 to v7, reviews and audits, the owner's messages, the session transcript and its summaries, sub-agent reports, fix and patch scripts, old result files. No existing file was edited. Numbers are quoted as recorded. "Not found" means not found in the records.

Coverage gaps: the main transcript starts on 8 Nov 16:21; earlier phases come from summaries, facts files, fix scripts and sub-agent reports. The owner's messages between 7 Nov 07:09 and 8 Nov 16:21 survive only as quotes in summaries.

## 1. Trajectory of the headline number

Costs in EUR/MWh are "with nuclear against without". Nuclear cost: overnight EUR/kW, build years, real rate; annual fixed cost in EUR/kW-yr in brackets. PI = first-plant costs for technologies without commercial plants, OB = target costs.

| # | Date, version | Model state | Nuclear cost used | Headline nuclear | Single cause of the change |
|---|---|---|---|---|---|
| 1 | 19 Oct, monthly calculation | monthly balance, no optimisation; nuclear alone at 90% load factor against PV and wind mixes | 5,000 and 8,300; 4% and 7 y, or 7% and 10 y; life 60 | no share computed (stand-alone 59 to 134) | start |
| 2 | 19 Oct, hourly model 1 | LP, 2019 only, 2 h; nuclear, PV, wind, batteries, existing hydro; no imports; PV 66.38 and wind 85 nominal | 7,600; 7 y; 5%; life 60 (613) | 28.5 GW, 64% | first system model |
| 3 | 19 Oct, v1, first PDF | LP, 3 h, years 2016-2019 optimised one at a time; availability 92%; 10% adequacy margin | same (613) | 34 GW, 74%; 101 against 149 | years, step, availability and margin changed together; bridge not found |
| 4 | 20 Oct, v2 | auction prices as real lifetime cost (PV 42.2, wind 63.1); main PV auction | 7,600; 7 y; 5%; life 80; +5 EUR/MWh back-end (596) | 20 GW, 33%; 94 against 107 | renewable prices corrected (old basis: 32 GW, 68%) |
| 5 | 24 Oct, v3 | four years optimised jointly; hydro floor 37% | same (596) | 23 GW, 36%; 97 against 122 | joint planning instead of one optimisation per year |
| 6 | 25 Oct, v4 | v3 plus 1% near-optimal band and 100-hour storage variant | same | 23 GW, 36%; band 21-28 GW | none |
| 7 | 7 Nov, v5 | PV supply curve (ground cap 50 GW); monthly nuclear availability; wind unlimited; demand 312 TWh | same (596) | 24.8 GW, 45%; 94.9 against 132.1 | PV land cap (unlimited PV: 22.3 GW, 37%) |
| 8 | 7 Nov, v6 | demand 400 TWh; PECD profiles; finite PV and wind blocks; existing fleets; grid cost; bio and geo subtracted; no imports | 7,600; 7 y; 5%; life 80 | 38.5 GW, 59% (band 36.0-43.5); 97.6 against 204.2 | 2040 demand |
| 9 | 8 Nov, v7 first runs | 6 h; every technology a decision variable; imports up to 18.9 GW, 38% firm in critical weeks | gross Dukovany 7,750; 7 y; 5% | 19.1 GW, 34.8% (PI); 18.2 GW (OB) | imports and new technologies |
| 10 | 8 Nov, v7 curve | same | Dukovany net of fuel 7,360, later 7,370; 7 y; 5% (598) | 23.9 GW, 44.3% (PI); 23.3 GW (OB) | fuel taken out of the contract price |
| 11 | 9 Nov, v7 first documents | 3 h | same (598) | 24.4 GW, 45.6% (PI); 24.2 GW (OB) | step 6 h to 3 h |
| 12 | 9 Nov, v7 after review | same | owner's costs added: 8,430; 7 y; 5% (663) | 16.3 GW, 29.5% (PI); 15.2 GW (OB) | owner's costs |
| 13 | 9 Nov, v7 sent | same | 8,540; 7 y; 5% (670) | 16.0 GW, 28.9% (PI); 14.6 GW, 26.8% (OB); at 6 h 14.15 GW, 25.6% | exchange rate 25 to 24.688 CZK/EUR |
| 14 | 10-11 Nov, v8 | net self-sufficiency: yearly imports no greater than exports, no foreign help in three critical weeks a year | same (670) | 23.0 GW, 44.7% (PI); 20.8 GW, 40.0% (OB); at 6 h 20.45 GW, 39.4% | import rule |

Bridges in the records (GW of nuclear):
- v5 to v6: 25.0 (v5 reproduced) -> 37.8 demand 400 TWh -> 36.2 bio and geo subtracted -> 36.8 hydro 43.4 TWh -> 37.6 PECD profiles -> 36.9 PV curve and existing PV -> 38.0 wind curve -> 38.5 grid cost and reserve.
- v6 to v7 at 6 h and fixed cost 598 (PI): 38.4 (v6 rerun) -> 27.9 imports -> 27.9 new pumped hydro -> 26.4 geothermal -> 23.3 bioenergy -> 23.3 solar thermal, compressed air, hydrogen -> 23.9 smart charging and interruptible load -> 23.9 full model.
- As told to the owner: 38.5 (v6) -> 27.9 with imports -> 23.9 with other technologies -> 14.1 with owner's costs -> 16.0 at 3 h -> 23.0 with net self-sufficiency.

"About 70%" is the first PDF: 74% at 7,600 EUR/kW (84-85% in its 5,000 cases). A central share of about 15% was not found: the lowest central results are 14.1 GW (25.6%, 6 h) and 16.0 GW (28.9%, 3 h). Shares near 15% appear only with capital at 7% (OB 15.4% at 3 h under the new rule; PI 11.9% under the old).


## 2. Error log

98 entries, in time order. Found by: O = owner objection, R = independent review or audit, S = self-check by the main session or a working agent. Pat = pattern letter (section 3). Small wording slips caught in the same review are grouped in one entry. By category: cost input 15, source citation 7, model code 6, data 7, method 26, wording or claim 33, document build 4. By status: fixed 80, declared as limit 12, still open 6.

| # | Version, date | Category | What was wrong | Found | Correction | Effect on the nuclear result | Status | Pat |
|---|---|---|---|---|---|---|---|---|
| 1 | 19 Oct, chat | cost input | Flamanville 23.7 bn all-in (with financing) used as the nuclear cost and delay reference: an outlier, not comparable with overnight costs | O | median build time (6.3 y, 5.7 since 1990); Flamanville about 8,000 EUR/kW overnight | not quantified (no model yet) | fixed | B |
| 2 | 19 Oct, chat | wording or claim | "Above 8,300 EUR/kW nuclear does not pay", taken from an unpublished study against the project's own calculation | O | retracted | not quantified | fixed | F |
| 3 | 19 Oct, chat | source citation | "RSE 16-17 bn" was a Newcleo spokesman's claim | S | dropped | none | fixed | C |
| 4 | 19 Oct, monthly paper | method | 100% nuclear at 90% load factor on flat demand compared with seasonally penalised renewables; the recommended mix was never computed | R | hourly LP built | stand-alone cost at 75% load factor 66/104/156 EUR/MWh instead of 59/92/134 | fixed | D |
| 5 | 19 Oct, monthly paper | cost input | Base cost 5,000 EUR/kW called "ministerial": per the reviewer it is a promotion platform's estimate for SMRs, interest excluded, while SMR studies were dismissed elsewhere | R, O | 7,600 (Dukovany) made central, 9,100 added; 5,000 kept as series case until v6, dropped in v7 | 7,600 at 7% and 10 y: 125 EUR/MWh against 92 at 5,000 | fixed | A |
| 6 | 19 Oct, monthly paper | method | Grid cost (13.7 EUR/MWh) charged to renewables only; nuclear had no grid, reserve, decommissioning or waste cost | R | back-end fee in v2; grid on both sides in v6 (PV 13, wind 8, nuclear 2 EUR/MWh) | reviewer estimate +5 to +15 EUR/MWh on nuclear | fixed | D |
| 7 | 19 Oct, monthly paper | method | Greenfield renewable mix: existing hydro, bioenergy, geothermal, imports left out | R | hydro in the hourly model; bio, geo and existing fleets in v6; imports in v7 | reviewer estimate: mix 10 to 25 EUR/MWh cheaper | fixed | D |
| 8 | 19 Oct, monthly paper | data | Wind GW from the old fleet's 19.5% capacity factor (124 GW); one-year monthly profile | R | PECD 2030 profiles in v6 (2,227 h) | not quantified | fixed | I |
| 9 | 19 Oct, monthly paper | source citation | Seasonal hydrogen at 37.6 EUR/kg from a press release on salt caverns in Northern Ireland, electrolysers and turbines excluded; seasonal Li-ion (over 2,200 EUR/MWh) used as a straw man | R | marked as lower bound; v7 uses a storage study (Hystories) | none on the share | fixed | C |
| 10 | 19 Oct, monthly paper | wording or claim | Comparatives false against the paper's own table: "least cost in all real scenarios" (nuclear 134 above the mix 108-129); "cheaper than the mix at 5%" (100 against 98); "best case never below nuclear" (nuclear 103-145 at 6-7% against 90) | R | reworded | none | fixed | F |
| 11 | 19 Oct, monthly paper | wording or claim | Unsupported absolutes: "the only peer-reviewed study", "delays depend largely on public choices" (evidence only for the USA), capital "towards 4-5%" without source; best case 76 hid battery losses (+3.8) and a 1.08 exchange rate | R | hedged or declared | none | fixed | F |
| 12 | 19 Oct, monthly paper | method | Interest during construction (13% and 42%) below Banca d'Italia (17% and 49%) without saying so | R | declared | reviewer estimate +1 to +4 EUR/MWh on nuclear | declared as limit | D |
| 13 | 19 Oct, monthly paper | method | Nuclear at 4-5% public capital, renewables at market auction prices; Hinkley and Vogtle omitted, Dukovany (lowest reference) presented as the European case | R | equal-financing variant (v2); uniform 7% rule and risk case (v7) | reviewer estimate: mix 118 -> about 103 EUR/MWh | fixed | D |
| 14 | 19 Oct, hourly model 1 | wording or claim | Recommendation "25-35 GW, 55-80%" not what the model gave (26-37 GW, 57-85%); two scenarios omitted; condition "7% and 10 y changes it" false (28 GW at 5,000) | R | recommendation written by fixed-cost bands | wording | fixed | F |
| 15 | 19 Oct, hourly model 1 | wording or claim | "Up to about 25 GW of PV" and "PV pays in the South" were not model results (PV 0 with grid cost; 8.4 GW at 75 EUR/MWh) | R | rewritten from the results | none | fixed | G |
| 16 | 19 Oct, hourly model 1 | method | Costs per MWh of total demand (monthly) compared with costs per MWh not met by hydro (hourly): 118 against 135; like for like 118 against 184. Recurred in v5 (132 against 76-92; correct 112.6) and v6 | R (three times) | single declared denominator from v6 | none | fixed | B |
| 17 | 19 Oct, hourly model 1 | method | Nuclear available 100% of the time; renewables implicitly at 6.5% capital against 4-5% (13 EUR/MWh: 135 against 122); one weather year (2019) | R | availability 92%, four years, 10% adequacy margin | 28.5 GW (64%) -> 34 GW (74%), all changes together | fixed | D |
| 18 | 19 Oct, hourly model 1 | wording or claim | Numbers without origin or mislabelled: "grid 155" (135 + 14 = 149; code had no grid parameter), "IEA 4,500 EUR/kW" (5,100 USD/kW), "consistent with the Politecnico study" (13 GW where that study has 0) | R | removed or fixed | none | fixed | A |
| 19 | 19 Oct, v1 | wording or claim | Model called "hourly" (3 h step), "2019 profiles" (2016-2019), "solved jointly over four years" (each year separately) | R | wording fixed; joint runs central from v3 | none | fixed | G |
| 20 | 19 Oct, v1 | wording or claim | Ranges wrong: "34-40 GW, 74-85% at 4-5% and 7 y" (9,100 at 5% gives 30 GW, 62%); sites 4-7 (4-8); rooftop 100-190 (120-185) EUR/MWh; Flamanville 16 (17) years | R | fixed | none | fixed | F |
| 21 | 19 Oct, v1 | document build | Table 2 missing rows and ranges; two rounding rules; wrong cross-reference; one symbol for two quantities; figure axis "% of demand" on normalised bars | R | fixed | none | fixed | J |
| 22 | 19 Oct, v1 | method | Full capacity credit to hydro 15 GW, pumped hydro 7.6 GW and batteries, on a 3-hour-mean peak, not flagged | R | declared; credits made parameters in v6 | see entries 44 and 46 | declared as limit | D |
| 23 | 20 Oct, v1 to v2 | cost input | PV priced at the NZIA auction (66.38 EUR/MWh, 1.1 GW, non-price criteria) instead of the main FER X auction (56.82, 7.7 GW) | O, R (external AI critiques relayed by the owner; exact trigger not found in the records) | 56.82 central, NZIA as variant | v2 NZIA variant 21 GW (39%) against 20 GW (33%) | fixed | A |
| 24 | 20 Oct, v1 to v2 | method | Renewables at nominal 20-year contract prices against nuclear over its full life | O | real lifetime cost: PV 42.2, wind 63.1 EUR/MWh, batteries 11,466 EUR/MWh-yr; nuclear life 80 | old basis 32 GW (68%) -> 20 GW (33%); v1 had 34 GW (74%) | fixed | B |
| 25 | 20 Oct, v1 to v2 | cost input | Nuclear without decommissioning and waste cost, life 60 | O, R | +5 EUR/MWh (Swedish fee 4.7-8.5); life 80 (US licence renewals) | no fee: 21 GW against 20; life 60: 19 against 20 | fixed | D |
| 26 | 20 Oct, v2 | wording or claim | "Market finance and 8-10-year builds" equated with exit (0-4 GW); the table gives 14 GW (7,600, 6%, 8 y) and 18 GW (5,000, 7%, 10 y). v1's "nuclear in every case" also had to go | R, S | fixed in 7 places | wording | fixed | F |
| 27 | 20 Oct, v2 | model code | Load-factor column averaged years with no nuclear as zero (13% instead of 51%) | R | recomputed | none | fixed | H |
| 28 | 20 Oct, v2 | wording or claim | Bias direction stated backwards twice (monthly calculation "favours renewables"; financing asymmetry "favours nuclear" while equal financing gives 85 against 107) | R | fixed | none | fixed | F |
| 29 | 20 Oct, v2 | wording or claim | "42 EUR is 30% above the IEA's 35 USD, in line with lower output": currencies mixed, output explains about 15%. Recurred in v7 (45 USD and +30% should be 47 USD and +35% at 1.1188) | R (twice) | fixed | none | fixed | B |
| 30 | 20 Oct, v2 | wording or claim | Slips: fee "at the centre of 4.7-8.5" (low band); "years beyond 60 weigh about 1" (1.4-2.5); wind 70-95 against 70-100; "nuclear does not enter" where 3 GW are built; "imports remove nuclear" (7 GW stay) | R | fixed | none | fixed | F |
| 31 | 24 Oct, v2 to v3 | method | Central result was the mean of single-year optimisations (perfect foresight each year): the no-nuclear system looked cheap (107) | O, R (Gemini critique relayed; owner: how can the optimum cost little less than full renewables) | four years optimised jointly | 20 GW (33%) -> 23 GW (36%); gap 13 -> 25 EUR/MWh | fixed | D |
| 32 | 24 Oct, v3 | data | Hydro minimum 30% of the monthly mean without basis | O, R | 37% (run-of-river share, Terna table dated 31/12/1999) | none: 23 GW; 0.6 and 1.5 EUR/MWh | fixed | I |
| 33 | 24 Oct, v3 | wording or claim | "14-22 GW with market finance" (14-28); "20-34%" (20-48%); "plan below the optimum in 11 of 12 cases" (9 below, 2 inside, 1 above); also in the v3 facts file | R | fix4 | wording | fixed | F |
| 34 | 24-25 Oct, v3 | wording or claim | "The gap of 25 is a lower bound; all simplifications go one way; imports are the only one against": flexibility (gap 17), imports (9) and 100-hour storage (7) go the other way | R, S | "simplifications in both directions" | none | fixed | F |
| 35 | 24 Oct, v3 | wording or claim | "Hydro matters little, 1-2 EUR/MWh": the inflow year moves the gap from 16 (2023) to 30 (2024). Variant with nominal prices described without its 60-year life and missing back-end fee | R | fix4, fix5 | 24 GW (dry) and 28 GW (wet) against 23 | fixed | F |
| 36 | 24 Oct, v3 | wording or claim | Nuclear load factor of 56% defended with a fuel-cost argument; owner: wrong. The rewrite ("seasonal, not daily") was wrong again: winter output is bimodal | O | forced runs (12 GW: 106-108 against 97; flat at 92%: 101; wind fixed 0-65 GW: 98-103); third explanation | none: 23 GW confirmed | fixed | F |
| 37 | 24 Oct to 7 Nov | method | 8% unavailability spread evenly over the year: direction known, only mentioned | S, R | monthly availability 0.97 and 0.87 (v5) | flat: 26.1 GW, 98.0 EUR/MWh against 24.8 GW, 94.9 | fixed | D |
| 38 | 25 Oct, v4 | wording or claim | Gap with flexibility 16 (17); 0.6/1.4 (1.5); leftover "most point the same way"; long storage missing from the Italian limits | R | fix12 | none | fixed | E |
| 39 | 7 Nov, v4 to v5 | method | PV unlimited at the auction price and 1,066 h for every GW, although scarce land had been agreed in chat (386 GW of PV without nuclear) | O | PV supply curve: ground 50 GW cap, rooftops 80 GW at 61.2, agrivoltaic at 53.4 EUR/MWh | unlimited PV 22.3 GW (37%) -> 24.8 GW (45%) | fixed | G |
| 40 | 7 Nov, v5 | method | Wind unlimited at 63.1 EUR/MWh (166 GW without nuclear) | R | declared in v5; finite blocks in v6 | v6 bridge 36.9 -> 38.0 GW; no-nuclear +33.0 EUR/MWh | fixed | D |
| 41 | 7 Nov, v5 | method | Auction-price conversion may count the years after the contract twice (life equal to contract: PV 49.7, wind 74.4 EUR/MWh) | R | variant proposed; no run found in the records | v3 proxies: PV at 49.3 gives 26 GW, wind at 74.2 gives 27 GW (against 23) | still open | D |
| 42 | 7 Nov, v5 | model code | Documents said the model included about 17 TWh of bioenergy; the code had no bioenergy or geothermal; the 17 TWh had no source | R, S | texts corrected; v6 subtracts 8 + 5.3 TWh; decision variables in v7 | v6 bridge 37.8 -> 36.2 GW | fixed | G |
| 43 | 7 Nov, v5 | method | Grid cost zero in the central case | R | v6: PV 13, wind 8, nuclear 2 EUR/MWh, double above 137 GW | v6 bridge 38.0 -> 38.5 GW; no-nuclear +22.9 EUR/MWh | fixed | D |
| 44 | 7 Nov, v5 audit | model code | The adequacy rule, not dispatch, sets batteries (104 GWh) and, with the PV cap, the plateau (24.8 GW at three fixed costs) presented as robustness; 104 GWh was in the recommendation | R | declared; GWh removed from the recommendation; credit variants (78-191 GWh) | margin 1.0: 25.1 GW against 24.8 | declared as limit | F |
| 45 | 7 Nov, v5 audit | model code | Imports not in the adequacy constraint while the text called them free reserve capacity | R | v6: credit 0.5 (assumption) | with 8 GW of imports: v5 13.8 GW, v6 28.4 GW (51%) | fixed | G |
| 46 | 7 Nov, v5 audit | method | Hydro 15 GW + pumped 7.6 GW at full credit = 36% of the requirement (July hydro sustains 7.1 GW) | R | variant with hydro credit 10 GW | 37.9 GW against 38.5 (v6) | declared as limit | D |
| 47 | 7 Nov, v5 audit | method | Existing PV (37 GW) and wind (12.9 GW) ignored; results compared as additions | R | v6: post-2016 PV 24.2 GW and wind 13.6 GW at O&M only | v6 bridge 37.6 -> 36.9 GW | fixed | D |
| 48 | 7 Nov, v5 audit | wording or claim | Preprint: single-year runs "through SciPy, identical results"; they used another solver interface and the claim could not be checked | R | sentence removed | none | fixed | G |
| 49 | 7 Nov, v5 audit | method | No ramp limits: nuclear goes from 50% to 100% in one step at no cost | R | declared | favours nuclear; not quantified | declared as limit | D |
| 50 | 7 Nov, v5 audit | data | Availability 0.97/0.87 written as fact: an assumption averaging 92% (US 2024 figure; world 83%) | R | labelled assumption; variant with mean 0.84 | v6: 43.0 GW, 104.1 EUR/MWh against 38.5 GW, 97.6 | declared as limit | I |
| 51 | 7 Nov, v5 audit | data | Hydro 46.0 TWh was the 2023-2024 mean (2016-2019: 43.4); pumped hydro 7.6 GW (Terna 7.29); 53 GWh unsourced | R | 43.4 TWh; 7.3 GW; 51 GWh as assumption | v6 bridge 36.2 -> 36.8 GW | fixed | I |
| 52 | 7 Nov, v5 audit | data | Demand of 2024 (312.3 TWh) for a system compared with 2040-2050 plans | R | v6: 400 TWh with heat pumps 15 and vehicles 47 (peak 56.7 -> 76.9 GW); plan compared in shares | v6 bridge 25.0 -> 37.8 GW | fixed | B |
| 53 | 7 Nov, v5 audit | data | PV and wind profiles were actual output rescaled to 1,066 h and 1,709 h every year: imposed capacity factor, no year-to-year variation, PV series covering about 80% of output | R | PECD capacity factors, not rescaled (1,375 h, 2,227 h) | v6 bridge 36.8 -> 37.6 GW | fixed | I |
| 54 | 7 Nov, v5 audit | cost input | Auction price at 1,066 h implies about 553 EUR/kW against 800 used for rooftop and agrivoltaic mark-ups; capital share 80% (76.4%); long storage at an implicit 1.08 USD/EUR (1.1188 elsewhere) | R | 76.4% in v6; exchange rate declared; level mismatch: no correction found | not quantified | still open | B |
| 55 | 7 Nov, v5 audit | source citation | 20% indexation of auction prices rests on one press article, unverified for wind | R | declared assumption (0%: PV 40.7; 100%: 48.2 EUR/MWh) | not quantified | still open | C |
| 56 | 7 Nov, v5 audit | wording or claim | "The share depends almost only on the fixed cost" is an identity of the model; band reported as a range of shares; gaps from rounded numbers (32 for 31.1); hand-typed figure values | R | reworded; figures read the result files | none | fixed | F |
| 57 | 7 Nov, v5 audit | wording or claim | Numbers without origin: "55% through batteries", gas variant 62-78 (recomputed 65-72), "912 scenarios" | R | removed | none | fixed | A |
| 58 | 7 Nov, v5 audit | wording or claim | Summary: "25 GW buildable by 2050; uranium, supply chain and materials are not the bottleneck", against the paper's own sections on enrichment, forgings, fuel and regulator staff; build rate unsourced | R | rewritten; pace set against France 1977-1990 | none | fixed | F |
| 59 | 7 Nov, v5 audit | source citation | "Disposal is already in the auction price" cited to a study on waste volumes; "11-163%" is an inversion of the published 10-62%; "countries changed course" unsourced | R | laws cited; marked as own conversion; sources added | none | fixed | C |
| 60 | 7 Nov, v6 research | data | 1,940 ha/GW (1,700); South "a third" more output (10-16% for new plants); rooftops 70-92 GW (140-193) | S | corrected in v6 | none on the headline | fixed | A |
| 61 | 7 Nov, v6 review | method | Imports set to zero in the central case with no number to justify it; no other firm zero-emission option (hydrogen, gas with capture, more geothermal or bioenergy, demand response) | R, O ("no arbitrary choices") | v7: every technology a decision variable | 38.4 -> 27.9 GW with imports -> 23.9 GW with the rest (6 h) | fixed | D |
| 62 | 7 Nov, v6 review | method | No-nuclear cost 204.2 was a cost with every supply block at its cap, on curves estimated by the author | R | declared; range 147-204 | none on GW | declared as limit | F |
| 63 | 7 Nov, v6 review | wording or claim | "Always at least 50 EUR/MWh above" (minimum 45.8); "high PV curve (375 GW)" (375 built of 511 available); load factor "50-79%" (56-75%) | R | fixed | none | fixed | F |
| 64 | 7 Nov, v6 review | document build | Placeholder "[RITMO]" left in the preprint; replacement debris and code names in a table; "25 k EUR/MW" for 25 EUR/MWh | R | fixed | none | fixed | J |
| 65 | 7 Nov, v6 review | source citation | Dukovany source did not state 1,055 MW, the signature or the "3.2-3.4 bn preparatory works" behind the 9,100 case (no source found); Flamanville figures cited to a newspaper giving others; wind cost source cited as anonymous with a wrong title | R | sources replaced; 9,100 labelled unverified, dropped in v7 | 9,100 cases rested on it (30.4 GW at 7% and 10 y) | fixed | C |
| 66 | 8 Nov, v7 | model code | Import availability of 38% in the worst weeks applied to the reserve only, not to dispatch | S | code patch | no-nuclear 80.97 -> 84.52 EUR/MWh | fixed | H |
| 67 | 8 Nov, v7 | cost input | Solar thermal at 4,100 h from a simulation of a 1 MW plant, world-average cost, fixed credit 0.95; hydrogen store cost unit unclear | S | 2,900 h, 9,491 and 3,287 EUR/kW, credit from the profile (0.972) | no-nuclear cost 84.52 -> 89.82 EUR/MWh; optimal nuclear 15.5 -> 19.1 GW (gross Dukovany cost, PI) | fixed | A |
| 68 | 8 Nov, v7 | cost input | Central nuclear cost left at the gross Dukovany price (7,750 with about ten years of fuel), against the cost rule applied to other technologies | O | five cost cases; central net of fuel | 19.1 GW (34.8%) -> 23.9 GW (44.3%), 6 h | fixed | B |
| 69 | 8 Nov, v7 | cost input | Fuel deducted at the whole 15 EUR/MWh variable cost (1,183 EUR/kW): central 6,570, a bias for nuclear | S | fuel only, 4.91 EUR/MWh: 387 EUR/kW, central 7,360 | not run as headline; curve has 26.8 GW at fixed cost 540, 23.9 at 598 | fixed | D |
| 70 | 8 Nov, v7 | method | Single cost-to-share curve dropped for case-by-case runs and bisection | O (twice) | curve restored, cases read as points | none | fixed | J |
| 71 | 8 Nov, v7 | model code | Threshold at 15 years written 7,200 EUR/kW (7,970); 7% figures 6,670, 4,920, 11,000 mixed two discount rates | S | formula checked by round trip | none | fixed | H |
| 72 | 8 Nov, v7 | method | "7% only matters for the conversion"; at 7% auction-priced technologies barely rose (PV 42.2 -> 44.3) while capex ones took the full rate; grid cost, nuclear's too, did not scale | S | uniform rule: PV 49.88, wind 74.61, grid x1.287 | central at 7%: 9.7 GW (first plant), 2.4 GW (target), 6 h | fixed | B |
| 73 | 9 Nov, v7 | document build | Code patched only on a remote sandbox that was wiped: results file, two patches and data lost | S | rebuilt locally; 5 reference cases within 0.02 EUR/MWh and 0.05 GW | none | fixed | J |
| 74 | 9 Nov, v7 | method | 6-hour step (memory limit) understates nuclear; first correction measured on two years only | S | 3 h runs on four years; extrapolation to 1 h only for the first-plant case | 23.9 -> 24.4 GW; gap 9.66 -> 11.22 EUR/MWh | fixed | D |
| 75 | 9 Nov, v7 | cost input | Risk case 9,900: passed on as a "range 8,400-9,900"; Olkiluoto 9,500 and Mochovce 8,060 had no source and could not be reproduced | S | recomputed 9,064 and 8,756; median 9,680 | risk case 4.6 -> 5.1 GW | fixed | A |
| 76 | 9 Nov, v7 | cost input | Fuel at 4.91 EUR/MWh implied an unchecked inflation factor 1.189 (official 1.1736: 4.85); documents said 7,360 "could not be reconstructed"; Flamanville in 2015 euros (8,000) beside 2025 costs (10,300) | S | 382 EUR/kW, central 7,370; Flamanville restated | none | fixed | A |
| 77 | 9 Nov, v7 review | cost input | Owner's costs missing from the central Dukovany cost while Vogtle and the risk case include them; "excludes owner's costs" had no source | R | divided by (1 - 0.1257): 8,430, then 8,540 EUR/kW | 24.4 GW (45.6%) -> 16.3 GW (29.5%), 3 h | fixed | B |
| 78 | 9 Nov, v7 review | source citation | Dukovany citation contained neither the 407 bn CZK price nor the fuel statement | R | correct article and ministry release cited | none | fixed | C |
| 79 | 9 Nov, v7 review | cost input | Fuel inside the Dukovany price: one source says yes, three report fuel as a separate 15-20 bn CZK | R | first source kept by choice; other reading 8,980 EUR/kW | old rule 13-14 GW against 16; new rule, 6 h, 18.2 against 20.5 GW | still open | C |
| 80 | 9 and 11 Nov | wording or claim | "A 15-year build leaves a few GW": true only with the risk cost; at the central cost 13.1 GW then, 11.9 GW now (first plant, 6 h). Came back on 11 Nov as "below 10 GW even at central cost" | R (twice) | the two cases separated | wording | fixed | F |
| 81 | 9 Nov, v7 review | wording or claim | 3 h headline next to unlabelled 6 h values; reactor count on 1.4 GW units (17) for a 1,055 MW reactor (23); target-case model said to have no SMR while tables show SMR runs; stale "17 reactors" after reruns | R | labelled and fixed | none | fixed | B |
| 82 | 9 Nov, v7 review | cost input | Barakah 4,371 documented as 24.4 bn USD of total financing over 5.6 GW (interest counted twice); the writer's earlier doubt had been dismissed. Vogtle 15,540 without derivation | R | Barakah from the 20.4 bn contract plus owner's costs: 4,670; Vogtle recomputed 15,656, kept | Barakah point 36.0 -> 34.5 GW (old rule, 6 h) | fixed | A |
| 83 | 9 Nov, v7 review | source citation | Bibliography: wholesale and gas price inputs without URL (the gas figure is a market index, not the hub price); 128 of 138 entries undated; grid lifetimes uncited; Olkiluoto "$11bn ($12bn)" read as euros | R | completed; Olkiluoto reading declared | none | fixed | C |
| 84 | 9 Nov, v7 | cost input | US price index for 2009-2015 taken from memory; CZK/EUR assumed at 25 | S | official series; ECB 2025 mean 24.688 | 8,430 -> 8,540: 16.3 -> 16.0 GW | fixed | A |
| 85 | 9 Nov, v7 | cost input | Owner's-cost share (12.57%) from a US database; European reference 15-20% of the contract price, primary study not read | S | declared; 20% gives 8,962 EUR/kW | old rule about 13 GW against 16 | declared as limit | I |
| 86 | 10 Nov | wording or claim | Each headline presented with more confidence than it deserved (admitted); "the result should not move much any more" one day before 16 -> 23 GW | O ("from 70 to 26") | curve and conditions shown instead of one number | none | fixed | F |
| 87 | 10 Nov | wording or claim | Bridge given to the owner starts "first PDF (v5), 5,000 EUR/kW, about 70%": the first PDF had 74% at 7,600; v5's central was 45% at 7,600; steps 74 -> 33 -> 36 -> 45 -> 59 left out | this audit | none found | none | still open | F |
| 88 | 10 Nov | wording or claim | Model imports (9% of demand) defended by comparison with today's 15.1% | O | withdrawn | none | fixed | B |
| 89 | 10 Nov, v7 to v8 | method | Imports without exports: up to 18.9 GW at a fixed price in all normal hours, nothing returned, 38% of import capacity counted as firm in critical weeks (the v7 spec had asked for exports) | O, then S | net self-sufficiency: yearly imports no greater than exports, exports unpaid, no foreign help in critical weeks | 15.95 GW (28.9%) -> 23.0 GW (44.7%), 3 h | fixed | D |
| 90 | 10 Nov | method | Decision rule replaced within minutes: first "new central only if the insurance costs under about 2 EUR/MWh", then "must work if every country plans alike"; the measured cost is 3.0 to 3.8 EUR/MWh (with nuclear, PI, 6 h) | this audit | documents declare the rule a policy choice | the first rule would have kept the 16 GW central | declared as limit | F |
| 91 | 11 Nov, v8 review | document build | Preprint compiled with old-rule figures; old-rule numbers left in methods, land use (256,000 ha, now about 300,000), batteries (187 GWh, now 205), plan range (8,000-10,400, now 9,300-12,200 EUR/kW), comparisons with other studies | R | rebuilt and fixed | none | fixed | E |
| 92 | 11 Nov, v8 review | wording or claim | Gaps mixed the two import rules (3.71 and -0.27 instead of 10.88 and 7.86 EUR/MWh) | R | fixed | none | fixed | B |
| 93 | 11 Nov, v8 review | wording or claim | Old rule said to rely on 4.4 GW from abroad in critical weeks; it was 0.38 x 18.2 = 6.9 GW | R | fixed | none | fixed | G |
| 94 | 11 Nov, v8 review | wording or claim | "The cost of capital changes the result more than anything": 7% gives 11.4 and 7.6 GW, 15-year builds 11.9 and 7.9, the risk case 9.0 and 4.6 (6 h). Also "under 1.5%" (1.52%), "nearly halve" (halve or more) | R, S | "fixed cost: financing and build time" | wording | fixed | F |
| 95 | 11 Nov, v8 | wording or claim | "At 3 h the thresholds rise" written before any 3 h point; the target-case threshold "765, about 10,100 EUR/kW" interpolated across a step | R, S | withdrawn from the documents; still in facts_v7.md 16.7 | none | still open | F |
| 96 | 11 Nov, v8 review | wording or claim | Sensitivities on solar thermal, SMR, gas with capture and import price called "upper bounds": they are old-rule results, not rerun | R | reworded as not recomputed | unknown under the new rule | declared as limit | E |
| 97 | 11 Nov, v8 review | wording or claim | Import rule: unpaid exports called "prudent"; rule not listed among choices favouring nuclear (gap 6.11 -> 9.00); neighbours always absorb exports; share counts exported nuclear output | R | declared | see section 4 | declared as limit | D |
| 98 | 11 Nov, v8 | method | 7% runs switch off wave, new pumped hydro and SMR (target case also 100-hour storage and new hydro): different technology sets across rates and cases | S | checked that none is built at 5%; target case declared not comparable | none found | declared as limit | B |

Raised and not upheld: battery auction premium as full cost (confirmed as a fair estimate, slightly low); two table-cell errors claimed by an external AI review; "too much wind" (forced runs confirmed the optimum). Errors in the political part of the first chat are outside this log.

## 3. Patterns

| Pat | Recurring kind of error | Entries |
|---|---|---|
| A | Numbers from memory or without a traceable source or derivation | 10 |
| B | Non-homogeneous comparisons (denominators, currencies and price years, discount rates, time steps, import rules, cost scope) | 13 |
| C | Citation that does not support the number | 8 |
| D | One-sided simplifications and asymmetries (one technology gets a cost, limit or option the other does not) | 21 |
| E | Stale numbers left in the text after a model change | 3 |
| F | Claims stronger than the results, or contradicting the project's own tables | 23 |
| G | Text describing something the model did not do | 7 |
| H | Code or arithmetic slips | 3 |
| I | Unverified assumptions or proxy data treated as fact | 6 |
| J | Process and build failures | 4 |

## 4. Still open

Declared in the documents or the records, not corrected.

| # | Open bias or limit | Direction on nuclear | Recorded size |
|---|---|---|---|
| 1 | Fuel inside the Dukovany price: sources conflict | less nuclear if fuel is extra | 8,980 EUR/kW: 18.2 against 20.5 GW (PI, 6 h) |
| 2 | Owner's costs 12.57% from US data; European reference 15-20% of the contract price | less nuclear | about 18 GW against 20.5 (PI, 6 h, read off the curve) |
| 3 | Risk-case inputs: Olkiluoto currency reading, Mochovce price year, Vogtle not rederived | risk case only | median 9,680, or 9,528 with the other reading |
| 4 | Time step 3 h; 1 h not reachable with the data | nuclear understated | PI gap 10.88 -> about 11.95 EUR/MWh; OB not estimable; GW at 1 h not found |
| 5 | Worst-weather years, 15-year builds, risk case and most thresholds only at 6 h or interpolated; four weather years in the central case | nuclear understated | worst years: 30.8 GW (PI), 24.3 (OB) against 20.45 and 18.35 |
| 6 | Single zone with a flat grid charge; no stability services for an inverter-based grid | favours no-nuclear | not quantified |
| 7 | PV and wind supply curves, hydrogen and compressed-air costs are own estimates or from studies; hydrogen storage in depleted fields exists only as pilots | favours no-nuclear | hydrogen cuts the no-nuclear cost by 16 EUR/MWh (v7 bridge) |
| 8 | Nuclear availability 92%, own assumption | favours nuclear | v6: mean 0.84 adds 6.5 EUR/MWh |
| 9 | No ramp limits; full capacity credit to hydro and pumped hydro; evening vehicle charging; flat bio and geo; no common-mode outages; no demand flexibility beyond smart charging and interruptible loads | favours nuclear | not quantified in v8 |
| 10 | Import rule is a policy choice | favours nuclear | 14.15 -> 20.45 GW; gap 6.11 -> 9.00 EUR/MWh (PI, 6 h) |
| 11 | Neighbours always absorb Italian exports; the share counts exported nuclear output (16.2 TWh at 3 h) | first favours no-nuclear, second inflates the share | no-nuclear system exports 31.7 TWh |
| 12 | Sensitivities on solar thermal, SMR, gas with capture and air capture, import price still on the old import rule | unknown | old rule: air capture at target cost cut the gap 9.66 -> 4.84 |
| 13 | OB model reduced (no 100-hour storage, wave, new pumped hydro, new hydro, SMR); 7% runs use reduced sets | OB not comparable with PI | no-nuclear 92.23 against 96.46 (6 h) |
| 14 | Auction-price conversion: 20% indexation from one press source; years after the contract possibly counted twice | nuclear understated if counted twice | PV 49.7 instead of 42.2 EUR/MWh |
| 15 | Own assumptions without source: solar thermal cap 10 GW; 100-hour storage life 20 y and O&M 20%; gas-with-capture build 3 y; grid scaling 1.287 at 7%; air-capture costs; pumped hydro 51 GWh; hydro floor 37% from a 1999 table | mixed | not quantified |
| 16 | Hydro budgets repeat the 2023-2024 monthly shape in every weather year | unknown | v3: gap 16 to 30 EUR/MWh across inflow years |
| 17 | Steady-state system: no build-rate limit or transition path (23 GW is about 22 reactors of 1,055 MW) | feasibility, not cost | not modelled |
| 18 | Record-keeping: facts_v7.md 16.7 keeps the withdrawn OB threshold; the 10 Nov bridge misstates its first step; PV price level against the 800 EUR/kW mark-up base never reconciled | none on the headline | none |
