#!/usr/bin/env python3
import argparse
import csv
import dataclasses
import json
import math
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mcap.reader import make_reader
from mcap_ros2.decoder import DecoderFactory


M7_JOINTS = [
    "left_shoulder_pitch_joint", "right_shoulder_pitch_joint",
    "left_shoulder_roll_joint", "right_shoulder_roll_joint",
    "left_arm_yaw_joint", "right_arm_yaw_joint",
    "left_elbow_pitch_joint", "right_elbow_pitch_joint",
    "left_elbow_yaw_joint", "right_elbow_yaw_joint",
    "left_wrist_pitch_joint", "right_wrist_pitch_joint",
    "left_wrist_roll_joint", "right_wrist_roll_joint",
    "waist_pitch_joint", "waist_yaw_joint", "waist_roll_joint",
    "neck_yaw_joint", "neck_pitch_joint",
    "left_hand_palm", "right_hand_palm",
]

L3_EXTRA_JOINTS = [
    "left_hip_yaw_joint", "right_hip_yaw_joint",
    "left_hip_roll_joint", "right_hip_roll_joint",
    "left_hip_pitch_joint", "right_hip_pitch_joint",
    "left_knee_joint", "right_knee_joint",
    "left_ankle_pitch_joint", "right_ankle_pitch_joint",
    "left_ankle_roll_joint", "right_ankle_roll_joint",
]

MODEL_JOINTS = {
    "M7": M7_JOINTS,
    "L3": M7_JOINTS + L3_EXTRA_JOINTS,
}

FIELDS = ("position", "velocity", "effort", "feedforward", "kp", "kd")
REQUIRED_TOPICS = (
    "/hybrid_body_controller/commands",
    "/joint_states",
    "/temperature",
)
FINGER_MARKERS = (
    "_thumb_",
    "_index_",
    "_mid_",
    "_ring_",
    "_pinky_",
)


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")


def value_at(values: Any, index: int) -> float | None:
    if values is None or index >= len(values):
        return None
    value = values[index]
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
        return float(value)
    return None


def numeric_list(value: Any) -> list[float] | None:
    if isinstance(value, (list, tuple)) and value:
        result = []
        for item in value:
            if not isinstance(item, (int, float)) or isinstance(item, bool):
                return None
            result.append(float(item))
        return result
    return None


def find_numeric_sequence(decoded: Any) -> list[float] | None:
    preferred = ("temperature", "temperatures", "data", "values", "value")
    for name in preferred:
        if hasattr(decoded, name):
            seq = numeric_list(getattr(decoded, name))
            if seq:
                return seq
    if dataclasses.is_dataclass(decoded):
        for field in dataclasses.fields(decoded):
            seq = numeric_list(getattr(decoded, field.name))
            if seq:
                return seq
    return None


def extract_names(decoded: Any) -> list[str]:
    for attr in ("name", "joint_name", "joint_names", "names"):
        if hasattr(decoded, attr):
            names = getattr(decoded, attr)
            if isinstance(names, (list, tuple)):
                return [str(name) for name in names]
    return []


def msg_to_joint_values(decoded: Any) -> dict[str, dict[str, float]]:
    names = extract_names(decoded)
    out: dict[str, dict[str, float]] = {}
    for i, name in enumerate(names):
        joint = str(name)
        values: dict[str, float] = {}
        for field in FIELDS:
            if hasattr(decoded, field):
                val = value_at(getattr(decoded, field), i)
                if val is not None:
                    values[field] = val
        if values:
            out[joint] = values
    return out


def add_sample(samples: dict[str, list[tuple[float, float]]], key: str, t: float, value: float | None) -> None:
    if value is not None:
        samples[key].append((t, value))


def add_sample_with_time(
    samples: dict[str, list[dict[str, Any]]],
    key: str,
    log_time_ns: int,
    rel_s: float,
    value: float | None,
    tz_hours: int,
) -> None:
    if value is None:
        return
    samples[key].append({
        "time": fmt_iso(log_time_ns, tz_hours),
        "log_time_ns": log_time_ns,
        "t": rel_s,
        "value": value,
    })


