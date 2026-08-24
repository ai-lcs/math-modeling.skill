#!/usr/bin/env python3
"""Report visual-delivery risks in a rendered figure and optional plotting code.

This is a heuristic lint. It does not establish scientific correctness and should
be used with visual inspection plus comparison to the source data.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


def luminance(rgb: np.ndarray) -> np.ndarray:
    values = rgb.astype(np.float32) / 255.0
    linear = np.where(values <= 0.04045, values / 12.92, ((values + 0.055) / 1.055) ** 2.4)
    return 0.2126 * linear[..., 0] + 0.7152 * linear[..., 1] + 0.0722 * linear[..., 2]


def corner_background(rgb: np.ndarray) -> np.ndarray:
    height, width, _ = rgb.shape
    edge = max(1, min(12, height // 20, width // 20))
    patches = [
        rgb[:edge, :edge], rgb[:edge, width - edge:],
        rgb[height - edge:, :edge], rgb[height - edge:, width - edge:],
    ]
    return np.median(np.concatenate([patch.reshape(-1, 3) for patch in patches]), axis=0)


def inspect_image(path: Path) -> dict[str, Any]:
    opened = Image.open(path)
    rgba = opened.convert("RGBA")
    canvas = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    rgb = np.asarray(Image.alpha_composite(canvas, rgba).convert("RGB"))
    height, width, _ = rgb.shape
    background = corner_background(rgb)
    difference = np.max(np.abs(rgb.astype(np.int16) - background.astype(np.int16)), axis=2)
    content = difference > 12
    coverage = float(content.mean())
    warnings: list[dict[str, str]] = []
    margins: dict[str, float | int]
    if content.any():
        y, x = np.where(content)
        margins = {
            "left_px": int(x.min()), "right_px": int(width - 1 - x.max()),
            "top_px": int(y.min()), "bottom_px": int(height - 1 - y.max()),
        }
    else:
        margins = {"left_px": 0, "right_px": 0, "top_px": 0, "bottom_px": 0}
        warnings.append({"severity": "critical", "message": "no visible content detected"})
    for edge_name, value in list(margins.items()):
        axis_size = width if edge_name.startswith(("left", "right")) else height
        margins[edge_name.replace("_px", "_rate")] = value / axis_size
    if width < 1000 or height < 600:
        warnings.append({"severity": "major", "message": "raster dimensions may be too small for document insertion"})
    aspect = width / height if height else math.inf
    if aspect > 4.0 or aspect < 0.25:
        warnings.append({"severity": "major", "message": "extreme aspect ratio; check final-size readability"})
    if content.any() and min(value for key, value in margins.items() if key.endswith("_rate")) < 0.002:
        warnings.append({"severity": "critical", "message": "visible content nearly touches an image edge; clipping risk"})
    if coverage < 0.01:
        warnings.append({"severity": "minor", "message": "very low content coverage; verify that blank space is intentional"})
    if coverage > 0.85:
        warnings.append({"severity": "major", "message": "very high content coverage; figure may be crowded"})
    content_luminance = luminance(rgb)[content]
    if len(content_luminance) >= 100 and float(np.quantile(content_luminance, 0.95) - np.quantile(content_luminance, 0.05)) < 0.08:
        warnings.append({"severity": "minor", "message": "low contrast among visible marks; inspect text and line legibility"})
    alpha = np.asarray(rgba)[..., 3]
    return {
        "path": str(path), "format": opened.format, "mode": opened.mode,
        "width_px": width, "height_px": height, "aspect_ratio": aspect,
        "file_size_bytes": path.stat().st_size, "content_coverage": coverage,
        "background_rgb": [int(round(value)) for value in background],
        "margins": margins, "transparent_pixel_rate": float((alpha < 255).mean()),
        "warnings": warnings,
    }


def inspect_code(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lower = text.lower()
    warnings: list[dict[str, str]] = []
    def warn(severity: str, message: str) -> None:
        warnings.append({"severity": severity, "message": message})
    if "savefig" not in lower:
        warn("critical", "no savefig call detected")
    if not any(extension in lower for extension in (".pdf", ".svg")):
        warn("minor", "no vector export path detected")
    if any(token in lower for token in ("cmap='jet'", 'cmap="jet"', "cmap='rainbow'", 'cmap="rainbow"')):
        warn("major", "jet or rainbow colormap detected")
    if "projection='3d'" in lower or 'projection="3d"' in lower:
        warn("major", "3D axes detected; verify that the data are inherently three-dimensional")
    if "twinx(" in lower or "twiny(" in lower:
        warn("major", "dual axes detected; verify that no clearer alternative exists")
    if lower.count("legend(") > 1:
        warn("minor", "multiple legend calls detected; check for repeated legends")
    if "legend(" in lower and any(token in lower for token in ("annotate(", ".text(", "bar_label(")):
        warn("minor", "legend and direct labels both detected; inspect for duplicated information")
    if "constrained_layout=true" in lower and "tight_layout(" in lower:
        warn("minor", "both constrained_layout and tight_layout are used")
    if "np.random" in lower and "seed(" not in lower and "default_rng(" not in lower:
        warn("major", "randomness detected without an obvious seed")
    return {"path": str(path), "line_count": len(text.splitlines()), "warnings": warnings}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="PNG, JPEG, WEBP, or TIFF figure")
    parser.add_argument("--code", type=Path, help="optional Python plotting source")
    parser.add_argument("--output", type=Path, help="JSON output path; print to stdout when omitted")
    parser.add_argument("--strict", action="store_true", help="exit 2 when a critical lint warning is present")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    image = args.image.expanduser().resolve()
    if not image.is_file():
        print(f"error: image not found: {image}", file=sys.stderr)
        return 2
    try:
        image_report = inspect_image(image)
        code_report = None
        if args.code:
            code = args.code.expanduser().resolve()
            if not code.is_file():
                raise FileNotFoundError(f"code not found: {code}")
            code_report = inspect_code(code)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    warnings = list(image_report["warnings"]) + (list(code_report["warnings"]) if code_report else [])
    counts = {severity: sum(item["severity"] == severity for item in warnings) for severity in ("critical", "major", "minor")}
    report = {
        "image": image_report,
        "code": code_report,
        "summary": {"severity_counts": counts, "note": "Heuristic lint; verify source data and inspect the final rendered image."},
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 2 if args.strict and counts["critical"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
