from __future__ import absolute_import
from pyq import q
import py


def test_pypath():
    p = py.path.local('/abc/def')
    assert q('::', p) == ':' + p.strpath
