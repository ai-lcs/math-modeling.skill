#!/usr/bin/env python
"""数据指纹比对：二手表格进入论文前的机械准入门槛。

用法：
    python data_fingerprint.py --raw RAW.xlsx --cand CAND.xlsx \
        [--time-col DATE_TIME] [--value-col NTU]

对候选表(cand)与原始/权威表(raw)分别生成指纹并比对：
行数、唯一时间键、重复键、不可解析时刻样本、目标列极值及位置、缺失数。
任一硬性项不一致 -> 退出码 1（不通过）；一致 -> 退出码 0。

原始数据布局特殊（多月表拼接等）时，先用适配代码把它规整成
【时间键 + 数值列】的 DataFrame，再 import 本脚本的 fingerprint/compare，
报告字段保持不变。

自检：python data_fingerprint.py --selftest
"""
from __future__ import annotations

import argparse
import sys


def _load(path, sheet=None):
    import pandas as pd

    if str(path).lower().endswith(".csv"):
        return pd.read_csv(path)
    return pd.read_excel(path, sheet_name=sheet or 0)


def fingerprint(df, time_col=None, value_col=None):
    """对单张表生成指纹字典。"""
    import pandas as pd

    rep = {"rows": int(len(df))}
    if time_col and time_col in df.columns:
        t = df[time_col]
        rep["unique_time_keys"] = int(t.nunique())
        rep["dup_time_rows"] = int(t.duplicated().sum())
        parsed = pd.to_datetime(t, errors="coerce")
        mask_bad = parsed.isna() & t.notna()
        # 数值垃圾（如 5.87）会被当作 epoch 解析成 1970 年附近 —— 落在合理
        # 年份窗口之外的时刻同样视为非法，防止"假成功"混进表。
        mask_epoch = parsed.notna() & (
            (parsed.dt.year < 2000) | (parsed.dt.year > 2100)
        )
        rep["unparseable_time"] = int((mask_bad | mask_epoch).sum())
        rep["bad_time_samples"] = [str(x) for x in t[mask_bad | mask_epoch].head(5)]
    if value_col and value_col in df.columns:
        v = pd.to_numeric(df[value_col], errors="coerce")
        rep["value_na"] = int(v.isna().sum())
        if v.notna().any():
            rep["value_max"] = round(float(v.max()), 6)
            rep["value_max_at"] = (
                str(df.loc[v.idxmax(), time_col]) if time_col else str(v.idxmax())
            )
            rep["value_min"] = round(float(v.min()), 6)
            rep["value_min_at"] = (
                str(df.loc[v.idxmin(), time_col]) if time_col else str(v.idxmin())
            )
    return rep


def compare(rep_raw, rep_cand, keys):
    """返回 {字段: (raw值, cand值)} 形式的差异集。"""
    return {k: (rep_raw.get(k), rep_cand.get(k))
            for k in keys if rep_raw.get(k) != rep_cand.get(k)}


HARD_KEYS = ["rows", "unique_time_keys", "value_max", "value_min"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", help="原始/权威数据文件")
    ap.add_argument("--cand", help="候选表（待准入的工作簿/导出）")
    ap.add_argument("--time-col", dest="time_col", default=None)
    ap.add_argument("--value-col", dest="value_col", default=None)
    ap.add_argument("--sheet", default=None, help="excel 表单名（默认第一个）")
    ap.add_argument("--keys", nargs="*", default=HARD_KEYS,
                    help="参与硬性比对的指纹字段")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        import pandas as pd

        # 用真实时间戳构造，复刻"丢极值 + 注入数值垃圾时刻"的事故形态
        ts = pd.date_range("2025-01-01", periods=100, freq="h")
        base = pd.DataFrame({"T": [str(x) for x in ts],
                             "V": [i % 7 * 0.5 for i in range(100)]})
        base.loc[42, "V"] = 11.9  # 全局最大极值
        dirty = base.drop(index=[42]).copy()
        dirty = pd.concat(
            [dirty, pd.DataFrame({"T": ["5.87"] * 5, "V": [0.3] * 5})],
            ignore_index=True,
        )
        r1 = fingerprint(base, "T", "V")
        r2 = fingerprint(dirty, "T", "V")
        d = compare(r1, r2, HARD_KEYS)
        # 丢极值(-1键)+注5行同键(+1键)后 unique_time_keys 恰好抵消，
        # 但 rows/value_max/非法时刻必须暴露差异 —— 这正是真实事故的形态。
        assert set(d) >= {"rows", "value_max"}, d
        assert r2["unparseable_time"] == 5, r2
        assert set(r2["bad_time_samples"]) == {"5.87"}, r2
        print("SELFTEST PASS — 唯一键数恰好抵消时仍识别脏表：", d)
        return 0

    if not a.raw or not a.cand:
        ap.error("需要 --raw 与 --cand，或使用 --selftest")
    rr = fingerprint(_load(a.raw, a.sheet), a.time_col, a.value_col)
    cc = fingerprint(_load(a.cand, a.sheet), a.time_col, a.value_col)
    print("RAW :", rr)
    print("CAND:", cc)
    diffs = compare(rr, cc, a.keys)
    if diffs:
        print("\n指纹不一致 —— 候选表不得作为论文主表数据源：")
        for k, (rv, cv) in diffs.items():
            print(f"  {k}: raw={rv}  cand={cv}")
        return 1
    print("\n指纹一致：候选表通过准入。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
