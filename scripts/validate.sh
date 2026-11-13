#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$PWD/.venv/bin:$PATH"
export MPLCONFIGDIR="$PWD/work/mpl"
export DBT_SEND_ANONYMOUS_USAGE_STATS=false
mkdir -p work
ruff check src tests scripts
pytest -q
python -m compileall -q src
python scripts/check_outputs.py
