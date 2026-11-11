# Numeri del modello v7 (esecuzione locale, agente ad1d092a)

Convenzioni. Costo di sistema in EUR/MWh sulla domanda non coperta da idroelettrico esistente (356.6 TWh, colonna cost_new); N = nucleare GW; quota = quota nucleare sulla domanda totale (400 TWh). Tutte le esecuzioni: modo ZD (zero emissioni dirette), passo 6 h, anni di carico e meteo 2016 a 2019 ottimizzati insieme, import con prezzo x1.17 e disponibilita 38% nelle 3 settimane critiche di ogni anno (dispatch e riserva), salvo dove scritto. PI = caso primo impianto per le tecnologie senza impianti commerciali, OB = caso obiettivo, con il modello ridotto (senza onde, LDES, pompaggio nuovo, idroelettrico nuovo, SMR). Ogni numero ha il tag della esecuzione (colonna run) in D/v7run/results.jsonl; tutti i punti sono in D/repo/results/v7.json e v7_sweep.json. I valori marcati 'riferimento' vengono da D/v7res/reference_points.md (agente precedente, non rieseguiti salvo la convalida).

## 1. Formula fixN e capex

fixN (EUR/kW-anno) = capex x idc(r,y) x CRF(r,80) + parte fissa, con idc(r,y) = somma per k da 0 a y meno 1 di (1+r)^(y meno k meno 0.5), divisa per y, e CRF(r,n) = r(1+r)^n/((1+r)^n meno 1). Parte fissa: O&M 17 EUR/MWh x 0.9 x 8760 = 134.03, piu rete 2 EUR/MWh x disponibilita media x 8760 = 16.11 al 5%; al 7% la rete e moltiplicata per CRF(7%,40)/CRF(5%,40) = 1.287, quindi 154.77 (assunzione nostra per la scala della rete, ARERA 615/2023 per i costi). Inversa: capex = (fixN meno parte fissa) / (idc x CRF80).

