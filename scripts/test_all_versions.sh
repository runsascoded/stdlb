#!/usr/bin/env bash
# Test stdlb across all Python versions

set -e

VERSIONS=("3.10" "3.11" "3.12" "3.13")

echo "Testing stdlb across Python versions..."
echo

for version in "${VERSIONS[@]}"; do
    venv_path=".venv/$version.*/bin/python"
    python_bin=$(ls -d $venv_path 2>/dev/null | head -1)

    if [ -z "$python_bin" ]; then
        echo "⚠️  Python $version not found, skipping"
        continue
    fi

    echo "=== Testing Python $version ($python_bin) ==="

    # Install dependencies if needed
    if ! $python_bin -c "import pytest" 2>/dev/null; then
        echo "  Installing pytest..."
        $python_bin -m pip install -q pytest
    fi

    # Install stdlb in editable mode
    $python_bin -m pip install -q -e .

    # Run tests
    $python_bin -m pytest tests/test_imports.py -v --tb=line 2>&1 | tail -5
    echo
done

echo "✓ All tests complete"
