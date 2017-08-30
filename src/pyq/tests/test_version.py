from __future__ import absolute_import
import sys
import pytest
import pkg_resources


def test_version():
    from pyq import __version__ as v
    pv = pkg_resources.parse_version(v)
    assert pv
    assert v != 'unknown'


@pytest.fixture
def no_version_pyq(monkeypatch):
    monkeypatch.setitem(sys.modules, 'pyq.version', None)
    monkeypatch.delitem(sys.modules, 'pyq', raising=False)
    monkeypatch.delitem(sys.modules, 'pyq._k', raising=False)
    import pyq
    return pyq


def test_no_version(no_version_pyq):
    assert no_version_pyq.__version__ == 'unknown'
