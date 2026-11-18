# Math Modeling Skill

做数模时，队友发来两份结果表，行数一样，论文到底该用哪份？还有一种常见情况：验证时每一步都能拿到前一刻的真值，交付时却要一次预测未来 12 小时。这些问题越早发现，越少返工。

我写这个 Skill，就是想让 AI 帮忙查清这些事。它能陪你选题、拆题、核对数据和模型，也能把队友的代码结果整理成论文母稿。做到哪一步，由你说了算。

## 安装

用 Codex 的话，在终端执行：

```sh
git clone https://github.com/ai-lcs/math-modeling.skill.git ~/.agents/skills/math-modeling
```

装好后，在 Codex 里用 `$math-modeling` 开始。其他支持 Agent Skills 的工具，把整个仓库放进各自的 Skill 目录即可。[Codex 安装说明](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

## 可以直接这样问

> $math-modeling 帮我对照这两份结果表。按时间键检查 NTU 列，列出差异，先别动原文件。

> $math-modeling 只看问题二。帮我把建模手的公式和代码里的变量对上，先讲懂，再写正文。

> $math-modeling 对照原题审一遍终稿，看看有没有漏答，摘要里的数字能不能找到出处。

## 仓库里有什么

- [SKILL.md](SKILL.md) 是入口，负责按任务选流程。做正式比赛时，先核对当届规则和 AI 使用要求。
- [references/](references/) 放具体方法和案例。[我的论文写作习惯](references/paper-hand-preferences.md) 也单独放在这里，想沿用时再用。
- [scripts/](scripts/) 可以单独运行。数据比对只核对指定的时间键和数值列；占位符扫描只找疑似漏填。两者都把「检查未完成」单独报告。
- [paper-formatting](paper-formatting/SKILL.md) 是可选的 Word 排版 Skill，带有公式、三线表和章节替换工具。

```sh
python scripts/data_fingerprint.py --raw raw.csv --cand candidate.csv --time-col DATE_TIME --value-col NTU
python scripts/scan_placeholders.py draft.md
```

数据比对需要 `pandas`，读 `.xlsx` 还需要 `openpyxl`（`.xls` 用 `xlrd`）；扫描 Word 需要 `python-docx`。

如果你遇到了检查没抓到的问题，欢迎开个 Issue。能附最小复现例子就更好了。

[MIT License](LICENSE)
