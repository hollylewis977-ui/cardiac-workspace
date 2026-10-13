#!/usr/bin/env bash
set -euo pipefail
SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec "${PYTHON_BIN:-python3}" "$SCRIPT_ROOT/tools/research_queue.py" "$@"
