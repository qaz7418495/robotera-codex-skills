# MCAP Report Tool 维护说明

本文记录 `mcap-report` 的长期架构约束、关键业务规则和维护入口。

## 架构边界

MCAP 分析的唯一实现位于：

```text
tools/mcap-report/
├── bin/mcap-report
├── scripts/mcap_summary.py
├── scripts/mcap_joint_module_report.py
├── scripts/build_feishu_report_assets.py
├── install.sh
├── uninstall.sh
└── requirements-mcap-report.txt
```

`skills/mcap-robot-analysis/SKILL.md` 只负责让 Codex 识别需求并调用
`mcap-report`，不保存分析实现。

维护规则：

- Topic、统计、图表、CSV、飞书报告、上传逻辑均修改 Tool。
- 只有触发条件或调用命令变化时才修改 Skill。
- 不要在 Skill 下重新复制分析脚本。

## 分析 Topic

默认分析：

- `/hybrid_body_controller/commands`
- `/joint_states`
- `/temperature`

缺少 Topic 时继续生成报告，并在报告中标注。

## 业务约束

- 长时间窗口默认降采样为 `10Hz`。
- CSV 同时保留实际时间、`log_time_ns` 和相对时间。
- 图表横轴使用 MCAP 实际时间，格式为日期和时分秒。
- 每个关节生成一张 2×2 PNG：
  - feedback effort
  - command position vs feedback position
  - driver/motor temperature
  - feedback velocity
- 关键统计显示全部关节，不只显示 TOP N。
- 主要均值指标使用 `abs_mean`，并分别统计
  `positive_abs_mean`、`negative_abs_mean`。
- 左右对称关节对比包含极值、均值、绝对均值、正负向绝对均值、
  range 和温升斜率。
- 手指力矩单位与整机关节不同，不参与整机关节力矩排名和左右力矩对比。

## 容错与恢复

### 飞书上传

- 大于 20MB 的附件由 `lark-cli` 分片上传。
- 临时网络错误默认自动重试 4 次。
- `delivery.json` 保存文档 ID、上传状态和已上传文件。
- 上传中断后使用：

```bash
mcap-report --publish-only <output_dir>
```

工具会复用已有飞书文档并跳过已上传产物。

### 未完整 MCAP

MCAP 缺少 Footer、录制异常结束或索引损坏时：

- 工具自动切换为顺序读取。
- 顺序读取关闭全局时间排序，避免读到损坏文件尾后才输出数据。
- 达到用户指定时长后立即停止。
- 报告明确标注源 MCAP 未完整结束。
- 如果文件开头已经损坏，则无法恢复。

## 安装与验证

安装：

```bash
./tools/mcap-report/install.sh
source ~/.bashrc
mcap-report --doctor
```

升级后需要重新执行安装脚本，才能覆盖
`~/.local/share/robotera-mcap-report` 中的已安装版本。

最小本地验证：

```bash
mcap-report <bag.mcap> --end-sec 1 --local-only
```

完整发布验证：

```bash
mcap-report <bag.mcap> --duration-min 30 --sample-hz 10
```

## 重要路径

- 源码仓库：`/home/user/codex_workspace_1/robotera-codex-skills`
- 已安装 Tool：`~/.local/share/robotera-mcap-report`
- CLI：`~/.local/bin/mcap-report`
- 默认产物：`~/mcap_analysis_outputs/`
- 远程仓库：`https://github.com/qaz7418495/robotera-codex-skills`

