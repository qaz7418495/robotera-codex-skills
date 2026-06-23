---
name: mcap-robot-analysis
description: Use when analyzing ROS2 MCAP/rosbag files for ROBOTERA robot joint-module data and producing a Feishu data-analysis report. Covers command/feedback/temperature topics, per-joint 2x2 PNG charts, CSV artifacts, left-right joint comparisons, and final Feishu document delivery. Trigger on .mcap, MCAP, rosbag, ROS2 bag, joint_states, temperature, HybridJointCommand, robot telemetry, or requests to analyze robot data.
metadata:
  short-description: Generate ROBOTERA MCAP joint reports as Feishu documents
---

# MCAP Robot Joint Report

This skill has one primary workflow: analyze a ROS2 MCAP robot bag and return a Feishu document report. Local CSV and PNG files are intermediate artifacts; the final user-facing result must be the Feishu document URL.

## Scope

Analyze the required ROBOTERA joint-module topics:

- `/hybrid_body_controller/commands`: joint command data.
- `/joint_states`: joint feedback data.
- `/temperature`: joint temperature data.

Use other topics only as explicit fallback or extra context when the required topics are absent and the user approves.

## Required Outputs

The final Feishu report must contain or attach all artifacts:

- CSV attachments:
  - `joint_command_samples.csv`
  - `joint_feedback_samples.csv`
  - `joint_temperature_samples.csv`
  - `joint_stats.csv`
  - `left_right_compare.csv`
- One 2x2 PNG per analyzed joint:
  - feedback effort
  - command position vs feedback position
  - driver temperature vs motor temperature
  - feedback velocity
- In-document summary tables:
  - input range and analyzed topics
  - artifact inventory
  - all-joint statistical ranges from `joint_stats.csv`, using absolute mean metrics instead of signed mean
  - all left/right comparison rows from `left_right_compare.csv`, excluding finger joints
- Caveats:
  - missing required topic
  - empty artifact such as no `/temperature` samples
  - requested duration longer than available MCAP data
  - sampling rate and selected time range

## Standard Workflow

1. Locate the `.mcap` file with `find . -maxdepth 3 -name '*.mcap'` if the user did not specify a path.
2. Run a low-token overview with `scripts/mcap_summary.py` when the package is unfamiliar.
3. Decide the selected time range:
   - If user requests a duration, pass it with `--end-sec`.
   - If requested duration exceeds available bag data, analyze all available data and state this in the report.
- Default sample rate is `10Hz`.
4. Generate the local report package with `scripts/mcap_joint_module_report.py`.
5. Generate Feishu XML and staged assets with `scripts/build_feishu_report_assets.py`.
6. Create the Feishu document with `lark-cli docs +create --api-version v2 --content @<feishu_report.xml>`.
7. Insert every CSV artifact with `lark-cli docs +media-insert --type file`.
8. Insert every PNG in `feishu_assets/charts/` with `lark-cli docs +media-insert --align center --width 900 --caption <name>`.
9. Verify the document can be fetched with `docs +fetch --scope outline`.
10. Final response: return the Feishu document URL first, then concise notes about selected duration, missing topics, artifact counts, and the local output directory.

Do not stop after creating local files unless Feishu writing is blocked by auth, permission, or network errors.

## Commands

Run scripts with the workspace Python packages when available:

```bash
SKILL_DIR="$HOME/.codex/skills/mcap-robot-analysis"
PYTHONPATH=.tools/python-packages python3 "$SKILL_DIR/scripts/mcap_summary.py" <bag.mcap>
PYTHONPATH=.tools/python-packages MPLCONFIGDIR=/tmp/mpl python3 "$SKILL_DIR/scripts/mcap_joint_module_report.py" <bag.mcap> --output-dir "$HOME/mcap_analysis_outputs/<bag_stem>" --model auto --sample-hz 10 --end-sec <seconds>
PYTHONPATH=.tools/python-packages python3 "$SKILL_DIR/scripts/build_feishu_report_assets.py" "$HOME/mcap_analysis_outputs/<bag_stem>"
```

Feishu document creation and artifact insertion:

