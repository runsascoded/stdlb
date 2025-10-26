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
    """Test that all symbols in the snapshot are still exported.

    Note: Platform-specific symbols (like certain socket/signal constants)
    may not be present on all systems, so we allow some missing symbols.
    """
    with open(snapshot_path) as f:
        expected = json.load(f)

    # Get current exports
    current_globals = globals()

    # Platform-specific prefixes that may not exist on all systems
    platform_specific_prefixes = (
        'AF_', 'AI_', 'EAI_', 'IPPROTO_', 'IP_', 'IPV6_', 'SO_',
        'MSG_', 'NI_', 'SHUT_', 'TCP_', 'CLOCK_', 'SIG',
        'O_', 'PF_', 'SCM_', 'LOCAL_', 'SYSPROTO_',
    )

    # Version/platform-specific symbols that may not exist everywhere
    optional_symbols = {
        # Python version differences (removed in 3.12+)
        'NameConstant', 'Num', 'Str', 'SafeConfigParser',
        # macOS-specific
        'Bytes', 'Ellipsis', 'a2b_hqx', 'b2a_hqx', 'chflags', 'lchflags', 'lchmod',
        'rldecode_hqx', 'rlecode_hqx',
    }

    missing = []
    for name in expected:
        if name not in current_globals:
            # Allow platform-specific symbols to be missing
            if name.startswith(platform_specific_prefixes):
                continue
            # Allow known optional symbols
            if name in optional_symbols:
                continue
            missing.append(name)

    if missing:
        pytest.fail(
            f"Missing {len(missing)} expected exports:\n" +
            "\n".join(f"  - {name}" for name in sorted(missing)[:20]) +
            (f"\n  ... and {len(missing) - 20} more" if len(missing) > 20 else "")
        )


def test_no_unexpected_removals():
    """Test that no symbols were removed compared to snapshot.

    Note: Platform-specific symbols are allowed to be missing.
    """
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

    # Platform-specific prefixes that may not exist on all systems
    platform_specific_prefixes = (
        'AF_', 'AI_', 'EAI_', 'IPPROTO_', 'IP_', 'IPV6_', 'SO_',
        'MSG_', 'NI_', 'SHUT_', 'TCP_', 'CLOCK_', 'SIG',
        'O_', 'PF_', 'SCM_', 'LOCAL_', 'SYSPROTO_',
    )

    # Version/platform-specific symbols that may not exist everywhere
    optional_symbols = {
        # Python version differences (removed in 3.12+)
        'NameConstant', 'Num', 'Str', 'SafeConfigParser',
        # macOS-specific
        'Bytes', 'Ellipsis', 'a2b_hqx', 'b2a_hqx', 'chflags', 'lchflags', 'lchmod',
        'rldecode_hqx', 'rlecode_hqx',
    }

    # Filter out platform-specific symbols
    removed = {
        name for name in removed
        if not name.startswith(platform_specific_prefixes)
        and name not in optional_symbols
    }

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
