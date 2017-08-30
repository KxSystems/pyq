from __future__ import absolute_import
import sys
import pytest


@pytest.fixture
def no_numpy_pyq(monkeypatch):
    monkeypatch.setitem(sys.modules, 'numpy', None)
    pyq_modules = [m for m in sys.modules
                   if m is not None and (m == 'pyq' or m.startswith('pyq.'))]
    for m in pyq_modules:
        monkeypatch.delitem(sys.modules, m)
    import pyq
    return pyq


def test_no_numpy(no_numpy_pyq):
    # TODO: Figure out how to run all tests that don't require numpy.
    assert no_numpy_pyq.K(0) == 0
