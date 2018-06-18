from __future__ import absolute_import
import py


def test_pypath(q):
    p = py.path.local('/abc/def')
    # NB: On Windows, the result is ":C:/abc/def"
    assert str(q('::', p)).endswith(':/abc/def')
