# ROBOTERA Codex Skills

This repository contains shareable Codex skills for ROBOTERA work.

## Skills

- `mcap-robot-analysis`: Analyze ROS2 MCAP robot joint-module data and produce Feishu reports.
- `robotera-ops`: ROBOTERA robot operation and troubleshooting knowledge base.

## Standalone MCAP Tool

The MCAP pipeline can run without Codex. Install it once:

```bash
./tools/mcap-report/install.sh
lark-cli config init
lark-cli auth login --domain docs
mcap-report --doctor
```

Then run it from any directory without activating a virtual environment:

```bash
mcap-report /path/to/input.mcap --duration-min 30 --sample-hz 10
```

See [tools/mcap-report/docs/README.md](tools/mcap-report/docs/README.md) for installation,
publishing, dry-run, and failure recovery instructions.

## Install

Clone the repository and link the desired skills into `~/.codex/skills`:

```bash
git clone <repo-url> robotera-codex-skills
mkdir -p ~/.codex/skills
ln -s "$(pwd)/robotera-codex-skills/skills/mcap-robot-analysis" ~/.codex/skills/mcap-robot-analysis
ln -s "$(pwd)/robotera-codex-skills/skills/robotera-ops" ~/.codex/skills/robotera-ops
```

If a skill directory already exists, move or remove it before creating the symlink.

## Update

```bash
cd robotera-codex-skills
git pull
```

## Notes

- Do not commit MCAP files, generated CSV/PNG reports, Feishu export artifacts, credentials, or temporary media links.
- The bundled references are cached text snapshots. If current source content is required, provide the current document URL to the agent at runtime.
