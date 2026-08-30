# -*- coding: utf-8 -*-
"""OMML formula + three-line table builders (extracted from battle-tested
build_final2.py, 2026 contest 1B final.docx pipeline).

latex2mathml -> MML2OMML.XSL (ships with MS Office) -> lxml XSLT -> oMath.
Smoke test:  python omml_lib.py
"""
import os
from lxml import etree
import latex2mathml.converter as conv

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(ns, t): return '{%s}%s' % (ns, t)

XSL_PATH = r'C:/Program Files/Microsoft Office/root/Office16/MML2OMML.XSL'
if not os.path.exists(XSL_PATH):  # fallback: search common Office roots
    for cand in (r'C:/Program Files (x86)/Microsoft Office/root/Office16/MML2OMML.XSL',):
        if os.path.exists(cand):
            XSL_PATH = cand
            break
XSLT = etree.XSLT(etree.parse(XSL_PATH))


def latex_to_omath(latex):
    """LaTeX string -> OMML <m:oMath> element, runs forced to Cambria Math."""
    mml = conv.convert(latex)
    om = XSLT(etree.fromstring(mml.encode())).getroot()
    for el in om.iter():
        for a in list(el.attrib):
            if a.startswith('{http://www.w3.org/2000/xmlns/}'):
                del el.attrib[a]
    for mr in om.iter(q(M, 'r')):
        w_rpr = mr.find(q(W, 'rPr'))
        if w_rpr is None:
            w_rpr = etree.Element(q(W, 'rPr'))
            m_t = mr.find(q(M, 't'))
            if m_t is not None:
                m_t.addprevious(w_rpr)
            else:
                mr.append(w_rpr)
        rf = w_rpr.find(q(W, 'rFonts'))
        if rf is None:
            rf = etree.SubElement(w_rpr, q(W, 'rFonts'))
        rf.set(q(W, 'ascii'), 'Cambria Math')
        rf.set(q(W, 'hAnsi'), 'Cambria Math')
    return om


def _noframe_borders(tblpr):
    tb = etree.SubElement(tblpr, q(W, 'tblBorders'))
    for b in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = etree.SubElement(tb, q(W, b))
        e.set(q(W, 'val'), 'none'); e.set(q(W, 'sz'), '0')
        e.set(q(W, 'space'), '0'); e.set(q(W, 'color'), 'auto')


def eq_table(omath, number, w_left=8469, w_right=818, style_id=None):
    """1-row 2-col borderless equation table:
    left cell oMathPara (formula), right cell bold full-width （N）, vAlign center.
    style_id is PER-DOCUMENT (this doc used '13', after Word resave '50') --
    resolve dynamically from the target doc, or pass None to omit."""
    tbl = etree.Element(q(W, 'tbl'))
    tblPr = etree.SubElement(tbl, q(W, 'tblPr'))
    if style_id:
        ts = etree.SubElement(tblPr, q(W, 'tblStyle')); ts.set(q(W, 'val'), style_id)
    tw = etree.SubElement(tblPr, q(W, 'tblW')); tw.set(q(W, 'w'), '0'); tw.set(q(W, 'type'), 'auto')
    _noframe_borders(tblPr)
    tl = etree.SubElement(tblPr, q(W, 'tblLook'))
    for k, v in (('val', '04A0'), ('firstRow', '1'), ('lastRow', '0'), ('firstColumn', '1'),
                 ('lastColumn', '0'), ('noHBand', '0'), ('noVBand', '1')):
        tl.set(q(W, k), v)
    grid = etree.SubElement(tbl, q(W, 'tblGrid'))
    for wd in (w_left, w_right):
        g = etree.SubElement(grid, q(W, 'gridCol')); g.set(q(W, 'w'), str(wd))
    tr = etree.SubElement(tbl, q(W, 'tr'))
    # left: formula cell
    tc1 = etree.SubElement(tr, q(W, 'tc'))
    tp1 = etree.SubElement(tc1, q(W, 'tcPr'))
    tw1 = etree.SubElement(tp1, q(W, 'tcW')); tw1.set(q(W, 'w'), str(w_left)); tw1.set(q(W, 'type'), 'dxa')
    p1 = etree.SubElement(tc1, q(W, 'p'))
    pp1 = etree.SubElement(p1, q(W, 'pPr'))
    sp1 = etree.SubElement(pp1, q(W, 'spacing')); sp1.set(q(W, 'before'), '48'); sp1.set(q(W, 'after'), '48')
    ind1 = etree.SubElement(pp1, q(W, 'ind')); ind1.set(q(W, 'firstLineChars'), '0'); ind1.set(q(W, 'firstLine'), '0')
    op = etree.SubElement(p1, q(M, 'oMathPara'))
    op.append(omath)
    # right: bold full-width number, vertically centered
    tc2 = etree.SubElement(tr, q(W, 'tc'))
    tp2 = etree.SubElement(tc2, q(W, 'tcPr'))
    tw2 = etree.SubElement(tp2, q(W, 'tcW')); tw2.set(q(W, 'w'), str(w_right)); tw2.set(q(W, 'type'), 'dxa')
    va2 = etree.SubElement(tp2, q(W, 'vAlign')); va2.set(q(W, 'val'), 'center')
    p2 = etree.SubElement(tc2, q(W, 'p'))
    pp2 = etree.SubElement(p2, q(W, 'pPr'))
    sp2 = etree.SubElement(pp2, q(W, 'spacing')); sp2.set(q(W, 'before'), '48'); sp2.set(q(W, 'after'), '48')
    ind2 = etree.SubElement(pp2, q(W, 'ind')); ind2.set(q(W, 'firstLineChars'), '0'); ind2.set(q(W, 'firstLine'), '0')
    rpr2 = etree.SubElement(pp2, q(W, 'rPr'))
    etree.SubElement(rpr2, q(W, 'b')); etree.SubElement(rpr2, q(W, 'bCs'))
    for ch in ('（', str(number), '）'):
        r = etree.SubElement(p2, q(W, 'r'))
        rpr = etree.SubElement(r, q(W, 'rPr'))
        etree.SubElement(rpr, q(W, 'b')); etree.SubElement(rpr, q(W, 'bCs'))
        t = etree.SubElement(r, q(W, 't')); t.text = ch
    return tbl


