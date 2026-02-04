#!/bin/bash
pip install -e .[dev]
ruff format
ruff check --fix
python -m unittest discover -s tests/multitax/unit/ -v
python -m unittest discover -s tests/multitax/integration/ -v

pdoc -o docs multitax multitax.multitax multitax.utils