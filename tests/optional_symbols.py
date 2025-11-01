"""Configuration for platform/version-specific symbols in stdlb.

This module explicitly documents which symbols may or may not be present
based on Python version and platform.
"""
import sys

# Specification of optional symbols with explicit version/platform requirements
OPTIONAL_SYMBOLS = {
    # Removed in Python 3.12+
    'NameConstant': {
        'removed_in': (3, 12),
        'module': 'ast',
        'reason': 'Deprecated AST node type'
    },
    'Num': {
        'removed_in': (3, 12),
        'module': 'ast',
        'reason': 'Deprecated AST node type'
    },
    'Str': {
        'removed_in': (3, 12),
        'module': 'ast',
        'reason': 'Deprecated AST node type'
    },
    'SafeConfigParser': {
        'removed_in': (3, 12),
        'module': 'configparser',
        'reason': 'Renamed to ConfigParser'
    },

    # Removed in Python 3.13+
    'LegacyInterpolation': {
        'removed_in': (3, 13),
        'module': 'configparser',
        'reason': 'Legacy interpolation removed'
    },
    'enable_shared_cache': {
        'removed_in': (3, 13),
        'module': 'sqlite3',
        'reason': 'Deprecated sqlite3 feature'
    },
    'format': {
        'removed_in': (3, 13),
        'module': 'locale',
        'reason': 'Use format_string instead'
    },
    'resetlocale': {
        'removed_in': (3, 13),
        'module': 'locale',
        'reason': 'Deprecated locale function'
    },
    'template': {
        'removed_in': (3, 13),
        'module': 're',
        'reason': 'RegexFlag.TEMPLATE removed'
    },

    # Added in Python 3.12+
    'ALLOW_MISSING': {
        'added_in': (3, 12),
        'module': 'genericpath',
        'reason': 'New path flag'
    },

    # macOS-only symbols
    'Bytes': {
        'platforms': ['darwin'],
        'module': 'builtins',
        'reason': 'macOS-specific type alias'
    },
    'Ellipsis': {
        'platforms': ['darwin'],
        'module': 'builtins',
        'reason': 'macOS-specific builtin'
    },
    'a2b_hqx': {
        'platforms': ['darwin'],
        'module': 'binascii',
        'reason': 'BinHex encoding (macOS Classic)'
    },
    'b2a_hqx': {
        'platforms': ['darwin'],
        'module': 'binascii',
        'reason': 'BinHex encoding (macOS Classic)'
    },
    'rledecode_hqx': {
        'removed_in': (3, 11),
        'module': 'binascii',
        'reason': 'BinHex run-length decoding (removed in 3.11+)'
    },
    'rlecode_hqx': {
        'platforms': ['darwin'],
        'module': 'binascii',
        'reason': 'BinHex run-length encoding (macOS Classic)'
    },
    'chflags': {
        'platforms': ['darwin'],
        'module': 'os',
        'reason': 'BSD file flags (macOS/BSD only)'
    },
    'lchflags': {
        'platforms': ['darwin'],
        'module': 'os',
        'reason': 'BSD file flags for symlinks (macOS/BSD only)'
    },
    'lchmod': {
        'platforms': ['darwin'],
        'module': 'os',
        'reason': 'Change symlink permissions (macOS/BSD only)'
    },

    # Unix-only symbols (not on Windows)
    'AbstractChildWatcher': {
        'platforms': ['darwin', 'linux'],
        'module': 'asyncio',
        'reason': 'Unix-only asyncio child watcher'
    },
    'FastChildWatcher': {
        'platforms': ['darwin', 'linux'],
        'module': 'asyncio',
        'reason': 'Unix-only asyncio child watcher'
    },
    'MultiLoopChildWatcher': {
        'platforms': ['darwin', 'linux'],
        'module': 'asyncio',
        'reason': 'Unix-only asyncio child watcher'
    },
    'SafeChildWatcher': {
        'platforms': ['darwin', 'linux'],
        'module': 'asyncio',
        'reason': 'Unix-only asyncio child watcher'
    },
    'ThreadedChildWatcher': {
        'platforms': ['darwin', 'linux'],
        'module': 'asyncio',
        'reason': 'Unix-only asyncio child watcher'
    },
    'PidfdChildWatcher': {
        'platforms': ['linux'],
        'module': 'asyncio',
        'reason': 'Linux-only asyncio child watcher (uses pidfd)'
    },
    'ItimerError': {
        'platforms': ['darwin', 'linux'],
        'module': 'signal',
        'reason': 'Unix-only interval timer exception'
    },
    'NGROUPS_MAX': {
        'platforms': ['darwin', 'linux'],
        'module': 'posix',
        'reason': 'Unix-only max supplementary groups constant'
    },

    # Common Unix-only functions (os/posix module)
    # Note: There are many more - these are the most common ones.
    # Pattern: Functions that start with these prefixes are likely Unix-only:
    # clock_, conf, get/set (process/user/group related), chroot, etc.
    'Sigmasks': {
        'platforms': ['darwin', 'linux'],
        'module': 'signal',
        'reason': 'Unix-only signal mask enumeration'
    },
    'abiflags': {
        'platforms': ['darwin', 'linux'],
        'module': 'sys',
        'reason': 'Unix-only ABI flags string'
    },
}


def is_symbol_expected(symbol_name: str, python_version=None, platform=None) -> bool:
    """Check if a symbol is expected to be present.

    Args:
        symbol_name: Name of the symbol to check
        python_version: Python version tuple (major, minor), defaults to sys.version_info
        platform: Platform name (e.g., 'darwin', 'linux'), defaults to sys.platform

    Returns:
        True if the symbol is expected to be present, False otherwise
    """
    if symbol_name not in OPTIONAL_SYMBOLS:
        return True  # Not optional, should always be present

    spec = OPTIONAL_SYMBOLS[symbol_name]
    version = python_version or sys.version_info[:2]
    plat = platform or sys.platform

    # Check if removed in this version
    if 'removed_in' in spec:
        if version >= spec['removed_in']:
            return False

    # Check if added in this version
    if 'added_in' in spec:
        if version < spec['added_in']:
            return False

    # Check platform
    if 'platforms' in spec:
        if plat not in spec['platforms']:
            return False

    return True


def get_optional_symbol_names() -> set:
    """Get set of all optional symbol names."""
    return set(OPTIONAL_SYMBOLS.keys())
