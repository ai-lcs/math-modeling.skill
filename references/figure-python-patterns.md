# 便携 Python 制图模式

## 目录

1. 独立脚本结构
2. 样式与中文字体
3. 直接标注与重点突出
4. 不确定性与多子图
5. 导出

## 1. 分离数据准备与绘图

使用自包含脚本，不依赖 notebook 隐藏状态：

```python
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DATA = Path("data/result.csv")
OUT = Path("figures")


def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def prepare_data(raw: pd.DataFrame) -> pd.DataFrame:
    data = raw.copy()
    # 只执行已确认并明确命名的变换。
    return data


def draw(data: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7.2, 4.6), constrained_layout=True)
    # 在此绘图；不要在这里重新拟合模型或改写评价指标。
    return fig


def save(fig: plt.Figure, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    save(draw(prepare_data(load_data(DATA))), OUT / "descriptive_name")


if __name__ == "__main__":
    main()
```

把输入路径、输出路径、参数和随机种子集中声明。函数名称表达数据处理与绘图的边界，避免一个函数同时清洗、训练、评价和绘图。

## 2. 明确样式并检测中文字体

不要依赖用户全局 Matplotlib 设置。只设置少量、与当前图相关的参数：

```python
from matplotlib import font_manager

available = {font.name for font in font_manager.fontManager.ttflist}
candidates = ["Noto Sans CJK SC", "Source Han Sans CN", "Microsoft YaHei", "SimHei"]
for family in candidates:
    if family in available:
        plt.rcParams["font.sans-serif"] = [family, "DejaVu Sans"]
        break

plt.rcParams.update({
    "font.size": 10,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.unicode_minus": False,
})
```

画布比例随信息量变化，不把所有图强制成同一尺寸。缩放到论文实际宽度检查最小文字、线型和标记。

## 3. 减少图例查找与无意义配色

少量线条且末端标签不冲突时，可直接标注并省略图例：

```python
for name, group in data.groupby("series", sort=False):
    ordered = group.sort_values("time")
    line, = ax.plot(ordered["time"], ordered["value"])
    last = ordered.iloc[-1]
    ax.annotate(str(name), (last["time"], last["value"]),
                xytext=(5, 0), textcoords="offset points",
                va="center", color=line.get_color())
```

标签碰撞时改用紧凑图例，不强迫直接标注。不要同时完整保留图例和每条线的直接标签。

只强调由数据或用户决策确定的重点：

```python
colors = ["#2F6B9A" if method == selected else "#B8BEC6"
          for method in summary["method"]]
ax.barh(summary["method"], summary["score"], color=colors)
```

不要为了“丰富”给每个柱、点或线分配独立颜色。

## 4. 呈现真实不确定性和可比多子图

有真实区间时使用误差棒或区间带：

```python
ax.errorbar(summary["estimate"], summary["method"],
            xerr=[summary["estimate"] - summary["lower"],
                  summary["upper"] - summary["estimate"]],
            fmt="o", capsize=3)
```

不能从一个点估计凭空生成区间。注明置信区间、预测区间、标准差或重复运行范围的定义。

只有面板构成同一比较时才使用多子图：

```python
fig, axes = plt.subplots(1, len(metrics), figsize=(3.2 * len(metrics), 4.2),
                         sharey=True, constrained_layout=True)
```

保持模型顺序、颜色语义和适用的共同尺度；不同单位不强迫共用数值轴。共享图例和标签时确保不会掩盖面板差异。

## 5. 保存并检查实际文件

- PNG 通常至少 300 dpi；线、标记和文字为主的图同时保存 PDF 或 SVG；
- 超大散点图可在矢量文件中栅格化数据层，避免 SVG 体积失控；
- 使用稳定、描述性的文件名，把绘图代码、最终绘图数据和输出放在可追溯位置；
- 批处理保存后关闭 figure；
- 检查保存文件，而不只看交互窗口；
- 运行 `scripts/audit_figure.py` 后，仍要肉眼查看并回查原始数据。
