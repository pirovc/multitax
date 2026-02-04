#!/bin/bash
ruff format
ruff check --fix

pdoc -o docs multitax multitax.multitax multitax.utils