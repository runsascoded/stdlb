#!/usr/bin/env python
"""Compare stdlb exports between git refs (tags, commits, branches).

Usage:
    python scripts/compare_versions.py v0.0.4 HEAD
    python scripts/compare_versions.py v0.0.4 main
"""
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from collections import Counter


def get_exports_for_ref(ref: str, repo_root: Path) -> dict[str, str | None]:
    """Get exports snapshot for a given git ref."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Export the tree at this ref
        subprocess.run(
            ['git', 'archive', ref],
            cwd=repo_root,
            stdout=open(tmppath / 'archive.tar', 'wb'),
            check=True,
        )

        # Extract archive
        subprocess.run(
            ['tar', 'xf', 'archive.tar'],
            cwd=tmppath,
            check=True,
        )

        # Write a helper script that does the import at module level
        helper_script = tmppath / '_get_exports.py'
        helper_script.write_text("""
import sys
import json

# Capture state before import
_before = set(globals().keys())

# Import stdlb
from stdlb import *

# Capture state after import
_after = set(globals().keys())

# Find new symbols
new_symbols = sorted(_after - _before - {'_before', '_after'})

# Build snapshot
snapshot = {}
for name in new_symbols:
    obj = globals()[name]

    # Get FQN
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
print(json.dumps(snapshot))
""")

        # Run the helper script
        result = subprocess.run(
            [sys.executable, str(helper_script)],
            cwd=tmppath,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"Error running helper script:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(1)

        return json.loads(result.stdout)


def print_diff(old_snapshot: dict, new_snapshot: dict, old_ref: str, new_ref: str):
    """Print a diff between two snapshots."""
    old_set = set(old_snapshot.keys())
    new_set = set(new_snapshot.keys())

    added = new_set - old_set
    removed = old_set - new_set
    common = old_set & new_set

    # Check for FQN changes in common symbols
    changed = {
        name for name in common
        if old_snapshot[name] != new_snapshot[name]
    }

    print(f"Comparing {old_ref} → {new_ref}")
    print(f"  {old_ref}: {len(old_set)} symbols")
    print(f"  {new_ref}: {len(new_set)} symbols")
    print()

    if added:
        print(f"✨ Added {len(added)} symbols:")
        for name in sorted(added)[:50]:
            fqn = new_snapshot[name]
            print(f"  + {name}" + (f" (from {fqn})" if fqn else ""))
        if len(added) > 50:
            print(f"  ... and {len(added) - 50} more")
        print()

        # Summarize by module
        modules = Counter()
        for name in added:
            fqn = new_snapshot[name]
            if fqn:
                module = fqn.split('.')[0]
                modules[module] += 1
        print(f"  Breakdown by module:")
        for module, count in modules.most_common(10):
            print(f"    {module}: {count}")
        if len(modules) > 10:
            print(f"    ... and {len(modules) - 10} more modules")
        print()

    if removed:
        print(f"❌ Removed {len(removed)} symbols:")
        for name in sorted(removed)[:50]:
            fqn = old_snapshot[name]
            print(f"  - {name}" + (f" (from {fqn})" if fqn else ""))
        if len(removed) > 50:
            print(f"  ... and {len(removed) - 50} more")
        print()

    if changed:
        print(f"🔄 Changed FQN for {len(changed)} symbols:")
        for name in sorted(changed)[:20]:
            print(f"  ~ {name}:")
            print(f"      {old_ref}: {old_snapshot[name]}")
            print(f"      {new_ref}: {new_snapshot[name]}")
        if len(changed) > 20:
            print(f"  ... and {len(changed) - 20} more")
        print()


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/compare_versions.py <old-ref> <new-ref>")
        print("Example: python scripts/compare_versions.py v0.0.4 HEAD")
        sys.exit(1)

    old_ref = sys.argv[1]
    new_ref = sys.argv[2]

    repo_root = Path(__file__).parent.parent

    print(f"Analyzing {old_ref}...")
    old_snapshot = get_exports_for_ref(old_ref, repo_root)

    print(f"Analyzing {new_ref}...")
    new_snapshot = get_exports_for_ref(new_ref, repo_root)

    print()
    print_diff(old_snapshot, new_snapshot, old_ref, new_ref)


if __name__ == '__main__':
    main()
