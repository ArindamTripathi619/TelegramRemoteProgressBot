#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python}"

"$PYTHON_BIN" -m pip install -r requirements-dev.txt
"$PYTHON_BIN" -m pytest -q
"$PYTHON_BIN" -m build --sdist --wheel

echo "Preflight passed: dependencies installed, tests passed, build artifacts generated."
