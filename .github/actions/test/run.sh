#!/bin/bash
set -e
echo "Installing project..."
poetry install --with dev
echo "Running tests..."
poetry run coverage run -m pytest tests --full-trace
poetry run coverage report -m -i
poetry run coverage html -i
