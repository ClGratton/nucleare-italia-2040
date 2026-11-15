# -*- coding: utf-8 -*-
# White paper v8 (14 novembre 2026). Contenuto: elementi (tipo, ...) letti da build.py.
#
# ORIGINE DEI NUMERI
#   F  = docs/v8_facts.md            (repo nucleare-italia-2040, commit f3a60a8)
#   R  = docs/results_v8.md          (generato dalle esecuzioni; le tabelle marcate "da R" sono lette dal file a ogni build)
#   T  = model/techs_v8.json         (dati di ingresso e note 'src')
#   A  = docs/audit/audit_v8_findings.md (punti A1..D9)
#   H  = docs/audit/audit_history.md (traiettoria e registro degli errori)
#   S  = docs/audit/v8_symmetric_costs.md (fonti con URL)
# I valori marcati "nostro calcolo" nel testo sono aritmetica su numeri di queste fonti; il calcolo è nel commento accanto.
# Gli URL di ČT24, Eurostat (cambio), POWER Magazine, Hystories, PECD, Terna-Snam e ARERA 12/2026 non sono nei file di audit:
# vengono dalla bibliografia della versione 7 (solo riferimento bibliografico, nessun numero).
import re, os

REPO = '/home/claude/nucleare-italia-2040'
TITLE = "La quota di nucleare che conviene all'Italia nel 2040"
SUBTITLE = "Il sistema elettrico di minor costo a zero emissioni dirette, con una sola regola di costo per tutte le fonti"
DATE = "15 novembre 2026, versione 8"
COVER_TITLE = ["La quota di nucleare che conviene", "all'Italia nel 2040"]
COVER_SUB = ["Il sistema elettrico di minor costo a zero emissioni dirette,", "con una sola regola di costo per tutte le fonti"]

C = []
def h1(t): C.append(['h1', t])
def h2(t): C.append(['h2', t])
def p(t): C.append(['p', t])
def b(items): C.append(['bullets', items])
def fig(path, cap, wfrac=1.0): C.append(['fig', path, cap, wfrac])
def tab(rows, widths, cap, align=None, fs=8.2, keep=None): C.append(['table', rows, widths, cap, align, fs, keep])
def box(title, paras): C.append(['box', title, paras])
def sources(): C.append(['sources'])

# ---------------------------------------------------------------- lettura di results_v8.md
def _read_md_tables(path):
    """Restituisce {titolo: [righe]} per ogni tabella di results_v8.md. Titolo = '<n. sezione>|<titolo in grassetto o vuoto>'."""
    out = {}; sec = ''; title = ''; cur = None
    for line in open(path, encoding='utf-8').read().split('\n'):
        if line.startswith('## '):
            sec = line[3:].split('.')[0].strip(); title = ''; cur = None
        elif line.startswith('**') and line.rstrip().endswith(')') or (line.startswith('**') and line.rstrip().endswith('**')):
            title = line.split('**')[1].strip(); cur = None
        elif line.startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if set(''.join(cells)) <= set('-: '):
                continue
            key = sec + '|' + title
            if cur != key:
                cur = key; out[key] = []
            out[key].append(cells)
        else:
            cur = None
    return out

RES = _read_md_tables(os.path.join(REPO, 'docs', 'results_v8.md'))

def it(s, nd=None):
    """Numero in formato italiano: virgola decimale, punto per le migliaia. Accetta stringhe di results_v8.md."""
    s = str(s).strip()
    if s == '': return ''
    if re.fullmatch(r'\d{1,3}(,\d{3})+', s):          # 10,200 (migliaia all'inglese)
        return s.replace(',', '.')
    if re.fullmatch(r'-?\d+(\.\d+)?', s):
        if nd is not None: s = ('%.' + str(nd) + 'f') % float(s)
        ip, _, dp = s.partition('.')
        neg = ip.startswith('-'); ip = ip.lstrip('-')
        if len(ip) > 3: ip = ip[:-3] + '.' + ip[-3:]
        return ('-' if neg else '') + ip + ((',' + dp) if dp else '')
    return s

def band(s):
    """'16-28 GW' -> '16-28'; '36-36 GW' -> '36'."""
    a, bb = s.replace(' GW', '').split('-')
    return a if a == bb else a + '-' + bb

# ---------------------------------------------------------------- fonti (numerate in ordine di prima citazione)
NV = " Fonte non verificata in questa revisione."
SRC = {
 'ec': ("Commissione europea, aiuto di Stato SA.117794, Cechia, nuove unità nucleari di Dukovany 5 e 6: decisione di avvio dell'indagine approfondita, Gazzetta ufficiale dell'Unione europea C/2026/2825, 27 maggio 2026 (costi, potenza, modello finanziario e costi di esercizio notificati dallo Stato ceco).", ["https://eur-lex.europa.eu/eli/C/2026/2825/oj/eng/pdf"]),
 'ct24': ('Česká televize, ČT24, Dukovany budou stát mnohem víc než 407 miliard, říkají experti, 13 ottobre 2025 (spesa di preparazione dello Stato: 85 miliardi di corone). La pagina è stata ritrovata con una ricerca in questa revisione; il numero non è stato ricontrollato sul testo.', ['https://ct24.ceskatelevize.cz/clanek/ekonomika/dukovany-budou-stat-mnohem-vic-nez-407-miliard-rikaji-experti-366038']),
 'ecb': ("Banca centrale europea, cambio di riferimento medio del 2025: 24,688 corone ceche per euro (serie Eurostat ert_bil_eur_a; valore controllato nella revisione dell'11 novembre, pagina non riaperta in questa revisione).", []),
 'dds': ('Terna e Snam, Documento di descrizione degli scenari 2024 (valori ripresi dal registro di audit, punti B e C8). Fonte non verificata in questa revisione.', []),
 'pecd': ('ENTSO-E, Pan-European Climate Database (PECD) 2021.3, fattori di capacità orari, Zenodo. Fonte non verificata in questa revisione.', []),
 'sole24': ("Il Sole 24 Ore, Energy, from which countries is the energy imported to Italy? (2024: importazioni da Svizzera 43,1%, Francia 41,6%; importazioni nette 51 TWh, 16,3% del fabbisogno).", ['https://en.ilsole24ore.com/art/which-countries-energy-is-imported-AHgiDyCD']),
 'bdf': ("Banque de France, Energy balance in 2022: the crisis in nuclear power generation came at the worst possible time, 2023 (Francia importatrice netta di elettricità nel 2022 per la fermata di reattori).", ['https://www.banque-france.fr/system/files/2023-11/Energy_balance_in_2022_the_crisis_in_nuclear_power_generation_came_at_the_worst_possible_time_.pdf']),
 'econsuisse': ("economiesuisse, Winter electricity: ten years of stepping in place are enough, 2025 (Svizzera importatrice netta quasi ogni giorno da metà ottobre, con la centrale di Gösgen ferma).", ['https://jahrbuch-2025.economiesuisse.ch/en/articles/winter-electricity-ten-years-stepping-place-are-enough']),
 'gme': ('GME, Relazione annuale 2025 (PUN medio 2025: 115,94 €/MWh; prezzi alle frontiere; nel 2025 importazioni 55,2 TWh ed esportazioni 7,4 TWh).', ['https://www.mercatoelettrico.org/Portals/0/Documents/it-IT/Gme_RelazioneAnnualeWeb_2025.pdf']),
 'rte': ("RTE, Annual review 2025, Prices (media francese 2025 del mercato del giorno prima).", ["https://analysesetdonnees.rte-france.com/en/annual-review-2025/prices"]),
 'arera366': ("ARERA, delibera 366/2025/R/eel (capacità di importazione sulle sei frontiere: 11.535 MW).", ["https://www.arera.it/fileadmin/allegati/docs/25/366-2025-R-eel.pdf"]),
 'ternacap': ('Terna, Rapporto di identificazione delle capacità obiettivo 2025 (limiti sulla frontiera nord: 10.435 MW in importazione e 4.995 MW in esportazione; frontiera est: 1.100 MW in ciascuna direzione). Il totale di 6.095 MW in esportazione è una somma nostra: 4.995 più 1.100.', ['https://energiaoltre.it/wp-content/uploads/2025/03/Terna_Rapporto_Identificazione_Capacita_Obiettivo_2025_8dd5a76773e5cf4.pdf']),
 'ternapds': ('Terna, Piano di sviluppo 2025, Overview (oltre 23 miliardi di euro; 65 GW di rinnovabili in più al 2030).', ['https://arera.it/fileadmin/allegati/operatori/pds/25/Piano_di_Sviluppo_-_Overview.pdf']),
 'polimi': ("Politecnico di Milano, Energy &amp; Strategy, Renewable Energy Report 2025.", ["https://www.infobuildenergia.it/wp-content/uploads/2025/05/RER_Short_25_Digital.pdf"]),
 'gse': ("GSE, studio sui costi di generazione per ARERA, delibera 239/2025/R/efr, Allegato A.", ["https://www.arera.it/fileadmin/allegati/docs/25/239-2025-R-efr-ALLEGATO_A.pdf"]),
 'itsol': ("Italia Solare, Impianti utility scale, 22 ottobre 2025.", ["https://www.free-energia.it/FREE_NEW/wp-content/uploads/2025/10/Pizzini-20251022-presentazione-free.pdf"]),
 'pvps': ("IEA PVPS, National Survey Report of PV Power Applications in Italy 2024 (indirizzo come nel registro di audit dell'11 novembre: contiene la parola «Chinese» ma il registro lo indica come il rapporto sull'Italia; non riaperto in questa revisione).", ['https://iea-pvps.org/wp-content/uploads/2025/10/TASK1-Chinese-National-Survey-Report-of-PV-Power-Applications-in-Italy-2024.pdf']),
 'gsestat': ("GSE, Solare fotovoltaico, Rapporto statistico 2025 (parco nazionale: 1.117 ore equivalenti).", ["https://www.infobuildenergia.it/wp-content/uploads/2026/11/Solare-Fotovoltaico-Rapporto-Statistico-2025.pdf"]),
 'mase': ("MASE, valutazioni di impatto ambientale, relazioni di producibilità di progetti fotovoltaici in Puglia.", ["https://va.mite.gov.it/File/Documento/1022596", "https://va.mite.gov.it/File/Documento/1048911", "https://va.mite.gov.it/File/Documento/1158839"]),
 'fraunhofer': ("Fraunhofer ISE, Levelized Cost of Electricity, Renewable Energy Technologies, 2024.", ["https://www.ise.fraunhofer.de/content/dam/ise/en/documents/publications/studies/EN2024_ISE_Study_Levelized_Cost_of_Electricity_Renewable_Energy_Technologies.pdf"]),
 'nrelfleet': ("NREL, PV Fleet Performance Data Initiative, 2024 (degrado osservato del parco statunitense).", ["https://www.nrel.gov/news/program/2024/how-extreme-weather-and-system-aging-affect-the-us-photovoltaic-fleet"]),
 'anev': ("ANEV, brochure 2026 (parco eolico italiano nel 2025).", ["https://www.anev.org/wp-content/uploads/2026/06/Anev_brochure_2026.pdf"]),
 'arera332': ("ARERA, delibera 332/2026/R/eel (costo di riferimento di un sistema al litio da 4 ore: 150,5 € per kWh utile).", ["https://www.arera.it/fileadmin/allegati/docs/26/332-2026-R-eel.pdf"]),
 'ternastor': ("Terna, studio sulle tecnologie di accumulo, ARERA 168/2025/R/eel, Allegato A.", ["https://arera.it/fileadmin/allegati/docs/25/168-2025-R-eel-ALLEGATO_A.pdf"]),
 'essnews': ("ESS News, Italy's first MACSE battery auction, 1 ottobre 2025.", ["https://www.ess-news.com/2025/10/01/italys-first-macse-battery-auction-smashes-expectations-10-gwh-awarded-at-record-low-prices/"]),
 'baringa': ("Baringa, Did you miss out on Italy's MACSE auction.", ["https://www.baringa.com/en/insights/low-carbon-capital/did-you-miss-out-on-italys-macse-auction/italy-macse-auction/"]),
 'modo': ("Modo Energy, Italy MACSE results: low prices, economics, 8 ottobre 2025.", ["https://modoenergy.com/research/en/italy-macse-results-low-prices-economics-october-25"]),
 'modoferx': ("Modo Energy, Italy FER-X auction, 11 dicembre 2025.", ["https://modoenergy.com/research/italy-fer-x-auction-solar-wind-renewables-december-25"]),
 'andersen': ("Andersen, FER-X Transitorio, approfondimento, marzo 2025.", ["https://it.andersen.com/wp-content/uploads/2026/04/andersen-approfondimento-energy-FER-X-Transitorio-03-2025.pdf"]),
 'wfw': ("Watson Farley &amp; Williams, Italy's new transitional FER-X decree.", ["https://www.wfw.com/articles/italys-new-transitional-fer-x-decree-incentives-for-renewable-energy-projects-for-2025/?l=it"]),
 'iea': ("IEA, Global Hydrogen Review 2025, Assumptions Annex.", ["https://iea.blob.core.windows.net/assets/15673ab3-a86a-4434-bff4-490bb42d3563/GlobalHydrogenReview2025AssumptionsAnnex.pdf"]),
 'hystories': ('Hystories, Deliverable D8.6, Italian case study, 15 giugno 2023 (costo dello stoccaggio in giacimento esaurito: 3,76 €/kg, intervallo 2,06-14,95 €/kg; riaperto e confermato in questa revisione).', ['https://hystories.eu/wp-content/uploads/2023/12/Hystories_D8.6-Italian-Case-Study_def.pdf']),
 'power': ("POWER Magazine, Ontario authorizes OPG to start construction of first commercial SMR, maggio 2025 (BWRX-300 a Darlington: 7,7 miliardi di dollari canadesi per l'unità 1, 20,9 per quattro unità). La pagina è stata ritrovata con una ricerca in questa revisione; i numeri non sono stati ricontrollati sul testo.", ['https://www.powermag.com/ontario-authorizes-opg-to-start-construction-of-first-commercial-nuclear-smr']),
 'wna': ("World Nuclear Association, World Nuclear Performance Report 2025.", ["https://world-nuclear.org/our-association/publications/world-nuclear-performance-report/Global-nuclear-industry-performance"]),
 'iaea': ("IAEA, Nuclear Power Reactors in the World, Reference Data Series 2, edizione 45.", ["https://www-pub.iaea.org/MTCD/Publications/PDF/RDS-2-45_web.pdf"]),
 'arera12': ("ARERA, delibera 12/2026/R/eel del 3 febbraio 2026 (carico interrompibile: 2,4 GW a 46 €/kW all'anno, al massimo 120 ore l'anno; citata in model/techs_v8.json). Fonte non verificata in questa revisione.", []),
 'barakah': ("Barakah: contratto di costruzione del dicembre 2009 da 20,4 miliardi di dollari (registro di audit, docs/audit/audit_v8_findings.md, punto A8)." + NV, []),
 'saeul': ("Shin Hanul: bilancio di 6,5 mila miliardi di won per unità da 1,4 GW (registro di audit, punto A9)." + NV, []),
 'risk': ("Mediana dei cantieri occidentali: Flamanville 3 (EDF, 13,2 miliardi di euro 2015), Olkiluoto 3, Mochovce 3-4 (6,7 miliardi di euro per il completamento), Vogtle 3-4 (registro di audit, punto A10)." + NV, []),
 'vogtle': ("Vogtle 3 e 4: Associated Press, 25 maggio 2023 (31 miliardi di dollari a carico dei proprietari, capitale e oneri finanziari; registro di audit, punto A7)." + NV, []),
 'france': ("RTE, Annual electricity review 2024, Key findings (produzione nucleare francese del 2024; pagina riaperta in questa revisione). Il fattore di carico del 67% è un valore del registro di audit, punto C2, che la pagina non riporta: non verificato in questa revisione.", ["https://analysesetdonnees.rte-france.com/en/annual-review-2024/keyfindings"]),
 'arera564': ("ARERA, delibera 564/2023 (carico interrompibile fino a 3,75 GW a 105 €/kW all'anno; citata in model/techs_v8.json)." + NV, []),
 'techsrc': ("Fonti indicate nel file model/techs_v8.json per i dati minori dell'Appendice C. Solare termodinamico: Andasol 1, 310 milioni di euro per 49,9 MW nel 2008 (SolarPACES), e IRENA, Renewable Power Generation Costs in 2024, media mondiale di 3.677 $/kW. Geotermico: IRENA 2024, NREL ATB 2024, Fervo (7.000 $/kW oggi, obiettivo 3.000 $/kW). Bioenergie: nota di ricerca del progetto e AIEL 2025 (cippato a 33 €/MWh termico). Aria compressa: Hydrostor, Silver City (1.914 €/kW, 239 € per kWh, 8 ore), e obiettivo dichiarato da Energy Dome. Pompaggi: Terna (7,3 GW), Ambrosetti (53 GWh), scenario Terna-Snam (4,5 GW e 35 GWh; 2.330 €/kW a 8 ore). Accumulo da 100 ore: Form Energy, obiettivo del 2021 di 20 $ per kWh. Turbina a idrogeno: ACER. Ricarica intelligente: Transport &amp; Environment 2024. Nuove interconnessioni: progetti Terna e ARERA, 7,33 GW in tutto." + NV, []),
 'repo': ("Repository del progetto: codice del modello, dati di ingresso con le fonti (model/techs_v8.json), risultati (docs/results_v8.md) e registro di audit (docs/audit/).", ["https://github.com/ClGratton/nucleare-italia-2040"]),
}
SOURCES_NOTE = "Le pagine con indirizzo vengono dal registro di audit dell'11 novembre 2026, salvo dove indicato. In questa revisione è stato possibile riaprire solo poche pagine: dove un numero non è stato ricontrollato sulla fonte, la voce lo dice e, se l'indirizzo non viene dal registro di audit, non lo riporta."

