# -*- coding: utf-8 -*-
"""Replace a heading-anchored section between two .docx files.

Section = from the paragraph whose outline level / style marks it as heading N
with matching title text, up to (not including) the next heading of level <= N
(or end of body). The source section is deep-copied into the target at the
same position, replacing the old section.

CAUTION on cross-file styles/numbering: the copy keeps SOURCE style ids.
If target doc lacks those ids, formatting degrades silently. This script
keeps each file's styles.xml untouched (mechanical copy, no style merge) --
check afterwards (audit_styles) whether the source uses styles the target
lacks, and reconcile manually if needed.

Usage:
  python docx_section_swap.py <target.docx> <source.docx> <heading_title> [--dry]

Tested with synthetic docs (2026-08): text chapters and OMML equation tables
survive the swap intact; python-docx reopens the result. media relationship
remap NOT handled -- sections containing IMAGES get broken rIds; for those,
copy images manually or extend the script first.
"""
import sys, os, zipfile
from copy import deepcopy
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)


def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def heading_level(p, max_level=4):
    """Return outline level 1..N if p is a heading, else 0."""
    ppr = p.find(q('pPr'))
    if ppr is None:
        return 0
    ol = ppr.find(q('outlineLvl'))
    if ol is not None and ol.get(q('val')).isdigit():
        return min(int(ol.get(q('val'))) + 1, max_level)
    ps = ppr.find(q('pStyle'))
    if ps is not None:
        sid = ps.get(q('val'), '')
        for i in range(1, max_level + 1):
            if sid in (str(i), 'Heading%d' % i, 'heading%d' % i, '%d' % i) \
               or ('Heading%d' % i) in sid or ('标题%d' % i) in sid:
                return i
    return 0


def find_section(body, title):
    """Return (start_idx, end_idx) of children list delimiting the section."""
    children = list(body)
    start = None
    for i, el in enumerate(children):
        if el.tag == q('p'):
            lvl = heading_level(el)
            if lvl >= 1 and title in para_text(el):
                start = i
                break
    if start is None:
        return None
    lvl = heading_level(children[start])
    end = len(children)
    for j in range(start + 1, len(children)):
        el = children[j]
        if el.tag == q('p'):
            l2 = heading_level(el)
            if 1 <= l2 <= lvl:
                end = j
                break
    return start, end


def main():
    argv = [a for a in sys.argv[1:] if a != '--dry']
    dry = '--dry' in sys.argv
    if len(argv) != 3:
        sys.exit(__doc__)
    tgt_path, src_path, title = argv
    zt = zipfile.ZipFile(tgt_path)
    ts = zipfile.ZipFile(src_path)
    tdoc = etree.fromstring(zt.read('word/document.xml'))
    sdoc = etree.fromstring(ts.read('word/document.xml'))
    tbody = tdoc.find(q('body'))
    sbody = sdoc.find(q('body'))
    sec = find_section(sbody, title)
    if sec is None:
        print('heading not found in SOURCE: %r' % title)
        sys.exit(1)
    s0, s1 = sec
    new_els = [deepcopy(el) for el in list(sbody)[s0:s1]]
    tsec = find_section(tbody, title)
    if tsec is None:
        print('heading not found in TARGET: %r -- nothing to replace' % title)
        sys.exit(1)
    t0, t1 = tsec
    # style audit: source styles used vs target styles defined
    tstyles = set()
    try:
        st = etree.fromstring(zt.read('word/styles.xml'))
        tstyles = {s.get(q('styleId')) for s in st.iter(q('style'))}
    except KeyError:
        pass
    used = set()
    for el in new_els:
        for ps in el.iter(q('pStyle')):
            used.add(ps.get(q('val')))
    missing = used - tstyles
    if missing:
        print('STYLE WARNING: source uses styles not in target: %s' % sorted(missing))
    # splice
    children = list(tbody)
    anchor = children[t1] if t1 < len(children) else None
    old = children[t0:t1]
    for el in old:
        tbody.remove(el)
    for el in new_els:
        if anchor is not None:
            anchor.addprevious(el)
        else:
            tbody.append(el)
    print('replaced section %r: %d -> %d elements' % (title, t1 - t0, len(new_els)))
    if dry:
        print('DRY RUN ok, nothing written')
        return
    data_new = etree.tostring(tdoc, xml_declaration=True, encoding='UTF-8', standalone=True)
    out = tgt_path + '.tmp'
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zo:
        for name in zt.namelist():
            zo.writestr(name, data_new if name == 'word/document.xml' else zt.read(name))
    zt.close(); ts.close()
    os.replace(out, tgt_path)
    from docx import Document
    d = Document(tgt_path)
    print('written: %s (%d paras, %d tables, python-docx opens OK)'
          % (tgt_path, len(d.paragraphs), len(d.tables)))


if __name__ == '__main__':
    main()
