#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""论文成稿的空占位符与数字缺失扫描（提交前门禁）。

用法：
    python scan_placeholders.py FILE [FILE ...]

对每个文件逐行扫描「漏填数字 / 占位符」模式，输出 `file:line: 模式` 清单。
仅诊断、不修改文件。扫描 UTF-8 .md/.txt 和 .docx 的正文段落与顶层表格。
不校验数字正确性或其来源。退出码：0 = 未检出疑似项；1 = 检出疑似项；
2 = 至少一个输入无法扫描（即使其他输入检出疑似项）。

设计原则：宁少报、不误报。数学论文里「X：」后跟公式是常态，所以对「冒号/谓语
结尾」类模式会看下一行——下一行若是公式（$、\\(、\\[ 开头，或含 =/∑/∫/±），判定为
「公式在下一行」，不算漏填。真正要抓的是：动词后直接跟句读、参数名后缺值、显式占位符。
"""

import re
import sys
import os

# (正则, 说明) —— 只报高置信模式
PATTERNS = [
    # 比较级/结论动词后直接跟句读（「最高。」「最低，」）
    (r'(最高|最低|最大|最小|最优|最佳|约为|约等于|大致为|选取|选用|最终取)[。，；、）)】]', '结论词后直接跟句读（可能漏数值）'),
    # 谓语「为/是」后直接跟右括号或句读（「测试集为）」「聚类数为。」）
    (r'(测试集|验证集|训练集|R\s*[²2]|RMSE|MAE|MSE|AIC|BIC|p\s*值|准确率|精度|系数|参数)[为是][）)。，；]', '指标/名词后「为是」直接结束（漏数值）'),
    # 参数名后缺具体值（「聚类数时」「虽然时」「取 k=」）
    (r'(聚类数|折数|阶数|结点数|节点数|层数|隐藏层|学习率|惩罚参数|衰减时间|最大滞后)[^0-9\d=≈≈，。；]{0,3}时', '参数名后缺具体值（如「聚类数时」）'),
    (r'(虽然|当|若|而)\s*时', '条件从句缺参数（如「虽然时」）'),
    # 显式占位符
    (r'[□▢＿]{2,}|第\s*[□▢＿]|图\s*\d*[□▢＿]|表\s*\d*[□▢＿]|式\s*\(\s*[□▢＿]|\([□▢＿]+\)', '显式占位符（□/▢/＿）'),
]


def looks_like_formula(line):
    s = line.strip()
    if not s:
        return False
    if s.startswith(('$', '\\(', '\\[', '$$')):
        return True
    # 含数学标记且以运算符/等号为主
    return bool(re.search(r'[=≈±∑∫√\\]|\\[a-zA-Z]+', s))


def extract_docx(path):
    from docx import Document
    doc = Document(path)
    paras = [p.text for p in doc.paragraphs]
    table_lines = []
    for t in doc.tables:
        for row in t.rows:
            cells = [c.text.strip() for c in row.cells]
            table_lines.append(' | '.join(cells))
    return paras, table_lines


def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.docx':
        paras, tables = extract_docx(path)
        return paras + tables
    if ext not in ('.md', '.txt'):
        raise ValueError(f'不支持的文件格式：{ext}')
    with open(path, encoding='utf-8-sig') as f:
        return f.read().splitlines()


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    hits = 0
    failed = 0
    for path in argv:
        try:
            lines = extract_text(path)
            if not any(line.strip(' |\t') for line in lines):
                raise ValueError('没有可扫描的文本')
        except Exception as exc:
            print(f'  [检查未完成] {path}: {exc}', file=sys.stderr)
            failed += 1
            continue
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                continue
            # 表格空单元格（中间有空列）
            if stripped.startswith('|') and re.search(r'\|\s+\|', stripped):
                print(f'{path}:{i}: 表格空单元格: {stripped[:70]}')
                hits += 1
                continue
            # 冒号结尾的行：若下一行是公式，跳过
            if stripped.endswith(('：', ':', '为', '是')) and i < len(lines):
                nxt = lines[i].strip() if i < len(lines) else ''
                if looks_like_formula(nxt):
                    continue
            for pat, desc in PATTERNS:
                if re.search(pat, stripped):
                    print(f'{path}:{i}: [{desc}] {stripped[:80]}')
                    hits += 1
                    break
    print(f'\n已扫描文件共 {hits} 处疑似漏填；{failed} 个文件未完成扫描。')
    if failed:
        return 2
    return 0 if hits == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
