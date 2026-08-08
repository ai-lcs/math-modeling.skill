# 数学建模.skill

一个面向数学建模竞赛的 Codex Skill（亦可用在其他Agent上）。它以题目覆盖、证据链、模型—数据—代码—论文一致性和当届规则合规为主线，协助完成从选题到提交审计的端到端工作。

## 它解决什么问题

- 读题、拆题和逐问交付物检查；
- 选题比较、最小可行试做和放弃信号；
- 数据结构、质量、样本口径和泄漏审计；
- 基线、候选模型、数学定义和实现映射；
- 代码运行、结果验证、稳健性和失效诊断；
- 以论文手为主干，先讲懂模型与公式，再把建模手和代码手成果组织为可人工深改的论文母稿；
- 章节合同、二级与三级标题树、公式图表证据槽、局部锁定和最新稿回归控制；
- 图表选型、参考图重建、成图检查和论文表达；
- 摘要、正文、附录、答辩与提交前全链路审计；
- 当届规则、AI 使用、引用和支撑材料合规检查。

核心原则是：完整性和正确性优先于表面创新；所有关键数字、图表和结论都应能够追溯到真实数据、代码、配置或已核验来源。

## 仓库结构

```text
数学建模.skill/
├── README.md
├── .gitignore
└── math-modeling/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── references/
    │   ├── competition-compliance.md
    │   ├── figure-production.md
    │   ├── figure-python-patterns.md
    │   ├── final-audit.md
    │   ├── paper-hand-workflow.md
    │   ├── paper-and-visualization.md
    │   ├── problem-types-and-validation.md
    │   ├── statistical-problems.md
    │   ├── topic-selection.md
    │   └── workflow-templates.md
    └── scripts/
        ├── audit_figure.py
        └── profile_tabular_data.py
```

`SKILL.md` 保存核心工作流；专项规则放在 `references/` 中按需读取；两个脚本分别用于表格数据结构画像和成图启发式审计。脚本结果只是诊断线索，不能替代对原始数据、统计口径和最终图片的人工核验。

## 安装

### 方式一：让 Codex 安装

仓库发布后，在 Codex 中发送：

```text
请使用 $skill-installer 从以下 GitHub 路径安装 math-modeling：
https://github.com/ai-lcs/math-modeling.skill/tree/main/math-modeling
```

安装完成后，在下一轮对话中使用 `$math-modeling`。

### 方式二：手动安装

克隆仓库后，将整个 `math-modeling` 文件夹复制到：

```text
Windows: %USERPROFILE%\.codex\skills\math-modeling
macOS/Linux: ~/.codex/skills/math-modeling
```

如果目标位置已经存在旧版本，请先备份旧目录，再用新目录完整替换；不要只覆盖个别文件，以免留下过期参考资料。重新开启任务后，Codex 会读取更新后的 Skill 列表。

## 使用示例

明确调用：

```text
使用 $math-modeling 阅读这道赛题和全部附件，先做选题可行性分析，不要直接生成完整论文。
```

```text
使用 $math-modeling 审计当前数据、模型代码和论文，按“必须修正、建议修正、可选优化”输出问题。
```

```text
使用 $math-modeling 根据真实运行结果设计论文图表，并检查图能够支持和不能单独证明的结论。
```

```text
使用 $math-modeling 进入论文手模式：先把建模手思路和代码结果讲清楚，再给出标题树、证据槽和可继续人工修改的论文母稿；不要改动我已锁定的章节。
```

当请求明显涉及数学建模竞赛、赛题求解、数据审计、模型验证、论文或提交检查时，Codex 也可以根据 Skill 描述自动选择它。

## 可选脚本依赖

Skill 的文字工作流不依赖特定 Python 库。若使用附带脚本，需要：

- Python 3.10 或更高版本；
- `numpy`；
- `pandas`；
- `Pillow`；
- 读取 Excel 时通常还需要 `openpyxl`；
- 读取 Parquet 或 Feather 时通常还需要 `pyarrow`。

示例：

```text
python math-modeling/scripts/profile_tabular_data.py <数据文件> --output <画像.json>
python math-modeling/scripts/audit_figure.py <图片> --code <绘图脚本> --output <审计.json>
```

脚本拒绝把 pickle 等可执行序列化格式当作普通数据读取。

## 使用边界

- 不保证奖项、排名或特定评分结果；
- 不编造数据、文献、参数、代码输出、统计量或竞赛规则；
- 未实际运行的代码不得被描述为已经得到结果；
- 竞赛规则和 AI 使用要求可能变化，正式使用和提交前必须重新核验当届官方文件；
- 教师培训中的页数、模型数和图表数只在对应任务明确要求时执行，不作为所有比赛的固定模板；
- AI 可以辅助组织、检查和实现，但参赛队仍需对原创性、真实性、数学正确性和最终提交负责。

## 当前验证状态

- Skill 目录和 YAML 元数据已通过结构验证；
- 两个 Python 脚本已通过语法检查；
- 表格画像脚本已使用样例 CSV 运行；
- 图片审计脚本已使用样例 PNG 和绘图代码运行；
- 论文手标题树、锁定范围以及“理解公式—筛选入文公式”两类独立前向测试已通过；
- 尚未宣称完成多题型、完整比赛周期的独立端到端压力测试。