# =============================================================================================================
# SINTESI
# =============================================================================================================
h1("Sintesi")
# F1, F2
p("Questo documento risponde a una domanda: quanta potenza nucleare contiene il sistema elettrico italiano di minor costo, a zero emissioni dirette, con la domanda prevista per il 2040 (400 TWh l'anno). Il calcolo usa un modello che sceglie insieme tutti gli impianti (fotovoltaico, eolico, nucleare, accumuli, idrogeno, scambi con l'estero) e controlla che la domanda sia coperta in ogni intervallo di 3 ore di quattro anni meteorologici, dal 2016 al 2019.")
# F3, F4, F2
p("Il risultato poggia su tre scelte. Una sola regola di costo vale per tutte le fonti: costo di costruzione ai prezzi di oggi, interessi durante il cantiere, vita tecnica ed esercizio, senza sussidi e senza prezzi d'asta. Il nucleare costa 10.200 €/kW netti, con 9 anni di cantiere e 60 di vita. È una somma nostra: il prezzo del contratto della centrale ceca di Dukovany, riportato nella decisione della Commissione europea [@ec], più i costi del proprietario, presi da una fonte pubblica ceca [@ct24]. Sta alla base dell'intervallo che la Commissione riporta, 10.095-12.710 €/kW in euro 2025. Il sistema non si appoggia agli altri paesi: ogni anno esporta tanta energia quanta ne importa e nelle tre settimane più difficili di ogni anno non conta su centrali estere.")
# F1, R1
p("Con queste regole e capitale al 5% reale il sistema di minor costo ha 23,2 GW di nucleare, pari al 44,5% della domanda, se le tecnologie che non hanno ancora impianti commerciali (idrogeno, aria compressa, solare termodinamico, piccoli reattori) costano come i primi impianti realizzati: è il caso PI, primo impianto. Ne ha 15,7 GW, il 30,5%, se quelle tecnologie raggiungono i costi obiettivo dichiarati dai produttori: è il caso OB, obiettivo. Con capitale al 7% i valori sono 15,6 GW (PI) e 11,1 GW (OB, tutti piccoli reattori modulari). In tutto il documento la potenza nucleare comprende i piccoli reattori modulari.")
p("I risultati principali sono sette. Tutti i valori sono a passo di 3 ore; i costi sono in euro 2025 per MWh di domanda non coperta dall'idroelettrico esistente (356,6 TWh l'anno).")
b([
 # F5 (flat optimum)
 "<b>L'ottimo è piatto.</b> Nel caso PI al 5% ogni potenza tra 16 e 28 GW costa entro l'1% del minimo. Il valore di 23,2 GW è il centro di una fascia larga: piccoli cambi nei costi spostano l'ottimo di molti GW e il costo del sistema di poco. Nel caso OB al 5% la fascia è 12-20 GW; al 7% è 12-20 GW (PI) e 4-16 GW (OB).",
 # F1, F8
 "<b>Circa 15 GW stanno dentro o vicino all'ottimo nella maggior parte dei casi, non in tutti.</b> Al 5% reggono con il nucleare tra il costo del contratto e il punto medio dell'intervallo ufficiale (punto medio, 11.400 €/kW: 16 GW nel caso PI e 12 GW nel caso OB) e, al 7%, nel caso PI al costo del contratto (15,6 GW). Non reggono quando due condizioni sfavorevoli si sommano: OB al 7% (11 GW); OB al massimo dell'intervallo senza piccoli reattori (8 GW); 7% con il massimo dell'intervallo (PI 4 GW; OB, solo reattori grandi: 0); 7% con la mediana dei cantieri occidentali (PI 8 GW; OB, solo reattori grandi: 0); OB al costo di Vogtle (solo reattori grandi: 0). Non reggono neppure, da sola, con la regola sugli scambi della versione 7 (7-12 GW). Nel caso OB al 7% il sistema ha comunque 11,1 GW di piccoli reattori qualunque sia il costo dei reattori grandi, e al costo di Vogtle al 5% circa 14,4 GW di piccoli reattori. Sulla griglia di 4 GW, 16 GW stanno entro l'1% del minimo in 11 delle 20 combinazioni tra i cinque casi di costo dal contratto in su e le quattro curve.",
 # R1
 "<b>Il nucleare abbassa il costo del sistema.</b> Al 5% il sistema con nucleare costa 114,42 €/MWh contro 127,77 senza (PI): 13,35 €/MWh in meno, cioè 4,8 miliardi di euro l'anno. Nel caso OB costa 107,53 contro 114,39: 6,86 €/MWh, 2,4 miliardi l'anno. Al 7% il risparmio è 8,59 €/MWh (PI) e 2,63 €/MWh (OB).",
 # F5, R2
 "<b>I primi GW valgono più degli ultimi.</b> Nel caso PI al 5% i primi 4 GW valgono 1.318 €/kW all'anno, più del costo annuo di una centrale costruita come a Vogtle (1.147): convengono in tutti i casi di costo esaminati. Nel caso OB senza piccoli reattori valgono 1.145 €/kW all'anno: alla pari con il costo di Vogtle, non sopra.",
 # F5, R4
 "<b>Tra le regole del sistema quella sugli scambi con l'estero sposta di più il risultato; il costo del nucleare lo sposta ancora di più.</b> Con la regola della versione 7, che è un insieme di cinque cambi, il nucleare ottimo scende a 11,9 GW (PI) e 7,2 GW (OB). In quella regola l'Italia importa 52-71 TWh l'anno e non esporta nulla, contro 55,2 TWh importati e 7,4 esportati nel 2025: è circa la dipendenza di oggi. Nelle settimane critiche, tutte tra novembre e febbraio, quella dipendenza è in buona parte nucleare dei vicini: un sistema senza nucleare costruito così lo importa. Il caso centrale non conta su quelle centrali, e questo costa 4,44 €/MWh con nucleare (1,6 miliardi di euro l'anno) e 11,82 €/MWh senza (4,2 miliardi) nel caso PI; 4,15 €/MWh (1,5 miliardi) e 8,87 €/MWh (3,2 miliardi) nel caso OB. I casi di costo del nucleare coprono da 0 a 40 GW.",
 # F5, F8, R3, R4
 "<b>Il risultato dipende da quanto costa costruire e finanziare.</b> Il nucleare deve essere finanziato a un tasso vicino a quello delle alternative. Con il nucleare al 7% e tutto il resto al 5% l'ottimo è 4 GW nel caso PI (0-12 GW entro l'1%) e 0 nel caso OB (anche i piccoli reattori al 7% non entrerebbero); con il nucleare al 6% è 16 GW (PI) e 8 GW (OB senza piccoli reattori). Al punto medio dell'intervallo ufficiale (11.400 €/kW) l'ottimo sulla griglia di 4 GW è 16 GW (PI) e 12 GW (OB); al massimo (12.700 €/kW) è 12 GW (PI) e 8 GW (OB con i soli reattori grandi). Con cantieri di 7 anni invece di 9 l'ottimo libero sale a 26,7 GW (PI) e 18,2 GW (OB).",
 # F6
 "<b>Il valore è vicino a quello della versione precedente per una coincidenza.</b> Tra la versione 7 con autosufficienza e la versione 8 sono cambiate molte cose, in direzioni opposte: il costo fisso annuo del nucleare è salito del 36%, quello del fotovoltaico a terra del 54% e quello delle batterie dell'88%; sono cambiati anche il prezzo delle esportazioni, il criterio per le settimane critiche, la disponibilità del nucleare e due errori di codice. La sezione 7 ricostruisce tutti i cambi, dal 74% del primo documento a oggi, e riassume il registro dei 98 errori trovati.",
])
# F8
box("Raccomandazione", [
 "Pianificare un parco nucleare di circa 15 GW: circa 15 unità APR1000 da 976 MW netti, pari a circa il 30% della domanda 2040. È la parte giustificata nella maggior parte dei casi: è l'ottimo con le alternative al costo obiettivo (OB al 5%: 15,7 GW), con capitale al 7% e costi di primo impianto (PI al 7%: 15,6 GW) e, nel caso PI, con il nucleare al massimo dell'intervallo ufficiale di costo (14,0 GW). Al punto medio dell'intervallo ufficiale, con capitale al 5%, i 15 GW reggono ancora: 16 GW nel caso PI e 12 GW nel caso OB. Tenere aperta l'opzione di crescere fino a circa 23 GW se idrogeno, aria compressa e solare termodinamico non raggiungono i costi obiettivo (PI al 5%: 23,2 GW; 16-28 GW entro l'1% del costo minimo).",
 "<b>Condizioni.</b> Centrali costruite al costo del contratto di Dukovany più i costi del proprietario (circa 10.200 €/kW netti, 9 anni di cantiere); nucleare finanziato a un tasso vicino a quello delle alternative (nel caso centrale il 5% reale per tutte le fonti; con il 7% per tutte i 15 GW reggono solo con le alternative ai costi dei primi impianti): con il nucleare al 7% e il resto al 5% l'ottimo scende a 4 GW (PI) e 0 (OB). Per questo contano strumenti come quelli di Dukovany (prestito statale, contratto per differenza), come FER-X li dà alle rinnovabili. Infine la scelta di non contare su centrali estere nelle settimane critiche, che ha un prezzo: 4,44 €/MWh con nucleare nel caso PI.",
 "<b>Condizioni che la cambiano.</b> Capitale al 7% insieme ad alternative al costo obiettivo: 11 GW, come piccoli reattori. Oppure il nucleare finanziato a un tasso più alto delle alternative: al 7% con il resto al 5%, 4 GW (PI) e 0 (OB, solo reattori grandi). Oppure la scelta di restare alla dipendenza di oggi dalle importazioni: 7-12 GW.",
 "<b>Casi in cui i 15 GW non reggono.</b> Quando due condizioni sfavorevoli si sommano. Capitale al 7% con il nucleare al massimo dell'intervallo (PI 4 GW; OB, solo reattori grandi: 0) o al costo della mediana dei cantieri occidentali (PI 8 GW; OB, solo reattori grandi: 0); nel caso OB al 7% restano comunque 11,1 GW di piccoli reattori. Alternative al costo obiettivo con il nucleare al costo di Vogtle (solo reattori grandi: 0; circa 14,4 GW di piccoli reattori) o al massimo dell'intervallo: lì l'ottimo è 14,4 GW solo come piccoli reattori al costo obiettivo, e con i soli reattori grandi è 8 GW, con ogni potenza tra 0 e 12 GW entro l'1% del minimo (risparmio 0,88 €/MWh). Nel caso PI al 5% i primi 4 GW convengono in tutti i casi di costo esaminati, Vogtle compreso.",
])

