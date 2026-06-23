---
name: robotera-ops
description: Use as the ROBOTERA robot knowledge base for ROBOTERA/XBOT/XOS/ROS2 robots, including operation manuals, SDK workflows, deployment and upgrade troubleshooting, logs, firmware/software versions, joints, calibration, teleoperation, navigation, hardware notes, testing data, fault analysis, architecture notes, product behavior, and other robot-related knowledge. Use for Chinese or English requests mentioning 机器人, ROBOTERA, XBOT, XOS, SDK, ROS2, B4, M7, L3, 关节, 标零, 抱闸, 遥操作, 导航, 升级, 部署, 故障, 测试, 数据, 硬件, log, or 192.168.8.100.
metadata:
  short-description: ROBOTERA robot knowledge base
---

# ROBOTERA Knowledge

This skill provides indexed access to ROBOTERA robot knowledge. It is not limited to commands: it can include operation manuals, troubleshooting notes, testing knowledge, robot behavior, hardware information, architecture notes, data analysis references, and project-specific robot context.

## Required Safety Behavior

- Treat robot motion, brake release, calibration, firmware upgrade, deployment, and power control as potentially hazardous.
- Before suggesting commands that can move the robot, release brakes, write joint parameters, change masks, update firmware, or power-cycle components, state the operational preconditions from the manual and call out any required human supervision or emergency-stop readiness.
- Do not invent robot commands. If the needed command is not in this skill, inspect the source references or ask for the specific robot/model/context.
- Prefer non-destructive inspection commands before write/control commands.

## Source Selection

Start with [references/sources.md](references/sources.md) to find the relevant source document and cached reference.

For the current core manual:

- Read [references/robotera-manual-2.0.md](references/robotera-manual-2.0.md) for ROBOTERA 机器人操作手册 2.0.
- Read [references/sdk-2.0-usage-guide.md](references/sdk-2.0-usage-guide.md) for SDK 2.0 architecture, startup flow context, ROS_DOMAIN_ID guidance, new-machine setup sequence, maintenance config directories, and common SDK 2.0 error summaries.
- Read [references/fault-sdk-log-analysis.md](references/fault-sdk-log-analysis.md) for SDK log interpretation and fault diagnosis.
- Read [references/deployment-local-sdk.md](references/deployment-local-sdk.md) for local SDK deployment and deployment-related troubleshooting.
- Use `rg` against `references/` first for specific commands, topics, services, robot models, faults, tests, data terms, hardware names, or architecture terms.

Recommended search examples:

```bash
SKILL_DIR="$HOME/.codex/skills/robotera-ops"
rg -n "ready_service|activate_service|query_xbot_state|dynamic_launch" "$SKILL_DIR/references"
rg -n "标零|抱闸|error_mask|save_param|固件升级" "$SKILL_DIR/references"
rg -n "部署|升级|docker|GRUB|退出码|exit code|141" "$SKILL_DIR/references"
rg -n "SDK 2.0|ROS_DOMAIN_ID|xbot_battery|EC 状态|关节阶跃|ENC|developer_mode" "$SKILL_DIR/references"
rg -n "故障|现象|原因|解决|测试|数据|架构|硬件|传感器" "$SKILL_DIR/references"
```

## Working Pattern

1. Identify the robot/model and operation type when the request is ambiguous.
2. Search the cached references for exact terms from the user request.
3. Quote or summarize only the relevant knowledge, procedure, diagnosis, command sequence, or preconditions.
4. If the cached reference may be stale or the user asks for the latest content, ask for the current source document URL and fetch it with `lark-doc`.
5. When adding another document later, append it to `sources.md` and add a dedicated cached file under `references/`.

## Reference Organization

Use one cached Markdown file per source document. Prefer descriptive filenames by topic, for example:

- `robotera-manual-2.0.md` for operation manuals.
- `fault-analysis-<topic>.md` for fault diagnosis knowledge.
- `test-data-<topic>.md` for testing and analysis notes.
- `hardware-<topic>.md` for hardware or sensor knowledge.
- `architecture-<topic>.md` for system design and module interaction notes.

## Common Topics In The Core Manual

- 使用注意事项 and minimum software versions.
- Log retrieval and log analysis entry points.
- XOS/system/software version checks.
- SDK startup: standard mode, developer mode, root/developer command paths.
- SDK 2.0 architecture overview, ROS_DOMAIN_ID ranges, new-machine setup sequence, and common SDK 2.0 error summaries.
- `config.json` parameters.
- SDK state query and state transitions.
- Joint lists for B4, M7, and L3.
- Joint SN, firmware/module versions, masks, torque factors, friction compensation, zero calibration, brakes.
- Battery, LED, temperature, IMU, remote controller, gamepad data.
- Fixed actions, teleoperation, aging tests, offline dance playback, navigation workflow.
- SDK log interpretation and fault diagnosis.
- Local SDK deployment and deployment precautions.
