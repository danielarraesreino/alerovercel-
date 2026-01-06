#!/bin/bash
set -e

echo "===== Running AleroPrice Test Suite ====="

# Add current directory to python path
export PYTHONPATH=$PYTHONPATH:.

# Run pytest
echo "Running Unit Tests..."
pytest tests/unit -v

echo "===== All Tests Passed! System is Stable. ====="
