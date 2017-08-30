from __future__ import absolute_import
import pytest
import os

try:
    import pathlib
except ImportError:
    try:
        import pathlib2 as pathlib
    except ImportError:
        pathlib = None
from pyq import K

pytestmark = pytest.mark.skipif(pathlib is None,
                                reason="pathlib is not available")


@pytest.mark.parametrize('x', [
    'a',
    os.path.join('a', 'b'),
    os.path.join('a', 'b', 'c'),
])
def test_convert_path(x):
    p = pathlib.Path(x)
    assert str(K(p)) == ':' + x
