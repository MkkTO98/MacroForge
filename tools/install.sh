#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v uv >/dev/null 2>&1; then
  printf 'ERROR: uv is required on this PEP 668/no-pip host. Install uv, or run one-shot commands with an environment that has PyYAML.
' >&2
  exit 1
fi
uv venv --allow-existing >/dev/null
uv sync --locked --group test >/dev/null
chmod +x tools/*.py
printf '[ok] ProjectForge tools prepared in .venv from the committed test dependency lock.\n'
printf 'Use: uv run --locked --group test python tools/check_coherence.py --project . --json\n'
