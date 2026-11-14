# -*- coding: utf-8 -*-
# Costruisce white_paper_nucleare_italia_v8.pdf da content.py (reportlab).
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import content
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image,
                                Table, TableStyle, PageBreak, KeepTogether, ListFlowable, ListItem)
from reportlab.platypus.doctemplate import NextPageTemplate
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

FD = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('Serif', FD+'DejaVuSerif.ttf'))
pdfmetrics.registerFont(TTFont('Serif-B', FD+'DejaVuSerif-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Serif-I', FD+'DejaVuSerif-Italic.ttf'))
pdfmetrics.registerFont(TTFont('Serif-BI', FD+'DejaVuSerif-BoldItalic.ttf'))
pdfmetrics.registerFont(TTFont('Sans', FD+'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Sans-B', FD+'DejaVuSans-Bold.ttf'))
addMapping('Serif', 0, 0, 'Serif'); addMapping('Serif', 1, 0, 'Serif-B')
addMapping('Serif', 0, 1, 'Serif-I'); addMapping('Serif', 1, 1, 'Serif-BI')
addMapping('Sans', 0, 0, 'Sans'); addMapping('Sans', 1, 0, 'Sans-B')
addMapping('Sans', 0, 1, 'Sans'); addMapping('Sans', 1, 1, 'Sans-B')

INK = colors.HexColor('#1a1a19'); MUTED = colors.HexColor('#52514e')
ACCENT = colors.HexColor('#184f95'); RULE = colors.HexColor('#cfcec8'); BOXBG = colors.HexColor('#eef3fa')

body = ParagraphStyle('body', fontName='Serif', fontSize=9.2, leading=12.8, alignment=TA_JUSTIFY,
                      textColor=INK, spaceAfter=5.0)
bullet = ParagraphStyle('bullet', parent=body, spaceAfter=3)
h1s = ParagraphStyle('h1', fontName='Sans-B', fontSize=14, leading=18, textColor=ACCENT,
                     spaceBefore=12, spaceAfter=6, keepWithNext=1)
h2s = ParagraphStyle('h2', fontName='Sans-B', fontSize=10.5, leading=13.5, textColor=INK,
                     spaceBefore=7, spaceAfter=3.5, keepWithNext=1)
cap = ParagraphStyle('cap', fontName='Sans', fontSize=7.8, leading=10.2, textColor=MUTED,
                     spaceBefore=3, spaceAfter=9)
boxt = ParagraphStyle('boxt', fontName='Sans-B', fontSize=10, leading=13, textColor=ACCENT, spaceAfter=3)
boxp = ParagraphStyle('boxp', parent=body, fontSize=9.1, leading=12.7, spaceAfter=4.2)
src = ParagraphStyle('src', fontName='Sans', fontSize=7.3, leading=9.4, textColor=INK,
                     leftIndent=18, firstLineIndent=-18, spaceAfter=2.2, wordWrap='CJK')

W, H = A4
LM = RM = 2.1*cm; TM = 2.1*cm; BM = 1.8*cm
FW = W - LM - RM

def on_page(c, doc):
    c.saveState()
    if doc.page > 1:
        c.setFont('Sans', 7.5); c.setFillColor(MUTED)
        c.drawString(LM, H-1.35*cm, content.TITLE)
        c.drawRightString(W-RM, H-1.35*cm, content.DATE)
        c.setStrokeColor(RULE); c.setLineWidth(0.5); c.line(LM, H-1.5*cm, W-RM, H-1.5*cm)
        c.drawCentredString(W/2, 1.2*cm, str(doc.page))
    c.restoreState()

def cover(c, doc):
    c.saveState()
    c.setFillColor(ACCENT); c.rect(0, H-9.5*cm, W, 9.5*cm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont('Sans', 9); c.drawString(LM, H-2.4*cm, 'WHITE PAPER')
    c.setFont('Sans-B', 24)
    y = H-4.4*cm
    for line in content.COVER_TITLE:
        c.drawString(LM, y, line); y -= 1.0*cm
    c.setFont('Sans', 11)
    for line in content.COVER_SUB:
        y -= 0.1*cm; c.drawString(LM, y, line); y -= 0.55*cm
    c.setFont('Sans', 9); c.drawString(LM, H-8.6*cm, content.DATE)
    c.restoreState()

OUT = os.path.join(HERE, 'white_paper_nucleare_italia_v8.pdf')
doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
                      title=content.TITLE, author='', subject=content.SUBTITLE)
frame_cover = Frame(LM, BM, FW, H-TM-BM-8.2*cm, id='cover')
frame = Frame(LM, BM, FW, H-TM-BM, id='normal')
doc.addPageTemplates([PageTemplate('cover', [frame_cover], onPage=cover),
                      PageTemplate('normal', [frame], onPage=on_page)])
story = [NextPageTemplate('normal')]

def bullets(items):
    return ListFlowable([ListItem(Paragraph(t, bullet), leftIndent=12, value='•') for t in items],
                        bulletType='bullet', bulletFontName='Serif', bulletFontSize=8, leftIndent=12,
                        spaceBefore=0, spaceAfter=6)

AL = {'l': TA_LEFT, 'r': TA_RIGHT, 'c': TA_CENTER}
PAD = 3.5

