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
- 🎯 **Comprehensive coverage**: 79+ stdlib modules available (up from ~20 in earlier versions)
- 🐍 **Python 3.10-3.13 support**: Automatically includes version-specific modules
- ⚡ **Fast**: Imports in ~2ms
- 🔒 **Safe**: Preserves all `__builtins__`, resolves name collisions intelligently

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

Importing seems to take a few milliseconds (on my Macbook Air):
```ipython
%%time
from stdlb import *
# CPU times: user 914 µs, sys: 397 µs, total: 1.31 ms
# Wall time: 1.6 ms
```

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
path  # resolves to os.path, not sys.path
join  # os.path.join, not shlex.join
```

### Aliases <a id="aliases"></a>

For convenience, `datetime.datetime` is also exposed as `dt`, and a few of its members are exported directly:
```python
dt.now()       # datetime.datetime(2023, 8, 3, 10, 9, 43, 981458)
fromtimestamp  # datetime.datetime.fromtimestamp
fromisoformat  # datetime.datetime.fromisoformat
```

### Custom `cached_property` <a id="cached-property"></a>
One additional bit of functionality is [this custom `cached_property` decorator](stdlb/cached_property.py), which omits an unnecessary/unserializable lock found in `functools.cached_property`. [cpython#87634](https://github.com/python/cpython/issues/87634) has more info, seems like [a fix is coming in Python 3.12](https://github.com/python/cpython/issues/87634#issuecomment-1467140709).

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
uv run python scripts/generate_init.py > stdlb/__init__.py
```

### Scripts

- `scripts/discover_stdlib.py`: Analyze the stdlib and identify modules to include
- `scripts/generate_init.py`: Generate `stdlb/__init__.py` from stdlib discovery
- `scripts/quick_test.py`: Quick functionality test across Python versions
