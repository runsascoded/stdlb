#!/usr/bin/env python
"""Document all exports from stdlb for the current platform and Python version.

This helps identify platform-specific and version-specific symbols.
Run via GitHub Actions on multiple platforms to compare.
"""
import sys
import platform as platform_module
from collections import defaultdict

# Import stdlb
from stdlb import *

print(f"Platform: {platform_module.system()} {platform_module.release()}")
print(f"Python: {sys.version}")
print(f"=" * 80)
print()

# Get all exports
all_exports = sorted([name for name in dir() if not name.startswith('_')])

print(f"Total exports: {len(all_exports)}")
print()

# Categorize by type and case
uppercase = [n for n in all_exports if n.isupper()]
lowercase = [n for n in all_exports if not n.isupper()]
classes = []
functions = []
modules = []
constants = []

for name in lowercase:
    obj = globals()[name]
    obj_type = type(obj).__name__
    if obj_type in ('type', 'ABCMeta'):
        classes.append(name)
    elif obj_type in ('function', 'builtin_function_or_method', 'method_descriptor'):
        functions.append(name)
    elif obj_type == 'module':
        modules.append(name)
    else:
        constants.append(name)

print(f"Uppercase constants: {len(uppercase)}")
print(f"Classes: {len(classes)}")
print(f"Functions: {len(functions)}")
print(f"Modules: {len(modules)}")
print(f"Other constants: {len(constants)}")
print()

# Group uppercase constants by prefix
print("=" * 80)
print("UPPERCASE CONSTANTS BY PREFIX")
print("=" * 80)
print()

prefixes = defaultdict(list)
for name in uppercase:
    prefix = name.split('_')[0] if '_' in name else name
    prefixes[prefix].append(name)

for prefix in sorted(prefixes.keys()):
    names = prefixes[prefix]
    print(f"{prefix}_* ({len(names)} symbols):")
    if len(names) <= 20:
        for name in names:
            obj = globals()[name]
            obj_type = type(obj).__name__
            # Try to get module
            module = getattr(obj, '__module__', '<builtin>')
            print(f"  {name}: {obj_type} from {module}")
    else:
        print(f"  {names[:10]}")
        print(f"  ... and {len(names) - 10} more")
    print()

# List potentially platform-specific prefixes
print("=" * 80)
print("LIKELY PLATFORM-SPECIFIC PREFIXES")
print("=" * 80)
print()

platform_specific_candidates = [
    'AF', 'AI', 'EAI', 'IPPROTO', 'IP', 'IPV6', 'SO', 'TCP',  # socket
    'MSG', 'NI', 'SHUT', 'SCM', 'LOCAL', 'PF', 'SYSPROTO',     # socket
    'SIG',  # signal
    'O', 'F', 'CLD', 'P', 'POSIX', 'PRIO', 'RTLD', 'SCHED',   # os
    'CLOCK',  # time/os
]

for prefix in platform_specific_candidates:
    matching = [n for n in uppercase if n.startswith(prefix + '_') or n == prefix]
    if matching:
        print(f"{prefix}_*: {len(matching)} symbols")
        print(f"  Examples: {matching[:5]}")
print()

# Known version-specific symbols
print("=" * 80)
print("PYTHON VERSION-SPECIFIC CHECK")
print("=" * 80)
print()

version_specific = [
    'NameConstant', 'Num', 'Str',  # ast, removed in 3.12+
    'SafeConfigParser',  # configparser, removed in 3.12+
    'graphlib', 'zoneinfo',  # added in 3.9
    'tomllib',  # added in 3.11
]

for name in version_specific:
    present = name in all_exports
    print(f"{name}: {'PRESENT' if present else 'MISSING'}")
