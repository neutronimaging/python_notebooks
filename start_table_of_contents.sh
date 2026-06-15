#!/usr/bin/env bash
set -euo pipefail

# Launch JupyterLab on the table of contents notebook using Firefox.
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOTEBOOK="notebooks/A_TABLE_OF_CONTENTS.ipynb"

cd "$REPO_DIR"
exec pixi run jupyter lab "$NOTEBOOK" --browser=firefox