# =============================================================================================================
# 1
# =============================================================================================================
h1("1. Il costo medio per MWh non basta")
p("Il confronto pubblico tra le fonti si fa quasi sempre con il costo medio di produzione di un MWh, il cosiddetto LCOE: i costi di un impianto divisi per l'energia che produce nella sua vita. Questo numero non dice quando l'energia arriva. Un sistema elettrico deve coprire la domanda in ogni ora, comprese le sere d'inverno senza sole e con poco vento. Per farlo con fonti che dipendono dal tempo servono impianti in più, accumuli, rete e capacità di riserva, e una parte dell'energia prodotta nelle ore di abbondanza resta inutilizzata. Questi costi non compaiono nel costo medio della singola fonte.")
p("Il costo che conta è quello dell'intero sistema che copre la domanda. Per questo il documento non confronta fonti singole: calcola il sistema di minor costo e guarda quanta potenza nucleare contiene. Il valore del nucleare si misura per differenza: di quanto scende il costo del sistema quando si aggiunge un blocco di potenza nucleare e tutto il resto viene ottimizzato di nuovo. Questo valore, in €/kW all'anno, si confronta con il costo fisso annuo di una centrale. Finché il valore del blocco supera il costo, costruirlo conviene.")
p("Il metodo ha un vantaggio pratico. La curva del valore non dipende dal costo ipotizzato per il nucleare: calcolata una volta, permette di leggere la potenza conveniente per qualsiasi costo, quello di Dukovany come quello di Barakah o di Vogtle. Chi non condivide il costo centrale di questo documento può mettere il proprio sulla stessa curva (sezione 5). Il dettaglio formale è nel preprint scientifico che accompagna questo documento.")

# =============================================================================================================
# 2
# =============================================================================================================
h1("2. Il modello")
# F2
p("Il modello è un programma lineare di espansione della capacità, risolto con il solutore HiGHS. Decide quanta potenza costruire di ogni tecnologia e come farla funzionare, in modo da coprire la domanda al costo totale minimo e con emissioni dirette nulle. L'Italia è un solo nodo: la rete interna entra come costo, non come vincolo (il costo è un'ipotesi degli autori, sezione 8). Un unico parco di impianti deve funzionare in tutti e quattro gli anni meteorologici 2016-2019, ottimizzati insieme a passo di 3 ore: 11.680 intervalli, tra 315.000 e 390.000 variabili e tra 365.000 e 475.000 vincoli (circa il doppio con otto anni meteorologici) per esecuzione. Il sistema calcolato è quello a regime, con tutti gli impianti già costruiti: il modello non descrive il percorso per arrivarci né i ritmi di costruzione.")
h2("Domanda e anni meteorologici")
# F2; A C8 (404-439); T (pecd)
p("La domanda è di 400 TWh l'anno: 338 di base, 15 per le pompe di calore e 47 per i veicoli elettrici. È poco sotto l'intervallo di 404-439 TWh del Documento di descrizione degli scenari 2024 di Terna e Snam [@dds]. Il profilo è il carico orario italiano misurato da Terna nel 2016-2019, abbinato alla produzione di sole e vento dello stesso anno meteorologico, presa dalla banca dati climatica europea PECD [@pecd]. L'idroelettrico esistente, 15 GW e 43,4 TWh l'anno, è un dato. Tutti i costi sono espressi per MWh dei restanti 356,6 TWh.")
h2("Tecnologie, caso PI e caso OB")
# F2; T (minload 0.5, av 0.90)
p("Sono variabili di decisione: fotovoltaico (a terra, agrivoltaico, tetti industriali e altri tetti, per zona e con suolo limitato), eolico a terra e in mare (in blocchi di potenza finita), nucleare grande, piccoli reattori modulari, batterie, idrogeno (elettrolizzatore, stoccaggio sotterraneo, turbina), aria compressa, accumulo da 100 ore, pompaggi, nuovo idroelettrico, geotermico, bioenergie, solare termodinamico, carico interrompibile, ricarica intelligente dei veicoli e interconnessioni. Il nucleare può scendere fino al 50% della potenza disponibile e ha una disponibilità media del 90%.")
p("Le tecnologie con impianti commerciali hanno un solo costo. Quelle senza (catena dell'idrogeno, aria compressa, solare termodinamico su larga scala, piccoli reattori modulari, accumulo da 100 ore, geotermico avanzato) ne hanno due: il costo dei primi impianti realizzati (PI) e il costo obiettivo dichiarato dai produttori (OB). L'accumulo da 100 ore è escluso dal caso PI perché non ha un costo osservato. Il caso OB non è un limite inferiore per il nucleare: porta al costo obiettivo tutte le tecnologie senza impianti commerciali, e quindi abbassa le alternative non nucleari ma anche i piccoli reattori, per cui con i reattori grandi cari può avere più nucleare del caso PI; fotovoltaico, eolico e batterie restano ai costi di oggi in entrambi i casi. Diverse varianti danno meno nucleare del caso OB centrale. I reattori grandi hanno lo stesso costo nei due casi.")
h2("Adeguatezza")
# F2; A B (credits: PV, wind 0); F7
p("La capacità su cui si può contare deve essere almeno 1,1 volte il picco di carico, che nei dati a 3 ore è 76,9 GW. Fotovoltaico ed eolico non contano per questo vincolo. Le batterie contano per la potenza moltiplicata per 4/6,6 e l'idroelettrico esistente per tutti i 15 GW: sono ipotesi.")
h2("Scambi con l'estero")
# F2; T (IMPORT src: residual load = load minus 100 GW PV and 40 GW onshore)
p("La regola centrale è uno scambio annuo in pareggio: in ogni anno l'Italia importa tanta energia quanta ne esporta. L'energia importata costa 115,94 €/MWh, il prezzo medio italiano del 2025 (PUN); quella esportata rende 61,07 €/MWh, il prezzo medio francese del 2025 [@gme, @rte]. La capacità di esportazione è 6.095/11.535 di quella di importazione, come nei limiti di Terna [@arera366, @ternacap]; i 6.095 MW di esportazione sono una somma nostra, 4.995 MW sulla frontiera nord più 1.100 MW sulla frontiera est. Nelle tre settimane di ogni anno con il carico residuo più alto il sistema non importa e la capacità estera non conta per l'adeguatezza. Il carico residuo è la domanda meno la produzione di 100 GW di fotovoltaico e 40 GW di eolico a terra.")
p("La ragione della regola è che un piano nazionale deve funzionare anche se tutti i paesi vicini pianificano allo stesso modo. Se ogni paese contasse sulle centrali degli altri nelle settimane critiche, quelle centrali non basterebbero per tutti. C'è poi una ragione di confronto. Le settimane critiche del modello cadono tutte tra novembre e febbraio: le 12 dei quattro anni sono in gennaio, febbraio, novembre e dicembre. Nel 2024 l'85% delle importazioni italiane veniva da Svizzera (43%) e Francia (42%) [@sole24]. In inverno la Francia ha il suo picco di domanda e la sua capacità sicura è nucleare; la Svizzera nell'inverno 2025/26 è stata importatrice netta quasi ogni giorno, con la centrale nucleare di Gösgen ferma [@econsuisse]; la Francia è stata importatrice netta nel 2022, quando ha dovuto fermare dei reattori [@bdf]. Contare sulle importazioni in quelle settimane vuol dire quindi contare in buona parte su centrali nucleari estere, proprio quando servono a casa loro. Un sistema italiano senza nucleare costruito così non è senza nucleare: lo importa. Per questo la regola centrale non è una scelta che favorisce il nucleare ma il modo di confrontare sistemi davvero diversi. La sezione 6 mostra comunque la regola della versione 7 come variante e ne dà il prezzo: 4,44 €/MWh con nucleare e 11,82 €/MWh senza nel caso PI.")
# R5
p("Gli scambi restano utili per spostare energia nel tempo, e il modello li usa: nel caso PI con nucleare scambia 17,7 TWh l'anno in ciascuna direzione.")

# =============================================================================================================
# 3
# =============================================================================================================
h1("3. Una sola regola di costo per tutte le fonti")
# F3
p("Ogni tecnologia, nucleare compreso, entra nel modello con un costo annuo calcolato allo stesso modo: costo di costruzione, moltiplicato per gli interessi durante il cantiere, ripartito in rate annue sulla vita tecnica, più i costi fissi di esercizio e manutenzione. Fanno eccezione tre voci per cui esiste solo un prezzo annuo: lo stoccaggio di idrogeno, l'accumulo da 100 ore e il carico interrompibile.")
p("Il costo di costruzione è quello senza interessi (overnight): comprende lo sviluppo del progetto e il collegamento alla rete, esclude gli imprevisti non spesi, i sussidi e i contributi pubblici. Gli interessi durante il cantiere si calcolano al tasso reale sugli anni di costruzione, con la spesa ripartita in parti uguali tra gli anni. La rata annua ripartisce il costo sulla vita tecnica dell'impianto allo stesso tasso reale.")
# F3; T (_doc: no learning to 2040 except target)
p("I valori sono in euro 2025, con potenza netta e produzione realistica. Dove è stato possibile vengono da impianti contrattati o costruiti nel 2024-2026 e da fonti ufficiali o regolatorie, ma non sempre: alcune fonti sono studi universitari, associazioni di settore e stampa specializzata, e i riferimenti per il solare termodinamico (Andasol, 2008) e per Barakah (contratto del 2009) sono più vecchi. Non c'è riduzione dei costi fino al 2040, salvo nei costi obiettivo del caso OB. Il motivo è che la scelta si fa oggi: il nucleare va contrattato adesso, ai prezzi di adesso, perché richiede dieci anni tra decisione e messa in servizio. Le alternative vanno confrontate allo stesso modo: fotovoltaico e batterie si costruiscono in uno o due anni, e l'idrogeno che dovrebbe sostituire il nucleare nelle settimane invernali è l'ultimo pezzo del sistema, da costruire prima di spegnere gli impianti fossili. Dare costi futuri solo alle alternative significherebbe confrontare un contratto di oggi con una previsione; darli a tutte, nucleare in serie compreso, significherebbe confrontare due previsioni. Il tasso reale è il 5% nel caso centrale e il 7% nella variante, uguale per tutte le tecnologie.")
h2("I prezzi d'asta non sono costi")
# F3; S5 (cumulation up to 40%, tax credits), S4 (MACSE; analysts), A B9 (implied 95 against 150.5)
p("Le versioni precedenti usavano per fotovoltaico, eolico e batterie i prezzi delle aste pubbliche. Un prezzo d'asta non è un costo. Il prezzo medio del fotovoltaico nell'asta FER-X del dicembre 2025, 56,82 €/MWh, è cumulabile con contributi in conto capitale fino al 40%, e in quel caso la tariffa è ridotta fino al 35% [@modoferx, @andersen, @wfw]. Il premio dell'asta MACSE per le batterie, 12.959 €/MWh all'anno, corrisponde a circa 95 € per kWh per batterie di circa 6,6 ore; il riferimento ARERA di 150,5 € per kWh vale per batterie da 4 ore, quindi i due numeri non descrivono lo stesso prodotto [@essnews, @arera332]. Secondo gli analisti le offerte contavano su ricavi successivi al contratto e su rendimenti bassi [@baringa, @modo].")
# A (rule set by the owner)
p("Usare quei prezzi per le rinnovabili e il costo pieno per il nucleare avrebbe confrontato grandezze diverse. La regola seguita nella revisione è che ogni correzione applicata a una fonte va verificata su tutte le altre: costi del proprietario, potenza netta, interessi durante il cantiere, vita, esercizio, produzione realistica.")
# T (vre.pv src: degradation mean 0.94; existing fleet 1,117 h), F4 (90%)
p("Produzione realistica vuol dire, per esempio, che il fotovoltaico perde lo 0,5% di resa l'anno (in media sulla vita produce il 94% del primo anno), che gli impianti esistenti producono quanto il parco osservato (1.117 ore equivalenti nel 2025 [@gsestat]) e che il nucleare ha la disponibilità del 90% dichiarata per Dukovany, non il 100%.")
# F3 table
tab([
 ["Tecnologia", "Costo di costruzione", "Esercizio fisso", "Vita, cantiere (anni)", "Costo annuo al 5%", "Fonte"],
 ["Nucleare grande (caso centrale)", "10.200 €/kW netto", "27,75 €/MWh", "60, 9", "911 €/kW all'anno", "[@ec, @ct24]"],
 ["Fotovoltaico a terra con inseguitore", "950 €/kWp", "20 €/kWp all'anno", "25, 1", "89 €/kWp all'anno", "[@polimi, @itsol, @gse]"],
 ["Agrivoltaico", "1.200 €/kWp", "20 €/kWp all'anno", "25, 1", "107 €/kWp all'anno", "[@polimi]"],
 ["Fotovoltaico su tetti industriali", "950 €/kWp", "20 €/kWp all'anno", "25, 1", "89 €/kWp all'anno", "[@gse, @polimi]"],
 ["Fotovoltaico su altri tetti", "1.250 €/kWp", "20 €/kWp all'anno", "25, 1", "111 €/kWp all'anno", "[@gse, @pvps]"],
 ["Eolico a terra", "1.600 €/kW", "40 €/kW all'anno", "25, 2", "159 €/kW all'anno", "[@polimi, @gse]"],
 ["Eolico in mare galleggiante", "4.750 €/kW", "100 €/kW all'anno", "25, 3", "463 €/kW all'anno", "[@polimi]"],
 ["Batterie da 4 ore", "168,6 € per kWh utile", "4,486 €/kWh all'anno", "15, 2", "21.547 €/MWh all'anno", "[@arera332]"],
 ["Elettrolizzatore (PI)", "2.056 €/kW", "3% l'anno", "20, 2", "", "[@iea]"],
 ["Stoccaggio di idrogeno (PI)", "", "", "", "113 €/MWh all'anno", "[@hystories]"],
 ["Piccoli reattori modulari (PI; OB)", "17.200; 11.700 €/kW", "come il nucleare grande", "60, 5", "1.264; 934 €/kW all'anno", "[@power]"],
], [25, 15, 18, 10, 20, 12],
 "Tabella 1. Costi principali con la regola unica, euro 2025. Nucleare: 40 €/MWh di esercizio in tutto, di cui 27,75 fissi e 12,25 variabili; costo annuo al 7%: 1.239 €/kW all'anno. Fotovoltaico: degrado dello 0,5% l'anno; tetti industriali: media di GSE (850) e PoliMi (1.000-1.100); altri tetti: media di GSE (1.100) e IEA PVPS (1.400). Eolico in mare: in Italia nessun impianto galleggiante è stato costruito. Batterie: 150,5 € per kWh utile per 1,12 di sovradimensionamento, rendimento 85%. Stoccaggio di idrogeno: per MWh di capacità utile, in un giacimento di gas esaurito, da uno studio a tavolino. Piccoli reattori: Darlington, unità 1 (PI) e programma di quattro unità (OB); costo annuo OB al 7%: 1.231 €/kW all'anno. Elenco completo nell'Appendice C; ogni valore e la sua fonte sono nel file model/techs_v8.json del repository [@repo].", align='lllrll', fs=7.8)