def _cell(tr, text):
    tc = etree.SubElement(tr, q(W, 'tc'))
    tp = etree.SubElement(tc, q(W, 'tcPr'))
    tw = etree.SubElement(tp, q(W, 'tcW')); tw.set(q(W, 'w'), '0'); tw.set(q(W, 'type'), 'auto')
    p = etree.SubElement(tc, q(W, 'p'))
    pp = etree.SubElement(p, q(W, 'pPr'))
    sp = etree.SubElement(pp, q(W, 'spacing')); sp.set(q(W, 'before'), '48'); sp.set(q(W, 'after'), '48')
    ind = etree.SubElement(pp, q(W, 'ind')); ind.set(q(W, 'firstLineChars'), '0'); ind.set(q(W, 'firstLine'), '0')
    jc = etree.SubElement(pp, q(W, 'jc')); jc.set(q(W, 'val'), 'center')
    r = etree.SubElement(p, q(W, 'r'))
    t = etree.SubElement(r, q(W, 't')); t.text = str(text)
    return tc


def three_line_table(headers, rows, col_widths, style_id=None):
    """Three-line (booktabs) table: top/bottom 1.5pt, header underline 0.75pt,
    no verticals, no header bold (Kevin's spec). Text size NOT set here --
    apply 五号 sz=21 afterwards via set_sz if the doc default differs."""
    tbl = etree.Element(q(W, 'tbl'))
    tblPr = etree.SubElement(tbl, q(W, 'tblPr'))
    if style_id:
        ts = etree.SubElement(tblPr, q(W, 'tblStyle')); ts.set(q(W, 'val'), style_id)
    tw = etree.SubElement(tblPr, q(W, 'tblW')); tw.set(q(W, 'w'), '0'); tw.set(q(W, 'type'), 'auto')
    tb = etree.SubElement(tblPr, q(W, 'tblBorders'))
    for b, sz in (('top', '12'), ('bottom', '12')):
        e = etree.SubElement(tb, q(W, b))
        e.set(q(W, 'val'), 'single'); e.set(q(W, 'sz'), sz)
        e.set(q(W, 'space'), '0'); e.set(q(W, 'color'), 'auto')
    for b in ('left', 'right', 'insideH', 'insideV'):
        e = etree.SubElement(tb, q(W, b))
        e.set(q(W, 'val'), 'none'); e.set(q(W, 'sz'), '0')
        e.set(q(W, 'space'), '0'); e.set(q(W, 'color'), 'auto')
    tl = etree.SubElement(tblPr, q(W, 'tblLook'))
    for k, v in (('val', '04A0'), ('firstRow', '1'), ('lastRow', '0'), ('firstColumn', '1'),
                 ('lastColumn', '0'), ('noHBand', '0'), ('noVBand', '1')):
        tl.set(q(W, k), v)
    grid = etree.SubElement(tbl, q(W, 'tblGrid'))
    for wd in col_widths:
        g = etree.SubElement(grid, q(W, 'gridCol')); g.set(q(W, 'w'), str(wd))
    trh = etree.SubElement(tbl, q(W, 'tr'))
    for h in headers:
        tc = _cell(trh, h)
        tp = tc.find(q(W, 'tcPr'))
        tcb = etree.SubElement(tp, q(W, 'tcBorders'))
        e = etree.SubElement(tcb, q(W, 'bottom'))
        e.set(q(W, 'val'), 'single'); e.set(q(W, 'sz'), '6')
        e.set(q(W, 'space'), '0'); e.set(q(W, 'color'), 'auto')
    for row in rows:
        trd = etree.SubElement(tbl, q(W, 'tr'))
        for c in row:
            _cell(trd, c)
    return tbl


