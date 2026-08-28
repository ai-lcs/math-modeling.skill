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
└── scripts/                         ← 可执行脚本（数据指纹、占位符扫描、图形审计、数据画像）
    ├── data_fingerprint.py          ← 二手数据指纹比对（机械准入门槛）
    ├── scan_placeholders.py         ← 论文成稿空占位符与数字缺失扫描
    ├── audit_figure.py              ← 图表一致性审计
    └── profile_tabular_data.py      ← 数据画像与质量报告
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

当请求明显涉及数学建模竞赛、赛题求解、数据审计、模型验证、论文或提交检查时，Agent 可以根据 `SKILL.md` 中的 `description` 自动选择它。

## 贡献

欢迎提交 Issue 和 PR。核心设计哲学：

- **只吸收可嵌入强人工流程的"零件"**：独立门禁、校验脚本、局部规则，拒绝需要替换整体编排方式的"黑盒"方案
- **机械化强制优于说教**：每条重要规则都应能变成脚本或门禁，不依赖 Agent 自觉
- **人机分工边界清晰**：人做决策、Agent 做有界任务；审计不能依赖自觉，要做成机械步骤

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
