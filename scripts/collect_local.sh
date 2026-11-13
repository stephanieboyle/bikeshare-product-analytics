#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p work
# Collector owns a non-blocking process lock and a persistent next-request deadline.
exec .venv/bin/bikeshare collect --count 1 --interval 120 >>work/collector.log 2>&1
