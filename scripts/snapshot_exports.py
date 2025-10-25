#!/usr/bin/env python
"""Snapshot all exports from stdlb for regression testing.

Captures all symbols exported by `from stdlb import *` along with their
fully-qualified names (FQNs) for comparison and regression detection.
"""
import sys
import json
from pathlib import Path

# Add parent directory to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

# Capture state before import
_before = set(globals().keys())

# Import stdlb
from stdlb import *

# Capture state after import
_after = set(globals().keys())

# Find new symbols (exclude our internal variables)
new_symbols = sorted(_after - _before - {'_before', '_after'})

# Build snapshot of all exports with their FQNs
snapshot = {}
for name in new_symbols:
    obj = globals()[name]

    # Get FQN (fully-qualified name)
    fqn = None
    if hasattr(obj, '__module__'):
        module = obj.__module__
        if hasattr(obj, '__qualname__'):
            fqn = f"{module}.{obj.__qualname__}"
        elif hasattr(obj, '__name__'):
            fqn = f"{module}.{obj.__name__}"
        else:
            fqn = f"{module}.{type(obj).__name__}"

    snapshot[name] = fqn

# Output as JSON
output_path = repo_root / 'tests' / 'exports_snapshot.json'
with open(output_path, 'w') as f:
    json.dump(snapshot, f, indent=2, sort_keys=True)

print(f"✓ Snapshot written to {output_path}")
print(f"  Total exports: {len(snapshot)}")

# Print summary of null FQNs
null_fqns = [name for name, fqn in snapshot.items() if fqn is None]
if null_fqns:
    print(f"\n  Symbols without FQN: {len(null_fqns)}")
    if len(null_fqns) <= 10:
        for name in null_fqns:
            print(f"    - {name}")
    else:
        for name in null_fqns[:10]:
            print(f"    - {name}")
        print(f"    ... and {len(null_fqns) - 10} more")
