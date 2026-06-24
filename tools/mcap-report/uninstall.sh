#!/usr/bin/env bash
set -euo pipefail

INSTALL_ROOT="${MCAP_REPORT_INSTALL_ROOT:-$HOME/.local/share/robotera-mcap-report}"
BIN_DIR="${MCAP_REPORT_BIN_DIR:-$HOME/.local/bin}"

usage() {
  cat <<'EOF'
Usage: ./tools/mcap-report/uninstall.sh

Removes the standalone MCAP report application. It does not remove lark-cli,
Feishu authentication, source repositories, or generated reports.
EOF
}

while (($#)); do
  case "$1" in
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
done

rm -f "$BIN_DIR/mcap-report"
rm -rf "$INSTALL_ROOT"

echo "Removed:"
echo "  $BIN_DIR/mcap-report"
echo "  $INSTALL_ROOT"
echo "lark-cli and Feishu authentication were not removed."
