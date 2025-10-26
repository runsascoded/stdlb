# `stdlb`

Wildcard-import the Python standard library

[![PyPI badge: "stdlb" library](https://img.shields.io/pypi/v/stdlb.svg)](https://pypi.python.org/pypi/stdlb)

```python
from stdlb import *

# Most of the standard library is now available:
print(f"Current directory: {getcwd()}")
stderr.write(f"Python version: {version}\n")
print(f"Today: {dt.now()}")
data = {"key": "value"}
dumps(data)  # json.dumps
```

**Features:**
- 🎯 **Comprehensive coverage**: 2127 symbols from 79+ stdlib modules (up from 841 symbols in v0.0.4)
- 🐍 **Python 3.10-3.13 support**: Automatically includes version-specific modules
- ⚡ **Fast**: Imports in ~57ms
- 🔒 **Safe**: Preserves all `__builtins__`, resolves name collisions intelligently
- 🧪 **Well-tested**: Snapshot testing tracks all exports to prevent regressions

- [Install](#install)
- [Coverage](#coverage)
- [Notes](#notes)
    - [Collision Resolution](#collisions)
        - [`__builtins` vs. module members](#builtins)
        - [Module/Members](#module-members)
    - [Aliases](#aliases)
    - [Custom `cached_property`](#cached-property)
- [Development](#development)

## Install <a id="install"></a>
```bash
pip install stdlb
```

## Coverage <a id="coverage"></a>

`stdlb` now includes 79+ stdlib modules, including:

**Core utilities**: `os`, `sys`, `pathlib`, `subprocess`, `tempfile`, `shutil`, `glob`, `fnmatch`

**Data structures & algorithms**: `collections`, `itertools`, `heapq`, `bisect`, `array`, `queue`

**Text processing**: `re`, `string`, `textwrap`, `difflib`, `unicodedata`

**Data formats**: `json`, `csv`, `configparser`, `pickle`, `base64`, `binascii`

**Math & numbers**: `math`, `cmath`, `decimal`, `fractions`, `statistics`, `random`, `secrets`

**Date & time**: `datetime`, `time`, `calendar`, `timeit`

**Functional programming**: `functools`, `operator`, `itertools`

**Type hints**: `typing`, `types`, `dataclasses`, `enum`

**Concurrency**: `threading`, `asyncio`, `subprocess`, `signal`

**Networking**: `socket`, `urllib`, `http`, `html`, `mimetypes`

**Cryptography**: `hashlib`, `hmac`, `secrets`

**Compression**: `zlib`, `zipfile`

**And more**: `logging`, `warnings`, `traceback`, `pprint`, `platform`, `locale`, etc.

### Version-specific modules

- **Python 3.9+**: `graphlib`, `zoneinfo`
- **Python 3.11+**: `tomllib`

## Notes <a id="notes"></a>
I've found this especially useful in Jupyter notebooks, where I don't have an easy "add `import` statements as I add code" setup.

Import time is reasonable (~57ms) for the comprehensive coverage provided. See `scripts/benchmark_import.py` for detailed measurements.

### Collision Resolution <a id="collisions"></a>

#### `__builtins` vs. module members <a id="builtins"></a>
`stdlb` avoids overwriting `__builtins__` with conflicting module members, e.g.:
- `open` vs. `os.open`
- `compile` vs. `re.compile`
- `pow` vs. `math.pow`
- `copyright` vs. `sys.copyright`
- `BlockingIOError` vs. `io.BlockingIOError`

[`test.ipynb`](test.ipynb) is executed as part of [`ci.yml`](.github/workflows/ci.yml) to verify there are no `__builtins__` are unexpectedly shadowed.

#### Module/Members <a id="module-members"></a>
In a few cases, a top-level standard library module also contains a member with the same name (e.g. `datetime`, `shlex`, `time`). `stdlb` makes an effort to ensure the module "wins" in this case:

```python
from stdlb import *

datetime  # <module 'datetime' from '$PYTHON_HOME/lib/python3.9/datetime.py'>
shlex     # <module 'shlex' from '$PYTHON_HOME/lib/python3.9/shlex.py'>
time      # <module 'time' (built-in)>
```

A few names are disambiguated with the most sensible-seeming defaults:
```python
path     # resolves to os.path, not sys.path
join     # os.path.join, not shlex.join
Path     # pathlib.Path, not zipfile.Path
error    # re.error, not zlib.error
compress # itertools.compress, not zlib.compress
repeat   # itertools.repeat, not timeit.repeat
```

Use `scripts/compare_versions.py` to compare exports between versions and identify collisions.

### Aliases <a id="aliases"></a>

For convenience, `datetime.datetime` is also exposed as `dt`, and a few of its members are exported directly:
```python
dt.now()       # datetime.datetime(2023, 8, 3, 10, 9, 43, 981458)
fromtimestamp  # datetime.datetime.fromtimestamp
fromisoformat  # datetime.datetime.fromisoformat
```

### Custom `cached_property` <a id="cached-property"></a>
One additional bit of functionality is [this custom `cached_property` decorator](src/stdlb/cached_property.py), which omits an unnecessary/unserializable lock found in `functools.cached_property`. [cpython#87634](https://github.com/python/cpython/issues/87634) has more info, seems like [a fix is coming in Python 3.12](https://github.com/python/cpython/issues/87634#issuecomment-1467140709).

## Development <a id="development"></a>

This project uses [uv](https://github.com/astral-sh/uv) for development.

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Test across multiple Python versions
for v in .venv/3.*/bin/python; do $v scripts/quick_test.py; done

# Regenerate __init__.py (if needed)
python scripts/generate_init.py > src/stdlb/__init__.py

# Update exports snapshot
python scripts/snapshot_exports.py

# Compare versions to check for regressions
python scripts/compare_versions.py v0.0.4 HEAD
```

### Helper Scripts

#### Code Generation
- **`scripts/discover_stdlib.py`**: Analyze the stdlib and identify useful modules to include
- **`scripts/generate_init.py`**: Generate `src/stdlb/__init__.py` from configuration
  - Handles version-specific imports, module preservation, collision resolution
  - Configuration in `VERSION_REQUIREMENTS`, `PRESERVE_MODULE`, `COLLISION_PREFERENCES`

#### Testing & Quality Assurance
- **`scripts/quick_test.py`**: Quick functionality test across Python versions
- **`scripts/benchmark_import.py`**: Measure import time performance
- **`scripts/snapshot_exports.py`**: Generate JSON snapshot of all exported symbols
  - Output: `tests/exports_snapshot.json` (2127 symbols tracked)
  - Used by `tests/test_exports_snapshot.py` for regression detection
- **`scripts/compare_versions.py`**: Compare exports between git refs
  ```bash
  # Compare any two versions
  python scripts/compare_versions.py v0.0.4 v0.1.0
  python scripts/compare_versions.py <old-ref> <new-ref>

  # Show only FQN changes (collisions)
  python scripts/compare_versions.py v0.0.4 HEAD 2>/dev/null | grep -A 50 "Changed FQN"
  ```
