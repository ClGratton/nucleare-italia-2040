# -*- coding: utf-8 -*-
# Contenuto del white paper, modello v7. Ogni elemento: (tipo, ...)
# Tutti i numeri vengono da facts_v7.md, da v7res/reference_points.md o da calcoli aritmetici dichiarati nei commenti.
import re, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'repo'))
TITLE = "Il nucleare nel sistema elettrico italiano"
SUBTITLE = "Quanto nucleare conviene, in funzione del costo fisso annuo, con la domanda 2040"
DATE = "Novembre 2026"

C = []
def h1(t): C.append(('h1', t))
def h2(t): C.append(('h2', t))
def p(t): C.append(('p', t))
def b(items): C.append(('bullets', items))
def fig(path, cap): C.append(('fig', path, cap))
def tab(rows, widths, cap): C.append(('table', rows, widths, cap))
def box(title, text): C.append(('box', title, text))

import tables_v7 as T
import inputs_v7 as INP
def TB(name, *a):
    H, R = getattr(T, name)('it', *a)
    return [H] + R

