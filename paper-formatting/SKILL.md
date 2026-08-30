---
name: paper-formatting
description: Use when formatting Kevin's paper docx, OMML, tables, swaps.
version: 1.0
author: Kevin + Hermes
license: MIT
metadata:
  hermes:
    tags: [docx, omml, paper-formatting, word]
    related_skills: ["productivity:docx", "localized-docx-section-edit"]
---

# Kevin 的论文排版规范与工具库

## When to Use

Kevin 的论文/建模竞赛 Word 稿需要排版操作时：公式图片转 OMML、公式/表格字号、三线表、run 级文本修复、跨文档章节替换。规范以 2026 模拟赛 1B final.docx 管线定型（图片公式→OMML 全量转换 283/283 逐元素验证通过）。
**总纪律：只机械复刻原稿格式，不创新、不主动改内容；用户点名的问题才修，且最小改动。**

## 0. 开工前（每次必做）

1. **查 Word 锁**：目标文件同目录若有 `~$文件名.docx`，Word 正开着它 → 写盘必 PermissionError。先请用户关 Word，或直接输出修改后的文本让用户手贴。
2. **确认基准文件**：以用户当前指定的版本为准（上次为 `final.docx` 用户重存版）；**now.docx 等源稿永不修改**。
3. 大改前先跑一遍结构摸底（段落/表格/样式 ID 清单），Word 重存会导致 rId、媒体、样式 ID 全部漂移（上次实测：公式表样式 13→50、图片 rId 全变），**绝不能拿旧探测结果直接动手**。

## 0.5 Kevin 论文全文格式规格（2026-08 从 final.docx 实测提取）

以下为 final.docx 的真实参数，同类新论文排版以此为基准模板；换一篇论文时先重跑结构摸底确认，不照抄数值。

**文档默认（docDefaults）**：西文 Times New Roman / 中文宋体，小四（sz=24 半点）。

**页面**：A4 竖版（11907×16840 twip），页边距四边均 1418 twip（≈2.5cm），页眉/页脚距边界 1134 twip（≈2cm）。

**标题（自动编号，样式挂 numId=1，suff=space 即编号后空格而非制表符）**
- H1（样式"1"）：黑体四号（sz=28，14pt）、加粗、居中、段前/后 50、中文序号"一、二、三…"（chineseCountingThousand）
- H2（样式"2"）：黑体 13pt（sz=26，介于小四与四号之间，无字号名）、加粗、左对齐、段前/后 40，编号 `%1.%2`（如"4.1"，H1 中文数字+H2 阿拉伯数字混合）
- H3（样式"3"）：黑体、加粗、左对齐、段前/后 30、字号继承正文（=小四 24），编号 `%1.%2.%3`
- 三级为限；标题文字内不手写编号（编号由 numPr 自动生成）

**正文（Normal 样式"a"）**：宋体/Times New Roman 小四 sz=24、两端对齐、段前/后 20、首行缩进 2 字符（firstLineChars=200）；列表段（List Paragraph）首行缩进改 420 twip 固定值。

**图注/表注（caption 样式 a3）**：黑体小四（sz 继承 24）、居中、编号"图 N"/"表 N"+一个空格（自动编号，suff=space）；表注在表上方、图注在图下方（文档实际排布）。

**图片**：嵌入式（inline drawing），独立段落；多数段落未设显式 jc（居中靠人工 Word 拖对齐——新插入图片时显式设 jc=center 更稳）。15 张图全 inline、无浮动 anchor。

**西文字体纪律**：正文西文/数字一律 Times New Roman（docDefaults 继承即可，勿显式设宋体）；公式 run 一律 Cambria Math；Word 重存后个别 run 可能被写成显式宋体 ascii——排版时发现显式宋体 ASCII run 顺手改为继承或 TNR，但不主动扫全文替换。

## 1. 公式规范

- **图片公式一律转原生 OMML**（可编辑），转换后删除原图片。
- **公式表**：1 行 2 列无边框表；左格 `oMathPara`（Cambria Math，12pt 继承默认）；右格编号**加粗、全角括号 （N）**，`vAlign=center`。
- **编号**：全文按文档顺序连续编号无缺号；行内符号、变量定义式按惯例不编号；重编号后正文“式（N）”引用必须同步。
- 公式表首格的注解文字（如 `j=1,2,3,4`）原样保留。
- 文本型变量正体：OMML run 的 `m:sty="p"`。

**LaTeX→OMML 管线（实测）**：`latex2mathml` → `MML2OMML.XSL`（`C:/Program Files/Microsoft Office/root/Office16/`，Office 自带）→ lxml XSLT → 插入 document.xml。注意 XSLT 输出需剥 xmlns 声明残留、run 强制 Cambria Math。
直接用 `scripts/omml_lib.py`：`latex_to_omath()` / `eq_table()` / `three_line_table()` / `set_number()` / `set_sz()`。

## 2. 表格与字号

- 三线表：顶/底线 1.5pt（sz=12）、表头下线 0.75pt（sz=6）、无竖线、**表头不加粗**。
- 字号（半点值）：表格文字五号 = sz 21；图注/表注小四 = sz 24；公式 12pt 继承不加显式覆盖。
- 图注/表注样式完全复刻原稿（含居中、加粗与否）。

## 3. 文本修改

- 替换目标串可能被 Word 拆进多个 run → 必须段落级拼串定位、run 级写入（首个重叠 run 承载新文本）。
- `scripts/docx_patch.py <file> <old> <new> [--dry]`：run 级安全替换，自动查 `~$` 锁、替换后验证旧串清零、其余 zip 条目逐字节复写。上次用于 `变由于量→变量间`。

## 4. 章节替换（跨文档）

- `scripts/docx_section_swap.py <target> <source> <heading_title> [--dry]`：按标题定界（标题样式/outlineLvl，同级截止），deepcopy 源章节元素插入目标文档。
- **已实测**：纯文本章节与 OMML 公式表完整存活；python-docx 可重开。
- **已实测的限制**：含**图片**的章节 rId 会断（未做媒体重映射）→ 图片章节需先手工处理或扩展脚本；样式 ID 跨文档不一致时格式静默降级 → 跟随 STYLE WARNING 核对。
- 插入后检查标题编号是否需顺延。

## 5. 交付与验收

- 交付方式：**直接输出结果**，不回头问要不要。
- 验收标准：逐元素 diff（上次 283/283 零意外差异的口径）——所有差异必须归入预期改动类，出现任何非预期差异即失败。
- 写盘后用 python-docx 重开一次确认无损坏。

## 工具脚本

- `scripts/omml_lib.py` — LaTeX→OMML、公式表、三线表构造器（冒烟测试通过）
- `scripts/docx_patch.py` — run 级文本替换（实战验证：final.docx 病句修复）
- `scripts/docx_section_swap.py` — 章节替换（合成文档端到端验证：文本+OMML 存活，图片不支持）

依赖：`pip install latex2mathml lxml python-docx`（机器已有）。
