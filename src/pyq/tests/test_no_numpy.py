import sys


def test_no_numpy(monkeypatch):
    monkeypatch.setitem(sys.modules, 'numpy', None)
    pyq_modules = [m for m in sys.modules
                   if m == 'pyq' or m.startswith('pyq.')]
    for m in pyq_modules:
        monkeypatch.delitem(sys.modules, m)
    from pyq import K
    # TODO: Figure out how to run all tests that don't require numpy.
    assert K(0) == 0