# =============================================================================================================
# 4
# =============================================================================================================
h1("4. Il costo del nucleare")
# F4; A A1-A6
p("Il caso centrale è Dukovany 5 e 6, due reattori APR1000 che l'impresa coreana KHNP costruirà in Repubblica Ceca. La fonte principale è la decisione con cui la Commissione europea ha aperto l'indagine sull'aiuto di Stato ceco, pubblicata il 27 maggio 2026 [@ec]: riporta il prezzo del contratto, la potenza, il modello finanziario e un intervallo per il costo complessivo. Il pacchetto di aiuti per le due unità è oggetto di un'indagine approfondita e non è stato approvato. I 10.200 €/kW netti del caso centrale non sono un numero della decisione. Sono una somma nostra: il contratto di costruzione riportato nella decisione (407 miliardi di corone) più i costi del proprietario (85 miliardi di corone, un dato pubblico della televisione ceca [@ct24], che nella decisione non c'è). Non sono costi a consuntivo: i lavori sono previsti dal 2029 e il primo collegamento alla rete a dicembre 2036 per l'unità 5 e a dicembre 2037 per l'unità 6. Che una centrale italiana costi quanto Dukovany è un'ipotesi.")
# F4, F10
p("Per il costo senza interessi delle due unità la decisione dà solo un intervallo: tra 20 e 25 miliardi di euro, con costruzione, contratto del combustibile, costi del proprietario e imprevisti. Tolto il combustibile sono 10.095-12.710 €/kW netti in euro 2025. Il nostro valore sta alla base dell'intervallo: corrisponde a una centrale costruita senza spendere gli imprevisti. È la stessa regola usata per tutte le fonti, che entrano al prezzo di contratto senza imprevisti: un piano si fa per costruire bene, e chi decide deve sapere quanto conviene in quel caso. Per questo il costo del nucleare non è tra i limiti della sezione 8. Il resto dell'intervallo è letto come caso di costo: il documento legge sulle curve anche il punto medio dell'intervallo (11.400 €/kW) e il massimo (12.700 €/kW). La Tabella 2 mostra come si arriva al valore centrale, passo per passo.")
# F4 (derivation); 492/24.688 = 19,93 (A A3); 85/24.688 = 3,44 mld, dentro 3,0-5,0 (F4)
tab([
 ["Passo", "Valore", "Nota"],
 ["1. Contratto di costruzione (EPC) con KHNP, giugno 2025", "407 miliardi di corone", "Il combustibile è un contratto separato (15-20 miliardi di corone per circa dieci anni) e non è dentro i 407 miliardi [@ec]"],
 ["2. Preparazione dello Stato e costi del proprietario", "85 miliardi di corone", "Dato pubblico della televisione ceca [@ct24], non presente nella decisione; è dentro l'intervallo di 3,0-5,0 miliardi di euro che la Commissione riporta per i costi di sviluppo"],
 ["3. Totale in euro", "492 miliardi di corone = 19,93 miliardi di euro", "Cambio medio BCE del 2025: 24,688 corone per euro [@ecb]"],
 ["4. Potenza netta", "2 × 976 MW = 1.952 MW", "«Fino a 976 MWe» vendibili per unità; 1.055 MWe è la potenza lorda"],
 ["5. Costo per kW netto", "10.210 €/kW, arrotondato a 10.200", "Nostro calcolo: passo 3 diviso passo 4"],
 ["6. Cantiere e vita", "9 anni e 60 anni", "Modello finanziario ceco"],
 ["7. Produzione", "15,4 TWh l'anno", "Pari al 90% della potenza netta"],
 ["8. Esercizio", "40 €/MWh", "Punto medio dell'intervallo ufficiale 35-45 €/MWh (esercizio fisso, investimenti nel ciclo di vita, combustibile, conto per i rifiuti, smantellamento): 27,75 fissi e 12,25 variabili"],
 ["9. Costo fisso annuo al 5%", "676 + 219 + 16 = 911 €/kW all'anno", "Capitale, esercizio fisso, rete. Al 7%: 1.239 €/kW all'anno"],
], [27, 25, 48],
 "Tabella 2. Derivazione del costo centrale del nucleare dai dati di Dukovany 5 e 6. Fonte dei dati: decisione della Commissione europea [@ec], salvo dove indicato. Le somme in euro e per kW sono nostro calcolo.")
# F7 (OPEX +-39)
p("Sul costo di esercizio l'intervallo ufficiale è 35-45 €/MWh. Con 35 il costo fisso annuo scende di circa 39 €/kW all'anno, con 45 sale di altrettanto.")
h2("Gli altri casi di costo")
# F4; R3 (fixN al 5% e al 7%)
p("La Tabella 3 elenca i casi di costo che il documento legge sulla curva del valore. Tutti usano gli stessi costi di esercizio, la stessa vita e la stessa disponibilità del caso centrale: cambiano solo il costo di costruzione e gli anni di cantiere.")
_cc = {r[0]: r for r in RES['3|PI 5%'][1:]}
_cc7 = {r[0]: r for r in RES['3|PI 7%'][1:]}
def _ccrow(name, key, note):
    r, r7 = _cc[key], _cc7[key]
    return [name, it(r[1]), r[2], it(r[3]), it(r7[3]), note]
tab([
 ["Caso di costo", "Costo (€/kW)", "Cantiere (anni)", "Costo fisso al 5%", "Costo fisso al 7%", "Descrizione"],
 _ccrow("Dukovany, contratto (caso centrale)", "Dukovany contract, central", "Contratto nella decisione della Commissione più costi del proprietario; base dell'intervallo ufficiale"),
 _ccrow("Dukovany in 7 anni", "Dukovany, 7 years", "Stesso costo, cantiere più breve"),
 _ccrow("Punto medio dell'intervallo ufficiale", "Dukovany, midpoint of EC bracket", "Con metà degli imprevisti spesi"),
 _ccrow("Massimo dell'intervallo ufficiale", "Dukovany, top of EC bracket", "Con tutti gli imprevisti spesi"),
 _ccrow("Barakah", "Barakah", "Contratto del dicembre 2009 da 20,4 miliardi di dollari, rivalutato, più i costi del proprietario, pari al 12,57% del costo complessivo, cioè il 14,4% in più del contratto (circa 4.800 €/kW senza). È un minimo: il costo finale non è pubblico [@barakah]"),
 _ccrow("Saeul (bilancio di Shin Hanul)", "Saeul budget", "Un bilancio di previsione, non un costo finale [@saeul]"),
 _ccrow("Mediana dei cantieri occidentali recenti", "Risk median", "Flamanville 3, Olkiluoto 3, Mochovce 3-4, Vogtle 3-4. Hinkley Point C è escluso: con Hinkley circa 10.300 €/kW [@risk]"),
 _ccrow("Vogtle", "Vogtle", "Vogtle 3 e 4, Stati Uniti [@vogtle]"),
], [22, 10, 10, 10, 10, 38],
 "Tabella 3. Casi di costo del nucleare. Costo fisso annuo in €/kW all'anno. I valori di Barakah, Saeul, Flamanville e Mochovce sono per kW lordo e quindi sottostimati di circa il 4-7%. Fonte: docs/results_v8.md, sezione 3, e docs/v8_facts.md, sezioni 4 e 10 [@repo].", align='lrrrrl', fs=7.8)
h2("Piccoli reattori modulari")
# F3; T (SMR src: proxy O&M)
p("Per i piccoli reattori il riferimento è il progetto BWRX-300 di Darlington, in Canada [@power]. Il costo della prima unità, 17.200 €/kW, è il caso PI; il costo medio del programma di quattro unità, 11.700 €/kW, è il caso OB. Il cantiere dura 5 anni per unità. I costi di esercizio sono quelli del nucleare grande: è un'ipotesi, perché non abbiamo trovato un valore specifico. Il costo fisso annuo al 5% è 1.264 €/kW all'anno (PI) e 934 (OB); al 7% il caso OB vale 1.231.")
h2("Gli errori della versione precedente")
# A A1, A2, A3, A6, A7, A8, A9; H #77; README (v7 row); F10 (18,0)
p("La versione 7 usava per Dukovany 8.540 €/kW, 7 anni di cantiere, 80 anni di vita, 32 €/MWh di esercizio e una disponibilità del 92%: un costo fisso di 670 €/kW all'anno. La revisione sui documenti ufficiali ha trovato questi errori.")
b([
 "<b>Combustibile e potenza.</b> Il costo era stato ridotto di 382 €/kW togliendo il combustibile dal prezzo del contratto, ma il combustibile è un contratto separato. Il prezzo era poi diviso per la potenza lorda: la potenza vendibile è 976 MW per unità, non 1.055, e il solo contratto di costruzione vale 8.446 €/kW netto.",
 "<b>Costi del proprietario.</b> Erano stimati con una percentuale presa da una banca dati statunitense (12,57%). Ora si usa il dato pubblico ceco, 85 miliardi di corone.",
 "<b>Confronto con il dato ufficiale.</b> 8.540 €/kW per 2,11 GW fanno 18,0 miliardi di euro, sotto il minimo ufficiale di 20 miliardi. Il modello finanziario ceco ha 9 anni di cantiere e 60 di esercizio, non 7 e 80, e costi di esercizio di 35-45 €/MWh, non 32.",
 "<b>Altri casi.</b> Vogtle era a 15.540 €/kW perché gli oneri finanziari erano contati due volte: il valore corretto è 13.400. Barakah era a 4.670 €/kW: con la rivalutazione corretta del contratto del 2009 e i costi del proprietario vale 5.500, che resta un minimo. Il caso chiamato Saeul è in realtà un bilancio di previsione di Shin Hanul. Il testo diceva anche che la Commissione aveva approvato l'aiuto: l'indagine è aperta.",
])

# =============================================================================================================
# 5
# =============================================================================================================
h1("5. Risultati")
h2("Il risultato centrale")
p("La Tabella 4 riporta l'ottimo libero nei quattro casi: il modello sceglie la potenza nucleare insieme a tutto il resto. Il risparmio è la differenza tra il costo del sistema senza nucleare e quello del sistema con nucleare.")
_c = RES['1|'][1:]
tab([["Caso", "Tasso", "Nucleare (GW)", "di cui piccoli reattori (GW)", "Quota della domanda (%)", "Costo con nucleare (€/MWh)", "Costo senza nucleare (€/MWh)", "Risparmio (€/MWh)", "Risparmio (miliardi di € l'anno)"]] +
    [[r[0], r[1], it(r[2]), it(r[3]), it(r[4]), it(r[5]), it(r[6]), it(r[7]), it(r[8])] for r in _c],
    [7, 8, 11, 13, 11, 12, 12, 12, 14],
 "Tabella 4. Risultati centrali, ottimo libero, passo di 3 ore, anni meteorologici 2016-2019. PI: costi di primo impianto per le tecnologie senza impianti commerciali. OB: costi obiettivo. Costi in euro 2025 per MWh di domanda non coperta dall'idroelettrico esistente (356,6 TWh). La quota del nucleare è la sua produzione divisa per la domanda e conta anche l'energia nucleare esportata. Fonte: docs/results_v8.md, sezione 1.", align='llrrrrrrr')
# R1
p("Nel caso OB al 7% i reattori sono tutti piccoli reattori modulari: al costo obiettivo costano 1.231 €/kW all'anno, poco meno dei reattori grandi (1.239). Costano di più da costruire (11.700 contro 10.200 €/kW), ma il cantiere di 5 anni invece di 9 fa pagare meno interessi durante la costruzione, e con il capitale al 7% questo risparmio supera la differenza di costo; al 5% no (934 contro 911). I 5 anni sono il programma del costruttore per la prima unità di Darlington, non un tempo osservato: con 7 anni il vantaggio sparirebbe. Senza piccoli reattori lo stesso caso dà 11,0 GW di reattori grandi, con un costo del sistema di 131,43 €/MWh contro 131,16.")

h2("La curva del valore")
p("La Figura 1 è il risultato principale. Per ogni blocco di 4 GW di potenza nucleare dà il valore del blocco: il costo fisso annuo, in €/kW all'anno, al quale il sistema è indifferente tra averlo e non averlo. La curva scende: ogni blocco in più vale meno del precedente. Le linee orizzontali sono il costo fisso annuo del nucleare nei diversi casi di costo. La lettura è semplice: conviene costruire finché la curva sta sopra la linea del costo.")
fig('fig_value_it.png', "Figura 1. Valore di ogni blocco di 4 GW di potenza nucleare, in €/kW all'anno, con capitale al 5% (a sinistra) e al 7% (a destra). Passo di 3 ore, anni 2016-2019. Blu: caso PI. Arancione continuo: caso OB senza piccoli reattori. Arancione punteggiato: caso OB con i piccoli reattori disponibili. Le linee orizzontali sono il costo fisso annuo del nucleare in quattro casi di costo: contratto di Dukovany, massimo dell'intervallo ufficiale, Vogtle e Barakah. Gli altri casi sono nella Tabella 3. Elaborazione propria, dati in docs/results_v8.md, sezione 2, e nell'Appendice A.")
# R2
p("Nel caso PI al 5% (linea blu, grafico di sinistra) i primi 4 GW valgono 1.318 €/kW all'anno, i blocchi successivi 1.220, 1.149, 1.074, 973 e 921. Il blocco da 24 a 28 GW vale 868, meno del costo centrale di 911: la curva incrocia il costo intorno a 24 GW, e l'ottimo libero è 23,2 GW. Il blocco da 36 a 40 GW vale 462 €/kW all'anno e quello da 40 a 48 GW 209. Al 7% (grafico di destra) il costo centrale sale a 1.239 €/kW all'anno: il blocco da 12 a 16 GW vale 1.286, quello da 16 a 20 GW vale 1.162, e l'ottimo libero è 15,6 GW.")
# R2 (OB no SMR)
p("Nel caso OB senza piccoli reattori (linea arancione continua) le alternative costano meno e il nucleare vale meno: 1.145 €/kW all'anno i primi 4 GW, poi 1.087, 1.058 e 965. Il blocco da 16 a 20 GW vale 877, sotto il costo centrale di 911: l'ottimo libero è 15,7 GW. Questa è la curva che misura il valore del nucleare nel caso OB.")
# F5; R2 (OB with SMR)
p("La linea punteggiata è una curva diversa: in ascissa c'è la potenza dei reattori grandi, e il modello può aggiungere piccoli reattori al costo obiettivo. Tra 4 e 16 GW ogni blocco di reattori grandi sostituisce piccoli reattori e vale quanto costano loro: 934, 934 e 927 €/kW all'anno al 5%. Il punto a 0 GW di questa curva è il sistema con soli piccoli reattori (14,4 GW al 5%, 11,1 GW al 7%), che non dipende dal costo dei reattori grandi; anche il primo blocco vale quindi quanto i piccoli reattori che sostituisce (934 al 5%, 1.231 al 7%). Da 16 GW in su al 5%, e da 12 GW in su al 7%, le due curve OB coincidono.")
h2("I primi 4 GW")
# F5
p("I primi 4 GW sono quelli che valgono di più. Nel caso PI al 5% valgono 1.318 €/kW all'anno, più del costo di una centrale costruita come a Vogtle (1.147). Nel caso OB senza piccoli reattori valgono 1.145: due euro sotto il costo di Vogtle, cioè alla pari. Al 7% valgono 1.582 (PI) e 1.360 (OB senza piccoli reattori), contro un costo centrale di 1.239 e un costo di Vogtle di 1.603.")
h2("I casi di costo sulla curva")
p("La Tabella 5 legge ogni caso di costo sulle due curve al 5%. La potenza ottima è letta sulla griglia di 4 GW: per questo il caso centrale dà 24 e 16 GW invece di 23,2 e 15,7. La fascia è l'insieme delle potenze che costano entro l'1% del minimo.")
_ob = {r[0]: r for r in RES['3|OB 5%, no SMR'][1:]}
def _row5(name, key):
    a, o = _cc[key], _ob[key]
    return [name, it(a[3]), a[4] + ' (' + band(a[7]) + ')', it(a[6]), o[4] + ' (' + band(o[7]) + ')', it(o[6])]
