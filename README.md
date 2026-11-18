# 数学建模竞赛协作 Skill

一个面向数学建模竞赛与统计类项目的 **Agent Skill**，适用于 Hermes、Codex、Cursor、Windsurf、Claude Code 或任何支持 `SKILL.md` 的 AI 编程/助手环境。

它以**题目覆盖、证据链、模型—数据—代码—论文一致性**和**当届规则合规**为主线，协助完成从选题到提交审计的端到端工作。

## 它解决什么问题

- 读题、拆题和逐问交付物检查
- 选题比较、最小可行试做和放弃信号
- 数据结构、质量、样本口径和泄漏审计
- 基线、候选模型、数学定义和实现映射
- 代码运行、结果验证、稳健性和失效诊断
- 以论文手为主干，先讲懂模型与公式，再把建模手和代码手成果组织为可人工深改的论文母稿
- 章节合同、二级与三级标题树、公式图表证据槽、局部锁定和最新稿回归控制
- 图表选型、参考图重建、成图检查和论文表达
- 摘要、正文、附录、答辩与提交前全链路审计
- 当届规则、AI 使用、引用和支撑材料合规检查
- 多 Agent（论文手/建模手/代码手/多个 AI）协作的版本、口径与冲突收敛

## 核心原则

完整性和正确性优先于表面创新；所有关键数字、图表和结论都应能够追溯到真实数据、代码、配置或已核验来源。多 Agent 协作时，验证口径必须与交付任务同构，冲突显式列出、按交付口径裁决。

## 仓库结构

```text
math-modeling.skill/
├── README.md
├── LICENSE                          ← MIT 许可证
├── .gitignore
├── SKILL.md                         ← 主入口：触发条件、质量优先级、工作模式选择
├── agents/                          ← 可选：各 Agent 平台的 interface 适配
│   └── openai.yaml
├── references/                      ← 参考文档（按任务类型组织）
│   ├── competition-compliance.md    ← 竞赛规则与 AI 使用合规
│   ├── paper-hand-workflow.md       ← 论文手主工作流
│   ├── paper-hand-preferences.md    ← 作者的论文工作偏好，按需启用
│   ├── paper-structure-patterns.md  ← 论文结构模式库
│   ├── paper-and-visualization.md   ← 论文结构、摘要、公式、表格与图表
│   ├── out-of-sample-evaluation-and-drift.md ← 外推评估与时间漂移
│   ├── multi-agent-convergence.md   ← 多 Agent 协作与口径收敛
│   ├── figure-production.md         ← 图表制作规范
│   ├── figure-python-patterns.md    ← Python 绘图模式
│   ├── final-audit.md               ← 提交前审计清单
│   ├── topic-selection.md           ← 选题与放弃信号
│   ├── problem-types-and-validation.md ← 问题类型与验证策略
│   ├── statistical-problems.md      ← 统计类问题建模范式
│   └── workflow-templates.md        ← 任务控制表模板
├── scripts/                         ← 可执行脚本（数据指纹、占位符扫描、图形审计、数据画像）
│   ├── data_fingerprint.py          ← 同口径时间序列表逐键核验
│   ├── scan_placeholders.py         ← 论文成稿空占位符与数字缺失扫描
│   ├── audit_figure.py              ← 图表一致性审计
│   └── profile_tabular_data.py      ← 数据画像与质量报告
└── paper-formatting/                ← 独立 Skill：论文 Word 排版规范与工具（见下）
    ├── SKILL.md                     ← 触发条件、格式规格、工作流与验收标准
    └── scripts/                     ← OMML 公式构造、run 级文本修补、章节替换
        ├── omml_lib.py              ← LaTeX→OMML、公式表、三线表构造器
        ├── docx_patch.py            ← run 级安全文本替换（跨 run 拆分免疫）
        └── docx_section_swap.py     ← 跨文档章节替换（标题定界、深拷贝插入）
```

## 可选 Skill：paper-formatting

以作者的 2026 模拟赛 1B 论文（final.docx）为基准的 **Word 排版规范**。仅在需要复刻该风格或复用工具时单独启用，新稿以当前模板为准。它覆盖：

- 图片公式 → 原生 OMML（latex2mathml + Office MML2OMML.XSL），公式表=1行2列无边框、编号加粗全角
- 三线表、图注/表注、字号映射（小四/五号半点值）、标题与正文段落实测参数
- 全文公式连续编号与正文"式（N）"引用同步纪律
- run 级文本修复（Word 重存导致的跨 run 拆分免疫）
- 跨文档章节替换（含已实测的限制：图片 rId 需另行处理）

