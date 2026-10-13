#!/usr/bin/env bash
set -euo pipefail
SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
if [[ $# -gt 1 ]] || [[ $# -eq 1 && "$1" != "--check" ]]; then
  echo "Usage: bash setup.sh [--check]; checks only. Use the existing cardiac Python environment." >&2
  exit 2
fi
exec "${PYTHON_BIN:-python3}" "$SCRIPT_ROOT/tools/cardiac_workspace.py" doctor
