#!/bin/bash
set -e

# Ensure we are in the project root
cd "$(dirname "$0")/.."

echo "Running Test Suite Generation Script..."
export PYTHONPATH=src
uv run python sandbox/generate_suite.py "$@"
