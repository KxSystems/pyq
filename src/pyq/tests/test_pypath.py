from __future__ import absolute_import
from pyq import q
import py


def test_pypath():
    assert q('::', py.path.local('/abc/def')) == q("`:/abc/def")
