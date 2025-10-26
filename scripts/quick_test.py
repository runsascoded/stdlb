#!/usr/bin/env python
"""Quick test of stdlb functionality."""
import sys
from pathlib import Path

# Add parent directory to path so we can import stdlb
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

print(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

# Test import
from stdlb import *

# Basic functionality tests
assert getcwd() is not None, "getcwd() failed"
assert datetime is not None, "datetime module not available"
assert dt is not None, "dt alias not available"
assert dt == datetime.datetime, "dt should equal datetime.datetime"

# Module preservation
assert hasattr(datetime, 'datetime'), "datetime should be a module"
assert hasattr(time, 'sleep'), "time should be a module"
assert hasattr(glob, 'glob'), "glob should be a module"

# Builtins not shadowed
builtins_dict = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
assert open == builtins_dict['open'], "open() should be builtin"
assert compile == builtins_dict['compile'], "compile() should be builtin"
assert pow == builtins_dict['pow'], "pow() should be builtin"

# Collision resolution
assert hasattr(path, 'join'), "path should be os.path"
result = join('/foo', 'bar')
if sys.platform == 'win32':
    # Windows preserves forward slash in first arg but joins with backslash
    assert result == '/foo\\bar', f"Expected '/foo\\bar' on Windows, got {result!r}"
else:
    # Unix uses forward slashes
    assert result == '/foo/bar', f"Expected '/foo/bar' on Unix, got {result!r}"

# Version-specific features
if sys.version_info >= (3, 11):
    import stdlb
    assert hasattr(stdlb, 'loads') or hasattr(stdlb, 'load'), "tomllib should be available in 3.11+"

if sys.version_info >= (3, 9):
    try:
        from stdlb import TopologicalSorter, ZoneInfo
        assert TopologicalSorter is not None, "TopologicalSorter should be available"
        assert ZoneInfo is not None, "ZoneInfo should be available"
    except ImportError as e:
        raise AssertionError(f"graphlib/zoneinfo should be available in 3.9+: {e}")

print("All tests passed")
