---
name: mcap-robot-analysis
description: Use when the user asks to analyze a ROBOTERA ROS2 MCAP/rosbag, joint_states, HybridJointCommand, temperature, robot telemetry, joint data, or requests a Feishu MCAP analysis report.
metadata:
  short-description: Call the standalone ROBOTERA MCAP report tool
---

# MCAP Robot Analysis

This Skill is only an intent router for the standalone `mcap-report` Tool.
Analysis, statistics, plotting, report generation, Feishu upload, retry, and
resume behavior are implemented under `tools/mcap-report/`.

## Workflow

1. Locate the user-specified `.mcap` file. If no path is given, search the
   current workspace without modifying the source file.
2. Unless the user specified otherwise, use `10Hz`.
3. Run the installed command:

```bash
mcap-report <bag.mcap> --duration-min <minutes> --sample-hz 10
```

4. If the installed command is unavailable but the repository is present, run:

```bash
tools/mcap-report/bin/mcap-report <bag.mcap> --duration-min <minutes> --sample-hz 10
```

5. Return the Feishu document URL and the local output directory.

## Recovery

If analysis completed but Feishu publishing failed, use the output directory
reported by the command:

```bash
mcap-report --publish-only <output_dir>
```

The Tool reads `delivery.json`, reuses the existing document, skips uploaded
artifacts, and retries transient network failures.

Do not manually reimplement the MCAP pipeline inside the Skill. Functional
changes belong in `tools/mcap-report/`; update this file only when invocation or
intent-routing behavior changes.
