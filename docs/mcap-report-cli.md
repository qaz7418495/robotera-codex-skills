# Standalone MCAP Report CLI

`mcap-report` runs the ROBOTERA MCAP analysis pipeline without Codex. Its input
is one `.mcap` file and its final output is a Feishu document URL.

## Prerequisites

- Ubuntu with Python 3.10 or newer.
- `lark-cli` installed and configured.
- A logged-in Feishu user with document creation and file upload permissions.

Check Feishu authentication:

```bash
lark-cli auth status
```

## Installation

From the repository root:

```bash
python3 -m venv .venv-mcap-report
. .venv-mcap-report/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-mcap-report.txt
chmod +x bin/mcap-report
```

Optional system-wide command for the current user:

```bash
mkdir -p ~/.local/bin
ln -s "$(pwd)/bin/mcap-report" ~/.local/bin/mcap-report
```

Ensure `~/.local/bin` is in `PATH`.

## Run

Analyze the complete MCAP and publish the report:

```bash
bin/mcap-report /path/to/input.mcap
```

Analyze the first 30 minutes at 10 Hz:

```bash
bin/mcap-report /path/to/input.mcap --duration-min 30 --sample-hz 10
```

Generate only local CSV/PNG/XML artifacts:

```bash
bin/mcap-report /path/to/input.mcap --duration-min 30 --local-only
```

Validate an existing output package without writing Feishu:

```bash
bin/mcap-report --publish-only /path/to/output_dir --dry-run
```

Publish an existing output package:

```bash
bin/mcap-report --publish-only /path/to/output_dir
```

Publish into an existing document, useful after an interrupted upload:

```bash
bin/mcap-report \
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
bin/mcap-report --publish-only /path/to/output_dir
```

If the document was already created, read its ID from `delivery.json` and pass
it with `--doc` to avoid creating another document.

## Current Constraints

- The command depends on `lark-cli`; it does not embed Feishu credentials.
- Missing `/temperature` data does not fail the report. Temperature charts and
  temperature slope fields remain empty.
- Finger effort is excluded from whole-body and left/right effort comparison.
- Uploading dozens of PNG files can take several minutes.
