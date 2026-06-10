#!/usr/bin/env python
"""从曲线图中提取代表趋势点，并输出可复制到 Excel 的 TSV 表格。"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw


@dataclass
class LinearMap:
    pixel_1: float
    value_1: float
    pixel_2: float
    value_2: float

    def value_at(self, pixel: float) -> float:
        if self.pixel_1 == self.pixel_2:
            raise ValueError("校准点像素位置不能相同")
        scale = (self.value_2 - self.value_1) / (self.pixel_2 - self.pixel_1)
        return self.value_1 + (pixel - self.pixel_1) * scale

    def pixel_at(self, value: float) -> float:
        if self.value_1 == self.value_2:
            raise ValueError("校准点数值不能相同")
        scale = (self.pixel_2 - self.pixel_1) / (self.value_2 - self.value_1)
        return self.pixel_1 + (value - self.value_1) * scale


def build_map(axis: dict[str, Any], axis_name: str) -> LinearMap:
    ticks = axis.get("ticks", [])
    if len(ticks) < 2:
        raise ValueError(f"{axis_name} 至少需要两个校准刻度")
    return LinearMap(
        float(ticks[0]["pixel"]),
        float(ticks[0]["value"]),
        float(ticks[1]["pixel"]),
        float(ticks[1]["value"]),
    )


def make_dark_mask(image: Image.Image, roi: list[int], threshold: int) -> tuple[np.ndarray, tuple[int, int]]:
    left, top, right, bottom = [int(v) for v in roi]
    crop = image.crop((left, top, right, bottom)).convert("L")
    gray = np.asarray(crop)
    mask = gray <= threshold

    if mask.size:
        row_density = mask.mean(axis=1)
        col_density = mask.mean(axis=0)
        mask[row_density > 0.55, :] = False
        mask[:, col_density > 0.55] = False
    return mask, (left, top)


def median_or_nan(values: np.ndarray) -> float:
    if values.size == 0:
        return float("nan")
    return float(np.median(values))


def sample_shared_series(
    image: Image.Image,
    series: dict[str, Any],
    shared_axis: dict[str, Any],
    shared_map: LinearMap,
    threshold: int,
) -> list[tuple[float, str]]:
    mask, (left, top) = make_dark_mask(image, series["roi"], int(series.get("threshold", threshold)))
    orientation = shared_axis.get("orientation", "y")
    sample_values = shared_axis.get("sample_values")

    if not sample_values:
        raise ValueError("shared_axis.sample_values 不能为空")

    value_axis = build_map(series, series.get("column", "曲线"))
    half_window = int(series.get("window", 3))
    out: list[tuple[float, str]] = []

    for sample_value in sample_values:
        sample_pixel = shared_map.pixel_at(float(sample_value))
        local = int(round(sample_pixel - top if orientation == "y" else sample_pixel - left))

        if orientation == "y":
            lo = max(0, local - half_window)
            hi = min(mask.shape[0], local + half_window + 1)
            _, xs = np.where(mask[lo:hi, :])
            pixel = median_or_nan(xs + left)
        else:
            lo = max(0, local - half_window)
            hi = min(mask.shape[1], local + half_window + 1)
            ys, _ = np.where(mask[:, lo:hi])
            pixel = median_or_nan(ys + top)

        if math.isnan(pixel):
            out.append((float("nan"), "需人工复核"))
        else:
            out.append((value_axis.value_at(pixel), "可靠"))
    return out


def reduce_points(points: list[tuple[float, float]], target_count: int) -> list[tuple[float, float]]:
    clean = [(x, y) for x, y in points if not (math.isnan(x) or math.isnan(y))]
    if len(clean) <= target_count:
        return clean
    keep = {0, len(clean) - 1}
    for i in range(1, len(clean) - 1):
        x0, y0 = clean[i - 1]
        x1, y1 = clean[i]
        x2, y2 = clean[i + 1]
        score = abs((x2 - x0) * (y0 - y1) - (x0 - x1) * (y2 - y0))
        if score > 0:
            keep.add(i)
    if len(keep) < target_count:
        step = max(1, len(clean) // target_count)
        keep.update(range(0, len(clean), step))
    chosen = sorted(keep)
    if len(chosen) > target_count:
        interior = chosen[1:-1]
        stride = len(interior) / max(1, target_count - 2)
        chosen = [0] + [interior[int(i * stride)] for i in range(target_count - 2)] + [len(clean) - 1]
    return [clean[i] for i in sorted(set(chosen))]


def sample_long_series(
    image: Image.Image,
    series: dict[str, Any],
    x_map: LinearMap,
    y_map: LinearMap,
    threshold: int,
    target_count: int,
) -> list[tuple[float, float, str]]:
    mask, (left, top) = make_dark_mask(image, series["roi"], int(series.get("threshold", threshold)))
    ys, xs = np.where(mask)
    if xs.size == 0:
        return []
    pixels = sorted(zip(xs + left, ys + top), key=lambda p: (p[1], p[0]))
    raw = [(x_map.value_at(px), y_map.value_at(py)) for px, py in pixels]
    return [(x, y, "可靠") for x, y in reduce_points(raw, target_count)]


def connected_components(mask: np.ndarray) -> list[list[tuple[int, int]]]:
    height, width = mask.shape
    seen = np.zeros(mask.shape, dtype=bool)
    components: list[list[tuple[int, int]]] = []

    for y in range(height):
        for x in range(width):
            if not mask[y, x] or seen[y, x]:
                continue
            stack = [(x, y)]
            seen[y, x] = True
            component: list[tuple[int, int]] = []
            while stack:
                cx, cy = stack.pop()
                component.append((cx, cy))
                for ny in range(max(0, cy - 1), min(height, cy + 2)):
                    for nx in range(max(0, cx - 1), min(width, cx + 2)):
                        if mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((nx, ny))
            components.append(component)
    return components


def sample_point_series(
    image: Image.Image,
    series: dict[str, Any],
    x_map: LinearMap,
    y_map: LinearMap,
    threshold: int,
) -> list[tuple[float, float, str]]:
    mask, (left, top) = make_dark_mask(image, series["roi"], int(series.get("threshold", threshold)))
    min_pixels = int(series.get("min_pixels", 3))
    max_pixels = int(series.get("max_pixels", 300))
    points: list[tuple[float, float, str]] = []

    for component in connected_components(mask):
        size = len(component)
        if size < min_pixels or size > max_pixels:
            continue
        xs = np.array([p[0] for p in component], dtype=float)
        ys = np.array([p[1] for p in component], dtype=float)
        width = float(xs.max() - xs.min() + 1)
        height = float(ys.max() - ys.min() + 1)
        if width > 25 or height > 25:
            continue
        px = float(xs.mean() + left)
        py = float(ys.mean() + top)
        points.append((x_map.value_at(px), y_map.value_at(py), "可靠"))

    return sorted(points, key=lambda item: (item[0], item[1]))


def format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        text = f"{value:.6f}".rstrip("0").rstrip(".")
        return "0" if text == "-0" else text
    return str(value)


def clean_name(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    if not text or set(text) <= {"?"}:
        return fallback
    return text


def rows_to_tsv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "备注\n未提取到数据，需人工复核"
    headers = list(rows[0].keys())
    lines = ["\t".join(headers)]
    for row in rows:
        lines.append("\t".join(format_value(row.get(header)) for header in headers))
    return "\n".join(lines)


def draw_overlay(image: Image.Image, rows: list[dict[str, Any]], config: dict[str, Any], path: Path) -> None:
    canvas = image.convert("RGB").copy()
    draw = ImageDraw.Draw(canvas)
    colors = ["red", "blue", "green", "purple", "orange", "cyan"]

    if config.get("mode", "shared_axis") == "shared_axis":
        shared = config["shared_axis"]
        shared_map = build_map(shared, "共享轴")
        orientation = shared.get("orientation", "y")
        for idx, series in enumerate(config.get("series", [])):
            column = series.get("column", f"曲线{idx + 1}")
            value_map = build_map(series, column)
            color = colors[idx % len(colors)]
            for row in rows:
                if row.get(column) in (None, "", "需人工复核"):
                    continue
                shared_value = float(row[shared["column"]])
                curve_value = float(row[column])
                if orientation == "y":
                    x = value_map.pixel_at(curve_value)
                    y = shared_map.pixel_at(shared_value)
                else:
                    x = shared_map.pixel_at(shared_value)
                    y = value_map.pixel_at(curve_value)
                draw.ellipse((x - 3, y - 3, x + 3, y + 3), outline=color, width=2)
    elif config.get("mode") in {"long", "points"}:
        x_map = build_map(config["x_axis"], "横坐标轴")
        y_map = build_map(config["y_axis"], "纵坐标轴")
        for row in rows:
            if row.get("横坐标数值") in (None, "") or row.get("纵坐标数值") in (None, ""):
                continue
            x = x_map.pixel_at(float(row["横坐标数值"]))
            y = y_map.pixel_at(float(row["纵坐标数值"]))
            draw.ellipse((x - 4, y - 4, x + 4, y + 4), outline="red", width=2)

    canvas.save(path)


def collect_rows(
    image: Image.Image,
    config: dict[str, Any],
    threshold: int,
    target_count: int,
) -> list[dict[str, Any]]:
    mode = config.get("mode", "shared_axis")

    if mode == "shared_axis":
        shared_axis = config["shared_axis"]
        shared_map = build_map(shared_axis, "共享轴")
        sample_values = [float(v) for v in shared_axis.get("sample_values", [])]
        if not sample_values:
            raise ValueError("shared_axis.sample_values 不能为空")

        sampled_by_series = {
            s.get("column", f"曲线{i + 1}"): sample_shared_series(image, s, shared_axis, shared_map, threshold)
            for i, s in enumerate(config.get("series", []))
        }
        rows: list[dict[str, Any]] = []
        for idx, shared_value in enumerate(sample_values):
            row: dict[str, Any] = {shared_axis["column"]: shared_value}
            notes = []
            for column, values in sampled_by_series.items():
                value, note = values[idx]
                row[column] = None if math.isnan(value) else round(value, 6)
                if note != "可靠":
                    notes.append(f"{column}:{note}")
            row["备注"] = "可靠" if not notes else "；".join(notes)
            rows.append(row)
        return rows

    if mode == "long":
        x_map = build_map(config["x_axis"], "横坐标轴")
        y_map = build_map(config["y_axis"], "纵坐标轴")
        rows = []
        for series in config.get("series", []):
            for x, y, note in sample_long_series(image, series, x_map, y_map, threshold, target_count):
                rows.append(
                    {
                        "曲线名称": clean_name(series.get("name"), "曲线"),
                        "横坐标数值": round(x, 6),
                        "纵坐标数值": round(y, 6),
                        "备注": note,
                    }
                )
        return rows

    if mode == "points":
        x_map = build_map(config["x_axis"], "横坐标轴")
        y_map = build_map(config["y_axis"], "纵坐标轴")
        rows = []
        point_index = 1
        for series in config.get("series", []):
            for x, y, note in sample_point_series(image, series, x_map, y_map, threshold):
                rows.append(
                    {
                        "点位编号": point_index,
                        "曲线名称": clean_name(series.get("name"), "点位"),
                        "横坐标数值": round(x, 6),
                        "纵坐标数值": round(y, 6),
                        "备注": note,
                    }
                )
                point_index += 1
        return rows

    raise ValueError("mode 只能是 shared_axis、long 或 points")


def run(
    image_path: Path,
    config_path: Path,
    outdir: Path,
    threshold: int,
    target_count: int,
    overlay: bool,
    tsv_path: Path | None,
) -> None:
    image = Image.open(image_path).convert("RGB")
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    rows = collect_rows(image, config, threshold, target_count)

    if overlay:
        outdir.mkdir(parents=True, exist_ok=True)
        draw_overlay(image, rows, config, outdir / "overlay_check.png")

    tsv = rows_to_tsv(rows)
    if tsv_path is not None:
        tsv_path.parent.mkdir(parents=True, exist_ok=True)
        tsv_path.write_text(tsv + "\n", encoding="utf-8")
    print(tsv)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="从曲线图中提取代表趋势点，并输出可复制到 Excel 的 TSV 表格。")
    parser.add_argument("--image", required=True, type=Path, help="输入图片路径")
    parser.add_argument("--config", required=True, type=Path, help="校准 JSON 路径")
    parser.add_argument("--outdir", required=True, type=Path, help="叠加检查图输出目录")
    parser.add_argument("--threshold", type=int, default=150, help="深色像素阈值")
    parser.add_argument("--points", type=int, default=15, help="长表模式每条曲线保留的目标点数")
    parser.add_argument("--tsv", type=Path, help="可选：写出 UTF-8 TSV 表格文件")
    parser.add_argument("--no-overlay", action="store_true", help="不生成叠加检查图")
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    run(args.image, args.config, args.outdir, args.threshold, args.points, not args.no_overlay, args.tsv)


if __name__ == "__main__":
    main()
