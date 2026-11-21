"""Fail if the documents still carry input values replaced on 21 Nov 2026 or the wording about runs made before the corrections.

Run after the documents are updated with the results of the runs on the corrected inputs:
    python tools/check_stale_values.py
Every hit must be removed or explained before release. Exit code 1 if anything is found.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = [ROOT / 'docs/white_paper/content.py', *sorted((ROOT / 'docs/preprint').glob('*.tex')), ROOT / 'docs/v8_facts.md']

# value replaced -> pattern (English and Italian number formats)
STALE = {
    'nuclear capex 10,200 EUR/kW': r'10[.,]?\{?,?\}?200\b',
    'fixN 911 (5%)': r'\b911\b',
    'fixN 1,239 (7%)': r'\b1[.,]?\{?,?\}?239\b',
    'new foreign lines 7.33 GW': r'\b7[.,]33\b',
    'Korean budget 2,965 EUR/kW': r'\b2[.,]?\{?,?\}?965\b',
    'Korean fixN 426': r'\b426\b',
    'compressed storage 239 EUR/kWh': r'\b239\b',
    'compressed storage 105 EUR/kWh': r'\b105\s*(\\,)?\s*(EUR|€)/kWh',
    'interruptible 3.75 GW': r'\b3[.,]75\s*(\\,)?\s*GW',
    'CZK 85 bn owner costs': r'\b85\s*(\\,)?\s*(bn|miliardi)',
    'wording: runs before corrections': r'before some inputs were corrected|corrected after the runs|inputs of the runs|dati delle esecuzioni|corretti dopo le esecuzioni|valori delle esecuzioni',
}

def main():
    hits = 0
    for f in DOCS:
        if not f.exists():
            continue
        for i, line in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
            for what, pat in STALE.items():
                if re.search(pat, line):
                    hits += 1
                    print(f"{f.relative_to(ROOT)}:{i}: {what}: {line.strip()[:160]}")
    print(f"{hits} hit(s)")
    sys.exit(1 if hits else 0)

if __name__ == '__main__':
    main()
