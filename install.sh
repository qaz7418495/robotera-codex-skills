#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_ROOT="${MCAP_REPORT_INSTALL_ROOT:-$HOME/.local/share/robotera-mcap-report}"
BIN_DIR="${MCAP_REPORT_BIN_DIR:-$HOME/.local/bin}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SKIP_PYTHON_DEPS=0
SKIP_LARK_CLI=0

usage() {
  cat <<'EOF'
Usage: ./install.sh [options]

Options:
  --skip-python-deps  Do not install Python packages (for offline/testing use)
  --skip-lark-cli     Do not install lark-cli when it is missing
  -h, --help          Show this help

Environment:
  MCAP_REPORT_INSTALL_ROOT  Application directory
  MCAP_REPORT_BIN_DIR       Command directory
  PYTHON_BIN                Python executable (default: python3)
EOF
}

while (($#)); do
  case "$1" in
    --skip-python-deps)
      SKIP_PYTHON_DEPS=1
      ;;
    --skip-lark-cli)
      SKIP_LARK_CLI=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "ERROR: $PYTHON_BIN was not found. Install Python 3.10 or newer." >&2
  exit 1
fi

if ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
  echo "ERROR: Python 3.10 or newer is required." >&2
  exit 1
fi

echo "Installing application files to $INSTALL_ROOT"
mkdir -p "$INSTALL_ROOT" "$BIN_DIR"
rm -rf "$INSTALL_ROOT/bin" "$INSTALL_ROOT/skills" "$INSTALL_ROOT/docs"
cp -a "$SOURCE_DIR/bin" "$INSTALL_ROOT/bin"
cp -a "$SOURCE_DIR/skills" "$INSTALL_ROOT/skills"
cp -a "$SOURCE_DIR/docs" "$INSTALL_ROOT/docs"
cp "$SOURCE_DIR/requirements-mcap-report.txt" "$INSTALL_ROOT/"
cp "$SOURCE_DIR/README.md" "$INSTALL_ROOT/"

if [[ ! -x "$INSTALL_ROOT/.venv/bin/python" ]]; then
  echo "Creating isolated Python environment"
  VENV_ARGS=()
  if ((SKIP_PYTHON_DEPS == 1)); then
    VENV_ARGS+=(--without-pip)
  fi
  if ! "$PYTHON_BIN" -m venv "${VENV_ARGS[@]}" "$INSTALL_ROOT/.venv"; then
    rm -rf "$INSTALL_ROOT/.venv"
    if command -v apt-get >/dev/null 2>&1 && command -v sudo >/dev/null 2>&1; then
      echo "python3-venv is missing. Installing it with apt."
      sudo apt-get install -y python3-venv
      "$PYTHON_BIN" -m venv "$INSTALL_ROOT/.venv"
    else
      echo "ERROR: Python venv support is missing." >&2
      echo "Install the venv package for your Python distribution and rerun ./install.sh." >&2
      exit 1
    fi
  fi
fi

if ((SKIP_PYTHON_DEPS == 0)); then
  echo "Installing Python dependencies"
  "$INSTALL_ROOT/.venv/bin/python" -m pip install --upgrade pip
  "$INSTALL_ROOT/.venv/bin/python" -m pip install -r "$INSTALL_ROOT/requirements-mcap-report.txt"
fi

cat >"$BIN_DIR/mcap-report" <<EOF
#!/usr/bin/env bash
exec "$INSTALL_ROOT/.venv/bin/python" "$INSTALL_ROOT/bin/mcap-report" "\$@"
EOF
chmod +x "$BIN_DIR/mcap-report"

if ! command -v lark-cli >/dev/null 2>&1; then
  if ((SKIP_LARK_CLI == 0)); then
    if command -v npm >/dev/null 2>&1; then
      echo "Installing lark-cli"
      npm install -g @larksuite/cli
    else
      echo "WARNING: npm is missing; install Node.js/npm, then run:" >&2
      echo "  npm install -g @larksuite/cli" >&2
    fi
  else
    echo "WARNING: lark-cli installation skipped." >&2
  fi
fi

echo
echo "Installation complete."
echo "Command: $BIN_DIR/mcap-report"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo "Add this to your shell configuration, then reopen the terminal:"
  echo "  export PATH=\"$BIN_DIR:\$PATH\""
fi
echo
echo "Run environment check:"
echo "  $BIN_DIR/mcap-report --doctor"
echo
echo "If Feishu is not configured or logged in:"
echo "  lark-cli config init"
echo "  lark-cli auth login --domain docs"