def set_number(tbl, num):
    """Rewrite the （N） cell of an EXISTING equation table (renumbering)."""
    for tc in tbl.iter(q(W, 'tc')):
        joined = ''.join(t.text or '' for t in tc.iter(q(W, 't')))
        if '（' in joined and '）' in joined:
            p = tc.find(q(W, 'p'))
            rpr_ref = None
            for r in list(p.findall(q(W, 'r'))):
                if rpr_ref is None:
                    from copy import deepcopy
                    rpr_ref = deepcopy(r.find(q(W, 'rPr')))
                p.remove(r)
            from copy import deepcopy
            for ch in ('（', str(num), '）'):
                r = etree.SubElement(p, q(W, 'r'))
                if rpr_ref is not None:
                    r.append(deepcopy(rpr_ref))
                t = etree.SubElement(r, q(W, 't')); t.text = ch
            return True
    return False


# half-point font sizes: 小四=24 (12pt), 五号=21 (10.5pt), 小五=18 (9pt)
SZ = {'小四': '24', '五号': '21', '小五': '18', '四号': '28', '小三': '30'}


def set_sz(rpr, val='21'):
    """Set/replace w:sz + w:szCs on a run's rPr, respecting schema order."""
    sz = rpr.find(q(W, 'sz'))
    if sz is not None:
        sz.set(q(W, 'val'), val)
        szc = rpr.find(q(W, 'szCs'))
        if szc is not None:
            szc.set(q(W, 'val'), val)
        return
    AFTER = ('highlight', 'u', 'effect', 'bdr', 'shd', 'fitText', 'vertAlign', 'rtl', 'cs',
             'em', 'lang', 'eastAsianLayout', 'specVanish', 'oMath')
    szel = etree.Element(q(W, 'sz')); szel.set(q(W, 'val'), val)
    szcel = etree.Element(q(W, 'szCs')); szcel.set(q(W, 'val'), val)
    for ch in rpr:
        if etree.QName(ch).localname in AFTER:
            ch.addprevious(szel)
            ch.addprevious(szcel)
            return
    rpr.append(szel); rpr.append(szcel)


if __name__ == '__main__':
    # smoke test: build equation table + three-line table, verify XML structure
    body = etree.Element(q(W, 'body'))
    eq = eq_table(latex_to_omath(r'\bar{s}_j = \frac{1}{n}\sum_{t=1}^{n} s_j(X_{tj})'), 1)
    body.append(eq)
    body.append(three_line_table(['折数', '训练样本范围', '训练样本数'],
                                 [['1', '1~768', '768'], ['2', '1~1488', '1488']],
                                 [1000, 3000, 2000]))
    doc = etree.Element(q(W, 'document'), nsmap={'w': W, 'm': M})
    doc.append(body)
    xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    doc2 = etree.fromstring(xml)
    tbls = doc2.findall('.//' + q(W, 'tbl'))
    math_els = doc2.findall('.//' + q(M, 'oMath'))
    assert len(tbls) == 2 and len(math_els) == 1
    t0 = tbls[0]
    assert '（1）' in ''.join(t.text or '' for t in t0.iter(q(W, 't')))
    print('omml_lib smoke OK: 2 tables, 1 oMath, number （1） rendered')
