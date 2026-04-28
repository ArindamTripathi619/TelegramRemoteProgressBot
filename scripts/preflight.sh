#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VENV_PYTHON="$ROOT_DIR/.venv/bin/python"
INSTALL_DEPS=0

if [[ "${1:-}" == "--install" ]]; then
	INSTALL_DEPS=1
elif [[ -n "${1:-}" ]]; then
	echo "Usage: bash scripts/preflight.sh [--install]" >&2
	exit 2
fi

if [[ ! -x "$VENV_PYTHON" ]]; then
	echo "Error: project venv interpreter not found at $VENV_PYTHON" >&2
	echo "Create it first: python3 -m venv .venv" >&2
	echo "Then install deps once: $VENV_PYTHON -m pip install -r requirements-dev.txt" >&2
	exit 1
fi

if [[ "$INSTALL_DEPS" -eq 1 ]]; then
	"$VENV_PYTHON" -m pip install -r requirements-dev.txt
fi

"$VENV_PYTHON" -m mypy --config-file mypy.ini src/openbridge/workflows.py
"$VENV_PYTHON" scripts/check_config_drift.py
"$VENV_PYTHON" -m pytest -q
"$VENV_PYTHON" -m build --sdist --wheel

echo "Preflight passed: typing, config/docs drift, tests, and build checks succeeded."