```bash
lark-cli docs +create --api-version v2 --content @feishu_report.xml --format json
lark-cli docs +media-insert --doc <doc_id> --file <csv> --type file --format json
lark-cli docs +media-insert --doc <doc_id> --file <png> --align center --width 900 --caption "<chart_name>" --format json
```

## Script Responsibilities

- `scripts/mcap_summary.py`: lightweight MCAP metadata and topic summary.
- `scripts/mcap_joint_module_report.py`: stream required topics, downsample, compute statistics, generate CSVs, generate one 2x2 PNG per joint, and write `report_manifest.json`.
- `scripts/build_feishu_report_assets.py`: copy artifacts into `feishu_assets/` and generate `feishu_report.xml` for `docs +create`.

## Joint And Temperature Rules

Built-in model maps:

- `M7`: upper body, waist, neck, and hand-palm joints.
- `L3`: all `M7` joints plus hip, knee, and ankle joints.
- Auto-detect `L3` when leg joints appear; otherwise default to `M7`.

Use the actual MCAP joint names. Treat documentation spelling differences as non-authoritative; for example, `left_ankle_rollr_joint` is considered a typo unless it appears in the MCAP.

Finger-joint comparison constraint:

- Do not include finger joints in `left_right_compare.csv`.
- Do not compare finger effort with whole-body joint effort in conclusions.
- Reason: finger effort/torque units differ from the whole-body actuator units, so direct left/right or whole-body effort ranking is misleading.
- Treat these as finger joints: `left_hand_*`, `right_hand_*`, and names containing `_thumb_`, `_index_`, `_mid_`, `_ring_`, or `_pinky_`.
- Finger joints may still have their own 2x2 PNG and rows in `joint_stats.csv`; only cross-joint/left-right comparison is constrained.

Statistics constraints:

- Keep signed `mean` in `joint_stats.csv` for traceability, but do not use it as the main activity indicator in summaries or conclusions.
- Use `abs_mean` for overall activity magnitude because signed positive/negative motion can cancel out.
- Use `positive_abs_mean` and `negative_abs_mean` separately to show asymmetric positive/negative activity ranges.
- Key summary tables in the Feishu report must show `abs_mean`, `positive_abs_mean`, and `negative_abs_mean`.
- Key summary tables must include all matching joints, not only TOP N, unless the user explicitly asks for a ranked excerpt.
- Left/right comparison should include `abs_mean`, `positive_abs_mean`, and `negative_abs_mean` deltas when available.
- Left/right comparison tables in the Feishu report must include all rows from `left_right_compare.csv`, not only TOP N, unless the user explicitly asks for a shortened excerpt.

Plotting constraint:

- PNG chart x-axes must use actual timestamps extracted from MCAP log time, not relative elapsed time.
- Every subplot must show explicit date and time labels; use `YYYY-MM-DD` on one line and `HH:MM:SS` on the next line.
- Do not rely on Matplotlib's default date offset/auto-hiding behavior, because it may show only `HH:MM:SS` or hide labels on shared x-axes.
- CSV sample files must include both `time` and `log_time_ns`; relative `t` may remain as an auxiliary column.

Temperature parsing:

- Inspect the actual decoded message format.
- If the temperature message contains names, use those names.
- If the message is a numeric array, map by model joint order:
  - even index: driver temperature
  - odd index: motor temperature
  - pair `2*n` / `2*n+1` belongs to the `n`th joint.

## Output Directory

Use:

```text
$HOME/mcap_analysis_outputs/<bag_stem>_<optional_range>/
```

The directory should contain:

- `joint_command_samples.csv`
- `joint_feedback_samples.csv`
- `joint_temperature_samples.csv`
- `joint_stats.csv`
- `left_right_compare.csv`
- `report_manifest.json`
- `report.md`
- `feishu_report.xml`
- `feishu_assets/`
- `charts/*.png`

## Performance Rules

- Keep the source MCAP read-only.
- Stream messages; do not load full-rate decoded messages into memory.
- Default to `10Hz` samples for long windows.
- Use full rate only for short diagnostic windows.
- Do not paste large CSV contents into chat.
- Report missing `/temperature` as a caveat rather than failing the whole report.