def make_table(rows, widths, captxt, align, fs, keep=None):
    ncol = len(rows[0])
    align = (align or 'l' * ncol).ljust(ncol, 'l')
    cst = [ParagraphStyle('c%d' % i, fontName='Sans', fontSize=fs, leading=fs + 2.2, textColor=INK,
                          alignment=AL[a]) for i, a in enumerate(align)]
    hst = [ParagraphStyle('h%d' % i, fontName='Sans-B', fontSize=fs, leading=fs + 2.2, textColor=colors.white,
                          alignment=AL[a]) for i, a in enumerate(align)]
    secst = ParagraphStyle('sec', fontName='Sans-B', fontSize=fs, leading=fs + 2.2, textColor=INK)
    secrows = [i for i, r in enumerate(rows) if i > 0 and len(r) > 1 and r[0] and not any(r[1:])]
    data = [[Paragraph(x, hst[j]) for j, x in enumerate(rows[0])]]
    for i, r in enumerate(rows):
        if i == 0: continue
        if i in secrows:
            data.append([Paragraph(r[0], secst)] + [''] * (ncol - 1))
        else:
            data.append([Paragraph(x, cst[j]) for j, x in enumerate(r)])
    tot = sum(widths); cw = [FW * w / tot for w in widths]
    # controllo: nessuna parola più larga della colonna (altrimenti reportlab la spezza a metà)
    import re as _re
    for i, r in enumerate(rows):
        if i in secrows: continue
        for j, x in enumerate(r):
            font = 'Sans-B' if i == 0 else 'Sans'
            for wd in _re.sub(r'<[^>]+>', '', x).replace('&amp;', '&').split():
                wpt = pdfmetrics.stringWidth(wd, font, fs)
                if wpt > cw[j] - 2 * PAD - 0.5:
                    print('PAROLA TROPPO LARGA: tabella "%s", colonna %d, "%s" (%.0f > %.0f pt)' % (captxt[:12], j, wd, wpt, cw[j] - 2 * PAD))
    t = Table(data, colWidths=cw, hAlign='LEFT', repeatRows=1)
    ts = [('BACKGROUND', (0, 0), (-1, 0), ACCENT), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
          ('LINEBELOW', (0, 1), (-1, -1), 0.4, RULE), ('TOPPADDING', (0, 0), (-1, -1), 2.6),
          ('BOTTOMPADDING', (0, 0), (-1, -1), 2.6), ('LEFTPADDING', (0, 0), (-1, -1), PAD),
          ('RIGHTPADDING', (0, 0), (-1, -1), PAD)]
    for i in secrows:
        ts += [('SPAN', (0, i), (-1, i)), ('BACKGROUND', (0, i), (-1, i), BOXBG)]
        if i + 1 < len(rows): ts += [('NOSPLIT', (0, i), (-1, i + 1))]      # il titolo di gruppo resta con la riga che segue
    t.setStyle(TableStyle(ts))
    if keep if keep is not None else True:
        return [KeepTogether([t, Paragraph(captxt, cap)])]
    return [t, Paragraph(captxt, cap)]

for el in content.C:
    k = el[0]
    if k == 'h1':
        if el[1].startswith('Appendice A'):
            story.append(PageBreak())
        story.append(Paragraph(el[1], h1s))
    elif k == 'h2':
        story.append(Paragraph(el[1], h2s))
    elif k == 'p':
        story.append(Paragraph(el[1], body))
    elif k == 'bullets':
        story.append(bullets(el[1]))
    elif k == 'fig':
        img = Image(os.path.join(HERE, el[1]))
        ratio = img.imageHeight / img.imageWidth
        wfrac = el[3]
        img.drawWidth = FW * wfrac; img.drawHeight = FW * wfrac * ratio
        img.hAlign = 'CENTER'
        story.append(KeepTogether([Spacer(1, 4), img, Paragraph(el[2], cap)]))
    elif k == 'table':
        story.extend(make_table(*el[1:]))
    elif k == 'box':
        rows_b = [[Paragraph(el[1], boxt)]] + [[Paragraph(x, boxp)] for x in el[2]]
        bt = Table(rows_b, colWidths=[FW])          # una riga per capoverso: il riquadro può spezzarsi tra due pagine
        bt.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), BOXBG), ('LEFTPADDING', (0, 0), (-1, -1), 10),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 10), ('TOPPADDING', (0, 0), (-1, -1), 2),
                                ('TOPPADDING', (0, 0), (-1, 0), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                                ('BOTTOMPADDING', (0, -1), (-1, -1), 5), ('LINEBEFORE', (0, 0), (0, -1), 2.5, ACCENT)]))
        story.append(Spacer(1, 4)); story.append(bt); story.append(Spacer(1, 6))
    elif k == 'sources':
        story.append(Paragraph('Fonti', h1s))
        story.append(Paragraph(content.SOURCES_NOTE, body))
        for n, t, urls in content.SOURCES:
            links = ' ; '.join('<link href="%s" color="#184f95">%s</link>' % (u, u) for u in urls)
            story.append(Paragraph('[%d] %s%s' % (n, t, (' ' + links) if links else ''), src))

doc.build(story)
print('ok', OUT)
