# MCAP 飞书分析工具使用手册

`mcap-report` 可以在没有 Codex 的电脑上独立运行。输入一个 ROS2
`.mcap` 文件，工具会生成 CSV、每关节 2×2 图表、左右对称关节统计，
并创建一份飞书数据分析报告。

本目录包含完整实现：

- `bin/mcap-report`：命令入口、飞书发布、自动重试和断点续传。
- `scripts/mcap_summary.py`：MCAP Topic 与元数据概览。
- `scripts/mcap_joint_module_report.py`：解析、统计、CSV 和 PNG 生成。
- `scripts/build_feishu_report_assets.py`：飞书报告 XML 与上传产物整理。

Codex Skill 只负责识别需求并调用该 Tool，不再保存或复制分析脚本。

## 环境要求

- Ubuntu。
- Python 3.10 或更高版本。
- Git。
- 可正常使用的飞书账号。
- 安装 `lark-cli` 时需要 Node.js/npm；安装器会在缺少时自动处理。

## 安装

仓库是私有仓库，使用者必须先获得访问权限。

```bash
git clone https://github.com/qaz7418495/robotera-codex-skills.git
cd robotera-codex-skills
./tools/mcap-report/install.sh
```

安装器会自动：

- 将程序安装到 `~/.local/share/robotera-mcap-report`。
- 创建独立 Python 虚拟环境。
- 安装 Python 分析依赖。
- 缺少 `python3-venv` 时通过 sudo 安装。
- 缺少 `lark-cli` 时通过 npm 安装。
- 创建 `~/.local/bin/mcap-report` 命令。

安装完成后不需要执行 `source` 激活虚拟环境。

安装器会自动把命令目录写入 `~/.bashrc`。安装后在当前终端执行：

```bash
source ~/.bashrc
```

如果仍提示 `mcap-report：未找到命令`，先用绝对路径检查：

```bash
~/.local/bin/mcap-report --doctor
```

## 飞书首次配置

每位使用者必须配置并授权自己的飞书账号：

```bash
lark-cli config init
lark-cli auth login --domain docs
```

根据终端提示打开授权链接，并在浏览器中完成授权。

检查运行环境：

```bash
mcap-report --doctor
```

当输出包含 `"ready": true` 时，环境配置完成。

## 常用命令

### 生成完整飞书报告

```bash
mcap-report /绝对路径/数据包.mcap
```

### 分析前 30 分钟，采样频率 10 Hz

```bash
mcap-report /绝对路径/数据包.mcap \
  --duration-min 30 \
  --sample-hz 10
```

执行结束后，终端会输出飞书文档链接。

### 只生成本地产物，不写入飞书

```bash
mcap-report /绝对路径/数据包.mcap \
  --duration-min 30 \
  --local-only
```

### 检查已有产物是否可以发布

该命令不会创建或修改飞书文档：

```bash
mcap-report \
  --publish-only /绝对路径/分析产物目录 \
  --dry-run
```

### 重新发布已有产物

分析已经成功、但飞书上传失败时，无需重新解析 MCAP：

```bash
mcap-report --publish-only /绝对路径/分析产物目录
```

工具会自动读取该目录下的 `delivery.json`，复用已经创建的飞书文档，
跳过已成功上传的附件，并对临时网络错误自动重试。

如果飞书文档已经创建，可以复用已有文档：

```bash
mcap-report \
  --publish-only /绝对路径/分析产物目录 \
  --doc 文档ID \
  --doc-url "https://example.feishu.cn/docx/文档ID"
```

## 输出内容

默认本地产物目录：

```text
~/mcap_analysis_outputs/<MCAP文件名>_<运行时间>/
```

主要内容包括：

- `joint_command_samples.csv`
- `joint_feedback_samples.csv`
- `joint_temperature_samples.csv`
- `joint_stats.csv`
- `left_right_compare.csv`
- 每个关节一张 2×2 PNG 图
- `feishu_report.xml`
- `delivery.json`

`delivery.json` 会记录飞书文档 ID、文档链接、上传状态和已上传文件，
用于上传中断后的恢复。

## 更新

```bash
cd robotera-codex-skills
git pull
./tools/mcap-report/install.sh
```

## 卸载

```bash
cd robotera-codex-skills
./tools/mcap-report/uninstall.sh
```

卸载不会删除：

- 已生成的 MCAP 分析产物。
- `lark-cli`。
- 使用者的飞书授权信息。
- Git 仓库源码。

## 常见问题

### 找不到 `mcap-report`

```bash
source ~/.bashrc
hash -r
mcap-report --doctor
```

仍然找不到时执行：

```bash
~/.local/bin/mcap-report --doctor
```

### 缺少 Python 依赖

重新执行：

```bash
./tools/mcap-report/install.sh
```

### 飞书未登录或权限不足

先检查：

```bash
lark-cli auth status
mcap-report --doctor
```

必要时重新授权：

```bash
lark-cli auth login --domain docs
```

### 缺少温度数据

缺少 `/temperature` Topic 不会中断分析，但温度图和左右温升斜率字段
会保持为空。

### 上传失败

找到上次输出目录后执行：

```bash
mcap-report --publish-only /绝对路径/分析产物目录
```

这样不会重新处理大型 MCAP 文件。
