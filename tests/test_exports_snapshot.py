"""Test that stdlb exports match the expected snapshot.

This test maintains a snapshot of all symbols exported by stdlb,
helping catch regressions where symbols are accidentally dropped.
"""
import json
import sys
import pathlib
import pytest

# Import at module level
from stdlb import *

# Load snapshot (use pathlib before stdlb overwrites Path)
snapshot_path = pathlib.Path(__file__).parent / 'exports_snapshot.json'


def test_snapshot_exists():
    """Verify snapshot file exists."""
    assert snapshot_path.exists(), (
        f"Snapshot file missing: {snapshot_path}\n"
        "Run: python scripts/snapshot_exports.py"
    )


def test_all_expected_symbols_present():
    """Test that all symbols in the snapshot are still exported."""
    with open(snapshot_path) as f:
        expected = json.load(f)

    # Get current exports
    current_globals = globals()

    missing = []
    for name in expected:
        if name not in current_globals:
            missing.append(name)

    if missing:
        pytest.fail(
            f"Missing {len(missing)} expected exports:\n" +
            "\n".join(f"  - {name}" for name in sorted(missing)[:20]) +
            (f"\n  ... and {len(missing) - 20} more" if len(missing) > 20 else "")
        )


def test_no_unexpected_removals():
    """Test that no symbols were removed compared to snapshot."""
    with open(snapshot_path) as f:
        expected = json.load(f)

    # Get current exports (excluding test internals)
    before_import = {'sys', 'Path', 'pytest', 'json', '__name__', '__doc__',
                     '__package__', '__loader__', '__spec__', '__annotations__',
                     '__builtins__', '__file__', '__cached__', 'snapshot_path',
                     'test_snapshot_exists', 'test_all_expected_symbols_present',
                     'test_no_unexpected_removals', 'test_new_exports_documented'}
    current = {k for k in globals().keys() if k not in before_import}

    expected_set = set(expected.keys())
    removed = expected_set - current

    if removed:
        pytest.fail(
            f"Removed {len(removed)} symbols since snapshot:\n" +
            "\n".join(f"  - {name} (from {expected[name]})"
                     for name in sorted(removed)[:20]) +
            (f"\n  ... and {len(removed) - 20} more" if len(removed) > 20 else "") +
            "\n\nRun: python scripts/snapshot_exports.py  # to update snapshot"
        )


def test_new_exports_documented():
    """Warn about new exports not in snapshot (info only)."""
    with open(snapshot_path) as f:
        expected = json.load(f)

    # Get current exports
    before_import = {'sys', 'Path', 'pytest', 'json', '__name__', '__doc__',
                     '__package__', '__loader__', '__spec__', '__annotations__',
                     '__builtins__', '__file__', '__cached__', 'snapshot_path',
                     'test_snapshot_exists', 'test_all_expected_symbols_present',
                     'test_no_unexpected_removals', 'test_new_exports_documented'}
    current = {k for k in globals().keys() if k not in before_import}

    expected_set = set(expected.keys())
    new = current - expected_set

    if new:
        # This is just informational, not a failure
        print(f"\n\nℹ️  New exports not in snapshot ({len(new)} total):")
        for name in sorted(new)[:20]:
            obj = globals()[name]
            # Try to get FQN for display
            fqn = None
            if hasattr(obj, '__module__') and hasattr(obj, '__qualname__'):
                fqn = f"{obj.__module__}.{obj.__qualname__}"
            print(f"  + {name}" + (f" (from {fqn})" if fqn else ""))
        if len(new) > 20:
            print(f"  ... and {len(new) - 20} more")
        print("\nRun to update snapshot: python scripts/snapshot_exports.py")
