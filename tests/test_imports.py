"""Test stdlb imports across Python versions."""
import sys
import pytest

# Import at module level
from stdlb import *


def test_basic_import():
    """Test that stdlb can be imported."""
    # Check basic functionality
    assert getcwd() is not None
    assert datetime is not None
    assert dt is not None


def test_module_preservation():
    """Test that module references are preserved."""
    # These should be modules, not members
    assert hasattr(datetime, 'datetime')
    assert hasattr(time, 'sleep')
    assert hasattr(shlex, 'split')
    assert hasattr(glob, 'glob')


def test_builtins_not_shadowed():
    """Test that builtins are not shadowed."""
    # These should all be the builtin versions
    builtins_dict = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
    assert open == builtins_dict['open']
    assert compile == builtins_dict['compile']
    assert pow == builtins_dict['pow']
    assert copyright == builtins_dict['copyright']


def test_collision_resolution():
    """Test that name collisions are resolved correctly."""
    # path should be os.path, not sys.path
    assert hasattr(path, 'join')

    # join should be os.path.join, not shlex.join
    result = join('/foo', 'bar')
    if sys.platform == 'win32':
        # Windows preserves forward slash in first arg but joins with backslash
        assert result == '/foo\\bar', f"Expected '/foo\\bar' on Windows, got {result!r}"
    else:
        # Unix uses forward slashes
        assert result == '/foo/bar', f"Expected '/foo/bar' on Unix, got {result!r}"


def test_datetime_aliases():
    """Test datetime convenience aliases."""
    assert dt == datetime.datetime
    assert fromtimestamp == datetime.datetime.fromtimestamp
    assert fromisoformat == datetime.datetime.fromisoformat


@pytest.mark.skipif(sys.version_info < (3, 11), reason="tomllib added in 3.11")
def test_tomllib_available():
    """Test that tomllib is available in Python 3.11+."""
    import stdlb
    assert hasattr(stdlb, 'loads') or hasattr(stdlb, 'load')  # tomllib functions


@pytest.mark.skipif(sys.version_info < (3, 9), reason="graphlib added in 3.9")
def test_graphlib_available():
    """Test that graphlib is available in Python 3.9+."""
    try:
        from stdlb import TopologicalSorter
        assert TopologicalSorter is not None
    except ImportError:
        pytest.fail("graphlib.TopologicalSorter should be available")


@pytest.mark.skipif(sys.version_info < (3, 9), reason="zoneinfo added in 3.9")
def test_zoneinfo_available():
    """Test that zoneinfo is available in Python 3.9+."""
    try:
        from stdlb import ZoneInfo
        assert ZoneInfo is not None
    except ImportError:
        pytest.fail("zoneinfo.ZoneInfo should be available")


def test_sys_members():
    """Test that sys members are exported."""
    assert stderr is not None
    assert stdout is not None
    assert version is not None
