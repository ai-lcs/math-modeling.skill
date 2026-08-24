#!/usr/bin/env python3
"""Summarize a safe tabular file before mathematical-modeling visualization.

The script reports structure and potential plotting fields. It does not modify the
input, infer scientific conclusions, or accept executable serialized formats.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SUPPORTED_SUFFIXES = {
    ".csv",
    ".tsv",
    ".txt",
    ".xlsx",
    ".xls",
    ".json",
    ".jsonl",
    ".ndjson",
    ".parquet",
    ".feather",
}


def as_json(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
        return value if math.isfinite(value) else None
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (pd.Timestamp, pd.Timedelta, Path)):
        return str(value)
    if isinstance(value, dict):
        return {str(key): as_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [as_json(item) for item in value]
    if pd.isna(value):
        return None
    return value if isinstance(value, (str, int, float, bool)) else str(value)


def read_frame(path: Path, sheet: str | None, encoding: str | None, separator: str | None) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        allowed = ", ".join(sorted(SUPPORTED_SUFFIXES))
        raise ValueError(f"unsupported or unsafe file type '{suffix}'; supported: {allowed}")
    if suffix in {".csv", ".tsv", ".txt"}:
        sep = separator if separator is not None else ("\t" if suffix == ".tsv" else ",")
        return pd.read_csv(path, sep=sep, encoding=encoding)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, sheet_name=sheet if sheet is not None else 0)
    if suffix == ".json":
        try:
            return pd.read_json(path)
        except ValueError:
            return pd.read_json(path, lines=True)
    if suffix in {".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=True)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_feather(path)


def datetime_profile(series: pd.Series) -> dict[str, Any] | None:
    if pd.api.types.is_datetime64_any_dtype(series):
        parsed = pd.to_datetime(series, errors="coerce")
    elif pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        sample = series.dropna().astype(str).head(300)
        if len(sample) < 3 or sample.str.contains(r"[-/:]|\b(?:19|20)\d{2}\b", regex=True).mean() < 0.6:
            return None
        parsed_sample = pd.to_datetime(sample, errors="coerce")
        if parsed_sample.notna().mean() < 0.8:
            return None
        parsed = pd.to_datetime(series, errors="coerce")
    else:
        return None
    valid = parsed.dropna()
    return {
        "valid_rate": float(parsed.notna().mean()),
        "min": valid.min() if not valid.empty else None,
        "max": valid.max() if not valid.empty else None,
        "monotonic_increasing": bool(valid.is_monotonic_increasing) if not valid.empty else None,
    }


def roles_for(name: str, series: pd.Series, date_info: dict[str, Any] | None) -> list[str]:
    lower = name.strip().lower()
    count = max(len(series), 1)
    unique = int(series.nunique(dropna=True))
    roles: list[str] = []
    if date_info is not None or any(token in lower for token in ("date", "time", "year", "month", "day", "timestamp")):
        roles.append("time_candidate")
    if lower in {"lat", "latitude", "y_coord", "y_coordinate"} or "latitude" in lower:
        roles.append("latitude_candidate")
    if lower in {"lon", "lng", "longitude", "x_coord", "x_coordinate"} or "longitude" in lower:
        roles.append("longitude_candidate")
    if any(token in lower for token in ("id", "uuid", "code", "index")) and unique / count >= 0.8:
        roles.append("identifier_candidate")
    if pd.api.types.is_bool_dtype(series):
        roles.append("binary")
    elif pd.api.types.is_numeric_dtype(series):
        roles.append("numeric")
        if unique <= 12:
            roles.append("low_cardinality_numeric")
    elif unique <= max(20, int(0.1 * count)):
        roles.append("categorical_candidate")
    elif unique / count >= 0.8:
        roles.append("high_cardinality_text")
    else:
        roles.append("text")
    return roles


def profile_column(name: str, series: pd.Series, max_categories: int) -> dict[str, Any]:
    date_info = datetime_profile(series)
    non_null = series.dropna()
    result: dict[str, Any] = {
        "name": name,
        "dtype": str(series.dtype),
        "rows": int(len(series)),
        "non_null": int(len(non_null)),
        "missing": int(series.isna().sum()),
        "missing_rate": float(series.isna().mean()),
        "unique": int(series.nunique(dropna=True)),
        "constant_or_empty": bool(series.nunique(dropna=True) <= 1),
        "datetime": date_info,
        "roles": roles_for(name, series, date_info),
    }
    if pd.api.types.is_numeric_dtype(series):
        values = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        if not values.empty:
            quartiles = values.quantile([0.0, 0.25, 0.5, 0.75, 1.0])
            result["numeric"] = {
                "min": quartiles.loc[0.0],
                "q1": quartiles.loc[0.25],
                "median": quartiles.loc[0.5],
                "q3": quartiles.loc[0.75],
                "max": quartiles.loc[1.0],
                "mean": values.mean(),
                "std": values.std(ddof=1) if len(values) > 1 else 0.0,
                "zeros": int((values == 0).sum()),
                "negative": int((values < 0).sum()),
            }
    else:
        values = non_null.astype(str).value_counts().head(max_categories)
        result["top_values"] = [
            {"value": value, "count": int(count), "share": float(count / max(len(non_null), 1))}
            for value, count in values.items()
        ]
    return as_json(result)


def build_report(frame: pd.DataFrame, source: Path, max_categories: int, sample_rows: int) -> dict[str, Any]:
    columns = [profile_column(str(column), frame[column], max_categories) for column in frame.columns]
    numeric = [column["name"] for column in columns if "numeric" in column["roles"]]
    categorical = [column["name"] for column in columns if "categorical_candidate" in column["roles"]]
    time = [column["name"] for column in columns if "time_candidate" in column["roles"]]
    latitude = [column["name"] for column in columns if "latitude_candidate" in column["roles"]]
    longitude = [column["name"] for column in columns if "longitude_candidate" in column["roles"]]
    structures: list[str] = []
    if time and numeric:
        structures.append("time_or_sequence")
    if categorical and numeric:
        structures.append("group_comparison")
    if len(numeric) >= 2:
        structures.append("numeric_relationship")
    if latitude and longitude:
        structures.append("geospatial_points")
    if len(numeric) >= 3:
        structures.append("multimetric_or_multivariate")
    warnings: list[str] = []
    if frame.empty:
        warnings.append("dataset is empty")
    if frame.columns.duplicated().any():
        warnings.append("duplicate column names detected")
    duplicates = int(frame.duplicated().sum()) if len(frame) else 0
    if duplicates:
        warnings.append(f"{duplicates} fully duplicated rows detected")
    for column in columns:
        if column["missing_rate"] >= 0.5:
            warnings.append(f"column '{column['name']}' is at least 50 percent missing")
        if column["constant_or_empty"]:
            warnings.append(f"column '{column['name']}' is constant or all missing")
        if "identifier_candidate" in column["roles"] or "high_cardinality_text" in column["roles"]:
            warnings.append(f"column '{column['name']}' may be an identifier rather than a chart category")
    return as_json({
        "source": source,
        "shape": {"rows": int(frame.shape[0]), "columns": int(frame.shape[1])},
        "duplicate_rows": duplicates,
        "candidate_structures": structures,
        "candidate_columns": {
            "time": time,
            "numeric": numeric,
            "categorical": categorical,
            "latitude": latitude,
            "longitude": longitude,
        },
        "columns": columns,
        "sample_rows": frame.head(sample_rows).where(pd.notna(frame.head(sample_rows)), None).to_dict(orient="records"),
        "warnings": warnings,
        "note": "Candidate roles are structural hints, not verified scientific meanings.",
    })


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="safe tabular input file")
    parser.add_argument("--sheet", help="Excel sheet name; default is the first sheet")
    parser.add_argument("--encoding", help="text encoding for CSV, TSV, or TXT")
    parser.add_argument("--separator", help="delimiter for CSV, TSV, or TXT")
    parser.add_argument("--max-categories", type=int, default=10)
    parser.add_argument("--sample-rows", type=int, default=5)
    parser.add_argument("--output", type=Path, help="JSON output path; print to stdout when omitted")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = args.path.expanduser().resolve()
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2
    try:
        report = build_report(read_frame(path, args.sheet, args.encoding, args.separator), path, args.max_categories, args.sample_rows)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
