# Math Modeling Skill

一次模拟赛里，同一小问的结果表冒出了四种行数。大家各自跑出了结果，到了交稿前才把数据版本统一起来。预测题还有个容易看走眼的地方：验证时每走一步都能拿到上一刻的真值，交付时却要从一个时点直接预测未来 12 小时。按前一种方式选出的模型，到了交付时未必还能领先。

这个 Skill 是我拿来处理这些麻烦的。它面向数学建模竞赛和建模项目，从选题、拆题一直跟到论文和答辩。手头只差一个验证、一张图或一节正文，也可以只做那一段。

## 做题时能帮上什么

| 做到哪儿了 | 可以让 Skill 做什么 |
| --- | --- |
| 还在选题 | 对照题面和附件比较几道题，看看数据拿不拿得到、现有工具能不能跑、最后能交什么。先做一个小试验，再给推荐路线和换题信号。见[选题研判](references/topic-selection.md)。 |
| 题定了，数据还乱 | 按小问列出输入、交付物和前后依赖；核对字段、单位、时间范围、缺测、重复记录和数据泄漏。先记清异常和处理前后的差异，再决定怎么处理。见[统计题工作流](references/statistical-problems.md)和[任务与证据模板](references/workflow-templates.md)。 |
| 有了方案，想看看靠不靠谱 | 先跑能解释的基线，再比较候选模型；把符号和约束对到代码。按题型检查样本外表现、约束是否满足或结果对参数有多敏感，保留运行配置和输出。见[模型选择与验证](references/problem-types-and-validation.md)。 |
| 训练不错，交付一跑就掉分 | 核对预测时到底能看到哪些数据，区分滚动一步和固定起点多步预测。按实际步长重做对照，看看误差集中在哪些时段。水厂 NTU 的例子见[时序外推与漂移](references/out-of-sample-evaluation-and-drift.md)。 |
| 结果出来了，要做图、写稿 | 从最终数据生成图表，核对单位、样本范围和图上数字，再检查出图。用真实结果写摘要、公式和正文，说明哪些结论有证据、哪些还有疑问。见[制图流程](references/figure-production.md)、[Python 绘图示例](references/figure-python-patterns.md)和[论文写作参考](references/paper-and-visualization.md)。 |
| 准备交稿和答辩 | 拿原题逐问对终稿，查漏答、摘要错数、旧图、未填占位符；从提交包复跑关键结果。整理答辩里最该讲清的模型取舍和局限。见[终审清单](references/final-audit.md)和[竞赛合规](references/competition-compliance.md)。 |

正式比赛先核对**当届**规则，尤其是 AI 使用、引用及支撑材料要求。没有运行过的结果就标明未运行。已经拿来挑模型的测试数据，也别再把它的分数当独立验证。

## 给论文手和队友

我把[论文手工作流](references/paper-hand-workflow.md)单独写了一份。接过来的是公式草稿、几个脚本、几张图时，可以先做一张理解卡：这一问在解什么，公式里的量对应哪个字段和变量，最后那个数字从哪次运行出来。接着可以只要章节骨架，也可以直接要母稿。已经定稿的段落照原样保留，修改以你手上最新的稿子为准。

有多人交接时，[协作指南](references/multi-agent-convergence.md)和[台账模板](references/workflow-templates.md)可以用来记数据版本、结果位置，以及谁还需要确认哪件事。两份结果冲突，就把数据范围、评价方式和实际交付时能拿到的信息列在一起核对。

[论文结构样例](references/paper-structure-patterns.md)可以参考；[我的写作习惯](references/paper-hand-preferences.md)另外放着，想沿用再用。篇幅、标题层级、图表安排还是按本题和现稿来。

## 安装和用法

用 Codex 的话，把仓库克隆到用户 Skill 目录：

```sh
git clone https://github.com/ai-lcs/math-modeling.skill.git ~/.agents/skills/math-modeling
```

入口是 [SKILL.md](SKILL.md)。装好后在 Codex 里用 `$math-modeling`。其他支持 Agent Skills 的工具，把整个目录放到各自的 Skill 目录即可。[Codex 安装说明](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

几个可以直接拿去改的问法：

> $math-modeling 这两道题我们只够试一轮。先看附件和交付要求，给我一个今晚就能做完的小试验，先别写完整方案。

> $math-modeling 最终要从早上 8 点一次预测未来 12 小时。看看现在的验证有没有用到那时拿不到的数据，给我一个公平的基线。

> $math-modeling 只改问题二的结果分析。稿子和运行表都在这里，先对上数字，其他章节别动。

## 可以单独跑的脚本

| 脚本 | 用来查什么 |
| --- | --- |
| [数据画像](scripts/profile_tabular_data.py) | 看字段类型、缺失、重复和数值分布，初步判断哪些列适合画图。 |
| [时间序列表比对](scripts/data_fingerprint.py) | 对两张同口径的表逐时间键比一列数值。行数和极值都相同，中间值改了也能查出来。 |
| [图表检查](scripts/audit_figure.py) | 提示分辨率、裁边、留白和绘图代码中值得复查的地方。还要自己对照原数据和成图。 |
| [占位符扫描](scripts/scan_placeholders.py) | 扫描 Markdown、TXT 或 Word 的疑似漏填项，不能代替数字核对。 |

在仓库根目录运行，把下面的文件名和列名换成你自己的：

```sh
python scripts/profile_tabular_data.py raw.csv
python scripts/data_fingerprint.py --raw raw.csv --cand candidate.csv --time-col DATE_TIME --value-col NTU
python scripts/audit_figure.py figure.png --code plot.py
python scripts/scan_placeholders.py draft.md
```

数据画像和比对用 `pandas`，读 Excel 按格式装 `openpyxl`（`.xlsx`）或 `xlrd`（`.xls`）；图表检查用 `numpy` 和 `Pillow`；扫描 Word 用 `python-docx`。比对和扫描都用退出码 `2` 报告未完成的检查，遇到它先看报错。

## Word 排版单独用

[paper-formatting](paper-formatting/SKILL.md) 是另一个 Skill，收的是我那版 Word 论文用过的格式和工具。只需要排版时，可以把该子目录单独放进 Skill 目录：用 [OMML 工具](paper-formatting/scripts/omml_lib.py)把 LaTeX 转成可编辑公式或生成三线表，用[文本替换](paper-formatting/scripts/docx_patch.py)处理被 Word 拆开的词，也可以[按标题替换章节](paper-formatting/scripts/docx_section_swap.py)。

公式转换依赖 Office 的 `MML2OMML.XSL`；章节带图时，替换脚本不会自动重连图片。具体依赖和限制看[排版说明](paper-formatting/SKILL.md)，新稿先按自己的模板来。

遇到没查出来的问题，欢迎开个 [Issue](https://github.com/ai-lcs/math-modeling.skill/issues)。能附一小段可复现的数据、命令或稿件就更好了。

[MIT License](LICENSE)
