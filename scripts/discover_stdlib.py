#!/usr/bin/env -S uv run --quiet --script
# /// script
# dependencies = []
# ///
"""Discover and catalog Python standard library modules.

This script analyzes the stdlib to determine which modules should be included
in stdlb, handling version-specific modules and collision detection.
"""
import sys
import importlib
import pkgutil
import warnings
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Modules to skip (internal, deprecated, platform-specific, or problematic)
SKIP_MODULES = {
    # Internal/private modules (start with _)
    # (handled by pattern matching)

    # Platform-specific
    '_winapi', 'winreg', 'winsound', 'msilib', 'msvcrt',
    '_osx_support', '_aix_support', '_android_support', '_apple_support',

    # Test modules
    'test', 'unittest.test', 'distutils.tests', 'lib2to3.tests',
    '_testcapi', '_testinternalcapi', '_testbuffer', '_testimportmultiple',
    '_testmultiphase', '_ctypes_test', '_testconsole', '_testembed',
    '_testlimitedcapi',

    # Deprecated
    'imp', 'formatter', 'aifc', 'audioop', 'cgi', 'cgitb', 'chunk',
    'crypt', 'imghdr', 'mailcap', 'mimetools', 'nis', 'nntplib', 'ossaudiodev',
    'pipes', 'sndhdr', 'spwd', 'sunau', 'telnetlib', 'uu', 'xdrlib',

    # Special purpose / not useful for wildcard import
    '__hello__', '__phello__', 'antigravity', 'this',

    # Build/packaging tools (not useful in runtime)
    'ensurepip', 'venv', 'zipapp',

    # Already in builtins
    '__main__', '__future__',
}

# Modules that have useful members to import
USEFUL_MODULES = {
    'abc', 'array', 'ast', 'asyncio', 'base64', 'binascii', 'bisect',
    'calendar', 'cmath', 'code', 'codecs', 'collections', 'configparser',
    'contextlib', 'copy', 'csv', 'dataclasses', 'datetime', 'decimal',
    'difflib', 'enum', 'fnmatch', 'fractions', 'functools', 'glob',
    'graphlib', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'io',
    'itertools', 'json', 'locale', 'logging', 'math', 'mimetypes',
    'numbers', 'operator', 'os', 'pathlib', 'pickle', 'platform',
    'pprint', 'queue', 'random', 're', 'reprlib', 'secrets', 'shelve',
    'shlex', 'shutil', 'signal', 'socket', 'sqlite3', 'statistics',
    'string', 'struct', 'subprocess', 'sys', 'tempfile', 'textwrap',
    'threading', 'time', 'timeit', 'traceback', 'types', 'typing',
    'unicodedata', 'urllib', 'uuid', 'warnings', 'weakref', 'xml',
    'zipfile', 'zlib',

    # Python 3.8+
    'importlib.metadata',

    # Python 3.9+
    'graphlib', 'zoneinfo',

    # Python 3.10+
    'contextlib',  # added nullcontext in 3.10

    # Python 3.11+
    'tomllib', 'asyncio.taskgroups',

    # Python 3.12+
    'itertools',  # added batched in 3.12
}


def get_stdlib_modules() -> Set[str]:
    """Get all stdlib module names."""
    modules = set()

    # Use sys.stdlib_module_names if available (Python 3.10+)
    if hasattr(sys, 'stdlib_module_names'):
        modules.update(sys.stdlib_module_names)
    else:
        # Fallback: discover via pkgutil
        for importer, modname, ispkg in pkgutil.iter_modules():
            if hasattr(importer, 'path') and 'site-packages' not in str(importer.path):
                modules.add(modname)

    return modules


def should_skip_module(module_name: str) -> bool:
    """Determine if a module should be skipped."""
    # Skip private modules
    if module_name.startswith('_'):
        return True

    # Skip explicitly listed modules
    if module_name in SKIP_MODULES:
        return True

    # Skip submodules of skipped modules
    for skip in SKIP_MODULES:
        if module_name.startswith(skip + '.'):
            return True

    return False


def get_module_members(module_name: str) -> Tuple[List[str], List[str]]:
    """Get public members of a module.

    Returns:
        Tuple of (exportable_members, all_members)
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            module = importlib.import_module(module_name)

        # Get __all__ if available
        if hasattr(module, '__all__'):
            return list(module.__all__), list(module.__all__)

        # Otherwise, get all public members
        all_members = [name for name in dir(module) if not name.startswith('_')]
        return all_members, all_members

    except Exception as e:
        print(f"Warning: Could not import {module_name}: {e}", file=sys.stderr)
        return [], []


def check_builtins_collision(name: str) -> bool:
    """Check if a name exists in __builtins__."""
    builtins_dict = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
    return name in builtins_dict


def analyze_stdlib() -> Dict:
    """Analyze the stdlib and return categorized information."""
    all_modules = get_stdlib_modules()

    included_modules = []
    skipped_modules = []
    builtin_collisions = defaultdict(list)

    for module_name in sorted(all_modules):
        if should_skip_module(module_name):
            skipped_modules.append(module_name)
            continue

        # Check if module is useful
        if module_name not in USEFUL_MODULES:
            # Skip modules not in useful list for now
            skipped_modules.append(module_name)
            continue

        exportable, all_members = get_module_members(module_name)

        # Check for collisions
        collisions = []
        for member in exportable:
            if check_builtins_collision(member):
                collisions.append(member)
                builtin_collisions[member].append(module_name)

        included_modules.append({
            'name': module_name,
            'members': exportable,
            'collisions': collisions,
        })

    return {
        'included': included_modules,
        'skipped': skipped_modules,
        'builtin_collisions': dict(builtin_collisions),
        'python_version': sys.version_info[:3],
    }


def main():
    """Main entry point."""
    print(f"Python version: {'.'.join(map(str, sys.version_info[:3]))}")
    print()

    analysis = analyze_stdlib()

    print(f"Included modules: {len(analysis['included'])}")
    print(f"Skipped modules: {len(analysis['skipped'])}")
    print()

    print("Modules to include:")
    for mod in analysis['included']:
        collision_note = f" ({len(mod['collisions'])} collisions)" if mod['collisions'] else ""
        print(f"  - {mod['name']}{collision_note}")

    print()
    print("Builtin collisions to handle:")
    for name, modules in sorted(analysis['builtin_collisions'].items()):
        print(f"  - {name}: {', '.join(modules)}")


if __name__ == '__main__':
    main()
