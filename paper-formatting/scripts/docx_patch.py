# -*- coding: utf-8 -*-
"""Run-level text replace inside a .docx (robust to the target string being
split across multiple runs, which is the norm after Word edits / rsid churn).

Usage:
  python docx_patch.py <file.docx> <old_text> <new_text> [--dry]

- only word/document.xml is modified; every other part is rewritten byte-identical
- replacement text lands in the FIRST overlapping run (its formatting wins)
- refuses to run while Word holds the file (~$ lock present)
- exits non-zero if old_text not found
Tested on final.docx 变由于量->变量间 fix (2026 contest 1B).
"""
import sys, os, zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)


def replace_in_para(p, old, new, cap=200):
    all_t = list(p.iter(q('t')))
    n = 0
    while n < cap:
        full = ''.join(t.text or '' for t in all_t)
        idx = full.find(old)
        if idx < 0:
            return n
        s, e = idx, idx + len(old)
        pos = 0
        first = True
        for t in all_t:
            if not t.text:
                continue
            rs, re_ = pos, pos + len(t.text)
            pos = re_
            if re_ <= s or rs >= e:
                continue
            a = max(s, rs) - rs
            b = min(e, re_) - rs
            if first:
                t.text = t.text[:a] + new + t.text[b:]
                first = False
            else:
                t.text = t.text[:a] + t.text[b:]
        n += 1
    return n


def main():
    argv = [a for a in sys.argv[1:] if a != '--dry']
    dry = '--dry' in sys.argv
    if len(argv) != 3:
        sys.exit(__doc__)
    path, old, new = argv
    lock = os.path.join(os.path.dirname(path) or '.', '~$' + os.path.basename(path))
    if os.path.exists(lock):
        print('LOCKED: %s exists -- Word has the file open. Close it first.' % lock)
        sys.exit(2)
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    total = 0
    for p in doc.iter(q('p')):
        full = ''.join(t.text or '' for t in p.iter(q('t')))
        if old in full:
            got = replace_in_para(p, old, new)
            total += got
            print('patched %d x in para: %s...' % (got, full[:40]))
    if total == 0:
        print('NOT FOUND: %r' % old)
        sys.exit(1)
    leftovers = sum(1 for p in doc.iter(q('p'))
                    if old in ''.join(t.text or '' for t in p.iter(q('t'))))
    assert leftovers == 0, 'old text still present after patch'
    if dry:
        print('DRY RUN ok, %d replacement(s), nothing written' % total)
        return
    data_new = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    out = path + '.tmp'
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zo:
        for name in z.namelist():
            zo.writestr(name, data_new if name == 'word/document.xml' else z.read(name))
    z.close()
    os.replace(out, path)
    from docx import Document
    d = Document(path)
    print('written: %s (%d paras, %d tables, python-docx opens OK)'
          % (path, len(d.paragraphs), len(d.tables)))


if __name__ == '__main__':
    main()