tab([
 ["Caso di costo", "Costo fisso al 5% (€/kW all'anno)", "PI: potenza ottima e fascia (GW)", "PI: risparmio (€/MWh)", "OB: potenza ottima e fascia (GW)", "OB: risparmio (€/MWh)"],
 _row5("Dukovany, contratto (caso centrale)", "Dukovany contract, central"),
 _row5("Dukovany in 7 anni", "Dukovany, 7 years"),
 _row5("Mediana dei cantieri occidentali recenti", "Risk median"),
 _row5("Punto medio dell'intervallo ufficiale", "Dukovany, midpoint of EC bracket"),
 _row5("Massimo dell'intervallo ufficiale", "Dukovany, top of EC bracket"),
 _row5("Vogtle", "Vogtle"),
 _row5("Barakah", "Barakah"),
 _row5("Saeul (bilancio di Shin Hanul)", "Saeul budget"),
 ["Contratto, nucleare finanziato al 6% e il resto al 5%", "1.064", "16 (8-20)", "5,65", "8 (4-12)", "1,16"],
 ["Contratto, nucleare finanziato al 7% e il resto al 5%", "1.235", "4 (0-12)", "0,93", "0 (0-4)", "0,00"],
], [32, 14, 14, 13, 14, 13],
 "Tabella 5. Casi di costo letti sulle curve del valore al 5%, passo di 3 ore. OB: curva senza piccoli reattori. Potenza ottima sulla griglia di 4 GW; tra parentesi la fascia delle potenze entro l'1% del costo minimo. Risparmio rispetto al sistema senza nucleare. Fonte: docs/results_v8.md, sezione 3. Le ultime due righe leggono sulle curve al 5% il costo del contratto con il solo nucleare finanziato al 6% o al 7% (docs/v8_facts.md, sezione 14). Le stesse letture al 7% e sulla curva OB con piccoli reattori sono nell'Appendice B.", align='lrrrrr')
# R3
p("Con un cantiere di 7 anni l'ottimo resta a 24 GW nel caso PI e sale a 20 GW nel caso OB. Con i costi della mediana dei cantieri occidentali recenti scende a 16 GW (PI) e 12 GW (OB). Al punto medio dell'intervallo ufficiale è ancora 16 GW (PI, risparmio 8,95 €/MWh) e 12 GW (OB, risparmio 3,57 €/MWh); con capitale al 7% è 12 GW (PI, fascia 8-16) e 4 GW (OB senza piccoli reattori, fascia 0-8). Al massimo dell'intervallo ufficiale scende a 12 GW (PI) e 8 GW (OB); nel caso OB il risparmio è 0,88 €/MWh e anche zero GW sta nella fascia dell'1%. Al costo di Vogtle il caso PI dà ancora 12 GW con un risparmio di 2,76 €/MWh, il caso OB non costruisce reattori grandi (con i piccoli reattori disponibili ne costruisce circa 14,4 GW). Ai costi di Barakah e del bilancio di Shin Hanul l'ottimo è 36-40 GW; il primo valore è un minimo e il secondo un bilancio di previsione (Tabella 3).")

h2("L'ottimo è piatto")
# R2 costs; nostro calcolo: 114,436 x 1,01 = 115,58; 107,532 x 1,01 = 108,61
p("La Figura 2 mostra il costo del sistema al variare della potenza nucleare, al costo centrale e con capitale al 5%. Nel caso PI il costo è 115,25 €/MWh a 16 GW, 114,55 a 20 GW, 114,44 a 24 GW e 114,91 a 28 GW. Tutte queste potenze stanno entro l'1% dal minimo, cioè sotto 115,58 €/MWh (nostro calcolo). A 12 GW il costo è 117,07 e a 32 GW 116,66: fuori dalla fascia. Nel caso OB senza piccoli reattori la fascia è 12-20 GW, con il minimo a 16 GW (107,53 €/MWh).")
fig('fig_cost_it.png', "Figura 2. Costo del sistema in funzione della potenza nucleare, al costo centrale del nucleare e con capitale al 5%. Passo di 3 ore, anni 2016-2019. Costo in euro 2025 per MWh di domanda non coperta dall'idroelettrico esistente. Le fasce colorate indicano i costi entro l'1% dal minimo di ciascun caso. Elaborazione propria, dati in docs/results_v8.md, sezione 2, e nell'Appendice A.", wfrac=0.62)
# F5 flat optimum
p("Le fasce entro l'1% sono: 16-28 GW nel caso PI al 5%, 12-20 GW nel caso PI al 7%, 12-20 GW nel caso OB al 5% e 4-16 GW nel caso OB al 7%. Sulla curva con i piccoli reattori disponibili, dove la potenza conta solo i reattori grandi, le fasce sono 0-20 GW al 5% e 0-12 GW al 7%.")
p("Questo ha tre conseguenze per le decisioni.")
# nostro calcolo: 115,245 - 114,436 = 0,81; 109,024 - 107,532 = 1,49
b([
 "<b>Il numero esatto non è la decisione.</b> Dentro la fascia il costo cambia di meno dell'1%. La scelta della potenza può seguire criteri che il modello non vede: siti, capacità industriale, finanziamento, consenso.",
 "<b>Si può partire dalla parte comune.</b> I primi 15 GW circa stanno nella fascia, o al suo bordo, nel caso PI e nel caso OB. Crescere oltre conviene solo se idrogeno, aria compressa e solare termodinamico restano cari: si può decidere quando quei costi saranno noti.",
 "<b>Il costo dell'errore si può misurare.</b> Avere 16 GW in un mondo PI, dove l'ottimo sulla griglia è 24, costa 0,81 €/MWh in più del minimo. Avere 24 GW in un mondo OB, dove l'ottimo è 16, costa 1,49 €/MWh in più (nostro calcolo sulle curve dell'Appendice A).",
])
p("L'ottimo piatto spiega gli spostamenti di pochi GW da una versione all'altra, non tutta l'oscillazione del valore di testa (sezione 7).")

h2("I sistemi con e senza nucleare")
p("La Tabella 6 descrive i quattro sistemi con capitale al 5%: con e senza nucleare, nei casi PI e OB.")
# R5; A B (Terna-Snam 2040: 114-137 PV, 29-39 onshore)
p("Senza nucleare il sistema PI ha bisogno di 193 GW di fotovoltaico invece di 76, di 59,6 GW di eolico a terra invece di 33,4, di 281 GWh di batterie invece di 129 e di 14,8 TWh di stoccaggio di idrogeno invece di 2,1. I 59,6 GW di eolico sono tutti i blocchi tranne il peggiore (10 GW a 1.200 ore; i disponibili sono 69,6 GW), e tutti i blocchi di fotovoltaico a terra e agrivoltaico sono al loro tetto, insieme a due dei tre blocchi su tetti industriali. Per confronto, gli scenari di Terna e Snam al 2040 hanno 114-137 GW di fotovoltaico e 29-39 GW di eolico a terra [@dds]. Scambia con l'estero 27,7 TWh l'anno per direzione invece di 17,7.")
p("Nel caso OB il solare termodinamico arriva al tetto di 10 GW con e senza nucleare, e l'aria compressa prende il posto di quasi tutte le batterie nel sistema con nucleare. Il tetto di 10 GW è un'ipotesi nostra, non un dato.")
# R5 cost components
p("La composizione del costo aiuta a capire il risparmio. Nel sistema PI con nucleare il nucleare pesa per 65,43 €/MWh su 114,42, il fotovoltaico per 16,97, l'eolico a terra per 11,13, le batterie per 7,77 e l'idrogeno per 4,98. Nel sistema PI senza nucleare il fotovoltaico pesa per 56,19 €/MWh, l'eolico a terra per 23,83, le batterie per 17,00 e l'idrogeno per 11,22 (docs/results_v8.md, sezione 5).")
_s = {r[0]: r for r in RES['5|'][1:]}
_ord = ['PI with nuclear', 'PI without', 'OB with nuclear', 'OB without']
def _srow(name, j, f=lambda x: it(x)):
    return [name] + [f(_s[k][j]) for k in _ord]
_twh = lambda x: it('%.1f' % (float(x) / 1000.0))          # GWh -> TWh, una cifra decimale
_pct = lambda x: (it('%.1f' % (float(x) * 100)) if x else '')
tab([
 ["Grandezza", "PI con nucleare", "PI senza nucleare", "OB con nucleare", "OB senza nucleare"],
 _srow("Fotovoltaico (GW)", 1),
 _srow("Eolico a terra (GW)", 2),
 _srow("Eolico in mare (GW)", 3),
 _srow("Nucleare (GW)", 4),
 _srow("Solare termodinamico (GW)", 5),
 _srow("Batterie (GWh)", 6),
 _srow("Stoccaggio di idrogeno (TWh)", 7, _twh),
 _srow("Aria compressa (GWh)", 8),
 _srow("Interconnessione (GW)", 9),
 _srow("Energia scambiata, per direzione (TWh l'anno)", 10),
 _srow("Fattore di carico del nucleare (%)", 11, _pct),
], [36, 16, 16, 16, 16],
 "Tabella 6. I quattro sistemi centrali, capitale al 5%, passo di 3 ore. Fonte: docs/results_v8.md, sezione 5. Lo stoccaggio di idrogeno è convertito da GWh a TWh (nostro calcolo).", align='lrrrr')

# =============================================================================================================
# 6
# =============================================================================================================
h1("6. La tenuta del risultato")
p("La Tabella 7 lascia libero l'ottimo e cambia un'ipotesi alla volta, con due eccezioni: le righe sulla regola degli scambi della versione 7 e sui dati del nucleare della versione 7 cambiano più ipotesi insieme e sono indicate come insiemi. Tutte le varianti sono a passo di 3 ore e con capitale al 5%, quindi si confrontano direttamente con la prima riga.")
_VN = {
 'Central': "Caso centrale",
 'Exports earn nothing': "Le esportazioni non rendono nulla",
 'Exports earn the import price (115.94)': "Le esportazioni rendono il prezzo di importazione",
 'Net imports allowed up to 10% of demand': "Importazioni nette ammesse fino al 10% della domanda",
 'Net exports allowed': "Esportazioni nette ammesse",
 'Critical weeks chosen by low PV+wind (v7)': "Settimane critiche scelte per poco sole e vento",
 'v7 trade rule (bundle): 38% foreign capacity credit and availability in critical weeks, weeks chosen by low PV+wind, no exports, no annual balance, import price x1.17 in those weeks': "Insieme di cinque cambi: regola sugli scambi della versione 7",
 'Batteries at the MACSE award price': "Batterie al prezzo dell'asta MACSE",
 'Eight weather years (2016-2019 + 1994, 1998, 2014, 2015)': "Otto anni meteorologici, con i quattro peggiori",
 'Nuclear built in 7 years': "Nucleare costruito in 7 anni",
 'Nuclear at the top of the official bracket (12,700 EUR/kW)': "Nucleare al massimo dell'intervallo ufficiale",
 'Nuclear at the v7 inputs (bundle: 8,540 EUR/kW, 7 y, 80-year life, O&M 32, availability 92%; fixN 670)': "Insieme di cinque cambi: dati del nucleare della versione 7",
}
_v = RES['4|'][1:]
assert all(r[0] in _VN for r in _v), [r[0] for r in _v if r[0] not in _VN]
# F5 reading
p("Con il pareggio annuo e senza capacità estera nelle settimane critiche il nucleare ottimo sta tra 14,0 e 27,1 GW nel caso PI e tra 14,0 e 18,3 GW nel caso OB, in tutte le varianti tranne una: con i dati del nucleare della versione 7 è 33,6 GW (PI) e 28,4 GW (OB). Due precisazioni. Nel caso OB al massimo dell'intervallo ufficiale i 14,4 GW sono piccoli reattori; con i soli reattori grandi l'ottimo è 8 GW e ogni potenza tra 0 e 12 GW costa entro l'1% del minimo. In quella variante il caso OB ha più nucleare del caso PI (14,4 contro 14,0 GW) proprio perché mette anche i piccoli reattori al costo obiettivo. Con importazioni nette fino al 10% della domanda il sistema non è più autosufficiente e il nucleare è 23,4 GW (PI) e 12,6 GW (OB).")
h2("La regola sugli scambi e il prezzo dell'autosufficienza")
# F5 (bundle, decomposition, price of self-sufficiency), R4
p("Tra le regole del sistema quella sugli scambi con l'estero è quella che sposta di più il risultato. Il costo del nucleare lo sposta ancora di più: i casi di costo vanno da 0 a 40 GW. Con la regola della versione 7 il nucleare si dimezza: 11,9 GW invece di 23,2 (PI) e 7,2 invece di 15,7 (OB). Quella regola però è cinque cambi insieme: il 38% della capacità estera contato come sicuro e disponibile nelle settimane critiche, le settimane scelte per poco sole e vento, il prezzo di importazione moltiplicato per 1,17 in quelle settimane, nessuna esportazione e nessun pareggio annuo. I singoli cambi di cui abbiamo il risultato spostano meno: con importazioni nette fino al 10% della domanda il nucleare è 23,4 GW (PI) e 12,6 GW (OB); con le settimane critiche scelte per poco sole e vento è 18,2 e 14,5 GW. Il solo credito del 38% (centrali estere disponibili e contate come sicure nelle settimane critiche, con il pareggio annuo mantenuto) porta il nucleare a 17,9 GW (PI) e 14,1 GW (OB). È il singolo cambio che pesa di più nel caso PI, circa metà del calo, ma nel caso OB vale solo 1,6 GW. Nessun cambio da solo spiega il dimezzamento: viene dall'insieme, con le centrali estere disponibili nelle settimane critiche e senza pareggio annuo, così che le importazioni diventano una fonte sicura per tutto l'anno (52-71 TWh).")
tab([["Variante", "PI: nucleare (GW)", "PI: risparmio (€/MWh)", "OB: nucleare (GW)", "OB: risparmio (€/MWh)"]] +
    [[_VN[r[0]], it(r[1]), it(r[2]), it(r[5]), it(r[6])] for r in _v],
    [52, 12, 12, 12, 12],
 "Tabella 7. Varianti, capitale al 5%, ottimo libero, passo di 3 ore. Ogni riga cambia una sola ipotesi (le batterie MACSE cambiano prodotto, quindi prezzo e durata insieme), tranne le due righe indicate come insiemi: la regola sugli scambi della versione 7 (i cinque cambi sono elencati nel testo) e i dati del nucleare della versione 7 (8.540 €/kW, 7 anni di cantiere, 80 anni di vita, esercizio 32 €/MWh, disponibilità 92%; costo fisso 670 €/kW all'anno). Nella variante al massimo dell'intervallo ufficiale i 14,4 GW del caso OB sono piccoli reattori al costo obiettivo; con i soli reattori grandi l'ottimo è 8 GW (Tabella 5). Fonte: docs/results_v8.md, sezione 4.", align='lrrrr')
