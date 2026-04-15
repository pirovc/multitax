#!/bin/bash
set -euo pipefail

ruff format
ruff check --fix
echo "Unit tests"
python -m unittest discover -s tests/multitax/unit/
echo "Integration tests"
python -m unittest discover -s tests/multitax/integration/ -v

pdoc -o docs multitax multitax.multitax multitax.utils