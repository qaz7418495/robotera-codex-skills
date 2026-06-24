# ROBOTERA 工具与 Codex Skills

本仓库包含 ROBOTERA 机器人相关的 Codex Skills，以及一个可以脱离
Codex 独立运行的 MCAP 数据分析工具。

## 仓库内容

- `skills/mcap-robot-analysis`：ROS2 MCAP 关节数据分析 Skill。
- `skills/robotera-ops`：ROBOTERA 机器人操作与故障排查知识库。
- `tools/mcap-report`：独立 MCAP 分析工具，输入一个 `.mcap` 文件，输出一份飞书数据分析报告。

## 同事如何使用 MCAP 工具

### 1. 获取仓库

本仓库为私有仓库，需要先给使用者添加 GitHub 访问权限。

```bash
git clone https://github.com/qaz7418495/robotera-codex-skills.git
cd robotera-codex-skills
```

### 2. 一键安装

```bash
./tools/mcap-report/install.sh
```

安装过程中可能要求输入 sudo 密码，用于安装 Ubuntu 的
`python3-venv`。安装完成后不需要进入仓库，也不需要手动激活 Python
虚拟环境。

如果提示找不到 `mcap-report`，执行：

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 3. 首次配置飞书

每位使用者需要使用自己的飞书账号完成配置和授权：

```bash
lark-cli config init
lark-cli auth login --domain docs
```

根据终端提示，在浏览器中完成授权。

### 4. 检查环境

```bash
mcap-report --doctor
```

输出包含以下内容时表示可以使用：

```json
{
  "ready": true
}
```

### 5. 分析 MCAP

分析前 30 分钟、采样频率 10 Hz，并自动生成飞书报告：

```bash
mcap-report /绝对路径/数据包.mcap \
  --duration-min 30 \
  --sample-hz 10
```

执行成功后，终端会输出飞书文档链接。本地产物默认保存在：

```text
~/mcap_analysis_outputs/
```

完整操作说明见
[MCAP 工具使用手册](tools/mcap-report/docs/README.md)。

## 更新工具

```bash
cd robotera-codex-skills
git pull
./tools/mcap-report/install.sh
```

## 卸载工具

```bash
cd robotera-codex-skills
./tools/mcap-report/uninstall.sh
```

卸载不会删除已经生成的分析报告、`lark-cli` 或飞书授权信息。

## 安装 Codex Skills

只有需要在 Codex 中使用 Skills 时才执行：

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/skills/mcap-robot-analysis" ~/.codex/skills/mcap-robot-analysis
ln -s "$(pwd)/skills/robotera-ops" ~/.codex/skills/robotera-ops
```

独立使用 `mcap-report` 不需要安装 Codex。

## 注意事项

- 不要向仓库提交 MCAP、CSV、PNG、飞书导出产物、密钥或访问令牌。
- MCAP 文件较大时，分析和图片上传可能需要较长时间。
- 缺少 `/temperature` Topic 不会导致任务失败，但温度图和温升斜率为空。