p("Con la regola della versione 7 l'Italia importa 52,0 TWh l'anno nel sistema PI con nucleare, 57,7 in quello senza, 56,0 nel sistema OB con nucleare e 70,7 in quello senza, e non esporta nulla. Nel 2025 ha importato 55,2 TWh e ne ha esportati 7,4 [@gme]. La regola della versione 7 è quindi circa la dipendenza di oggi, e il caso centrale di questo documento è la scelta di chiuderla. La Tabella 8 dà il prezzo di questa scelta.")
_k7 = 'v7 trade rule (bundle): 38% foreign capacity credit and availability in critical weeks, weeks chosen by low PV+wind, no exports, no annual balance, import price x1.17 in those weeks'
_vv = {r[0]: r for r in _v}
# differenze e miliardi: docs/v8_facts.md, sezione 5 (calcolate sui valori non arrotondati); importazioni: stessa sezione
tab([
 ["Sistema", "Costo con la regola di questa versione (€/MWh)", "Costo con la regola della versione 7 (€/MWh)", "Differenza (€/MWh)", "Differenza (miliardi di € l'anno)", "Importazioni con la regola della versione 7 (TWh l'anno)"],
 ["PI con nucleare", it(_vv['Central'][3]), it(_vv[_k7][3]), "4,44", "1,6", "52,0"],
 ["PI senza nucleare", it(_vv['Central'][4]), it(_vv[_k7][4]), "11,82", "4,2", "57,7"],
 ["OB con nucleare", it(_vv['Central'][7]), it(_vv[_k7][7]), "4,15", "1,5", "56,0"],
 ["OB senza nucleare", it(_vv['Central'][8]), it(_vv[_k7][8]), "8,87", "3,2", "70,7"],
], [20, 17, 17, 16, 14, 18],
 "Tabella 8. Prezzo dell'autosufficienza: costo del sistema con la regola sugli scambi di questa versione e con quella della versione 7, capitale al 5%, passo di 3 ore. La differenza è il prezzo dell'autosufficienza. Nei sistemi con nucleare la potenza è l'ottimo libero di ciascuna regola. Fonte: docs/results_v8.md, sezione 4, e docs/v8_facts.md, sezione 5.", align='lrrrrr')
p("Il prezzo è più alto senza nucleare che con il nucleare: 11,82 contro 4,44 €/MWh nel caso PI, 8,87 contro 4,15 nel caso OB. Il motivo è che il sistema senza nucleare si appoggia di più sulle centrali dei vicini, che in inverno sono in buona parte nucleari (sezione 2). Quanta capacità avranno libera i vicini in quelle settimane non si può sapere né garantire, ed è proprio per questo che il caso centrale non ci conta: un piano nazionale non può reggersi sulla speranza che altri paesi abbiano energia in più e la vendano nelle settimane in cui serve a tutti. Le varianti con importazioni dicono solo quanto si risparmierebbe contandoci: con il 38% della capacità estera e il pareggio annuo il nucleare ottimo è 17,9 GW (PI) e 14,1 GW (OB).")
p("Anche il modo di scegliere le settimane critiche conta. La versione 7 prendeva le settimane con meno sole e vento, che spesso non sono quelle di maggiore scarsità: le due scelte hanno in comune solo 4 settimane su 12, e una delle settimane della versione 7 cadeva in agosto.")
# R4, R5; F5 (0,31 and 1,85); F10 (10% holds in PI, not in OB)
p("Il prezzo dell'energia esportata sposta il risultato nei due sensi. Se le esportazioni non rendono nulla il nucleare sale a 25,4 GW (PI) e 18,3 GW (OB); se rendono quanto costa importare scende a 18,0 e 14,1 GW. Il motivo è che il sistema senza nucleare esporta di più e guadagna di più da un prezzo di esportazione alto. Ammettere importazioni nette fino al 10% della domanda quasi non cambia il caso PI (da 23,2 a 23,4 GW) ma cambia il caso OB (da 15,7 a 12,6 GW, con il risparmio che scende da 6,86 a 4,09 €/MWh): che l'energia annua importata conti poco vale nel caso PI e non nel caso OB. Nel caso PI l'energia importata serve soprattutto al sistema senza nucleare: gli fa risparmiare 1,85 €/MWh (da 127,77 a 125,92), contro 0,31 €/MWh per il sistema con nucleare (da 114,42 a 114,11).")
h2("Costo del capitale e costo di costruzione")
# R1, R4; A A12
p("Passando dal 5% al 7% il costo fisso del nucleare sale da 911 a 1.239 €/kW all'anno e l'ottimo scende da 23,2 a 15,6 GW (PI) e da 15,7 a 11,1 GW (OB). Anche le alternative costano di più: il sistema PI senza nucleare passa da 127,77 a 149,58 €/MWh. Il risparmio resta positivo in tutti e quattro i casi (Tabella 4).")
p("Diverso è il caso in cui solo il nucleare paga un capitale più caro. Letto sulle curve al 5%, con il nucleare al 7% (1.235 €/kW all'anno, con l'onere di rete al tasso del sistema) l'ottimo è 4 GW nel caso PI (0-12 GW entro l'1%, risparmio 0,93 €/MWh) e 0 nel caso OB senza piccoli reattori (0-4 GW); anche i piccoli reattori al 7% (1.226 €/kW all'anno con la stessa regola per l'onere di rete) non entrerebbero. Con il nucleare al 6% (1.064 €/kW all'anno) l'ottimo è 16 GW (PI, 8-20 GW, risparmio 5,65 €/MWh) e 8 GW (OB senza piccoli reattori, 4-12 GW, risparmio 1,16 €/MWh). La raccomandazione richiede quindi che il nucleare sia finanziato a un tasso vicino a quello delle alternative. Per questo contano strumenti come il prestito statale e il contratto per differenza notificati per Dukovany, come FER-X li dà alle rinnovabili.")
p("Sul costo di costruzione le varianti confermano la lettura della curva. Con cantieri di 7 anni il nucleare sale a 26,7 GW (PI) e 18,2 GW (OB). Al massimo dell'intervallo ufficiale scende a 14,0 GW nel caso PI; nel caso OB i 14,4 GW sono piccoli reattori, e con i soli reattori grandi restano 8 GW.")
h2("Batterie al prezzo d'asta")
p("Se le batterie costassero quanto il premio dell'asta MACSE, circa 95 €/kWh per sistemi da circa 6,6 ore, contro i nostri 168,6 per sistemi da 4 ore (non lo stesso prodotto), il nucleare scenderebbe a 18,1 GW (PI) e 14,0 GW (OB): la raccomandazione di circa 15 GW non cambia. Il motivo è che le batterie spostano energia di qualche ora, dal giorno alla sera, e quel problema è già risolto a costi bassi. Quello che il nucleare sostituisce è l'energia sicura nelle settimane invernali con poco sole e poco vento, che senza nucleare viene dall'idrogeno: è lì il collo di bottiglia, non nelle batterie.")
h2("Anni meteorologici")
p("Il caso centrale usa quattro anni, dal 2016 al 2019. Con otto anni, aggiungendo i quattro peggiori della banca dati (1994, 1998, 2014, 2015), il nucleare sale a 27,1 GW nel caso PI e resta circa uguale nel caso OB (15,5 GW contro 15,7); il risparmio sale a 17,49 e 7,97 €/MWh. Per i quattro anni aggiunti il modello ripete il carico del 2016-2019 con il tempo del 1994, 1998, 2014 e 2015: lì carico e tempo non sono dello stesso anno. Anni più difficili aumentano il valore del nucleare quando le alternative sono care.")
h2("Passo temporale")
# F5 time step; nostro calcolo: 23,2 - 21,7 = 1,5; 15,7 - 13,7 = 2,0
p("Lo stesso modello a passo di 6 ore dà 21,7 GW (PI) e 13,7 GW (OB) al 5%. A 3 ore i valori sono 1,6 GW più alti nel caso PI (23,22 contro 21,66) e 1,9 GW nel caso OB (15,65 contro 13,73). I dati orari non sono stati ricostruiti. I risultati a 3 ore possono quindi sottostimare ancora un po' il nucleare: la direzione è nota dal passaggio da 12 a 6 a 3 ore, la dimensione no.")

# =============================================================================================================
# 7
# =============================================================================================================
h1("7. I cambi del risultato da una versione all'altra")
p("Questo studio ha avuto otto versioni in meno di quattro settimane e il valore di testa è passato dal 74% al 29% e poi al 44% della domanda. Il lettore deve poter giudicare quanto fidarsi del valore di oggi. La Tabella 9 dà la traiettoria, con la causa principale di ogni cambio.")
# F6; H section 1 (rows 3, 4, 5-6, 7, 8, 13, 14)
tab([
 ["Versione", "Data (2026)", "Cambio principale", "Nucleare ottimo"],
 ["v1, primo documento", "19 ottobre", "Primo modello di sistema: passo di 3 ore, anni 2016-2019 ottimizzati uno alla volta, nucleare a 7.600 €/kW", "34 GW, 74%"],
 ["v2", "20 ottobre", "Rinnovabili al costo reale sull'intera vita, non al prezzo nominale d'asta", "20 GW, 33%"],
 ["v3 e v4", "24-25 ottobre", "Quattro anni ottimizzati insieme con un solo parco", "23 GW, 36%"],
 ["v5", "7 novembre", "Limite di suolo per il fotovoltaico", "24,8 GW, 45%"],
 ["v6", "7 novembre", "Domanda 2040 di 400 TWh, nessuna importazione", "38,5 GW, 59%"],
 ["v7", "9 novembre", "Importazioni con capacità estera contata come sicura, tutte le tecnologie, costi del proprietario nel nucleare", "16,0 GW, 28,9% (PI)"],
 ["v7 con autosufficienza", "10-11 novembre", "Importazioni non superiori alle esportazioni, nessun aiuto estero nelle settimane critiche", "23,0 GW, 44,7% (PI)"],
 ["v8, questo documento", "15 novembre", "Una regola di costo per tutte le fonti, contratto di Dukovany più costi del proprietario, codice corretto", "23,2 GW, 44,5% (PI); 15,7 GW, 30,5% (OB)"],
], [17, 13, 50, 20],
 "Tabella 9. Traiettoria del valore di testa. Fino alla v5 la domanda era quella del 2024 (312 TWh nella v5), dalla v6 è 400 TWh: le versioni differiscono per passo, domanda e regole: la tabella è la storia del risultato, non un confronto tra risultati omogenei. Fonte: docs/audit/audit_history.md, sezione 1, e docs/v8_facts.md, sezione 6.", fs=7.8)
h2("Le correzioni della versione 8")
# F3 (changes against v7), F6, F10, R4
p("Il valore della versione 8 è quasi uguale a quello della versione precedente (23,2 contro 23,0 GW nel caso PI) per una coincidenza. Tra la versione 7 con autosufficienza e la versione 8 sono cambiati: il costo del nucleare, i costi di fotovoltaico, eolico e batterie, il prezzo delle esportazioni (da 0 a 61,07 €/MWh), il criterio per le settimane critiche (da poco sole e vento al carico residuo), la disponibilità del nucleare (dal 92% al 90%) e due errori di codice (la soglia di rete calcolata sul parco totale, il costo dell'eolico e della rete che ora segue il tasso). Le due correzioni più grandi sono andate in direzioni opposte.")
b([
 "<b>Il nucleare costa di più.</b> Con il contratto di Dukovany, i costi del proprietario e i dati del modello finanziario ceco il costo fisso annuo passa da 670 a 911 €/kW all'anno, il 36% in più.",
 "<b>Rinnovabili e batterie costano di più.</b> Con il costo pieno al posto dei prezzi d'asta il fotovoltaico a terra passa da 58 a 89 €/kWp all'anno (54% in più), le batterie da 11.466 a 21.547 €/MWh all'anno (88% in più), l'eolico a terra da circa 150 a 159 €/kW all'anno.",
])
p("Due varianti della Tabella 7 danno la misura di questi cambi, ciascuna come insieme di più ipotesi. Con i dati del nucleare della versione 7 e tutto il resto della versione 8 il modello darebbe 33,6 GW (PI) e 28,4 GW (OB). Con i costi della versione 8 e la regola sugli scambi della versione 7 darebbe 11,9 GW (PI) e 7,2 GW (OB).")
h2("L'ottimo piatto e gli spostamenti di pochi GW")
# F6; F10; A D8
p("Nel caso PI al 5% tutte le potenze tra 16 e 28 GW costano entro l'1% del minimo: una piccola variazione di un costo sposta l'ottimo di alcuni GW mentre il costo del sistema quasi non cambia. Era così anche nella versione 7, dove a passo di 6 ore la fascia andava da circa 13 a 28 GW. L'ottimo piatto spiega però gli spostamenti di pochi GW, non tutta l'oscillazione dal 74% al 29%: nel caso PI 36 GW costano il 4,3% in più dell'ottimo. Le oscillazioni grandi sono venute da regole, costi e domanda cambiati (Tabella 9). Per questo la versione 8 non presenta un solo numero ma la curva del valore, le fasce e le condizioni.")
h2("Il registro degli errori")
# H section 2 header and table (counted row by row: 15, 7, 6, 7, 26, 33, 4; fixed 80, declared 12, open 6); H section 3 patterns
p("Il progetto tiene un registro di tutti gli errori trovati dal primo documento a oggi: 98 voci, ciascuna con la versione, che cosa era sbagliato, chi l'ha trovato, la correzione e l'effetto sul risultato. All'11 novembre 80 voci erano corrette, 12 dichiarate come limiti e 6 ancora aperte.")
tab([
 ["Categoria", "Voci", "Esempio"],
 ["Affermazioni e formulazioni", "33", "Conclusioni più forti dei risultati, o in contrasto con le tabelle dello stesso documento"],
 ["Metodo", "26", "Rinnovabili al prezzo nominale d'asta contro nucleare sull'intera vita; importazioni senza esportazioni"],
 ["Dati di costo", "15", "Costi del proprietario assenti dal costo di Dukovany; combustibile tolto dal prezzo"],
 ["Dati", "7", "Domanda del 2024 per un sistema del 2040; profili di sole e vento riscalati"],
 ["Citazioni", "7", "Fonte che non contiene il numero citato"],
 ["Codice del modello", "6", "Disponibilità estera applicata alla riserva e non al funzionamento"],
 ["Costruzione dei documenti", "4", "Testo compilato con i numeri di una regola superata"],
 ["Totale", "98", ""],
], [26, 8, 66],
 "Tabella 10. Registro degli errori per categoria, come contato nel registro stesso. Fonte: docs/audit/audit_history.md, sezione 2 [@repo].", align='lrl')