| caso | capex EUR/kW | anni | r | fixN calcolato |
|---|---|---|---|---|
| Saeul | 2965 | 8 | 5% | 335.2 |
| Barakah | 4371 | 8 | 5% | 423.0 |
| Dukovany netto (centrale) | 7370 | 7 | 5% | 598.4 (esecuzioni a 598, capex 7363.6) |
| rischio (mediana di 4 costruzioni) | 9680 | 15 | 5% | 878.3 (risultati letti sulla curva) |
| rischio al 7% | 9680 | 15 | 7% | 1334.2 (oltre l'ultimo punto con import) |
| Vogtle | 15540 | 10 | 5% | 1172.2 |
| Dukovany netto al 7% | 7370 | 7 | 7% | 817.5 (esecuzioni a 817) |

Parte fissa: 150.14 al 5%, 154.77 al 7% (funzioni fix0 e capex_from_fix in driver7.py). Le esecuzioni usano capex = capex_from_fix(fixN) con 7 anni e r = 5% (o 7%).

## 2. Fattori al 7% per tecnologia

Regola unica: la parte capitale delle tecnologie con costo a offerta o a capex viene moltiplicata per CRF(7%,vita)/CRF(5%,vita); O&M, combustibile e prezzo dell'energia importata restano invariati. Il nucleare usa il proprio r (idc e CRF a 80 anni). Rapporti CRF calcolati:

| vita (anni) | CRF(7%)/CRF(5%) | tecnologie con quella vita |
|---|---|---|
| 20 | 1.1763 | biomasse e rifiuti, elettrolizzatore, LDES (assunzione nostra) |
| 25 | 1.2094 | geotermico nuovo, CSP, idroelettrico nuovo |
| 30 | 1.2388 | FV, eolico (vita 30 anni dopo conversione dal contratto di 20), pompaggio nuovo, CAES, gas CCS |
| 35 | 1.2646 | turbina H2 |
| 40 | 1.2871 | rete (ARERA 615/2023), import (cavi) |
| 60 | 1.3483 | SMR |
| 80 | 1.3779 | nucleare grande (con idc) |

Fattori complessivi sul costo (capitale piu O&M) riportati dall'agente precedente e verificati dalla convalida: FV e eolico 1.1826 (quota capitale 0.764), batterie 1.1117, LDES 1.141 (vita 20 anni e O&M 20% sono assunzioni nostre), rete x1.287, nucleare centrale fixN 598 a 5% e 817 a 7% (x1.366). Per le altre tecnologie il fattore complessivo dipende dalla quota di O&M (in techs_v7.json) e non e stato tabulato separatamente: nel codice si applica solo il rapporto CRF qui sopra alla parte capitale.

## 3. Convalida (prima di ogni esecuzione nuova)

| run | atteso (riferimento) | ottenuto | scarto |
|---|---|---|---|
| val_PI_none | 89.82 EUR/MWh, 0.0 GW | 89.81 EUR/MWh, 0.0 GW | -0.005 EUR/MWh, +0.00 GW |
| val_OB_none | 84.97 EUR/MWh, 0.0 GW | 84.97 EUR/MWh, 0.0 GW | -0.002 EUR/MWh, +0.00 GW |
| sw_PI_imp_598 | 80.14 EUR/MWh, 23.9 GW | 80.16 EUR/MWh, 23.9 GW | +0.018 EUR/MWh, -0.01 GW |
| sw_OB_imp_598 | 79.57 EUR/MWh, 23.4 GW | 79.59 EUR/MWh, 23.3 GW | +0.019 EUR/MWh, -0.05 GW |
| sw7b_PI_817 | 93.57 EUR/MWh, 9.7 GW | 93.57 EUR/MWh, 9.7 GW | +0.001 EUR/MWh, -0.04 GW |

Tolleranza richiesta 0.05 EUR/MWh e 0.2 GW: rispettata in tutti e 5 i casi (i valori attesi sono arrotondati a 0.01 e 0.1).

## 4. Con import, 5% (riferimento, non rieseguito) e soglie

Tabella con import al 5% (riferimento piu le due esecuzioni di convalida a fixN 598).

| fixN | PI costo | PI N GW | PI quota | OB costo | OB N GW | OB quota | fonte |
|---|---|---|---|---|---|---|---|
| 335 | 56.55 | 39.3 | 72.2% | 56.30 | 38.6 | 71.3% | PI:rif, OB:rif |
| 360 | 59.25 | 38.3 | 71.5% | 58.96 | 37.9 | 70.8% | PI:rif, OB:rif |
| 423 | 65.87 | 36.0 | 67.6% | 65.48 | 35.4 | 66.5% | PI:rif, OB:rif |
| 460 | 69.46 | 33.1 | 61.8% | 68.99 | 32.6 | 61.1% | PI:rif, OB:rif |
| 540 | 75.98 | 26.8 | 50.0% | 75.48 | 26.5 | 49.7% | PI:rif, OB:rif |
| 598 | 80.16 | 23.9 | 44.3% | 79.59 | 23.3 | 43.5% | PI:run, OB:run |
| 618 | 81.36 | 19.6 | 35.7% | 80.79 | 19.3 | 35.3% | PI:rif, OB:rif |
| 638 | 82.34 | 16.0 | 29.0% | 81.74 | 15.5 | 28.4% | PI:rif, OB:rif |
| 658 | 83.21 | 14.9 | 27.0% | 82.56 | 14.1 | 25.8% | PI:rif, OB:rif |
| 678 | 84.02 | 14.1 | 25.5% | 83.30 | 11.4 | 20.9% | PI:rif, OB:rif |
| 698 | 84.80 | 13.4 | 24.3% | 83.83 | 7.2 | 13.2% | PI:rif, OB:rif |
| 718 | 85.53 | 12.6 | 22.7% | 84.17 | 4.6 | 8.5% | PI:rif, OB:rif |
| 738 | 86.19 | 10.9 | 19.5% | 84.37 | 2.8 | 5.2% | PI:rif, OB:rif |
| 798 | 87.61 | 7.2 | 13.1% | 84.79 | 2.2 | 4.1% | PI:rif, OB:rif |
| 858 | 88.73 | 5.7 | 10.5% | 84.97 | 0.0 |  | PI:rif, OB:rif |
| 895 | 89.25 | 4.6 | 8.4% | 84.97 | 0.0 |  | PI:rif, OB:rif |
| 920 | 89.53 | 3.7 | 6.8% | 84.97 | 0.0 |  | PI:rif, OB:rif |
| 1040 | 89.82 | 0.0 |  | 84.97 | 0.0 |  | PI:rif, OB:rif |
| 1172 | 89.82 | 0.0 |  | 84.97 | 0.0 |  | PI:rif, OB:rif |

Senza nucleare: PI 89.81 (run val_PI_none), OB 84.97 (run val_OB_none). Soglie sotto 10 GW da interpolazione lineare dei punti 6 h: 
- PI: tra fixN 738 e 798, interpolato 753 EUR/kW-anno, capex equivalente 9905 EUR/kW a 7 anni, 8009 a 15 anni.
- OB: tra fixN 678 e 698, interpolato 685 EUR/kW-anno, capex equivalente 8789 EUR/kW a 7 anni, 7106 a 15 anni.

## 5. Senza import, 5% (esecuzioni locali)

Modello PI completo con import spento; OB con il modello ridotto. Senza nucleare: PI 120.17 (riferimento, confermato dal punto fixN 1140 che da 120.171 con N = 0), OB 101.57 (run sw_OB_noimp_none).

Tabella senza import al 5%.

| fixN | PI costo | PI N GW | PI quota | OB costo | OB N GW | OB quota | fonte |
|---|---|---|---|---|---|---|---|
| 335 | 58.46 | 42.7 | 73.9% | 58.11 | 41.7 | 73.3% | PI:rif, OB:rif |
| 423 | 68.91 | 41.5 | 72.5% | 68.23 | 39.6 | 72.5% | PI:rif, OB:rif |
| 598 | 88.10 | 36.1 | 60.4% | 85.14 | 29.4 | 56.0% | PI:run, OB:run |
| 700 | 97.46 | 31.3 | 51.7% | 92.79 | 21.6 | 41.7% | PI:rif, OB:rif |
| 800 | 105.44 | 24.6 | 37.9% | 97.35 | 11.5 | 22.0% | PI:run, OB:run |
| 850 |  |  |  | 98.94 | 11.3 | 21.8% | OB:run |
| 900 | 111.71 | 19.3 | 30.0% | 100.50 | 9.9 | 19.1% | PI:run, OB:run |
| 950 |  |  |  | 101.54 | 3.1 | 6.0% | OB:run |
| 960 |  |  |  | 101.57 | 0.0 | 0.0% | OB:run |
| 968 |  |  |  | 101.57 | 0.0 | 0.0% | OB:run |
| 975 |  |  |  | 101.57 | 0.0 | 0.0% | OB:run |
| 1000 |  |  |  | 101.57 | 0.0 | 0.0% | OB:run |
| 1020 |  |  |  | 101.57 | 0.0 | 0.0% | OB:run |
| 1040 | 118.46 | 14.3 | 21.7% | 101.57 | 0.0 | 0.0% | PI:run, OB:run |
| 1080 | 119.64 | 8.2 | 12.5% |  |  |  | PI:run |
| 1110 | 120.17 | 0.8 | 1.2% |  |  |  | PI:run |
| 1140 | 120.17 | 0.0 | 0.0% |  |  |  | PI:run |
| 1172 | 120.17 | 0.0 |  |  |  |  | PI:rif |

- PI senza import: sotto 10 GW tra fixN 1040 e 1080, interpolato 1068 (capex 15093 EUR/kW a 7 anni, 12203 a 15 anni).
- PI senza import: nucleare zero (meno di 0.05 GW) tra fixN 1110 e 1140 (capex tra 15782 e 16275 EUR/kW a 7 anni).
- OB senza import: sotto 10 GW tra fixN 850 e 900, interpolato 897 (capex 12280 EUR/kW a 7 anni, 9929 a 15 anni).
- OB senza import: nucleare zero (meno di 0.05 GW) tra fixN 950 e 960 (capex tra 13151 e 13316 EUR/kW a 7 anni).

Nota OB: tra 800 (11.46 GW) e 850 (11.32 GW) la curva e quasi piatta, poi scende a 9.92 GW a 900 e a 3.13 GW a 950; il nucleare e zero a 960 e oltre (960, 968, 975, 1000, 1020, 1040 tutti a costo 101.57, uguale al caso senza nucleare). La soglia dello zero e quindi tra 950 e 960. Il PI senza import ha il nucleare residuo di 0.83 GW a fixN 1110 e zero a 1140.

## 6. Con 7%: import e senza import

Tabella con import al 7% (riferimento piu la convalida a 817).

| fixN | PI costo | PI N GW | PI quota | OB costo | OB N GW | OB quota | fonte |
|---|---|---|---|---|---|---|---|
| 423 | 66.09 | 37.6 | 71.0% |  |  |  | PI:rif |
| 598 | 81.97 | 26.3 | 49.6% | 81.53 | 26.0 | 49.0% | PI:rif, OB:rif |
| 700 | 88.89 | 20.6 | 38.5% | 88.39 | 19.9 | 37.6% | PI:rif, OB:rif |
| 750 |  |  |  | 90.58 | 12.5 | 23.6% | OB:rif |
| 800 | 93.10 | 10.9 | 20.3% | 91.85 | 3.6 | 6.8% | PI:rif, OB:rif |
| 817 | 93.57 | 9.7 | 17.9% | 91.98 | 2.4 | 4.5% | PI:run, OB:run |
| 900 | 95.29 | 6.2 | 11.6% | 92.37 | 1.2 | 2.4% | PI:rif, OB:rif |

Senza nucleare con import al 7%: PI 97.41, OB 92.52 (riferimento).

Tabella senza import al 7% (esecuzioni locali).

| fixN | PI costo | PI N GW | PI quota | OB costo | OB N GW | OB quota | fonte |
|---|---|---|---|---|---|---|---|
| 598 | 89.07 | 38.9 | 68.0% | 86.88 | 32.6 | 62.6% | PI:run, OB:run |
| 700 | 99.20 | 33.3 | 56.7% | 95.42 | 28.2 | 53.9% | PI:run, OB:run |
| 800 | 107.97 | 27.7 | 45.9% | 102.59 | 18.8 | 36.1% | PI:run, OB:run |
| 900 | 115.66 | 25.9 | 41.8% | 107.22 | 12.5 | 24.0% | PI:run, OB:run |
| 960 |  |  |  | 109.09 | 10.8 | 20.9% | OB:run |
| 1040 | 123.32 | 16.5 | 25.5% | 111.23 | 5.5 | 10.5% | PI:run, OB:run |
| 1100 |  |  |  | 111.64 | 0.0 | 0.0% | OB:run |
| 1172 | 128.84 | 9.6 | 14.4% |  |  |  | PI:run |
| 1300 | 129.91 | 0.0 | 0.0% |  |  |  | PI:run |

Senza nucleare e senza import al 7%: PI 129.91 (run sw7ni_PI_none), OB 111.64 (run sw7ni_OB_none).
- PI senza import al 7%: sotto 10 GW tra fixN 1040 e 1172.
- OB senza import al 7%: sotto 10 GW tra fixN 960 e 1040.

Al 7% il modello usa R = 0.07 (variabile V7_R) e off = IMPORT, WAVE, PUMPED_NEW, SMR (OB anche LDES e HYDRO_NEW), come i punti con import del riferimento.

## 7. Correzione dal passo 6 h al passo 3 h, e convergenza

Metodo. Stesso modello e stessi anni (4 anni, se la memoria lo permette: picco di memoria misurato sotto), passo 6 h contro passo 3 h. I dati sono somme su 3 h: l'ora singola non e possibile. Per la convergenza: serie 12 h, 6 h, 3 h su 2 anni (2018 e 2019) e su 4 anni, stessi punti.

### 7.1 Quattro anni, 6 h contro 3 h

| punto | costo 6 h | costo 3 h | correzione costo | N 6 h | N 3 h | correzione N | run 3 h | RAM picco 3 h (MB) | durata 3 h (s) |
|---|---|---|---|---|---|---|---|---|---|
| PI senza nucleare | 89.81 | 93.90 | +4.09 | 0.0 | 0.0 | +0.00 | s3y4_PI_none_h3 | 1137 | 2539 |
| OB senza nucleare | 84.97 | 88.95 | +3.98 | 0.0 | 0.0 | +0.00 | s3y4_OB_none_h3 | 718 | 1484 |
| PI fixN 598 | 80.16 | 82.68 | +2.52 | 23.9 | 24.4 | +0.49 | s3y4_PI_598_h3 | 1245 | 3572 |
| OB fixN 598 | 79.59 | 82.07 | +2.48 | 23.3 | 24.2 | +0.86 | s3y4_OB_598_h3 | 757 | 1219 |
| PI fixN 750 | 86.54 | 89.69 | +3.16 | 9.6 | 11.3 | +1.70 | s3y4_PI_750_h3 | 1245 | 2896 |
| OB fixN 685 | 83.51 | 86.62 | +3.11 | 10.2 | 13.7 | +3.50 | s3y4_OB_685_h3 | 758 | 1652 |

Scarto (costo senza nucleare meno costo con nucleare a fixN 598), che e il valore del nucleare:

| caso | scarto 6 h | scarto 3 h | correzione |
|---|---|---|---|
| PI | 9.66 | 11.22 | +1.56 |
| OB | 5.38 | 6.88 | +1.50 |

- PI vicino alla soglia: scarto 6 h 3.28, scarto 3 h 4.21, correzione +0.93 EUR/MWh; N a parita di fixN sale da 9.6 a 11.3 GW.
- OB vicino alla soglia: scarto 6 h 1.46, scarto 3 h 2.33, correzione +0.87 EUR/MWh; N a parita di fixN sale da 10.2 a 13.7 GW.

Direzione del bias (misurata): passando da 6 h a 3 h il costo senza nucleare sale piu del costo con nucleare, quindi lo scarto cresce e, a parita di fixN, il nucleare ottimo cresce. Il passo 6 h sottostima quindi il valore del nucleare, la sua capacita ottima e le soglie. Spiegazione plausibile, non verificata: un passo grosso media via la variabilita di breve periodo che solare, eolico e accumuli devono coprire e che il nucleare in base non deve inseguire.

### 7.2 Convergenza 12 h, 6 h, 3 h

Due anni (2018, 2019): costo e scarto, serie 12 h, 6 h, 3 h.

| caso | costo senza nucleare 12/6/3 h | costo fixN 598 12/6/3 h | scarto 12 h | scarto 6 h | scarto 3 h | passo 12 a 6 | passo 6 a 3 | rapporto | N a 598 12/6/3 h |
|---|---|---|---|---|---|---|---|---|---|
| PI | 82.10 / 86.28 / 89.74 | 77.67 / 79.28 / 81.77 | 4.43 | 7.00 | 7.97 | +2.57 | +0.97 | 0.38 | 13.9 / 18.7 / 20.3 |
| OB | 79.66 / 82.86 / 86.50 | 76.94 / 78.73 / 81.22 | 2.72 | 4.13 | 5.28 | +1.42 | +1.15 | 0.81 | 13.6 / 19.1 / 20.7 |

Quattro anni (2016 a 2019): serie 12 h, 6 h, 3 h (6 h e 3 h dalle esecuzioni della sezione 7.1).

| caso | scarto 12 h | scarto 6 h | scarto 3 h | passo 12 a 6 | passo 6 a 3 | rapporto |
|---|---|---|---|---|---|---|
| PI | 5.74 | 9.66 | 11.22 | +3.91 | +1.56 | 0.40 |
| OB | 3.21 | 5.38 | 6.88 | +2.17 | +1.50 | 0.69 |

Estrapolazione di Richardson dello scarto. Si assume scarto(h) = G0 meno c x h^p con h in ore. Dai tre punti: 2^p = (passo 12 a 6)/(passo 6 a 3), poi c x 3^p = (passo 6 a 3)/(2^p meno 1), G0 = scarto(3 h) + c x 3^p, e scarto(1 h) = G0 meno c x 1^p. Il criterio del coordinatore (correzione 6 a 3 h circa meta di quella 12 a 6 h) corrisponde a un rapporto vicino a 0.5.

| anni | caso | rapporto | p | G0 (limite h a 0) | scarto stimato 1 h | correzione 3 a 1 h | giudizio |
|---|---|---|---|---|---|---|---|
| 2y | PI | 0.38 | 1.40 | 8.56 | 8.44 | +0.46 | rapporto tra 0.35 e 0.65: estrapolazione accettabile come stima |
| 2y | OB | 0.81 | 0.30 | 10.26 | 6.68 | +1.40 | rapporto fuori da 0.35 e 0.65: serie non nel regime asintotico, estrapolazione non affidabile |
| 4y | PI | 0.40 | 1.33 | 12.26 | 12.01 | +0.80 | rapporto tra 0.35 e 0.65: estrapolazione accettabile come stima |
| 4y | OB | 0.69 | 0.54 | 10.19 | 8.35 | +1.48 | rapporto fuori da 0.35 e 0.65: serie non nel regime asintotico, estrapolazione non affidabile |

I livelli di costo (non lo scarto) non convergono: per il PI con 598 il costo a 2 anni cresce di 1.60 da 12 a 6 h e di 2.49 da 6 a 3 h, quindi i costi assoluti a 6 h sono sottostimati di una quantita non stimabile per estrapolazione; lo scarto, che e la grandezza usata per le conclusioni, converge meglio per il PI. Per l'OB la serie e piu lenta e l'estrapolazione e solo indicativa.

### 7.3 Soglie corrette a 3 h

| caso | punto 3 h | N 3 h | note |
|---|---|---|---|
| PI | fixN 750 | 11.27 GW, costo 89.69 | passo 3 h, 4 anni |
| PI | fixN 780 | 7.99 GW, costo 90.51 | passo 3 h, 4 anni |
| OB | fixN 685 | 13.70 GW, costo 86.62 | passo 3 h, 4 anni |
| OB | fixN 705 | 11.29 GW, costo 87.33 | passo 3 h, 4 anni |

- PI: soglia sotto 10 GW a 3 h circa fixN 762 (interpolata), contro 750 a 6 h; capex equivalente 10054 EUR/kW a 7 anni.
- OB: soglia sotto 10 GW a 3 h circa fixN 716 (estrapolata linearmente dagli ultimi due punti), contro 685 a 6 h; capex equivalente 9298 EUR/kW a 7 anni.

### 7.4 Valori centrali corretti

Regola di correzione. Valore centrale = risultato a 3 h (4 anni). Per il solo PI si aggiunge la stima di Richardson verso 1 h dello scarto (sezione 7.2, 4 anni, rapporto 0.40, nel regime asintotico). Per l'OB il rapporto 0.69 e fuori dal regime asintotico: l'estrapolazione non e affidabile, quindi lo scarto a 3 h e un limite inferiore dello scarto a passo fine (il segno della correzione e certo, la sua dimensione non lo e).

| caso | costo senza nucleare 3 h | costo con nucleare 598 a 3 h | N 3 h GW | quota nucleare 3 h | scarto 6 h | scarto 3 h (centrale) | stima 1 h dello scarto |
|---|---|---|---|---|---|---|---|
| PI | 93.90 | 82.68 | 24.38 | 45.6% | 9.66 | 11.22 | 12.01 (correzione +0.80) |
| OB | 88.95 | 82.07 | 24.20 | 45.7% | 5.38 | 6.88 | non affidabile; 3 h e limite inferiore |

Punto centrale al 7% (fixN 816.6, import x1.17 con 38%, 4 anni):

| caso | costo senza nucleare 6 h | costo centrale 6 h | N 6 h | costo senza nucleare 3 h | costo centrale 3 h | N 3 h | quota 3 h | scarto 6 h | scarto 3 h |
|---|---|---|---|---|---|---|---|---|---|
| PI | 97.41 | 93.57 | 9.7 | 101.40 | 96.81 | 9.9 | 18.3% | 3.83 | 4.58 |
| OB | 92.52 | 91.98 | 2.4 | 96.67 | 95.55 | 6.1 | 11.7% | 0.55 | 1.12 |

## 8. Anni meteo peggiori

Criterio. Su 38 anni PECD (1982 a 2019) si calcola, per ogni anno, la media delle 3 settimane peggiori dell'indice combinato FV 171 GW piu eolico onshore 44.6 GW (profili PECD normalizzati). I quattro anni peggiori sono 2015 (13.58 GW medi), 1998 (14.50), 2014 (14.52) e 1994 (14.66), contro 16.3 a 19.1 GW per 2016 a 2019. Esecuzioni: il carico 2016, 2017, 2018, 2019 abbinato nell'ordine ai meteo 2015, 1998, 2014, 1994 (sostituzione, non aggiunta), ottimizzati insieme; fixN usato 597.8 (Dukovany netto 7360 EUR/kW, 7 anni, 5%, capex passato al modello 7363.6 da capex_from_fix(598)) per tutte le esecuzioni con nucleare. Le settimane critiche degli import sono ricalcolate sul nuovo meteo. Base = le esecuzioni con meteo 2016 a 2019 (val_*_none, sw_*_imp_598).

| caso | base senza nucleare | peggiori senza nucleare | aumento | base con nucleare 598 (N, quota) | peggiori con nucleare (N, quota) | aumento costo | aumento N |
|---|---|---|---|---|---|---|---|
| PI | 89.81 | 102.85 | +13.03 | 80.16 (23.9 GW, 44.3%) | 82.25 (29.0 GW, 53.7%) | +2.09 | +5.10 |
| OB | 84.97 | 92.54 | +7.58 | 79.59 (23.3 GW, 43.5%) | 81.77 (28.9 GW, 53.9%) | +2.18 | +5.56 |

Lo scarto (valore del nucleare) con meteo peggiore: PI 20.60 contro 9.66 in base; OB 10.77 contro 5.38 in base.

Riferimento a 2 anni dell'agente precedente (fixN non dichiarato, da verificare): PI senza nucleare 100.72; PI con nucleare base 79.26 / 18.72 GW, peggiori 81.28 / 27.81 GW; OB senza nucleare peggiori 90.54; OB con nucleare base 78.72 / 19.10 GW, peggiori 80.79 / 27.11 GW. Le serie a 2 anni di questa sessione (cv2, 6 h, anni 2018 e 2019) danno base PI 79.275 / 18.72 GW e OB 78.729 / 19.09 GW: coincidono con il riferimento, quindi fixN usato era 598.

Verifica del riferimento a 2 anni con le nostre esecuzioni (wx2, anni di carico 2018 e 2019, meteo peggiori 2015 e 1998):

| caso | riferimento | nostra esecuzione |
|---|---|---|
| wx2_PI_nonuc_worst | PI senza nucleare peggiori 100.72 | 100.72 / 0.0 GW |
| wx2_PI_nuc_base | PI nucleare base 79.26 / 18.72 GW | 79.26 / 18.7 GW |
| wx2_PI_nuc_worst | PI nucleare peggiori 81.28 / 27.81 GW | 81.28 / 27.8 GW |
| wx2_OB_nonuc_worst | OB senza nucleare peggiori 90.54 | 90.54 / 0.0 GW |
| wx2_OB_nuc_base | OB nucleare base 78.72 / 19.10 GW | 78.72 / 19.1 GW |
| wx2_OB_nuc_worst | OB nucleare peggiori 80.79 / 27.11 GW | 80.79 / 27.1 GW |

## 9. Ponte v6 a v7 (6 h, ZD, import x1.17 con 38%)

Ogni riga aggiunge un solo gruppo di tecnologie, in modo cumulativo; tutto il resto resta uguale. Riga 0: modello v6 (hl7.spec_v6, senza import, senza LDES) rieseguito nel codice v7; il suo costo a 3 h riproduce il valore v6 di facts_v6.md (204.2).

Riga di ancoraggio: v6 a 3 h senza nucleare 204.16 (run v6b_nonuc_h3, v6 riportato 204.2); stesso a 6 h 193.07 (run v6b_nonuc), cioe effetto del passo da solo -11.08. Con nucleare (fixN 598) v6 a 6 h: 94.09 / 38.4 GW (run v6b_nuc598).

### PI

| passo | costo senza nucleare | variazione | costo con nucleare fixN 598 | N GW | variazione | run senza / con |
|---|---|---|---|---|---|---|
| br0: v6 riprodotto nel codice v7 (tutte le tecnologie nuove spente) | 193.01 |  | 94.05 | 38.4 |  | r2_PI_br0_v6like / bn_PI_br0 |
| br1: + import (11.5 GW esistenti piu 7.3 nuovi, prezzo 115.94 x1.17 in 3 settimane critiche, disponibilita 38%) | 120.34 | -72.67 | 82.96 | 27.9 | -11.09 | r2_PI_br1_import / bn_PI_br1 |
| br2: + pompaggio nuovo | 120.34 | +0.00 | 82.96 | 27.9 | +0.00 | r2_PI_br2_pumped / bn_PI_br2 |
| br3: + geotermico (esistente, G1, G2, EGS) | 115.23 | -5.11 | 81.38 | 26.4 | -1.58 | r2_PI_br3_geo / bn_PI_br3 |
| br4: + bioenergie (biogas, solide, rifiuti) | 107.42 | -7.81 | 80.77 | 23.3 | -0.61 | r2_PI_br4_bio / bn_PI_br4 |
| br5: + CSP con accumulo | 107.41 | -0.01 | 80.77 | 23.3 | -0.01 | r2_PI_br5_csp / bn_PI_br5 |
| br6: + CAES | 107.41 | +0.00 | 80.77 | 23.3 | +0.00 | r2_PI_br6_caes / bn_PI_br6 |
| br7: + idrogeno (elettrolisi, caverne, turbina) | 91.41 | -16.00 | 80.77 | 23.3 | +0.00 | r2_PI_br7_h2 / bn_PI_br7 |
| br8: + EV smart e interrompibilita | 90.82 | -0.59 | 80.16 | 23.9 | -0.61 | r2_PI_br8_flex / bn_PI_br8 |
| br9: + LDES 100 h (solo PI) | 89.82 | -1.00 | 80.16 | 23.9 | +0.00 | r2_PI_br9 / bn_PI_br9 |
| br10: + idroelettrico nuovo (solo PI) | 89.81 | -0.01 | 80.16 | 23.9 | +0.00 | r2_PI_br10 / bn_PI_br10 |
| br11: + onde (solo PI): modello v7 completo | 89.81 | +0.00 | 80.16 | 23.9 | +0.00 | r2_PI_br11 / bn_PI_br11 |

### OB

| passo | costo senza nucleare | variazione | costo con nucleare fixN 598 | N GW | variazione | run senza / con |
|---|---|---|---|---|---|---|
| br0: v6 riprodotto nel codice v7 (tutte le tecnologie nuove spente) | 193.01 |  | 94.05 | 38.4 |  | r2_OB_br0_v6like / bn_OB_br0 |
| br1: + import (11.5 GW esistenti piu 7.3 nuovi, prezzo 115.94 x1.17 in 3 settimane critiche, disponibilita 38%) | 120.34 | -72.67 | 82.96 | 27.9 | -11.09 | r2_OB_br1_import / bn_OB_br1 |
| br2: + pompaggio nuovo | 120.34 | +0.00 | 82.96 | 27.9 | +0.00 | r2_OB_br2_pumped / bn_OB_br2 |
| br3: + geotermico (esistente, G1, G2, EGS) | 114.87 | -5.47 | 81.02 | 26.4 | -1.94 | r2_OB_br3_geo / bn_OB_br3 |
| br4: + bioenergie (biogas, solide, rifiuti) | 107.06 | -7.81 | 80.42 | 23.3 | -0.60 | r2_OB_br4_bio / bn_OB_br4 |
| br5: + CSP con accumulo | 105.15 | -1.91 | 80.41 | 23.3 | -0.01 | r2_OB_br5_csp / bn_OB_br5 |
| br6: + CAES | 101.35 | -3.80 | 80.21 | 23.3 | -0.20 | r2_OB_br6_caes / bn_OB_br6 |
| br7: + idrogeno (elettrolisi, caverne, turbina) | 85.55 | -15.80 | 80.21 | 23.3 | +0.00 | r2_OB_br7_h2 / bn_OB_br7 |
| br8: + EV smart e interrompibilita | 84.97 | -0.58 | 79.59 | 23.3 | -0.62 | r2_OB_br8_flex / bn_OB_br8 |

Il passo PI da br8 a br9 (LDES) vale 1.00 EUR/MWh senza nucleare e nulla con nucleare; in OB le tecnologie LDES, onde, pompaggio nuovo e idroelettrico nuovo sono spente a monte (modello ridotto) e i passi br2, br9 a br11 non cambiano nulla.  Il costo OB al passo br8 (84.968) coincide con la convalida val_OB_none, e il costo PI al passo br11 (89.815) con val_PI_none: il ponte chiude sul modello completo.

## 10. Sensibilita (6 h, 4 anni, con import)

### 10.1 CSP (solo OB, dove il CSP e usato)

| caso | senza nucleare costo | CSP installato GW | con nucleare 598 costo | N GW |
|---|---|---|---|---|
| base (CSP fino a 10 GW, 2900 h, credito 4 h) | 84.97 | 10.01 | 79.59 | 23.3 |
| tetto 3 GW di CSP nuovo | 86.28 (+1.31) | 3.01 | 79.59 (+0.000) | 23.3 |
| resa 2800 h | 85.29 (+0.32) | 10.01 | 79.59 (+0.000) | 23.3 |
| resa 3300 h | 83.81 (-1.16) | 10.01 | 79.59 (-0.002) | 23.2 |
| credito di capacita con accumulo 8 h | 85.03 (+0.06) | 10.01 | 79.59 (+0.000) | 23.3 |

Con nucleare a 598 il CSP non viene scelto in nessun caso (0.01 GW esistenti; a 3300 h 0.48 GW), quindi il nucleare ottimo cambia al piu di 0.2 GW. Il CSP vale solo nel caso senza nucleare. Il tetto di 10 GW e una nostra assunzione.

### 10.2 Import a doppio prezzo nelle settimane critiche (x2 invece di x1.17)

| caso | senza nucleare | variazione | con nucleare 598 | N GW | variazione |
|---|---|---|---|---|---|
| PI | 90.41 | +0.59 | 80.38 | 24.6 | +0.22 (N +0.76) |
| OB | 85.56 | +0.59 | 79.81 | 23.9 | +0.22 (N +0.58) |

### 10.3 SMR (nucleare grande spento, SMR libero; fixN equivalente dal log: il capex annuo per kW)

| caso | capex EUR/kW | fixN SMR (EUR/kW-anno) | costo | SMR GW | quota | fonte del capex |
|---|---|---|---|---|---|---|
| PI first | 17200 | 1179.1 | 89.81 | 0.0 | 0.0% | BWRX-300 Darlington unita 1, 7.7 mld CAD (POWER 05/2025) |
| PI rr | 6250 | 524.0 | 74.78 | 27.1 | 50.4% | Rolls-Royce 5000 a 7500, punto medio (stima dichiarata, non contratti) |
| PI it | 3500 | 359.5 | 59.20 | 38.3 | 71.5% | Il Sole 24 Ore 3500 (non contratti) |
| OB target | 11700 | 850.1 | 84.97 | 0.0 | 0.0% | Darlington 4 unita, 20.9 mld CAD (POWER 05/2025) |
| OB rr | 6250 | 524.0 | 74.27 | 27.2 | 50.6% | Rolls-Royce 5000 a 7500, punto medio (stima dichiarata, non contratti) |
| OB it | 3500 | 359.5 | 58.91 | 37.9 | 70.8% | Il Sole 24 Ore 3500 (non contratti) |

Con i capex dei contratti canadesi (17200 e 11700) l'SMR non entra (fixN 1179 e 850 contro soglie PI 750 e OB 685). Entra solo con i due capex non da contratti (6250 e 3500, fixN 524 e 360), con effetti molto grandi (27 e 38 GW): sono ipotesi di produttori e giornali, non offerte; vanno lette come scenari di confine, non come risultati.

### 10.4 NZ (emissioni nette zero): gas con CCS e DAC

Gas: 38.5 EUR/MWh, 0.202 tCO2/MWh termico, metano a monte 0.1 tCO2/MWh, stoccaggio 163 EUR/t, tetto 4 Mt/anno di CO2 stoccata. GAS_CCS primo impianto: 6300 EUR/kW, cattura 70%; obiettivo: 2800 EUR/kW, 95%. DAC: 650 EUR/t (primo impianto) e 100 EUR/t (obiettivo), costi completi comprensivi di energia (indicazione del coordinatore). Il gas senza CCS (GAS_NOCCS, 1850 EUR/kW, efficienza 62%) e una variante con tutte le emissioni compensate dal DAC.

| run | caso | costo | N GW | gas GW | DAC MtCO2/anno |
|---|---|---|---|---|---|
| se_NZ_PI_none | PI, senza nucleare, gas CCS primo impianto e DAC primo impianto | 89.81 | 0.0 | 0.0 | 0.0 |
| se_NZ_PI_nuc598 | PI, nucleare 598 | 80.16 | 23.9 | 0.0 | 0.0 |
| se_NZ_PI_none_noccs | PI, senza nucleare, gas senza CCS, DAC primo impianto | 89.01 | 0.0 | 5.446 | 0.719 |
| se_NZ_PI_none_targetboth | PI, senza nucleare, gas CCS e DAC obiettivo | 88.68 | 0.0 | 6.524 | 0.583 |
| se_NZ_PI_none_noccs_dactarget | PI, senza nucleare, gas senza CCS, DAC obiettivo | 85.00 | 0.0 | 13.445 | 27.618 |
| se_NZ_OB_none | OB, senza nucleare, gas CCS e DAC obiettivo | 84.97 | 0.0 | 0.0 | 0.0 |
| se_NZ_OB_nuc598 | OB, nucleare 598 | 79.59 | 23.3 | 0.0 | 0.0 |
| se_NZ_OB_none_noccs | OB, senza nucleare, gas senza CCS, DAC obiettivo | 83.14 | 0.0 | 10.251 | 19.086 |
| se_NZ_OB_none_firstboth | OB, senza nucleare, gas CCS e DAC primo impianto | 84.97 | 0.0 | 0.0 | 0.0 |
| se_NZ_OB_none_noccs_dacfirst | OB, senza nucleare, gas senza CCS, DAC primo impianto | 84.97 | 0.0 | 0.0 | 0.0 |

Il costo senza nucleare in ZD e 89.815 (PI) e 84.968 (OB). Letture: (a) con nucleare a fixN 598 il gas non entra in nessun caso e il costo NZ coincide con quello ZD; (b) senza nucleare il gas con CCS non entra ai costi del primo impianto (PI) ne ai costi obiettivo in OB; entra in PI ai costi obiettivo (6.524 GW, costo 88.68 contro 89.81); (c) il gas senza CCS con DAC compensa tutte le emissioni e riduce il costo senza nucleare rispetto a ZD di 0.81 EUR/MWh in PI con DAC primo impianto e di 4.81 con DAC obiettivo (13.4 GW di gas, 27.6 MtCO2 l'anno di DAC); in OB di 1.83 con DAC obiettivo, e di zero con DAC primo impianto. Con DAC obiettivo il PI senza nucleare costa 85.00, cioe lo scarto verso il nucleare a 598 (80.16) scende da 9.66 a 4.84; in OB scende da 5.38 a 3.55 (scarti a 6 h, nucleare ZD a 598). Il nucleare NZ con DAC obiettivo non e stato rieseguito: il gas non entra con nucleare nei casi provati (primo impianto), quindi lo scarto con DAC obiettivo e calcolato contro il nucleare ZD a 598. Il risultato dipende dal costo DAC (100 EUR/t obiettivo, 650 primo impianto, entrambi dall'indicazione del coordinatore).

## 11. Bias noti e limiti

1. Passo temporale: sezione 7; direzione nota (6 h sottostima il costo senza nucleare piu del costo con nucleare, quindi sottostima il valore del nucleare e le sue soglie).
2. Dati orari: le somme su 3 h non permettono il passo 1 h; la stima a 1 h e una estrapolazione, con affidabilita indicata caso per caso nella sezione 7.2.
3. Anni peggiori: solo il passo 6 h (somme su 6 h trasferite dal sandbox), media dei 3 settimane peggiori come criterio; il criterio non considera le ondate di freddo ne l'idroelettrico.
4. Il tetto del CSP a 10 GW, la vita 20 anni e l'O&M 20% del LDES, il tempo di costruzione del gas CCS (3 anni), la scala della rete al 7% sono assunzioni nostre.
5. Il caso OB usa un modello ridotto (senza LDES, onde, pompaggio nuovo, idroelettrico nuovo, SMR): i punti OB non sono confrontabili con PI per differenza di modello; la differenza e piccola (a 5% senza nucleare, OB ridotto 84.968).
6. Nessun dato e stato preso dalla memoria dell'utente; i valori di riferimento sono quelli di D/v7res/reference_points.md.

## 12. Origine dei casi di costo del nucleare (risolto 2026-11-09)

- Dukovany netto 7360 EUR/kW = contratto lordo 7750 EUR/kW (407 Md CZK per due unita, circa 2100 MW, con circa dieci anni di combustibile; WNN 05/06/2025) meno 382 EUR/kW di combustibile = 7368, arrotondato 7370. Combustibile: 4.85 EUR/MWh (le esecuzioni usarono 4.91, capex 7363.6, fixN 598.0; con 7370 fixN 598.4, differenza 0.4, risultati centrali invariati). Origine: 4.62 USD/MWh x 1.1736 (CPI-U 2025 media su 11 mesi / settembre 2021) / 1.1188 (WNA, Economics of Nuclear Power, aggiornata il 24/03/2026: 1663 USD/kg di UO2 = 0.46 c/kWh = 4.62 USD/MWh a prezzi settembre 2021; portato a EUR 2025 con US CPI-U e cambio 1.1188) x 10 anni x 0.9 x 8760 / 1000 = 387. 7750 meno 387 = 7363 (il modello usa 7363.6 per fixN 598). Il valore 4.91 e del coordinatore: il fattore CPI implicito (4.91 x 1.1188 / 4.62) e 1.189, non verificato da noi.
- Sensibilita lorda (combustibile non sottratto), 6 h, con import, 5%: Dukovany 7750 EUR/kW, PI 81.55 EUR/MWh, 19.1 GW, 34.8%; OB 80.97, 18.2 GW, 33.3% (contro 23.9 e 23.3 GW del caso netto).
- Valute: i cinque casi sono overnight EUR 2025/kW, da USD con US CPI-U al 2025 e poi 1 EUR = 1.1188 USD (Banca d'Italia, cambi di riferimento del 26/10/2026, https://www.bancaditalia.it/compiti/operazioni-cambi/cambio/cambi_rif_20261026, letto 09/11/2026). Barakah 4371 EUR/kW e vicino a 4357 USD/kW nominali (24.4 Md USD / circa 5.6 GW) per coincidenza di inflazione e cambio, non per errore di etichetta; netto del primo combustibile 4313 (1.3% in meno).
- Rischio 9680 EUR/kW con 15 anni (adottato il 2026-11-09, al posto di 9900/894.8): mediana di quattro costruzioni occidentali recenti, EUR 2025/kW: Mochovce 3-4 8756, Olkiluoto 3 9064, Flamanville 3 10300, Vogtle 15540; mediana (9064+10300)/2 = 9682, arrotondata a 9680; fixN 878.3 al 5% e 1334.2 al 7%. Risultati letti sulla curva per interpolazione lineare (6 h, import 5%): PI 5.1 GW (9%), OB 0; senza import 5%: PI 20.4 GW (32%), OB 10.5 (20%); al 7% con import e senza import: 0 (con import oltre l'ultimo punto, 900 con 6.2 GW PI: estrapolazione). Prima del 2026-11-09 il valore era 9900 (valori del coordinatore Mochovce 8060, Olkiluoto 9500). Ricontrollo sulle fonti (2026-11-09): OL3 circa 11 Md EUR (Nuclear Engineering International, 25/06/2025, testo '$11bn ($12bn)' letto come 11 Md EUR), 1600 MWe (1575 netti, WNA Finlandia): 6875 EUR/kW nominali, con IPCA (Eurostat, fattori 128.75/indice annuo) e spesa uniforme 2005-2022 (fattore medio 1.318) 9064 (-4.6% su 9500; 8907-9208 secondo il calendario). Mochovce 3-4: 6.7 Md EUR (WNN, ottobre 2026), 2 x 471 MWe (WNA: 440 netti per unita): 7113 nominali, spesa uniforme 2009-2025 (fattore 1.231) 8756 (+8.6% su 8060; con 880 MW 9373). Mediana ricalcolata (9064+10300)/2 = 9682; fixN a 15 anni 878.4 contro 894.8. Valori adottati (sopra); intervallo OL3 con altri calendari di spesa 8907-9208.
- Combustibile, controllo CPI-U (BLS, tabella storica, Table 1): settembre 2021 274.310; media 2025 su 11 mesi (ottobre mancante) 321.943; fattore 1.1736; 4.62 x 1.1736 / 1.1188 = 4.85 EUR/MWh contro 4.91 usato (+1.3%); combustibile 382 contro 387 EUR/kW. Nota: la pagina BLS porta due tabelle e l'etichetta CPI-U e ambigua; la prima tabella (settembre 2021 274.310) e la serie CPI-U.
- I valori 5000 e 9100 di techs_v7.json sono ereditati da v6 e non usati (campo _cases_unused).

- Risultati interpolati aggiornati: costo centrale con 15 anni (7370, fixN 704.5): PI 13.1 GW, OB 6.4; LCOE stand-alone 90% (EUR/MWh): Dukovany 88.9 (5%) e 116.1 (7%), rischio 124.4 e 181.6, rapporto 7%/5% centrale 1.306.

## 13. Caso centrale con costi del proprietario (revisione indipendente, 2026-11-09; valori con cambio 25 CZK/EUR, sostituiti dalla sezione 14)

Nota di metodo. Il 24 GW della prima stesura (3 h: 24.38 GW PI, 24.20 GW OB, fixN 598, capex 7370) usava il prezzo EPC del contratto di Dukovany al netto del combustibile e senza i costi del proprietario. Quel valore e ora il limite alto per il nucleare, non il caso centrale. Né il contratto né le fonti che lo riportano (WNN 05/06/2025, https://www.world-nuclear-news.org/articles/khnp-sets-out-plans-for-usd186bn-czech-nuclear-project; ČT24 13/10/2025; Forbes Česko 18/07/2025) danno i costi del proprietario, e non e stata trovata una stima pubblica di EDU II che li separi.

- Regola: costo overnight = EPC netto / (1 meno 0.1257), con 12.57% = quota dei costi del proprietario (conto 40) sul costo overnight di un PWR nella banca dati EEDB riportata da INL/RPT-23-72972, tabella 8. Fattore 1.1438.
- Centrale: (7750 meno 382) x 1.1438 = 8427, arrotondato 8430 EUR/kW, 7 anni; fixN 662.9 (5%) e 912.8 (7%); esecuzioni a fixN 663 (capex 8432.3) e 913 (capex 8432.4). Livello di prezzo: contratto di giugno 2025, quindi prezzi 2025, nessuna rivalutazione. Cambio ipotizzato 25 CZK/EUR: 7716 EUR/kW lordi con 2 x 1055 MWe, 7752 con 2100 MW; il modello usa 7750 (con 7716 il centrale sarebbe circa 8390, 0.5% in meno).
- Estremo alto: spese di preparazione dello Stato 85 Md CZK (ČT24), 21% di 407: 7368 x (1 + 85/407) = 8907, arrotondato 8910, fixN 692.1. Estremo basso: solo EPC netto del combustibile, 7370, fixN 598.4. Senza togliere il combustibile: 7750 x 1.1438 = 8864, fixN 689.3.
- Conflitto sul combustibile: WNN (e il comunicato del Ministero delle Finanze, non scaricabile) dicono che i 407 Md CZK comprendono circa dieci anni di combustibile; ČT24 (direttore EDU II) e Forbes riportano 15 Md CZK in piu per il primo combustibile. Il centrale lo toglie (decisione del coordinatore), con la sensibilita senza detrazione.
- Barakah: contratto 20.4 Md USD / 5.6 GW = 3643 USD/kW; fattore CPI-U 1.255 (spesa uniforme 2012-2024; gli indici annui 2009-2015 non sono nella pagina BLS consultata e sono a memoria); 4571 USD/kW; /1.1188 = 4086 EUR/kW; x 1.1438 = 4673, adottato 4670. fixN 441.6 al 5%. Prima 4371 (24.4 Md USD di finanziamento complessivo / 5.6 GW, che include interessi).
- Vogtle: circa 35 Md USD totali (Energytech 31/07/2023) meno circa 4 Md di oneri finanziari (IEEFA gennaio 2022: oltre 3.5, circa 4 al completamento) = 31 Md; 2 x 1117 MWe netti (dati di progetto); 13876 USD/kW; fattore CPI-U 1.262 (spesa uniforme 2013-2023); 17516 USD/kW; 15656 EUR/kW contro 15540 usato (+0.7%, sotto il 5%: mediana del rischio invariata a 9680). Estremi 30 e 35 Md: 15150 e 17680.
- OL3: la fonte (NEI, 25/06/2025) scrive '$11bn ($12bn)', letto come 11 Md EUR; se fossero 11 Md USD, OL3 8098 EUR/kW e mediana 9528 (meno 1.6%).
- Quindici anni: 15 anni da soli, con il costo centrale (fixN 784.2): PI 8,1 GW, OB 2,3 a 6 h (non piu 13.1 e 6.4, che erano a 7370); 15 anni con il costo di rischio (878.3): PI 5,1, OB 0,0.

### 13.1 Nuovi valori centrali (tag c2_ in D/v7run/results.jsonl)

| caso | N 6 h GW | quota 6 h | N 3 h GW | quota 3 h | costo senza nucleare 3 h | costo con nucleare 3 h | divario 3 h | stima 1 h |
|---|---|---|---|---|---|---|---|---|
| PI 5% fixN 663 | 14,69 | 26,6% | 16,28 | 29,5% | 93,90 | 86,26 | 7,64 | 7,92 (rapporto 0,39) |
| OB 5% fixN 663 | 13,99 | 25,7% | 15,21 | 27,9% | 88,95 | 85,74 | 3,21 | rapporto 1,62 |
| PI 7% fixN 913 | 6,06 | 11,3% | 6,67 | 12,3% | 101,40 | 99,10 | 2,30 | |
| OB 7% fixN 913 | 1,16 | 2,2% | 1,62 | 3,1% | 96,67 | 96,34 | 0,33 | |

Interpolati sulla curva a 6 h (con import, 5%, PI / OB): Saeul fixN 335: 39,3 / 38,6; Barakah 442: 34,5 / 34,0; estremo alto 692: 13,6 / 8,5; senza detrazione del combustibile 689: 13,7 / 9,1; rischio 878: 5,1 / 0,0. Senza import, 663 (5%): PI 33,0, OB 24,4; 913 (7%): PI 25,0, OB 12,1.

Le sensibilita, il ponte v6-v7 e gli anni peggiori: sensibilita (CSP, import doppio, NZ) e anni peggiori a fixN 663 con i tag c2s_ (stesse specifiche delle esecuzioni a 598, solo il capex del nucleare cambia); il ponte (sezione 9) resta a fixN 598 perche confronta con la versione precedente. LCOE stand-alone aggiornato: Barakah 69,0 (5%) e 87,3 (7%); Dukovany 97,0 e 128,1.

## 14. Chiusura degli input non verificati (2026-11-09, sera)

1. CPI-U 2009-2015: medie annue dei 12 valori mensili della serie FRED CPIAUCNS (= BLS CUUR0000SA0, non destagionalizzata): 2009 214.537; 2010 218.056; 2011 224.939; 2012 229.594; 2013 232.957; 2014 236.736; 2015 237.017; 2025 (11 mesi) 321.943. Fattori medi ricalcolati: Barakah (2012-2024) 1.2549, Vogtle (2013-2023) 1.2623, contro 1.255 e 1.262 usati: variazione inferiore a 0.1%, nessun valore cambia.
2. Cambio CZK/EUR: media annua 2025 del cambio di riferimento BCE, 24.688 (Eurostat ert_bil_eur_a), al posto dell'ipotesi 25. 407 Md CZK / 24.688 = 16.486 Md EUR; / 2.1 GW = 7850 EUR/kW (7813 con 2 x 1055 MW). Netto combustibile 382 = 7468; x 1.1438 = 8542, adottato 8540 (prima 8430, +1.3%). fixN 669.5 (5%) e 922.7 (7%) (prima 662.9 e 912.8): +6.7 e +9.9 EUR/kW-anno, sopra la soglia di 2, quindi rieseguiti (tag c3_, c3e_, c3s_; esecuzioni a fixN 670 e 923; EPC-only 7470, fixN 604 e 826; estremo alto 9030, fixN 699; senza detrarre il combustibile 8980, fixN 696; 15 anni con il costo centrale fixN 792.5).
3. Combustibile: WNN, i 407 Md CZK comprendono circa 10 anni di combustibile (carico iniziale e cinque ricariche); ČT24 e Forbes, 15 Md CZK in piu per il primo combustibile. Scelta: WNN, perche dice che cosa comprende il prezzo, le altre non dicono se i 15 Md siano dentro o fuori dai 407. Effetto dell'altra lettura: senza detrarre 382, capex 8980 invece di 8540 (+440 EUR/kW, +5%), fixN 696 invece di 670.
4. Costi del proprietario: centrale INL EEDB 12.57% del costo overnight (14.4% dell'EPC). Riferimento europeo: W. D'haeseleer, Synthesis on the Economics of Nuclear Energy, studio per la Commissione europea DG Energy, 27 novembre 2013: nessuna definizione unica, circa 15-20% dell'EPC da piu fonti (MIT 2003 e 2009, Parsons 2009, Rothwell 2010). 20% dell'EPC = 8962 EUR/kW, fixN 695. Gli estremi si leggono sulla curva.

### 14.1 Nuovi valori centrali (tag c3_)

| caso | N 6 h GW | quota 6 h | N 3 h GW | quota 3 h | costo senza nucleare 3 h | costo con nucleare 3 h | divario 3 h | stima 1 h |
|---|---|---|---|---|---|---|---|---|
| PI 5% fixN 670 | 14,15 | 25,6% | 15,95 | 28,9% | 93,90 | 86,58 | 7,32 | 7,92 (rapporto 0,39) |
| OB 5% fixN 670 | 12,94 | 23,8% | 14,58 | 26,8% | 88,95 | 86,03 | 2,92 | rapporto 1,62 |
| PI 7% fixN 923 | 5,97 | 11,2% | 6,46 | 11,9% | 101,40 | 99,28 | 2,11 | |
| OB 7% fixN 923 | 0,96 | 1,8% | 1,45 | 2,8% | 96,67 | 96,38 | 0,28 | |
| PI 5% EPC-only fixN 604 | | | 24,38 | 45,6% | | 83,09 | 10,81 | |
| OB 5% EPC-only fixN 604 | | | 23,68 | 44,5% | | 82,47 | 6,47 | |

## 15. Scenari di sicurezza energetica (2026-11-10)

Tutti i casi: 4 anni meteo, stesso modello del caso centrale c3 (import 18,9 GW = 11,5 esistenti + 7,3 nuovi, PUN 115,94 EUR/MWh, nucleare fixN 670 al 5%, 7 anni; 7%: fixN 923 con r = 0,07, come i tag c3 7pc). Il 598 e a 5%. Divario = costo senza nucleare meno costo con nucleare dello stesso scenario. Costo = EUR/MWh sulla domanda netta (come cost_new). Gli scenari usano il caso IMPORT credit0 (credito di capacita 0 e disponibilita 0 nelle 3 settimane critiche per anno). Nota: nelle richieste era indicato 913 per il 7%; e stato usato 923 per confrontarlo con c3_*_7pc_923 (differenza di 10 EUR/kW sul fix).

### 15.1 Riferimento: caso centrale (import con disponibilita 38% e credito 0,38 nelle settimane critiche)

| caso | costo EUR/MWh | N GW | quota nucleare | import TWh/anno | import GW installati | export TWh/anno | curtailment TWh | divario vs senza nucleare |
|---|---|---|---|---|---|---|---|---|
| PI 6 h senza nucleare | 89,815 | 0,00 | 0,0% | 53,57 | 18,86 | 0 | 11,15 |  |
| PI 6 h fixN 670 | 83,702 | 14,15 | 25,6% | 36,87 | 18,20 | 0 | 3,31 | 6,11 |
| PI 6 h 7% senza nucleare | 97,405 | 0,00 | 0,0% | 57,56 | 18,86 | 0 | 8,19 |  |
| PI 6 h 7% fixN 923 | 95,679 | 5,97 | 11,2% | 49,23 | 18,86 | 0 | 5,01 | 1,73 |
| PI 3 h senza nucleare | 93,901 | 0,00 | 0,0% | 53,75 | 18,86 | 0 | 11,31 |  |
| PI 3 h fixN 670 | 86,578 | 15,95 | 28,9% | 35,10 | 17,86 | 0 | 2,00 | 7,32 |
| OB 6 h senza nucleare | 84,968 | 0,00 | 0,0% | 54,01 | 18,86 | 0 | 7,30 |  |
| OB 6 h fixN 670 | 83,021 | 12,94 | 23,8% | 39,53 | 17,86 | 0 | 2,48 | 1,95 |
| OB 6 h 7% senza nucleare | 92,522 | 0,00 | 0,0% | 60,30 | 18,86 | 0 | 6,30 |  |
| OB 6 h 7% fixN 923 | 92,439 | 0,96 | 1,8% | 57,28 | 18,86 | 0 | 6,56 | 0,08 |
| OB 3 h senza nucleare | 88,946 | 0,00 | 0,0% | 57,01 | 18,86 | 0 | 9,11 |  |
| OB 3 h fixN 670 | 86,029 | 14,58 | 26,8% | 38,45 | 17,86 | 0 | 2,67 | 2,92 |

Dal risultato c3_PI_670_h6: import 36,874 TWh/anno (units.IMPORT.TWh), 18,196 GW installati su 18,865 disponibili. Il massimo import in GW nelle settimane critiche non e salvato (il modello non memorizza la dispatch oraria); il limite e 0,38 x 18,196 = 6,9 GW.

### 15.2 Scenario 'import non fermo' (tag imp0_): stesso import in tempi normali, nelle 3 settimane critiche disponibilita 0 e credito 0

| caso | costo EUR/MWh | N GW | quota nucleare | import TWh/anno | import GW installati | export TWh/anno | curtailment TWh | divario vs senza nucleare |
|---|---|---|---|---|---|---|---|---|
| PI 6 h senza nucleare | 93,335 | 0,00 | 0,0% | 48,29 | 18,86 | 0 | 10,73 |  |
| PI 6 h fixN 670 | 86,717 | 19,68 | 35,5% | 22,42 | 12,95 | 0 | 1,13 | 6,62 |
| PI 6 h fixN 598 | 81,881 | 27,06 | 49,6% | 15,98 | 11,54 | 0 | 0,17 | 11,45 |
| PI 6 h 7% senza nucleare | 101,718 | 0,00 | 0,0% | 52,74 | 18,86 | 0 | 6,64 |  |
| PI 6 h 7% fixN 923 | 99,789 | 7,31 | 13,7% | 41,12 | 17,86 | 0 | 4,00 | 1,93 |
| PI 3 h senza nucleare | 97,482 | 0,00 | 0,0% | 50,14 | 18,86 | 0 | 9,35 |  |
| PI 3 h fixN 670 | 89,392 | 22,03 | 40,5% | 20,79 | 12,29 | 0 | 0,26 | 8,09 |
| OB 6 h senza nucleare | 87,917 | 0,00 | 0,0% | 48,94 | 18,64 | 0 | 6,99 |  |
| OB 6 h fixN 670 | 84,969 | 15,46 | 28,6% | 28,74 | 12,37 | 0 | 1,85 | 2,95 |
| OB 6 h fixN 598 | 81,056 | 24,66 | 46,6% | 20,76 | 11,54 | 0 | 0,07 | 6,86 |
| OB 6 h 7% senza nucleare | 96,107 | 0,00 | 0,0% | 54,47 | 18,76 | 0 | 6,24 |  |
| OB 6 h 7% fixN 923 | 95,904 | 2,32 | 4,5% | 48,20 | 17,86 | 0 | 5,47 | 0,20 |
| OB 3 h senza nucleare | 91,924 | 0,00 | 0,0% | 51,68 | 18,86 | 0 | 8,48 |  |
| OB 3 h fixN 670 | 87,909 | 17,28 | 32,4% | 28,88 | 12,29 | 0 | 1,13 | 4,02 |

### 15.3 Scenario 'autosufficienza netta' (tag ss<X>_): export a ricavo zero (sink), limitato dalla capacita di interconnessione, import annuo <= export annuo + X x domanda; credit0

Validazione: con X = 100% e import centrale (credito e disponibilita 0,38) il modello riproduce c3 a 670 esattamente (ssval_PI_670_h6 83,702 contro 83,702; ssval_OB_670_h6 83,021 contro 83,021, export 0 TWh).

| caso | costo EUR/MWh | N GW | quota nucleare | import TWh/anno | import GW installati | export TWh/anno | curtailment TWh | divario vs senza nucleare |
|---|---|---|---|---|---|---|---|---|
| X=0% PI 6 h senza nucleare | 96,464 | 0,00 | 0,0% | 31,70 | 18,86 | 31,70 | 5,72 |  |
| X=0% PI 6 h fixN 670 | 87,468 | 20,45 | 39,4% | 18,24 | 12,47 | 18,24 | 0,11 | 9,00 |
| X=0% PI 6 h fixN 598 | 82,504 | 27,51 | 53,5% | 14,79 | 11,54 | 14,79 | 0,00 | 13,96 |
| X=0% PI 6 h 7% senza nucleare | 106,034 | 0,00 | 0,0% | 28,66 | 18,31 | 28,66 | 4,13 |  |
| X=0% PI 6 h 7% fixN 923 | 102,460 | 11,36 | 21,7% | 23,64 | 15,86 | 23,64 | 0,80 | 3,57 |
| X=0% OB 6 h senza nucleare | 92,234 | 0,00 | 0,0% | 30,44 | 16,54 | 30,44 | 7,01 |  |
| X=0% OB 6 h fixN 670 | 86,280 | 18,35 | 34,8% | 19,21 | 11,54 | 19,21 | 0,26 | 5,95 |
| X=0% OB 6 h fixN 598 | 81,857 | 26,18 | 51,5% | 14,85 | 11,54 | 14,85 | 0,00 | 10,38 |
| X=0% OB 6 h 7% senza nucleare | 101,570 | 0,00 | 0,0% | 28,17 | 15,42 | 28,17 | 5,58 |  |
| X=0% OB 6 h 7% fixN 923 | 99,849 | 7,56 | 14,7% | 24,87 | 13,31 | 24,87 | 2,16 | 1,72 |
| X=5% PI 6 h senza nucleare | 94,532 | 0,00 | 0,0% | 38,23 | 18,86 | 18,23 | 6,14 |  |
| X=5% PI 6 h fixN 670 | 86,772 | 20,51 | 36,8% | 20,12 | 12,47 | 1,77 | 0,71 | 7,76 |
| X=5% OB 6 h senza nucleare | 89,658 | 0,00 | 0,0% | 37,55 | 16,96 | 17,55 | 3,08 |  |
| X=5% OB 6 h fixN 670 | 85,176 | 16,09 | 30,1% | 26,36 | 12,29 | 6,36 | 0,16 | 4,48 |
| X=10% PI 6 h senza nucleare | 93,484 | 0,00 | 0,0% | 44,48 | 18,86 | 4,74 | 9,53 |  |
| X=10% PI 6 h fixN 670 | 86,717 | 19,68 | 35,5% | 22,42 | 12,95 | 0,00 | 1,13 | 6,77 |
| X=10% OB 6 h senza nucleare | 88,187 | 0,00 | 0,0% | 44,67 | 17,86 | 4,67 | 5,97 |  |
| X=10% OB 6 h fixN 670 | 84,969 | 15,46 | 28,6% | 28,74 | 12,37 | 0,00 | 1,86 | 3,22 |
| X=0% PI 3 h senza nucleare | 101,076 | 0,00 | 0,0% | 31,77 | 18,86 | 31,77 | 6,79 |  |
| X=0% PI 3 h fixN 670 | 90,194 | 23,01 | 44,7% | 16,24 | 11,79 | 16,24 | 0,02 | 10,88 |
| X=0% OB 3 h senza nucleare | 97,068 | 0,00 | 0,0% | 30,51 | 16,71 | 30,51 | 7,78 |  |
| X=0% OB 3 h fixN 670 | 89,213 | 20,83 | 40,0% | 17,98 | 11,54 | 17,98 | 0,12 | 7,86 |

Note di metodo: l'export e una variabile per passo temporale, limitata dalla capacita di interconnessione scelta per l'import (11,5 GW esistenti piu i blocchi nuovi), senza ricavo e senza costo di capacita; vincolo per anno meteo: somma import <= somma export + X x 400 TWh. Codice: hl7.solve7(export=...), run7 chiave export_X, driver7 set ss*/imp0_*. I tag imp0_* e ss* sono in v7run/results.jsonl.

## 16. Curva costo-quota con autosufficienza netta (X=0, credit0), 2026-11-11

Regola: import annuo <= export annuo (X=0), export a ricavo zero limitato dall'interconnessione, nessun credito di capacita e disponibilita 0 dell'import nelle 3 settimane critiche. Passo 6 h, 4 anni meteo 2016-2019, cantiere 7 anni. Capex equivalente: capex = (fixN - fisso) / (idc(r,y) x CRF(r,80)), fisso 150,14 (5%) o 154,77 (7%).

### 16.1 Curva al 5%

| fixN | capex 7 anni | PI costo | PI GW | PI quota | OB costo | OB GW | OB quota |
|---|---|---|---|---|---|---|---|
| 335 (Saeul) | 2.965 | 57,550 | 39,51 | 74,0% | 57,246 | 38,98 | 73,3% |
| 423 | 4.490 | 67,142 | 37,42 | 72,5% | 66,716 | 36,66 | 70,3% |
| 442 (Barakah) | 4.670 | 69,096 | 35,76 | 69,3% | 68,629 | 35,05 | 67,6% |
| 500 | 5.750 | 74,475 | 31,04 | 59,9% | 73,906 | 30,51 | 59,6% |
| 598 | 7.360 | 82,504 | 27,51 | 53,5% | 81,857 | 26,18 | 51,5% |
| 640 | 8.050 | 85,611 | 23,57 | 45,6% | 84,629 | 21,25 | 41,0% |
| 670 (centrale) | 8.540 | 87,468 | 20,45 | 39,4% | 86,280 | 18,35 | 34,8% |
| 700 | 9.040 | 89,071 | 17,81 | 33,8% | 87,808 | 18,11 | 34,4% |
| 750 | 9.870 | 91,198 | 12,12 | 22,4% | 89,408 | 8,10 | 15,3% |
| 800 | 10.690 | 92,883 | 11,90 | 22,2% | 90,514 | 7,81 | 15,0% |
| 850 | 11.510 | 94,434 | 9,53 | 17,7% | 91,460 | 5,18 | 9,9% |
| 878 (rischio) | 11.970 | 95,150 | 8,99 | 16,8% | 91,860 | 4,57 | 8,7% |
| 950 | 13.150 | 96,309 | 2,64 | 4,8% | 92,234 | 0 | 0 |
| 1050 | 14.800 | 96,464 | 0 | 0 | 92,234 | 0 | 0 |
| 1172 (Vogtle) | 15.540 (fixN dato) | 96,464 | 0 | 0 | 92,234 | 0 | 0 |

Nota: i capex in colonna per 423/500/640/750/850/950/1050 sono calcolati dalla formula; per i casi nominati sono i valori delle fonti (sezioni 12-14). Il caso di rischio usa fixN 878 = 9.680 EUR/kW con 15 anni.

Soglie (interpolazione lineare, 6 h): PI sotto 20 GW a fixN 675 (8.630 EUR/kW con 7 anni; 6.980 con 15 anni), sotto 10 GW a 840 (11.350; 9.170), zero tra 950 e 1050 (oltre 13.150; oltre 10.630). OB sotto 20 GW a 653 (8.270; 6.680), sotto 10 GW a 741 (9.710; 7.850), zero a 950 (13.150; 10.630).

Caso centrale con 15 anni di cantiere: fixN 792,5 -> PI circa 11,9 GW, OB circa 7,8 GW (interpolato).

### 16.2 Curva al 7% (fixN calcolato con r = 0,07; _sw7b)

| fixN | capex 7 anni | PI costo | PI GW | OB costo | OB GW |
|---|---|---|---|---|---|
| 700 | 6.060 | 91,974 | 25,73 | 91,324 | 25,23 |
| 800 | 7.180 | 98,141 | 14,70 | 96,723 | 14,46 |
| 923 (centrale) | 8.540 | 102,460 | 11,36 | 99,849 | 7,56 |
| 1000 | 9.400 | 104,767 | 9,44 | 101,293 | 4,08 |
| 1100 | 10.510 | 106,034 | 0 | 101,570 | 0 |
| 1334 (rischio) | 9.680, 15 anni | 106,034 | 0 | 101,570 | 0 |

### 16.3 Anni meteo peggiori (2015, 1998, 2014, 1994), fixN 670, 6 h

PI: costo 91,751, 30,79 GW (59,0%). OB: costo 89,941, 24,30 GW (48,2%). Negli anni peggiori l'ottimo sale di 6-10 GW: il nucleare fa da assicurazione contro le annate di poco vento e sole.

### 16.4 Anni peggiori senza nucleare e divari (aggiornamento)

ss0_wx4_PI_none_worst 110,643; ss0_wx4_OB_none_worst 100,307 (6 h). Divario negli anni peggiori: PI 110,643 - 91,751 = 18,89 (base 9,00); OB 100,307 - 89,941 = 10,37 (base 5,95).

### 16.5 Convergenza con autosufficienza netta (fixN 670, 4 anni)

| caso | costo 12 h senza / con | divario 12 h | divario 6 h | divario 3 h | rapporto | stima 1 h |
|---|---|---|---|---|---|---|
| PI | 90,830 / 86,167 (N 17,76) | 4,66 | 9,00 | 10,88 | 0,44 | 11,95 (G0 12,34, p 1,20) |
| OB | 87,485 / 84,192 (N 12,08) | 3,29 | 5,95 | 7,86 | 0,71 (fuori 0,35-0,65) | n.a., 3 h limite inferiore |

### 16.6 Prezzo della dipendenza (6 h, fixN 670)

| regola | PI senza N | PI con N | PI N GW | OB senza N | OB con N | OB N GW |
|---|---|---|---|---|---|---|
| X=0 | 96,464 | 87,468 | 20,45 | 92,234 | 86,280 | 18,35 |
| X=5% | 94,532 | 86,772 | 20,51 | 89,658 | 85,176 | 16,09 |
| X=10% (non vincolante con N) | 93,484 | 86,717 | 19,68 | 88,187 | 84,969 | 15,46 |
| imp0 | 93,335 | 86,717 | 19,68 | 87,917 | 84,969 | 15,46 |
| credito Terna (c3) | 89,815 | 83,702 | 14,15 | 84,968 | 83,021 | 12,94 |

Risparmio da X=0 a X=10%: con nucleare PI 0,75, OB 1,31 EUR/MWh; senza nucleare PI 2,98, OB 4,05.

### 16.7 Punti a 3 h (autosufficienza netta, 4 anni)

| tag | costo | N GW | quota |
|---|---|---|---|
| ss0_PI_780_h3 | 95,513 | 12,19 | 22,6% |
| ss0_OB_780_h3 | 93,713 | 8,23 | 15,9% |
| ss0_PI_850_h3 | 97,874 | 11,86 | 22,5% |
| ss0_OB_850_h3 | 95,322 | 8,08 | 15,5% |
| ss0_PI_7pc_923_h3 | 106,086 | 11,52 | 22,3% |
| ss0_OB_7pc_923_h3 | 103,791 | 7,90 | 15,4% |
| ss0_PI_7pc_none_h3 | 110,540 | 0 | 0 |
| ss0_OB_7pc_none_h3 | 106,144 | 0 | 0 |

Divario 7% a 3 h: PI 4,45, OB 2,35. Soglia 10 GW a 3 h: OB fixN 765 (10.100 EUR/kW a 7 anni); PI oltre 850 (11,9 GW a 850). Tra 780 e 850 la curva a 3 h e quasi piatta (PI circa 12, OB circa 8 GW).