def should_keep(last_t: dict[str, float], key: str, t: float, period: float) -> bool:
    prev = last_t.get(key)
    if prev is not None and t - prev < period:
        return False
    last_t[key] = t
    return True


def stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {
            "count": 0,
            "min": "",
            "max": "",
            "mean": "",
            "abs_mean": "",
            "positive_abs_mean": "",
            "negative_abs_mean": "",
            "std": "",
            "range": "",
        }
    n = len(values)
    mean = sum(values) / n
    positives = [v for v in values if v > 0]
    negatives = [v for v in values if v < 0]
    var = sum((v - mean) ** 2 for v in values) / n
    return {
        "count": n,
        "min": min(values),
        "max": max(values),
        "mean": mean,
        "abs_mean": sum(abs(v) for v in values) / n,
        "positive_abs_mean": (sum(abs(v) for v in positives) / len(positives)) if positives else "",
        "negative_abs_mean": (sum(abs(v) for v in negatives) / len(negatives)) if negatives else "",
        "std": math.sqrt(var),
        "range": max(values) - min(values),
    }


def slope(points: list[dict[str, Any]]) -> float | str:
    if len(points) < 2:
        return ""
    xs = [p["t"] for p in points]
    ys = [p["value"] for p in points]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    den = sum((x - x_mean) ** 2 for x in xs)
    if den == 0:
        return ""
    return sum((point["t"] - x_mean) * (point["value"] - y_mean) for point in points) / den