p("Gli errori che hanno spostato di più il risultato, detti in chiaro, sono questi.")
# H entries 4, 24, 31, 39, 52, 61, 89, 77; A A1, A3, A7, B1, B9, D1, D2; H #86
b([
 "<b>Confronto sbagliato in partenza.</b> Il primo calcolo confrontava un nucleare da solo, al 90% di utilizzo, con rinnovabili penalizzate dalla stagione. Il sistema misto non era mai stato calcolato.",
 "<b>Rinnovabili a prezzi nominali.</b> I prezzi d'asta a 20 anni erano confrontati con il nucleare sull'intera vita. La correzione ha portato il risultato dal 74% del primo documento al 33%.",
 "<b>Un anno alla volta.</b> Ottimizzare ogni anno meteorologico da solo faceva sembrare poco costoso il sistema senza nucleare.",
 "<b>Fotovoltaico ed eolico senza limiti.</b> Il modello poteva costruirne quantità illimitate al prezzo d'asta.",
 "<b>Domanda del 2024.</b> Il sistema era confrontato con piani al 2040-2050 usando 312 TWh invece di 400.",
 "<b>Importazioni.</b> Prima azzerate senza un numero che lo giustificasse, poi ammesse senza esportazioni e con il 38% della capacità estera contato come sicuro.",
 "<b>Costo di Dukovany.</b> Prima senza i costi del proprietario, poi con il combustibile tolto dal prezzo e con la potenza lorda al posto di quella netta (sezione 4).",
 "<b>Prezzi d'asta usati come costi</b> per fotovoltaico, eolico e batterie (sezione 3).",
 "<b>Due errori nel codice</b>, corretti nella versione 8. La soglia oltre la quale la rete costa di più contava solo gli impianti nuovi e non l'intero parco. Nelle esecuzioni al 7% il costo dell'eolico e della rete non seguiva il tasso. Entrambi penalizzavano il nucleare.",
 "<b>Troppa sicurezza.</b> Ogni valore di testa è stato presentato con più fiducia di quanta ne meritasse. Un giorno prima che il risultato passasse da 16 a 23 GW il testo diceva che non si sarebbe più mosso di molto.",
])
# H section 3: F 23, D 21, B 13, A 10
p("Per tipo, gli errori più frequenti sono le affermazioni più forti dei risultati (23 voci), le semplificazioni a senso unico, in cui una tecnologia riceve un costo, un limite o un'opzione che l'altra non ha (21), i confronti tra grandezze non omogenee (13) e i numeri senza una fonte o una derivazione tracciabile (10). La revisione dell'11 novembre 2026, fatta da verifiche indipendenti su costi del nucleare, altri costi, dati e codice, ha trovato errori in entrambe le direzioni.")
p("Dopo la revisione dell'11 novembre ci sono state altre due revisioni indipendenti, il 14 e il 15 novembre, con controlli ripetuti di correttezza e coerenza; le loro correzioni sono in questo documento. Il registro completo, la revisione dell'11 novembre e l'elenco delle fonti di costo sono nel repository del progetto [@repo], nella cartella docs/audit/: audit_history.md, audit_v8_findings.md e v8_symmetric_costs.md.")

# =============================================================================================================
# 8
# =============================================================================================================
h1("8. Limiti")
p("I limiti sono elencati qui con la direzione dell'effetto sul nucleare, quando è nota: prima le semplificazioni del modello che rendono il risultato prudente per il nucleare, poi i limiti che lo favoriscono, poi quelli che favoriscono il sistema senza nucleare, infine quelli di direzione non nota. Il costo di costruzione del nucleare non è un limite: segue la stessa regola delle altre fonti (sezione 4) e gli altri costi possibili sono letti sulle curve come casi.")
# F5, F7, F10, F12; H section 4; S7 (83%, 86,4%)
p("<b>Semplificazioni che rendono il risultato prudente per il nucleare.</b>")
b([
 "<b>Passo di 3 ore.</b> I dati orari non sono stati ricostruiti. Passando da 6 a 3 ore il nucleare sale di 1,6 GW (PI) e 1,9 GW (OB); a passo orario può salire ancora, di quanto non è noto.",
 "<b>Quattro anni meteorologici.</b> Con otto anni, compresi i quattro peggiori, il caso PI sale a 27,1 GW; il caso OB resta circa uguale (15,5 GW contro 15,7).",
 "<b>Un solo nodo e idroelettrico uguale ogni anno.</b> La rete interna non limita gli spostamenti di energia e mancano gli anni secchi: entrambe le cose favoriscono il sistema con più fotovoltaico.",
])
p("<b>Limiti che favoriscono il nucleare.</b>")
b([
 "<b>Tetti al fotovoltaico.</b> I tetti al fotovoltaico a terra e all'agrivoltaico sono una scelta nostra, e nel sistema PI senza nucleare tutti questi blocchi sono al tetto.",
 "<b>Flessibilità della domanda.</b> È limitata alla ricarica intelligente del 25% delle auto elettriche e al carico interrompibile.",
 "<b>Guasti di modo comune.</b> Il modello non ha fermate contemporanee di più reattori per la stessa causa.",
 "<b>Forma della disponibilità del nucleare.</b> La disponibilità è del 95% in inverno e in estate e dell'85% in primavera e in autunno, con una media del 90%; le settimane critiche cadono per due terzi nei mesi al 95%.",
 "<b>Fattore di carico del nucleare.</b> L'87,5-89,1% risulta dall'ottimizzazione con una disponibilità media del 90% e senza limiti di rampa. Può essere ottimistico rispetto a parchi che modulano molto (Francia 2024: 67% [@france]); il parco mondiale ha avuto l'83% nel 2024 e la mediana riportata dall'IAEA è l'86,4% [@wna, @iaea].",
])
p("<b>Limiti che favoriscono il sistema senza nucleare.</b>")
b([
 "<b>Rete di distribuzione.</b> Il rinforzo della rete di distribuzione non è contato. Serve soprattutto al fotovoltaico sui tetti e diffuso, che è di più nel sistema senza nucleare.",
 "<b>Stoccaggio di idrogeno ed elettrolizzatori.</b> Lo stoccaggio costa 3,76 €/kg, nella parte bassa dell'intervallo 2,06-14,95 €/kg dello studio da cui viene, che è uno studio a tavolino. Nel caso OB gli elettrolizzatori sono al costo obiettivo.",
 "<b>Paesi vicini non simulati.</b> Il prezzo di esportazione è una media annua. Favorisce il sistema che esporta di più, cioè quello senza nucleare.",
 "<b>Eolico esistente.</b> È tenuto al solo costo di esercizio anche se nel 2040 sarà oltre la sua vita tecnica.",
 "<b>Previsione perfetta.</b> Il modello conosce in anticipo il tempo di tutti gli anni meteorologici.",
])
p("<b>Limiti di direzione non nota.</b>")
b([
 "<b>Costo di rete.</b> È un'ipotesi degli autori, non un dato di Terna, e copre solo la trasmissione (il rinforzo della distribuzione, elencato a parte, non è contato). Ogni nuovo kW di fotovoltaico e di eolico a terra paga circa 240 €/kW (13 €/MWh per il fotovoltaico e 8 €/MWh per l'eolico, su 40 anni); i nuovi kW oltre 137 GW di eolico e fotovoltaico in totale pagano un secondo onere di circa 236 €/kW. L'eolico in mare non paga l'onere per MWh ma conta per la soglia e paga il secondo onere; il nucleare paga 2 €/MWh. Nel sistema PI senza nucleare la media su tutto il nuovo fotovoltaico ed eolico è circa 363 €/kW. Il Piano di sviluppo di Terna, oltre 23 miliardi di euro per 65 GW di rinnovabili in più al 2030 [@ternapds], implica in media circa 350 €/kW. Il confronto non dice in che direzione sbagli il nostro valore. Una verifica con circa 340 €/kW su ogni nuovo kW e il secondo onere oltre 108 GW dà 26,7 GW (PI) e 19,1 GW (OB), a passo di 3 ore.",
 "<b>Costi di oggi per tutte le fonti.</b> Nessuna tecnologia ha riduzioni di costo al 2040, nemmeno il nucleare, salvo i costi obiettivo del caso OB. Le proiezioni per fotovoltaico, batterie e nucleare costruito in serie scendono tutte, ma nessuna è un costo osservato, e lo studio non ne usa nessuna: la scelta si fa oggi, ai prezzi di oggi per tutte le fonti (sezione 3).",
 "<b>Crediti di capacità e tecnologie minori.</b> Sono ipotesi i crediti di capacità (batterie alla potenza per 4/6,6, idroelettrico a 15 GW pieni), i tempi di cantiere di diverse tecnologie minori e il tetto di 10 GW al solare termodinamico.",
 "<b>Sistema a regime.</b> Non ci sono limiti al ritmo di costruzione né un percorso di transizione: lo studio dice quanto nucleare conviene avere, non in quanti anni si può costruire.",
 "<b>Parti non riportate.</b> L'analisi dei costi mese per mese e il confronto con altri studi, presenti nella versione 7, non sono stati verificati di nuovo e sono fuori da questa versione.",
])

# =============================================================================================================
# 9
# =============================================================================================================
h1("9. Conclusione e raccomandazione")
p("Con una sola regola di costo per tutte le fonti, il nucleare al costo del contratto di Dukovany più i costi del proprietario e un sistema che non si appoggia agli altri paesi, il sistema elettrico italiano di minor costo per il 2040 contiene nucleare in tutti i casi centrali: 23,2 GW se le alternative restano ai costi dei primi impianti, 15,7 GW se raggiungono i costi obiettivo, 15,6 e 11,1 GW con capitale al 7%. Il risparmio va da 13,35 €/MWh (PI al 5%) a 2,63 €/MWh (OB al 7%).")
p("Il risultato non è un numero ma una fascia. Nel caso PI al 5% ogni potenza tra 16 e 28 GW costa entro l'1% del minimo; nel caso OB tra 12 e 20 GW. Il costo del nucleare sposta il risultato più di tutto: i casi di costo vanno da 0 a 40 GW. Tra le regole del sistema quella che lo sposta di più è la regola sugli scambi con l'estero: chiudere la dipendenza di oggi dalle importazioni costa 4,44 €/MWh con nucleare e 11,82 senza nel caso PI, e raddoppia circa il nucleare ottimo.")
# F8
p("La raccomandazione è una sola: pianificare un parco di circa 15 GW, circa 15 unità APR1000 da 976 MW netti e circa il 30% della domanda 2040, e tenere aperta l'opzione di crescere fino a circa 23 GW se idrogeno, aria compressa e solare termodinamico non raggiungono i costi obiettivo. Vale a tre condizioni: centrali costruite al costo del contratto di Dukovany più i costi del proprietario (circa 10.200 €/kW netti, 9 anni); nucleare finanziato a un tasso vicino a quello delle alternative (nel caso centrale il 5% reale per tutte le fonti; con il 7% per tutte i 15 GW reggono solo con le alternative ai costi dei primi impianti), con strumenti come il prestito statale e il contratto per differenza di Dukovany, come FER-X fa per le rinnovabili (con il nucleare al 7% e il resto al 5% l'ottimo è 4 GW nel caso PI e 0 nel caso OB, al 6% è 16 e 8 GW); la scelta di non contare su centrali estere nelle settimane critiche. Al punto medio dell'intervallo ufficiale di costo, con capitale al 5%, i 15 GW reggono ancora (16 GW nel caso PI, 12 nel caso OB).")
p("La raccomandazione cambia in tre casi: capitale al 7% per tutte le fonti insieme ad alternative al costo obiettivo (11 GW, come piccoli reattori); nucleare finanziato a un tasso più alto delle alternative (al 7% con il resto al 5%: 4 GW nel caso PI, 0 nel caso OB con soli reattori grandi); la scelta di restare alla dipendenza di oggi dalle importazioni (7-12 GW). I 15 GW non reggono quando due condizioni sfavorevoli si sommano: capitale al 7% con il nucleare al massimo dell'intervallo (PI 4 GW; OB, solo reattori grandi: 0) o al costo della mediana dei cantieri occidentali (PI 8 GW; OB, solo reattori grandi: 0), con 11,1 GW di piccoli reattori nel caso OB; alternative al costo obiettivo con il nucleare al costo di Vogtle (solo reattori grandi: 0; circa 14,4 GW di piccoli reattori) o al massimo dell'intervallo (8 GW di reattori grandi, risparmio 0,88 €/MWh). Il costo di costruzione e il tasso a cui si finanzia il nucleare sono quindi le prime cose da verificare.")
p("Dato che il valore di testa di questo studio è cambiato più volte, il lettore non deve fidarsi di un numero ma controllare la curva, i dati di ingresso e il registro degli errori, che sono pubblici [@repo].")

sources()

