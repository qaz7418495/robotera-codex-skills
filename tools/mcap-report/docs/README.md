# Standalone MCAP Report CLI

`mcap-report` runs the ROBOTERA MCAP analysis pipeline without Codex. Its input
is one `.mcap` file and its final output is a Feishu document URL.

## Prerequisites

- Ubuntu with Python 3.10 or newer.
- Git.
- Node.js/npm only when `lark-cli` is not already installed.
- A Feishu user with document creation and file upload permissions.

Codex is not required.

## One-Command Installation

Clone the repository and run the installer:

```bash
git clone https://github.com/qaz7418495/robotera-codex-skills.git
cd robotera-codex-skills
./tools/mcap-report/install.sh
```

The installer:

- Copies the application to `~/.local/share/robotera-mcap-report`.
- Creates an isolated Python virtual environment.
- Installs Ubuntu's `python3-venv` package through sudo when it is missing.
- Installs all Python dependencies.
- Installs `lark-cli` through npm when it is missing.
- Creates the command `~/.local/bin/mcap-report`.

If `~/.local/bin` is not in `PATH`, add this line to `~/.bashrc` and reopen the
terminal:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

No virtual environment activation is needed.

## First Feishu Setup

Each user must configure and authorize their own Feishu account:

```bash
lark-cli config init
lark-cli auth login --domain docs
```

Check the complete environment:

```bash
mcap-report --doctor
```

The command is ready when the output contains `"ready": true`.

## Run

Analyze the complete MCAP and publish the report:

```bash
mcap-report /path/to/input.mcap
```

Analyze the first 30 minutes at 10 Hz:

```bash
mcap-report /path/to/input.mcap --duration-min 30 --sample-hz 10
```

Generate only local CSV/PNG/XML artifacts:

```bash
mcap-report /path/to/input.mcap --duration-min 30 --local-only
```

Validate an existing output package without writing Feishu:

```bash
mcap-report --publish-only /path/to/output_dir --dry-run
```

Publish an existing output package:

```bash
mcap-report --publish-only /path/to/output_dir
```

Publish into an existing document, useful after an interrupted upload:

```bash
mcap-report \
  --publish-only /path/to/output_dir \
  --doc DOCUMENT_ID \
  --doc-url "https://example.feishu.cn/docx/DOCUMENT_ID"
```

## Outputs

The default local directory is:

```text
~/mcap_analysis_outputs/<mcap_stem>_<run_time>/
```

It contains CSV files, one 2x2 PNG per joint, Feishu XML, staged upload assets,
and `delivery.json`.

`delivery.json` records:

- Feishu document ID and URL.
- Upload status.
- Uploaded CSV and chart names.
- Local output directory.

## Failure Recovery

If analysis succeeds but Feishu publishing fails, do not rerun the MCAP
analysis. Use the output directory printed by the failed command:

```bash
mcap-report --publish-only /path/to/output_dir
```

If the document was already created, read its ID from `delivery.json` and pass
it with `--doc` to avoid creating another document.

## Upgrade

From the cloned repository:

```bash
git pull
./tools/mcap-report/install.sh
```

## Uninstall

From the cloned repository:

```bash
./tools/mcap-report/uninstall.sh
```

This removes the MCAP report application. It does not remove `lark-cli` or the
user's Feishu authentication.

## Current Constraints

- The command depends on `lark-cli`; it does not embed Feishu credentials.
- Missing `/temperature` data does not fail the report. Temperature charts and
  temperature slope fields remain empty.
- Finger effort is excluded from whole-body and left/right effort comparison.
- Uploading dozens of PNG files can take several minutes.
