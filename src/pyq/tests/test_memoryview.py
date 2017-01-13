from __future__ import absolute_import
from __future__ import unicode_literals
import pytest
import sys
from pyq import *

from .test_k import K_INT_CODE, K_LONG_CODE

@pytest.mark.parametrize(('t', 'r'), [
    ('?', 'b'),
    ('B', 'x'),
    ('h', 'h'),
    (K_INT_CODE, 'i'),
    (K_LONG_CODE, 'j'),
    ('f', 'e'),
    ('d', 'f'),
    ('s', 'c'),
])
def test_format(t, r):
    x = q('0' + r)
    m = memoryview(x)
    assert m.format == t


@pytest.mark.parametrize(('t', 'size'), [
    ('b', 1),
    ('g', 16),
    ('x', 1),
    ('h', 2),
    ('i', 4),
    ('j', 8),
    ('e', 4),
    ('f', 8),
    ('c', 1),
    ('p', 8),
    ('m', 4),
    ('d', 4),
    ('z', 8),
    ('n', 8),
    ('u', 4),
    ('v', 4),
    ('t', 4),
])
def test_itemsize(t, size):
    x = q('"%c"$()' % t)
    m = memoryview(x)
    assert m.itemsize == size


@pytest.mark.parametrize(('expr', 'ndim'), [
    ('0', 0),
    ('0 0', 1),
    ('(1 2;3 4)', 2),
])
def test_ndim(expr, ndim):
    x = q(expr)
    m = memoryview(x)
    assert m.ndim == ndim

@pytest.mark.parametrize(('expr', 'shape'), [
    ('0', None if sys.version_info[:2] < (3, 3) else ()),
    ('0 0', (2,)),
    ('(1 2 3;4 5 6)', (2, 3)),
])
def test_shape(expr, shape):
    x = q(expr)
    m = memoryview(x)
    assert m.shape == shape


@pytest.mark.parametrize(('expr', 'ro'), [
    ('0', False),
    ('`s#0 1', True),
    ('(1 2;3 4)', False),
])
def test_readonly(expr, ro):
    x = q(expr)
    m = memoryview(x)
    assert m.readonly == ro


@pytest.mark.parametrize('x', [
    '()', '(1;`)', '(1 2;3 4f)', '(1 2 3;4 5)',
])
def test_memoryview_errors(x):
    k = q(x)
    with pytest.raises(BufferError):
        memoryview(k)


def test_memoryview_bytes():
    x = q('0x203040')
    assert memoryview(x).tolist() == [0x20, 0x30, 0x40]

    y = q('"x"$"ABCD"')
    assert memoryview(y).tobytes() == b'ABCD'


def test_memoryview_enum(q):
    x = q('`sym?`a`b`c')
    m = memoryview(x)
    assert m.format == K_INT_CODE
