# `stdlb`

Wildcard-import the Python standard library

```python
from stdlb import *

# Most of the standard library is now available:
print(f"Current directory: {getcwd()}")
stderr.write("Python version: {version}\n")
```

## Install
```bash
pip install stdlb
```

## Notes
I've found this especially useful in Jupyter notebooks, where I don't have an easy "add `import` statements as I add code" setup.

Importing seems to take a few milliseconds (on my Macbook Air):
```ipython
%%time
from stdlb import *
# CPU times: user 914 µs, sys: 397 µs, total: 1.31 ms
# Wall time: 1.6 ms
```

### Collisions / Aliases
In a few cases, a top-level standard library module also contains a member with the same name (e.g. `datetime`, `shlex`). `stdlb` makes an effort to ensure the module "wins" in this case:

```python
from stdlb import *

datetime
# <module 'datetime' from '$PYTHON_HOME/lib/python3.9/datetime.py'>
shlex
# <module 'shlex' from '$PYTHON_HOME/lib/python3.9/shlex.py'>
```

For convenience, `datetime.datetime` is also exposed as `dt`:
```python
dt.now()
# datetime.datetime(2023, 8, 3, 10, 9, 43, 981458)
```

### Custom `cached_property`
One additional bit of functionality is [this custom `cached_property` decorator](stdlb/cached_property.py), which omits an unnecessary/unserializable lock found in `functools.cached_property`. [cpython#87634](https://github.com/python/cpython/issues/87634) has more info, seems like [a fix is coming in Python 3.12](https://github.com/python/cpython/issues/87634#issuecomment-1467140709).
