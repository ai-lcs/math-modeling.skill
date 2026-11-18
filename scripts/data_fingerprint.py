#!/usr/bin/env python
"""比较同口径时间序列表的时间键和一个指定数值列。

用法：python data_fingerprint.py --raw RAW.xlsx --cand CAND.xlsx
          --time-col DATE_TIME --value-col NTU [--sheet 数据]

支持 CSV、Excel。时间键须唯一，采用 YYYY-MM-DD 或 ISO 日期时间；
带时区的时间按同一时刻对齐，未标时区的时间不推断时区。数值精确比较，
允许双方在相同时间键上留空。其他列、数据来源和处理逻辑不在检查范围内。
退出码：0 = 所查范围一致；1 = 不一致；2 = 无法完成检查。
需要 pandas；Excel 另需对应的 pandas 读取引擎，例如 .xlsx 用 openpyxl。
不同口径、不同布局或合法重复时间键，请先明确变换与连接键，再另行核验。
"""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re
import sys


ISO_TIME = re.compile(
    r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d{1,9})?)?"
    r"(?:Z|[+-]\d{2}:?\d{2})?)?"
)


def _load(path, sheet):
    import pandas as pd

    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        table = pd.read_csv(path, header=None, dtype=str, keep_default_na=False)
    elif suffix in {".xls", ".xlsx"}:
        table = pd.read_excel(path, sheet_name=0 if sheet is None else sheet,
                              header=None, dtype=str, keep_default_na=False)
    else:
        raise ValueError(f"不支持的文件格式：{suffix}")
    if table.empty:
        raise ValueError("没有表头")
    data = table.iloc[1:].copy()
    data.columns = table.iloc[0].tolist()
    return data


def index_table(frame, time_col, value_col):
    import pandas as pd

    columns = frame.columns.tolist()
    missing_cols = [name for name in (time_col, value_col) if name not in columns]
    if missing_cols:
        raise ValueError(f"缺少列：{', '.join(missing_cols)}")
    if any(columns.count(name) > 1 for name in (time_col, value_col)):
        raise ValueError("所指定的键列或数值列存在重名")
    if frame.empty:
        raise ValueError("没有数据行")

    indexed = {}
    for row, (time_text, value_text) in enumerate(
        frame[[time_col, value_col]].itertuples(index=False, name=None), 1
    ):
        if not ISO_TIME.fullmatch(time_text.strip()):
            raise ValueError(f"第 {row} 个数据行的时间键不是有效 ISO 日期或时间：{time_text!r}")
        try:
            timestamp = pd.Timestamp(time_text.strip())
        except (ValueError, OverflowError) as exc:
            raise ValueError(f"第 {row} 个数据行的时间键无效：{time_text!r}") from exc
        if timestamp in indexed:
            raise ValueError(f"第 {row} 个数据行的时间键重复：{timestamp}")

        value = None
        if value_text.strip():
            try:
                value = Decimal(value_text.strip())
                if not value.is_finite():
                    raise InvalidOperation
            except InvalidOperation as exc:
                raise ValueError(f"第 {row} 个数据行不是有限数值：{value_text!r}") from exc
        indexed[timestamp] = value
    return indexed


def compare_tables(raw, cand):
    missing = [time for time in raw if time not in cand]
    extra = [time for time in cand if time not in raw]
    changed = [time for time in raw if time in cand and raw[time] != cand[time]]
    return missing, extra, changed


def _selftest():
    import pandas as pd

    base = pd.DataFrame({"T": ["2025-01-01", "2025-01-02", "2025-01-03"],
                         "V": ["0", "1", "10"]})
    raw = index_table(base, "T", "V")
    assert not any(compare_tables(raw, index_table(base.iloc[::-1], "T", "V")))
    changed = base.assign(V=["0", "9", "10"])
    assert len(compare_tables(raw, index_table(changed, "T", "V"))[2]) == 1
    shifted = base.assign(T=["2026-01-01", "2026-01-02", "2026-01-03"])
    assert tuple(map(len, compare_tables(raw, index_table(shifted, "T", "V")))) == (3, 3, 0)
    for invalid in (base.assign(T=["2025-01-01", "5.87", "2025-01-03"]),
                    base.assign(T=["2025-01-01", "2025-01-01", "2025-01-03"]),
                    base.drop(columns="V")):
        try:
            index_table(invalid, "T", "V")
        except ValueError:
            continue
        raise AssertionError("无效输入未被拒绝")
    print("SELFTEST PASS")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw", help="原始或权威数据文件")
    parser.add_argument("--cand", help="待核验的候选表")
    parser.add_argument("--time-col", help="两表共用的唯一时间键列名")
    parser.add_argument("--value-col", help="两表共用的数值列名")
    parser.add_argument("--sheet", help="两份 Excel 共用的表单名，默认首个表单")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not all((args.raw, args.cand, args.time_col, args.value_col)):
        parser.error("需要 --raw、--cand、--time-col 与 --value-col，或使用 --selftest")
    if args.time_col == args.value_col:
        parser.error("时间键和数值列必须不同")

    indexed = []
    for label, path in (("RAW", args.raw), ("CAND", args.cand)):
        try:
            indexed.append(index_table(_load(path, args.sheet), args.time_col, args.value_col))
        except Exception as exc:
            print(f"检查未完成（{label}: {path}）：{exc}", file=sys.stderr)
            return 2

    raw, cand = indexed
    missing, extra, changed = compare_tables(raw, cand)
    if missing or extra or changed:
        print(f"不一致：候选表缺少 {len(missing)} 个键，多出 {len(extra)} 个键，"
              f"同键数值不同 {len(changed)} 个。")
        for label, keys in (("缺少键", missing), ("多出键", extra), ("数值不同", changed)):
            for key in keys[:5]:
                detail = f"：原表={raw[key]}，候选表={cand[key]}" if label == "数值不同" else ""
                print(f"  {label} {key}{detail}")
        return 1
    print(f"所查范围一致：{len(raw)} 个时间键及列 {args.value_col!r} 的对应值。"
          "未检查其他列或数据来源。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
