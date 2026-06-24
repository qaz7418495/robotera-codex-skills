#!/usr/bin/env python3
import argparse
import csv
import html
import json
import shutil
from pathlib import Path
from typing import Any


CSV_ARTIFACTS = [
    "joint_command_samples.csv",
    "joint_feedback_samples.csv",
    "joint_temperature_samples.csv",
    "joint_stats.csv",
    "left_right_compare.csv",
]
FINGER_MARKERS = (
    "_thumb_",
    "_index_",
    "_mid_",
    "_ring_",
    "_pinky_",
)


def is_finger_joint(joint: str) -> bool:
    return joint.startswith("left_hand_") or joint.startswith("right_hand_") or any(marker in joint for marker in FINGER_MARKERS)


def esc(value: Any) -> str:
    return html.escape(str(value), quote=False)


def to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def table(headers: list[str], rows: list[list[Any]]) -> str:
    parts = ["<table><thead><tr>"]
    for header in headers:
        parts.append(f'<th background-color="light-gray">{esc(header)}</th>')
    parts.append("</tr></thead><tbody>")
    for row in rows:
        parts.append("<tr>")
        for cell in row:
            parts.append(f"<td>{esc(cell)}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def fmt_num(value: Any, default: str = "") -> str:
    num = to_float(value)
    if num is None:
        return default
    return f"{num:.4g}"


def metric_rows(rows: list[dict[str, str]]) -> list[list[str]]:
    out = []
    for row in rows:
        out.append([
            row.get("joint", ""),
            row.get("source", ""),
            row.get("field", ""),
            fmt_num(row.get("min")),
            fmt_num(row.get("max")),
            fmt_num(row.get("abs_mean")),
            fmt_num(row.get("positive_abs_mean")),
            fmt_num(row.get("negative_abs_mean")),
            fmt_num(row.get("range")),
        ])
    return out


def compare_rows(rows: list[dict[str, str]]) -> list[list[str]]:
    out = []
    for row in rows:
        out.append([
            row.get("pair", ""),
            row.get("source", ""),
            row.get("field", ""),
            row.get("left_joint", ""),
            row.get("right_joint", ""),
            fmt_num(row.get("left_min")),
            fmt_num(row.get("right_min")),
            fmt_num(row.get("delta_min")),
            fmt_num(row.get("left_max")),
            fmt_num(row.get("right_max")),
            fmt_num(row.get("delta_max")),
            fmt_num(row.get("left_mean")),
            fmt_num(row.get("right_mean")),
            fmt_num(row.get("delta_mean")),
            fmt_num(row.get("left_abs_mean")),
            fmt_num(row.get("right_abs_mean")),
            fmt_num(row.get("delta_abs_mean")),
            fmt_num(row.get("left_positive_abs_mean")),
            fmt_num(row.get("right_positive_abs_mean")),
            fmt_num(row.get("delta_positive_abs_mean")),
            fmt_num(row.get("left_negative_abs_mean")),
            fmt_num(row.get("right_negative_abs_mean")),
            fmt_num(row.get("delta_negative_abs_mean")),
            fmt_num(row.get("left_range")),
            fmt_num(row.get("right_range")),
            fmt_num(row.get("delta_range")),
            fmt_num(row.get("left_slope_per_second")),
            fmt_num(row.get("right_slope_per_second")),
            fmt_num(row.get("delta_slope_per_second")),
        ])
    return out


def sorted_by_range(rows: list[dict[str, str]], source: str, field: str, exclude_fingers: bool = False) -> list[dict[str, str]]:
    filtered = [
        row for row in rows
        if row.get("source") == source and row.get("field") == field and to_float(row.get("range")) is not None
    ]
    if exclude_fingers:
        filtered = [row for row in filtered if not is_finger_joint(row.get("joint", ""))]
    return sorted(filtered, key=lambda row: to_float(row.get("range")) or 0.0, reverse=True)


def stage_assets(output_dir: Path, assets_dir: Path) -> int:
    if assets_dir.exists():
        shutil.rmtree(assets_dir)
    assets_dir.mkdir(parents=True)
    for name in CSV_ARTIFACTS + ["report_manifest.json", "report.md"]:
        src = output_dir / name
        if src.exists():
            shutil.copy2(src, assets_dir / name)
    charts_src = output_dir / "charts"
    charts_dst = assets_dir / "charts"
    charts_dst.mkdir()
    for chart in sorted(charts_src.glob("*.png")):
        shutil.copy2(chart, charts_dst / chart.name)
    return len(list(charts_dst.glob("*.png")))


def build_xml(output_dir: Path, manifest: dict[str, Any], chart_count: int) -> str:
    stats_rows = read_csv(output_dir / "joint_stats.csv")
    compare = read_csv(output_dir / "left_right_compare.csv")
    compare_sorted = sorted(
        [row for row in compare if to_float(row.get("delta_range")) is not None],
        key=lambda row: abs(to_float(row.get("delta_range")) or 0.0),
        reverse=True,
    )

    requested = manifest.get("requested_duration_s")
    selected = manifest.get("selected_duration_s")
    requested_text = f"{requested / 60:.1f}min" if isinstance(requested, (int, float)) else "未指定"
    selected_text = f"{selected / 60:.1f}min" if isinstance(selected, (int, float)) else "未知"
    duration_note = ""
    if isinstance(requested, (int, float)) and isinstance(selected, (int, float)) and selected + 1 < requested:
        duration_note = f"用户请求 {requested_text} 数据；该包可分析数据约 {selected_text}，本报告按可用数据分析。"

    missing = manifest.get("missing_required_topics", [])
    empty = manifest.get("empty_analyzed_topics", [])
    caveats = []
    if duration_note:
        caveats.append(duration_note)
    if missing:
        caveats.append("缺失 topic：" + ", ".join(missing))
    if empty:
        caveats.append("空 topic/无样本：" + ", ".join(empty))
    caveats.append("手指关节力矩单位与整机关节不同，已从左右对比和整机 Effort 排名中排除。")
    if not caveats:
        caveats.append("未发现影响报告生成的必要数据缺口。")

    xml = [f"<title>{esc(manifest['report_title'])}</title>"]
    xml.append(
        '<callout emoji="📌" background-color="light-blue" border-color="blue">'
        "<p><b>结论摘要：</b>本报告为 MCAP 关节模组自动分析报告，已包含 CSV 中间产物、统计摘要、左右对称关节对比，以及每关节 2x2 PNG 图。"
        f"{esc(' '.join(caveats))}</p></callout>"
    )
    xml.append("<h1>一、输入与范围</h1>")
    xml.append(table(["项目", "值"], [
        ["MCAP文件", manifest.get("mcap_name", manifest.get("mcap", ""))],
        ["模型识别", manifest.get("model", "")],
        ["请求时长", requested_text],
        ["实际分析时长", selected_text],
        ["起止时间", f"{manifest.get('selected_start_iso', '')} - {manifest.get('selected_end_iso', '')}"],
        ["采样频率", f"{manifest.get('sample_hz', '')} Hz"],
        ["命令Topic", manifest.get("topics", {}).get("command", "")],
        ["反馈Topic", manifest.get("topics", {}).get("feedback", "")],
        ["温度Topic", manifest.get("topics", {}).get("temperature", "")],
    ]))
    xml.append("<h1>二、产物清单</h1>")
    xml.append(table(["产物", "说明"], [
        ["joint_command_samples.csv", "命令 topic 采样明细，作为附件插入"],
        ["joint_feedback_samples.csv", "反馈 topic 采样明细，作为附件插入"],
        ["joint_temperature_samples.csv", "温度 topic 采样明细，作为附件插入；缺数据时仅有表头"],
        ["joint_stats.csv", "每关节统计：count/min/max/mean/abs_mean/positive_abs_mean/negative_abs_mean/std/range/slope，作为附件插入"],
        ["left_right_compare.csv", "左右相同位置对比统计，作为附件插入"],
        [f"{chart_count} 张 PNG", "每个关节一张 2x2 图，逐张插入本文档"],
    ]))
    xml.append("<h1>三、关键统计摘要</h1>")
    xml.append("<h2>反馈位置变化范围（全部关节）</h2>")
    xml.append(table(["joint", "source", "field", "min", "max", "abs_mean", "positive_abs_mean", "negative_abs_mean", "range"], metric_rows(sorted_by_range(stats_rows, "feedback", "position"))))
    xml.append("<h2>反馈速度变化范围（全部关节）</h2>")
    xml.append(table(["joint", "source", "field", "min", "max", "abs_mean", "positive_abs_mean", "negative_abs_mean", "range"], metric_rows(sorted_by_range(stats_rows, "feedback", "velocity"))))
    xml.append("<h2>整机关节反馈 Effort 变化范围（全部关节，不含手指）</h2>")
    xml.append(table(["joint", "source", "field", "min", "max", "abs_mean", "positive_abs_mean", "negative_abs_mean", "range"], metric_rows(sorted_by_range(stats_rows, "feedback", "effort", exclude_fingers=True))))
    xml.append("<h2>命令位置变化范围（全部关节）</h2>")
    xml.append(table(["joint", "source", "field", "min", "max", "abs_mean", "positive_abs_mean", "negative_abs_mean", "range"], metric_rows(sorted_by_range(stats_rows, "command", "position"))))
    xml.append("<h1>四、左右对称关节对比</h1>")
    xml.append("<p>下表为左右相同位置的全量对比数据，按 range 差异绝对值排序；手指关节已按约束排除。温升斜率使用 slope_per_second 字段，仅在温度数据存在时有值。</p>")
    xml.append(table([
        "pair", "source", "field", "left_joint", "right_joint",
        "left_min", "right_min", "delta_min",
        "left_max", "right_max", "delta_max",
        "left_mean", "right_mean", "delta_mean",
        "left_abs_mean", "right_abs_mean", "delta_abs_mean",
        "left_pos_abs_mean", "right_pos_abs_mean", "delta_pos_abs_mean",
        "left_neg_abs_mean", "right_neg_abs_mean", "delta_neg_abs_mean",
        "left_range", "right_range", "delta_range",
        "left_slope/s", "right_slope/s", "delta_slope/s",
    ], compare_rows(compare_sorted)))
    xml.append("<h1>五、注意事项</h1>")
    for caveat in caveats:
        xml.append(f'<callout emoji="⚠️" background-color="light-yellow" border-color="yellow"><p>{esc(caveat)}</p></callout>')
    xml.append("<h1>六、附件与图表</h1>")
    xml.append("<p>本节后续由流程插入 CSV 附件和每关节 2x2 PNG 图。图片 caption 使用关节文件名。</p>")
    return "\n".join(xml) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Feishu XML and staged assets from an MCAP joint report output directory.")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--assets-dir", type=Path, default=None)
    parser.add_argument("--xml-output", type=Path, default=None)
    args = parser.parse_args()

    manifest_path = args.output_dir / "report_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assets_dir = args.assets_dir or (args.output_dir / "feishu_assets")
    xml_output = args.xml_output or (args.output_dir / "feishu_report.xml")

    chart_count = stage_assets(args.output_dir, assets_dir)
    xml_output.write_text(build_xml(args.output_dir, manifest, chart_count), encoding="utf-8")
    print(json.dumps({
        "report_title": manifest["report_title"],
        "xml_output": str(xml_output),
        "assets_dir": str(assets_dir),
        "csv_files": CSV_ARTIFACTS,
        "chart_count": chart_count,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