# =============================================================================================================
# APPENDICE
# =============================================================================================================
h1("Appendice A. Curve del valore")
p("Le tabelle riportano, per ogni potenza nucleare N, il costo del sistema e il valore del blocco che parte da N, cioè il costo fisso annuo al quale il sistema è indifferente tra avere quel blocco e non averlo. I blocchi sono di 4 GW; l'ultimo, dove è calcolato, va da 40 a 48 GW. Passo di 3 ore, anni 2016-2019. Le esecuzioni usano il costo centrale del nucleare (911 €/kW all'anno al 5%, 1.239 al 7%); il valore dei blocchi non dipende da quel costo. Fonte: docs/results_v8.md, sezione 2.")
def _curve(rate):
    P = {r[0]: r for r in RES['2|PI %s' % rate][1:]}
    O = {r[0]: r for r in RES['2|OB %s, no SMR' % rate][1:]}
    Sm = {r[0]: r for r in RES['2|OB %s, SMR available' % rate][1:]}
    rows = [["N (GW)", "PI: costo", "PI: valore del blocco", "OB senza: costo", "OB senza: valore del blocco", "OB con: costo", "OB con: valore del blocco"]]
    for n in P:
        rows.append([n] + sum(([it(X[n][1]), it(X[n][2])] if n in X else ['', ''] for X in (P, O, Sm)), []))
    return rows
_capA = " Costo del sistema in €/MWh; valore del blocco che parte da N in €/kW all'anno. OB senza: caso OB senza piccoli reattori, la curva del valore del nucleare nel caso OB. OB con: caso OB con piccoli reattori disponibili al costo obiettivo, dove N è la potenza dei reattori grandi."
tab(_curve('5%'), [10, 14, 16, 14, 16, 14, 16], "Tabella A1. Capitale al 5%." + _capA, align='rrrrrrr')
tab(_curve('7%'), [10, 14, 16, 14, 16, 14, 16], "Tabella A2. Capitale al 7%." + _capA + " Tra 4 e 16 GW al 5% e tra 4 e 12 GW al 7% il valore dei blocchi della curva OB con piccoli reattori è il costo dei piccoli reattori che i reattori grandi sostituiscono.", align='rrrrrrr')
h1("Appendice B. Casi di costo su ogni curva")
p("Per ogni caso di costo: potenza ottima sulla griglia di 4 GW, fascia delle potenze entro l'1% del costo minimo (tra parentesi) e risparmio rispetto al sistema senza nucleare. Il costo fisso annuo usa per tutti i casi l'esercizio, la vita e la disponibilità del caso centrale. Passo di 3 ore. Fonte: docs/results_v8.md, sezione 3.")
_CN = [
 ("Dukovany, contratto (caso centrale)", "Dukovany contract, central"), ("Dukovany in 7 anni", "Dukovany, 7 years"),
 ("Punto medio dell'intervallo ufficiale", "Dukovany, midpoint of EC bracket"),
 ("Massimo dell'intervallo ufficiale", "Dukovany, top of EC bracket"), ("Costruzione della versione 7 (8.540 €/kW, 7 anni)", "v7 central capex"),
 ("Barakah", "Barakah"), ("Saeul (bilancio di Shin Hanul)", "Saeul budget"),
 ("Mediana dei cantieri occidentali recenti", "Risk median"), ("Vogtle", "Vogtle"),
]
def _cases(rate):
    P = {r[0]: r for r in RES['3|PI %s' % rate][1:]}
    O = {r[0]: r for r in RES['3|OB %s, no SMR' % rate][1:]}
    Sm = {r[0]: r for r in RES['3|OB %s, SMR available' % rate][1:]}
    rows = [["Caso di costo", "Costo fisso (€/kW all'anno)", "PI: GW (fascia)", "PI: risparmio", "OB senza: GW (fascia)", "OB senza: risparmio", "OB con: GW (fascia)", "OB con: risparmio"]]
    for name, k in _CN:
        rows.append([name, it(P[k][3])] + sum(([X[k][4] + ' (' + band(X[k][7]) + ')', it(X[k][6])] for X in (P, O, Sm)), []))
    return rows
tab(_cases('5%'), [25, 11, 11, 10.5, 11, 10.5, 10.5, 10.5], "Tabella B1. Casi di costo sulle tre curve con capitale al 5%. Risparmio in €/MWh. OB senza e OB con: caso OB senza e con piccoli reattori.", align='lrrrrrrr', fs=7.6)
tab(_cases('7%'), [25, 11, 11, 10.5, 11, 10.5, 10.5, 10.5], "Tabella B2. Casi di costo sulle tre curve con capitale al 7%. Nella curva OB con piccoli reattori la potenza è quella dei reattori grandi: dove è 0 o 4 GW il sistema può avere comunque piccoli reattori (11,1 GW all'ottimo libero).", align='lrrrrrrr', fs=7.6)

h1("Appendice C. Dati di costo di ingresso")
p("I dati di costo delle tecnologie attive nel modello, dal file model/techs_v8.json del repository, che riporta per ciascuno la fonte o la dichiarazione che si tratta di un'ipotesi. Euro 2025. La regola di costo della sezione 3 (interessi durante il cantiere e rata annua al tasso reale del 5% o del 7%) si applica a tutte le righe tranne lo stoccaggio di idrogeno, l'accumulo da 100 ore e il carico interrompibile, che entrano con un prezzo annuo. Dove la fonte non è stata ricontrollata in questa revisione la voce corrispondente delle Fonti lo dice.")
# T (every row)
tab([
 ["Tecnologia", "Costo di costruzione", "Esercizio fisso", "Vita, cantiere (anni)", "Altri dati e fonte"],
 ["Nucleare e piccoli reattori", "", "", "", ""],
 ["Nucleare grande", "10.200 €/kW netto", "27,75 €/MWh al 90% di utilizzo; variabile 12,25 €/MWh", "60, 9", "Disponibilità media 90%; minimo tecnico 50%; rete 2 €/MWh [@ec, @ct24]"],
 ["Piccoli reattori modulari", "17.200 €/kW (PI); 11.700 €/kW (OB)", "come il nucleare grande (ipotesi)", "60, 5", "Darlington BWRX-300 [@power]"],
 ["Fotovoltaico", "", "", "", ""],
 ["A terra con inseguitore", "950 €/kWp", "20 €/kWp all'anno", "25, 1", "Degrado 0,5% l'anno; resa 1,12 volte il profilo a inclinazione fissa (in Puglia 1.596-1.712 kWh/kWp nei progetti depositati contro 1.462 kWh/kWp nel modello) [@polimi, @itsol, @mase]. Cantiere: ipotesi"],
 ["Agrivoltaico", "1.200 €/kWp", "20 €/kWp all'anno", "25, 1", "PoliMi 1.100-1.300 €/kWp; stesso moltiplicatore di resa dell'impianto a terra [@polimi]"],
 ["Tetti industriali", "950 €/kWp", "20 €/kWp all'anno", "25, 1", "Media di GSE (850 €/kWp) e PoliMi (1.000-1.100 €/kWp) [@gse, @polimi]"],
 ["Altri tetti", "1.250 €/kWp", "20 €/kWp all'anno", "25, 1", "Media di GSE (1.100 €/kWp) e IEA PVPS (1.400 €/kWp) [@gse, @pvps]"],
 ["Impianti esistenti", "nessuno", "20 €/kWp all'anno", "", "Resa scalata per 0,857: da 1.304 a 1.117 ore equivalenti l'anno, il parco osservato [@gsestat]"],
 ["Vita e degrado: confronto", "", "", "", "Vita 25 anni (PoliMi; GSE 20 anni, Fraunhofer 30 anni); degrado 0,5% l'anno (Fraunhofer ipotizza 0,25% l'anno; mediana osservata negli Stati Uniti 0,75% l'anno) [@fraunhofer, @nrelfleet]"],
 ["Eolico", "", "", "", ""],
 ["A terra", "1.600 €/kW", "40 €/kW all'anno", "25, 2", "PoliMi 1.500-1.700 €/kW; GSE 1.580-1.700 €/kW; blocchi da 2.400 a 1.200 ore equivalenti l'anno, 69,6 GW in tutto con l'esistente [@polimi, @gse]. Cantiere: ipotesi"],
 ["A terra, esistente", "nessuno", "40 €/kW all'anno", "", "13,6 GW a 1.600 ore l'anno (osservato nel 2025: 1.626 ore [@anev])"],
 ["In mare, fondazioni fisse", "3.400 €/kW", "80 €/kW all'anno", "25, 3", "PoliMi 3.300-3.500 €/kW [@polimi]. In Italia esiste un solo impianto a fondazioni fisse (Beleolico, Taranto, 30 MW, 2022)"],
 ["In mare, galleggiante", "4.750 €/kW", "100 €/kW all'anno", "25, 3", "PoliMi 4.500-5.000 €/kW [@polimi]. Nessun impianto galleggiante costruito in Italia"],
 ["Accumuli", "", "", "", ""],
 ["Batterie da 4 ore", "168,6 € per kWh utile", "4,486 €/kWh all'anno", "15, 2", "150,5 € per kWh utile per 1,12; rendimento 85%; credito di capacità pari alla potenza per 4/6,6 (ipotesi) [@arera332, @ternastor]"],
 ["Pompaggi esistenti", "nessuno", "nessuno", "", "7,3 GW, 53 GWh, rendimento 75% [@techsrc]"],
 ["Nuovi pompaggi", "291 € per kWh, 8 ore", "1,5% del costo di costruzione l'anno", "30, 5", "Fino a 35 GWh; rendimento 75% [@techsrc]"],
 ["Aria compressa", "239 € per kWh, 8 ore (PI); 105 € per kWh, 10 ore (OB)", "1,5% del costo di costruzione l'anno", "30, 3", "Rendimento 65%; vita di 30 anni: ipotesi degli autori [@techsrc]"],
 ["Accumulo da 100 ore", "compreso nel costo annuo", "1.486 €/MWh all'anno in tutto", "", "Obiettivo del produttore del 2021 (20 $ per kWh); rendimento 50%; escluso dal caso PI [@techsrc]"],
 ["Idrogeno", "", "", "", ""],
 ["Elettrolizzatore", "2.056 €/kW (PI); 450 €/kW (OB)", "3% del costo di costruzione l'anno (PI)", "20, 2", "Rendimento 63% (PI), 69% (OB) [@iea]"],
 ["Stoccaggio sotterraneo", "compreso nel costo annuo", "113 € per MWh di capacità utile all'anno (PI); 56 € (OB)", "", "Giacimento di gas esaurito, 3,76 €/kg, intervallo dello studio 2,06-14,95 €/kg [@hystories]"],
 ["Turbina a idrogeno", "1.079 €/kW (PI); 1.324 €/kW (OB)", "31 €/kW all'anno (PI); 44 €/kW all'anno (OB)", "35 (PI), 30 (OB); 4", "Rendimento 40% (PI), 55% (OB) [@techsrc]"],
 ["Altre fonti", "", "", "", ""],
 ["Solare termodinamico", "9.491 €/kW (PI); 3.287 €/kW (OB)", "67 €/kW all'anno", "25, 3", "2.900 MWh per MW l'anno; tetto di 10 GW: ipotesi degli autori [@techsrc]"],
 ["Geotermico", "3.589 €/kW e 5.675 €/kW; avanzato 6.257 €/kW (PI), 2.681 €/kW (OB)", "98 €/kW all'anno", "25, 3", "Nuovi blocchi di 0,183 GW, 0,8 GW e 0,5 GW; esistente 0,817 GW al solo esercizio [@techsrc]"],
 ["Bioenergie", "2.898 €/kW", "4% del costo di costruzione l'anno", "20, 2", "Limiti di energia: biogas 4,0 TWh l'anno, biomasse solide 2,5 TWh l'anno, rifiuti 2,2 TWh l'anno [@techsrc]"],
 ["Nuovo idroelettrico", "6.500 €/kW", "100 €/kW all'anno", "25, 3", "Fino a 0,24 GW [@gse]"],
 ["Idroelettrico esistente", "nessuno", "nessuno", "", "15 GW, 43,4 TWh l'anno, credito di capacità pieno (ipotesi)"],
 ["Domanda e scambi", "", "", "", ""],
 ["Carico interrompibile", "nessuno", "46 €/kW all'anno fino a 2,4 GW; 105 €/kW all'anno per altri 1,35 GW", "", "Al massimo 120 ore l'anno [@arera12, @arera564]"],
 ["Ricarica intelligente dei veicoli", "nessuno", "nessuno", "", "25% dei veicoli [@techsrc]; costo dell'infrastruttura non trovato e posto a zero: è un limite superiore del beneficio"],
 ["Interconnessioni", "esistenti 11,535 GW senza costo; nuove linee 1.120-1.900 €/kW", "1,5% del costo di costruzione l'anno", "40, 4", "Fino a 7,33 GW di nuove linee [@techsrc]; importazione a 115,94 €/MWh, esportazione a 61,07 €/MWh [@arera366, @gme]. Cantiere ed esercizio: ipotesi"],
 ["Rete di trasmissione", "circa 240 €/kW per ogni nuovo kW di fotovoltaico ed eolico a terra; circa 236 €/kW in più oltre 137 GW di eolico e fotovoltaico in totale", "13 €/MWh per il fotovoltaico, 8 €/MWh per l'eolico a terra, 2 €/MWh per il nucleare, nulla per l'eolico in mare", "40", "Ipotesi degli autori, non un dato di Terna (sezione 8)"],
], [16, 19, 18, 9, 38],
 "Tabella C1. Dati di costo di ingresso del modello. L'energia dalle onde è nel file dei dati ma è spenta in tutte le esecuzioni e non è elencata. Fonte: model/techs_v8.json e docs/audit/v8_symmetric_costs.md [@repo].", fs=7.2, keep=False)

# ---------------------------------------------------------------- numerazione delle fonti
_order = []
def _cite(m):
    keys = [k.strip().lstrip('@') for k in m.group(1).split(',')]
    for k in keys:
        if k not in SRC: raise KeyError(k)
        if k not in _order: _order.append(k)
    return '[' + ', '.join(str(n) for n in sorted(_order.index(k) + 1 for k in keys)) + ']'
_pat = re.compile(r'\[((?:@\w+)(?:,\s*@\w+)*)\]')
def _sub(x):
    if isinstance(x, str): return _pat.sub(_cite, x)
    if isinstance(x, list): return [_sub(y) for y in x]
    return x
C = [_sub(el) for el in C]
SOURCES = [(i + 1, SRC[k][0], SRC[k][1]) for i, k in enumerate(_order)]
_unused = [k for k in SRC if k not in _order]
if _unused: print('fonti non citate (escluse):', _unused)
