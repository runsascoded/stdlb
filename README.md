# `std`

Wildcard-import the Python standard library
```python
from std import *

# Most of the standard library is now available:
print(f"Current directory: {getcwd()}")
stderr.write("Python version: {version}\n")
```

## Install
```bash
pip install std
```

## Notes
I've found this especially useful in Jupyter notebooks, where I don't have an easy "add `import` statements as I add code" setup.

Importing seems to take a few milliseconds (on my Macbook Air):
```ipython
%%time
from std import *
# CPU times: user 914 µs, sys: 397 µs, total: 1.31 ms
# Wall time: 1.6 ms
```

### Custom `cached_property`
One additional bit of functionality is [this custom `cached_property` decorator](std/cached_property.py), which omits an unnecessary/unserializable lock found in `functools.cached_property`. [cpython#87634](https://github.com/python/cpython/issues/87634) has more info, seems like [a fix is coming in Python 3.12](https://github.com/python/cpython/issues/87634#issuecomment-1467140709).