随附三个脚本均有冒烟/端到端测试记录，可直接复用。安装时如需单独启用该 Skill：

```bash
# 方式一：随主 skill 克隆后手动复制
git clone https://github.com/ai-lcs/math-modeling.skill.git
cp -r math-modeling.skill/paper-formatting <agent-skills-dir>/paper-formatting

# 方式二：独立克隆仓库子目录（sparse checkout）
git clone --filter=blob:none --sparse https://github.com/ai-lcs/math-modeling.skill.git
cd math-modeling.skill && git sparse-checkout set paper-formatting
```

## 安装方式

将本仓库克隆或下载到 Agent 的 skill 目录下：

```bash
git clone https://github.com/ai-lcs/math-modeling.skill.git <agent-skills-dir>/math-modeling
```

不同平台的 skill 目录：

- **Codex**: `~/.codex/skills/math-modeling`
- **Cursor**: `~/.cursor/skills/math-modeling`（或项目级 `.cursor/skills/`）
- **Windsurf**: `~/.windsurf/skills/math-modeling`
- **Claude Code**: `~/.claude/skills/math-modeling`
- **Hermes**: `~/AppData/Local/hermes/skills/math-modeling`（Windows）

如果目标位置已存在旧版本，请先备份旧目录，再用新目录完整替换。重新开启任务后，Agent 会读取更新后的 Skill 描述并自动匹配。

## 触发条件

当请求涉及数学建模竞赛或项目时，按用户要求进入全流程或对应专项。通用统计问答、普通润色或单纯 Word 排版不自动进入建模流程。

`SKILL.md` 保存通用证据规则与任务路由；`references/` 按题型提供条件化的技术建议和案例；`references/paper-hand-preferences.md` 的作者偏好只在用户或项目采用时启用。

## 核验脚本

```bash
python scripts/data_fingerprint.py --raw raw.csv --cand candidate.csv --time-col DATE_TIME --value-col NTU
python scripts/scan_placeholders.py draft.md
```

- `data_fingerprint.py` 适用于同口径、唯一时间键的 CSV 或 Excel。必须指定时间列和数值列；时间使用 ISO 日期或日期时间。`0` 表示所查键和值一致，`1` 表示不一致，`2` 表示未完成检查。其他字段和来源需另核验；如需比较多列，可逐列执行。依赖 `pandas`，读取 `.xlsx` 另需 `openpyxl`，读取 `.xls` 另需 `xlrd`。
- `scan_placeholders.py` 检查 UTF-8 Markdown、TXT 和 Word 正文及顶层表格，读 Word 需 `python-docx`。`0` 表示未检出疑似项，`1` 表示检出疑似项，`2` 表示至少一个输入未完成扫描。它不会验证数字是否正确。

## 贡献

欢迎提交 Issue 和 PR。核心设计哲学：

- 能确定验证边界的检查用脚本执行；脚本只为实际覆盖的范围提供结果。
- 技术建议写清适用条件，案例记录和个人习惯不自动成为所有任务的要求。
- 由当前请求决定分工、授权与所需核验。

## Star History

<a href="https://www.star-history.com/?type=date&repos=ai-lcs%2Fmath-modeling.skill">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=ai-lcs/math-modeling.skill&type=date&theme=dark&legend=top-left&sealed_token=FPHVimhXuchi-V33SMbggfQ2w3k4Dti8AMUcuzO7lC9B1dFSrMXymOIVoTSISgYrZyt5XFVDUK9O8pga4iWrUiBsc3J_g0nJwuptnSxT7BrW-lJEA_iT4A" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=ai-lcs/math-modeling.skill&type=date&legend=top-left&sealed_token=FPHVimhXuchi-V33SMbggfQ2w3k4Dti8AMUcuzO7lC9B1dFSrMXymOIVoTSISgYrZyt5XFVDUK9O8pga4iWrUiBsc3J_g0nJwuptnSxT7BrW-lJEA_iT4A" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=ai-lcs/math-modeling.skill&type=date&legend=top-left&sealed_token=FPHVimhXuchi-V33SMbggfQ2w3k4Dti8AMUcuzO7lC9B1dFSrMXymOIVoTSISgYrZyt5XFVDUK9O8pga4iWrUiBsc3J_g0nJwuptnSxT7BrW-lJEA_iT4A" />
 </picture>
</a>

## License

MIT
