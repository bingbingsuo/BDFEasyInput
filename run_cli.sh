#!/bin/bash
# Wrapper script for running BDFEasyInput CLI from any directory
# This script ensures proper Python path for editable installs

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BDF_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Activate virtual environment if it exists
if [ -f "$BDF_ROOT/venv_bdf/bin/activate" ]; then
    source "$BDF_ROOT/venv_bdf/bin/activate"
fi

# Set PYTHONPATH to include bdf root for editable installs
export PYTHONPATH="$BDF_ROOT:$PYTHONPATH"

# Run the CLI
python -m bdfeasyinput.cli "$@"