def write_signal_csv(path: Path, samples: dict[str, list[dict[str, Any]]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["signal", "time", "log_time_ns", "t", "value"])
        for signal in sorted(samples):
            for point in samples[signal]:
                writer.writerow([
                    signal,
                    point["time"],
                    point["log_time_ns"],
                    f"{point['t']:.6f}",
                    f"{point['value']:.9g}",
                ])


def write_stats_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def pairs_for(joints: list[str]) -> list[tuple[str, str, str]]:
    joint_set = set(joints)
    pairs = []
    for left in joints:
        if not left.startswith("left_"):
            continue
        if is_finger_joint(left):
            continue
        right = "right_" + left[len("left_"):]
        if right in joint_set and not is_finger_joint(right):
            pairs.append((left[len("left_"):], left, right))
    return pairs


def is_finger_joint(joint: str) -> bool:
    return joint.startswith("left_hand_") or joint.startswith("right_hand_") or any(marker in joint for marker in FINGER_MARKERS)


def plot_series(ax, points: list[dict[str, Any]], label: str, color: str) -> None:
    if not points:
        ax.text(0.5, 0.5, "no data", transform=ax.transAxes, ha="center", va="center")
        return
    xs = [datetime.fromisoformat(p["time"]).replace(tzinfo=None) for p in points]
    ys = [p["value"] for p in points]
    ax.plot(xs, ys, label=label, linewidth=0.9, color=color)


def point_times(*series_groups: dict[str, list[dict[str, Any]]]) -> list[datetime]:
    times: list[datetime] = []
    for group in series_groups:
        for points in group.values():
            for point in points:
                times.append(datetime.fromisoformat(point["time"]).replace(tzinfo=None))
    return times


def chart_joint(
    joint: str,
    output: Path,
    feedback: dict[str, list[dict[str, Any]]],
    commands: dict[str, list[dict[str, Any]]],
    temps: dict[str, list[dict[str, Any]]],
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(16, 9), sharex=False)
    fig.suptitle(joint, fontsize=14)
    all_times = point_times(feedback, commands, temps)
    xlim = None
    if all_times:
        start = min(all_times)
        end = max(all_times)
        if start == end:
            end = start + timedelta(seconds=1)
        xlim = (start, end)

    ax = axes[0][0]
    plot_series(ax, feedback.get(f"{joint}.effort", []), "feedback effort", "#b6b51c")
    ax.set_title("Effort")
    ax.set_ylabel("effort")

    ax = axes[0][1]
    plot_series(ax, commands.get(f"{joint}.position", []), "command position", "#20b8c7")
    plot_series(ax, feedback.get(f"{joint}.position", []), "feedback position", "#1f77b4")
    ax.set_title("Command vs Feedback Position")
    ax.set_ylabel("rad")

    ax = axes[1][0]
    plot_series(ax, temps.get(f"{joint}.driver_temperature", []), "driver temperature", "#22c55e")
    plot_series(ax, temps.get(f"{joint}.motor_temperature", []), "motor temperature", "#f97316")
    ax.set_title("Temperature")
    ax.set_ylabel("degC")

    ax = axes[1][1]
    plot_series(ax, feedback.get(f"{joint}.velocity", []), "feedback velocity", "#dc2626")
    ax.set_title("Velocity")
    ax.set_ylabel("rad/s")

    for ax in axes.flat:
        ax.grid(True, alpha=0.3, linestyle=":")
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(loc="best", fontsize=8)
        ax.set_xlabel("actual time")
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M:%S"))
        if xlim:
            ax.set_xlim(*xlim)
        ax.tick_params(axis="x", labelrotation=0, labelbottom=True)
    plt.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(output, dpi=170, bbox_inches="tight")
    plt.close(fig)


def detect_model(seen_joints: set[str], requested: str) -> str:
    if requested != "auto":
        return requested
    if any(joint in seen_joints for joint in L3_EXTRA_JOINTS):
        return "L3"
    return "M7"


def fmt_time(ns: int, tz_hours: int) -> str:
    tz = timezone(timedelta(hours=tz_hours))
    return datetime.fromtimestamp(ns / 1e9, tz).strftime("%Y%m%d_%H%M%S")


def fmt_iso(ns: int, tz_hours: int) -> str:
    tz = timezone(timedelta(hours=tz_hours))
    return datetime.fromtimestamp(ns / 1e9, tz).isoformat(timespec="milliseconds")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate joint-module CSVs and 2x2 PNG charts from ROS2 MCAP.")
    parser.add_argument("mcap", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", choices=["auto", "M7", "L3"], default="auto")
    parser.add_argument("--command-topic", default="/hybrid_body_controller/commands")
    parser.add_argument("--feedback-topic", default="/joint_states")
    parser.add_argument("--temperature-topic", default="/temperature")
    parser.add_argument("--sample-hz", type=float, default=10.0)
    parser.add_argument("--start-sec", type=float, default=None)
    parser.add_argument("--end-sec", type=float, default=None)
    parser.add_argument("--tz-hours", type=int, default=8)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    charts_dir = args.output_dir / "charts"
    charts_dir.mkdir(exist_ok=True)
    period = 1.0 / args.sample_hz if args.sample_hz > 0 else 0.0

    feedback: dict[str, list[dict[str, Any]]] = defaultdict(list)
    commands: dict[str, list[dict[str, Any]]] = defaultdict(list)
    temps: dict[str, list[dict[str, Any]]] = defaultdict(list)
    last_keep: dict[str, float] = {}
    seen_joints: set[str] = set()
    first_ns = None
    start_ns = end_ns = None
    selected_start_ns = None
    selected_end_ns = None
    topic_counts: dict[str, int] = defaultdict(int)
    all_topics: set[str] = set()

    with args.mcap.open("rb") as f:
        reader = make_reader(f, decoder_factories=[DecoderFactory()])
        summary = reader.get_summary()
        start_ns = summary.statistics.message_start_time
        end_ns = summary.statistics.message_end_time
        topics = [args.command_topic, args.feedback_topic, args.temperature_topic]
        for channel in summary.channels.values():
            all_topics.add(channel.topic)

        for schema, channel, message, decoded in reader.iter_decoded_messages(topics=topics):
            if first_ns is None:
                first_ns = summary.statistics.message_start_time
            rel_s = (message.log_time - first_ns) / 1e9
            if args.start_sec is not None and rel_s < args.start_sec:
                continue
            if args.end_sec is not None and rel_s > args.end_sec:
                break
            if selected_start_ns is None:
                selected_start_ns = message.log_time
            selected_end_ns = message.log_time
            topic_counts[channel.topic] += 1

            if channel.topic in (args.command_topic, args.feedback_topic):
                joint_values = msg_to_joint_values(decoded)
                for joint, values in joint_values.items():
                    seen_joints.add(joint)
                    target = commands if channel.topic == args.command_topic else feedback
                    for field, value in values.items():
                        key = f"{joint}.{field}"
                        if period == 0 or should_keep(last_keep, f"{channel.topic}:{key}", rel_s, period):
                            add_sample_with_time(target, key, message.log_time, rel_s, value, args.tz_hours)
                continue

            if channel.topic == args.temperature_topic:
                seq = find_numeric_sequence(decoded)
                if not seq:
                    continue
                names = extract_names(decoded)
                if names and len(names) * 2 <= len(seq):
                    temp_joints = names
                else:
                    model = detect_model(seen_joints, args.model)
                    temp_joints = MODEL_JOINTS[model]
                for i, joint in enumerate(temp_joints):
                    driver_i = 2 * i
                    motor_i = 2 * i + 1
                    if driver_i >= len(seq):
                        break
                    seen_joints.add(joint)
                    if period == 0 or should_keep(last_keep, f"{channel.topic}:{joint}", rel_s, period):
                        add_sample_with_time(temps, f"{joint}.driver_temperature", message.log_time, rel_s, seq[driver_i], args.tz_hours)
                        if motor_i < len(seq):
                            add_sample_with_time(temps, f"{joint}.motor_temperature", message.log_time, rel_s, seq[motor_i], args.tz_hours)

    model = detect_model(seen_joints, args.model)
    ordered_joints = [joint for joint in MODEL_JOINTS[model] if joint in seen_joints]
    ordered_joints += sorted(seen_joints - set(ordered_joints))

    write_signal_csv(args.output_dir / "joint_feedback_samples.csv", feedback)
    write_signal_csv(args.output_dir / "joint_command_samples.csv", commands)
    write_signal_csv(args.output_dir / "joint_temperature_samples.csv", temps)

    stat_rows = []
    for joint in ordered_joints:
        for source, sample_map in (("feedback", feedback), ("command", commands), ("temperature", temps)):
            fields = sorted(key.split(".", 1)[1] for key in sample_map if key.startswith(f"{joint}."))
            for field in fields:
                points = sample_map.get(f"{joint}.{field}", [])
                values = [point["value"] for point in points]
                row = {"joint": joint, "source": source, "field": field}
                row.update(stats(values))
                if source == "temperature":
                    row["slope_per_second"] = slope(points)
                else:
                    row["slope_per_second"] = ""
                stat_rows.append(row)
    stat_fields = [
        "joint", "source", "field", "count", "min", "max", "mean",
        "abs_mean", "positive_abs_mean", "negative_abs_mean",
        "std", "range", "slope_per_second",
    ]
    write_stats_csv(args.output_dir / "joint_stats.csv", stat_rows, stat_fields)

    stat_lookup = {(r["joint"], r["source"], r["field"]): r for r in stat_rows}
    compare_rows = []
    compare_fields = [
        "pair", "left_joint", "right_joint", "source", "field",
        "left_min", "right_min", "delta_min",
        "left_max", "right_max", "delta_max",
        "left_mean", "right_mean", "delta_mean",
        "left_abs_mean", "right_abs_mean", "delta_abs_mean",
        "left_positive_abs_mean", "right_positive_abs_mean", "delta_positive_abs_mean",
        "left_negative_abs_mean", "right_negative_abs_mean", "delta_negative_abs_mean",
        "left_range", "right_range", "delta_range",
        "left_slope_per_second", "right_slope_per_second", "delta_slope_per_second",
    ]
    for pair, left, right in pairs_for(ordered_joints):
        for source, field in [
            ("feedback", "position"),
            ("feedback", "velocity"),
            ("feedback", "effort"),
            ("command", "position"),
            ("temperature", "driver_temperature"),
            ("temperature", "motor_temperature"),
        ]:
            lrow = stat_lookup.get((left, source, field))
            rrow = stat_lookup.get((right, source, field))
            if not lrow or not rrow:
                continue
            row = {"pair": pair, "left_joint": left, "right_joint": right, "source": source, "field": field}
            for metric in ("min", "max", "mean", "abs_mean", "positive_abs_mean", "negative_abs_mean", "range", "slope_per_second"):
                lv = lrow[metric]
                rv = rrow[metric]
                row[f"left_{metric}"] = lv
                row[f"right_{metric}"] = rv
                row[f"delta_{metric}"] = (lv - rv) if isinstance(lv, (int, float)) and isinstance(rv, (int, float)) else ""
            compare_rows.append(row)
    write_stats_csv(args.output_dir / "left_right_compare.csv", compare_rows, compare_fields)

    chart_paths = []
    for joint in ordered_joints:
        output = charts_dir / f"{safe_name(joint)}_2x2.png"
        chart_joint(joint, output, feedback, commands, temps)
        chart_paths.append(output)

    report_title = f"MCAP机器人关节数据分析报告_{model}_{args.mcap.stem}"
    if start_ns:
        report_title += f"_{fmt_time(start_ns, args.tz_hours)}"
    requested_duration_s = args.end_sec - (args.start_sec or 0.0) if args.end_sec is not None else None
    bag_duration_s = (end_ns - start_ns) / 1e9 if start_ns and end_ns else None
    selected_duration_s = (selected_end_ns - selected_start_ns) / 1e9 if selected_start_ns and selected_end_ns else 0.0
    analyzed_topics = [args.command_topic, args.feedback_topic, args.temperature_topic]
    missing_required_topics = [topic for topic in analyzed_topics if topic not in all_topics]
    empty_analyzed_topics = [topic for topic in analyzed_topics if topic_counts.get(topic, 0) == 0]
    manifest = {
        "report_title": report_title,
        "mcap": str(args.mcap),
        "mcap_name": args.mcap.name,
        "mcap_size_bytes": args.mcap.stat().st_size,
        "model": model,
        "bag_start_local": fmt_time(start_ns, args.tz_hours) if start_ns else "",
        "bag_end_local": fmt_time(end_ns, args.tz_hours) if end_ns else "",
        "bag_start_iso": fmt_iso(start_ns, args.tz_hours) if start_ns else "",
        "bag_end_iso": fmt_iso(end_ns, args.tz_hours) if end_ns else "",
        "bag_duration_s": bag_duration_s,
        "selected_start_iso": fmt_iso(selected_start_ns, args.tz_hours) if selected_start_ns else "",
        "selected_end_iso": fmt_iso(selected_end_ns, args.tz_hours) if selected_end_ns else "",
        "selected_duration_s": selected_duration_s,
        "requested_duration_s": requested_duration_s,
        "sample_hz": args.sample_hz,
        "topics": {
            "command": args.command_topic,
            "feedback": args.feedback_topic,
            "temperature": args.temperature_topic,
        },
        "topic_sample_counts": dict(topic_counts),
        "missing_required_topics": missing_required_topics,
        "empty_analyzed_topics": empty_analyzed_topics,
        "joint_count": len(ordered_joints),
        "outputs": {
            "joint_feedback_samples": str(args.output_dir / "joint_feedback_samples.csv"),
            "joint_command_samples": str(args.output_dir / "joint_command_samples.csv"),
            "joint_temperature_samples": str(args.output_dir / "joint_temperature_samples.csv"),
            "joint_stats": str(args.output_dir / "joint_stats.csv"),
            "left_right_compare": str(args.output_dir / "left_right_compare.csv"),
            "charts_dir": str(charts_dir),
        },
        "charts": [str(path) for path in chart_paths],
    }
    (args.output_dir / "report_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        f"# {report_title}",
        "",
        f"- MCAP: `{args.mcap.name}`",
        f"- Model: `{model}`",
        f"- Time: `{manifest['bag_start_local']}` - `{manifest['bag_end_local']}`",
        f"- Selected duration: `{selected_duration_s:.3f}s`",
        f"- Sample Hz: `{args.sample_hz}`",
        f"- Topics: `{args.command_topic}`, `{args.feedback_topic}`, `{args.temperature_topic}`",
        "",
        "## Outputs",
        "",
        "- `joint_feedback_samples.csv`",
        "- `joint_command_samples.csv`",
        "- `joint_temperature_samples.csv`",
        "- `joint_stats.csv`",
        "- `left_right_compare.csv`",
        f"- `{charts_dir.name}/`: one 2x2 PNG per joint",
    ]
    (args.output_dir / "report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
