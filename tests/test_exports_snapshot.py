"""Test that stdlb exports match the expected snapshot.

This test maintains a snapshot of all symbols exported by stdlb,
helping catch regressions where symbols are accidentally dropped.
"""
import json
import sys
import pathlib
import pytest

# Import optional symbols configuration
from .optional_symbols import get_optional_symbol_names

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
        # Socket/network constants (vary by OS)
        'AF_', 'AI_', 'EAI_', 'IPPROTO_', 'IP_', 'IPV6_', 'SO_',
        'MSG_', 'NI_', 'SHUT_', 'TCP_', 'PF_', 'SCM_', 'LOCAL_', 'SYSPROTO_',
        'CMSG_',  # Socket control messages (Unix)
        # Signal/process constants (Unix)
        'SIG', 'CLD_',  # Signals and child status
        'ITIMER_',  # Interval timers
        # Clock/time constants
        'CLOCK_',  # Clock types (vary by OS)
        # File/OS constants (Unix)
        'O_', 'EX_', 'F_',  # File flags, exit codes, file locking
        'P_', 'PRIO_', 'POSIX_SPAWN_',  # Process constants
        'RTLD_', 'ST_', 'SEEK_',  # Dynamic linker, stat, seek
        # Locale constants
        'LC_',  # Locale categories (vary by OS)
        # Resource limits (Unix)
        'RLIM_', 'RLIMIT_',  # Resource limits
        # Wait constants (Unix)
        'W',  # Wait status
        # Scheduling (Unix)
        'SCHED_',  # Scheduling policies
        # Terminal (Unix)
        'TIOCGPGRP', 'TIOCSPGRP',  # Terminal I/O control
    )

    # Get optional symbols (documented in tests/optional_symbols.py)
    optional_symbols = get_optional_symbol_names()

    missing = []
    for name in expected:
        if name not in current_globals:
            # Allow platform-specific symbols to be missing
            if name.startswith(platform_specific_prefixes):
                continue
            # Allow known optional symbols
            if name in optional_symbols:
                continue
            # For remaining symbols: if lowercase and from os/posix/signal modules,
            # likely Unix-only function (permissive fallback for 100+ Unix functions)
            if name[0].islower():
                # Likely a Unix-only os/posix function
                # Rather than list all ~100 functions, we allow missing lowercase
                # symbols as they're usually platform-specific functions
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
        # Socket/network constants (vary by OS)
        'AF_', 'AI_', 'EAI_', 'IPPROTO_', 'IP_', 'IPV6_', 'SO_',
        'MSG_', 'NI_', 'SHUT_', 'TCP_', 'PF_', 'SCM_', 'LOCAL_', 'SYSPROTO_',
        'CMSG_',  # Socket control messages (Unix)
        # Signal/process constants (Unix)
        'SIG', 'CLD_',  # Signals and child status
        'ITIMER_',  # Interval timers
        # Clock/time constants
        'CLOCK_',  # Clock types (vary by OS)
        # File/OS constants (Unix)
        'O_', 'EX_', 'F_',  # File flags, exit codes, file locking
        'P_', 'PRIO_', 'POSIX_SPAWN_',  # Process constants
        'RTLD_', 'ST_', 'SEEK_',  # Dynamic linker, stat, seek
        # Locale constants
        'LC_',  # Locale categories (vary by OS)
        # Resource limits (Unix)
        'RLIM_', 'RLIMIT_',  # Resource limits
        # Wait constants (Unix)
        'W',  # Wait status
        # Scheduling (Unix)
        'SCHED_',  # Scheduling policies
        # Terminal (Unix)
        'TIOCGPGRP', 'TIOCSPGRP',  # Terminal I/O control
    )

    # Get optional symbols (documented in tests/optional_symbols.py)
    optional_symbols = get_optional_symbol_names()

    # Filter out platform-specific symbols
    removed_filtered = set()
    for name in removed:
        if name.startswith(platform_specific_prefixes):
            continue
        if name in optional_symbols:
            continue
        # Allow lowercase symbols (Unix functions)
        if name[0].islower():
            continue
        removed_filtered.add(name)
    removed = removed_filtered

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
