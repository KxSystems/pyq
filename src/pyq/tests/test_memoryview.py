from __future__ import absolute_import
from __future__ import unicode_literals

import struct

import pytest

from pyq import *
from pyq import _PY3K, Q_VERSION
from .test_k import K_INT_CODE, K_LONG_CODE

SYM_NA = int(K.int.na if Q_VERSION < 3.6 else K.long.na)


def mv_release(m):
    """Release memoryview"""
    release = getattr(m, 'release', None)
    if release is not None:
        release()


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
    mv_release(m)


@pytest.mark.parametrize(('t', 'size'), [
    ('b', 1),
    pytest.mark.skipif("1 or Q_VERSION < 3", ('g', 16)),  # TODO
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
    m = x.data
    assert m.itemsize == size
    # Scalar
    n = x.first.data
    assert n.ndim == 0
    # NB: Python 2 memoryview does not have nbytes
    assert getattr(n, 'nbytes', size) == m.itemsize == size
    mv_release(m)
    mv_release(n)


@pytest.mark.parametrize(('expr', 'ndim'), [
    ('0', 0),
    ('0 0', 1),
    ('(1 2;3 4)', 2),
])
def test_ndim(expr, ndim):
    x = q(expr)
    m = x.data
    assert m.ndim == ndim
    mv_release(m)


@pytest.mark.parametrize(('expr', 'shape'), [
    ('0', None if sys.version_info[:2] < (3, 3) else ()),
    ('0 0', (2,)),
    ('(1 2 3;4 5 6)', (2, 3)),
])
def test_shape(expr, shape):
    x = q(expr)
    m = x.data
    assert m.shape == shape
    mv_release(m)


@pytest.mark.parametrize(('expr', 'ro'), [
    ('0', False),
    ('`s#0 1', True),
    ('(1 2;3 4)', False),
])
def test_readonly(expr, ro):
    x = q(expr)
    m = x.data
    assert m.readonly == ro
    mv_release(m)


@pytest.mark.parametrize('x', [
    '()', '(1;`)', '(1 2;3 4f)', '(1 2 3;4 5)',
])
def test_memoryview_errors(x):
    k = q(x)
    with pytest.raises(BufferError):
        memoryview(k)


def test_memoryview_bytes():
    x = q('0x203040')
    m = memoryview(x)
    assert m.tolist() == [0x20, 0x30, 0x40]
    mv_release(m)

    y = q('"x"$"ABCD"')
    m = memoryview(y)
    assert m.tobytes() == b'ABCD'
    mv_release(m)


def test_memoryview_enum(q):
    x = q('`sym?`a`b`c')
    m = x.data
    assert m.format == K_INT_CODE if Q_VERSION < 3.6 else K_LONG_CODE
    mv_release(m)


@pytest.mark.parametrize('t', [
    'b',
    # XXX: GUID support is not implemented.
    # pytest.mark.skipif("Q_VERSION < 3", 'g'),
    'x',
    'h',
    'i',
    'j',
    'e',
    'f',
    'c',
])
def test_data_attr_eq_memoryview(t):
    # Start with an empty list
    x = q('"%c"$()' % t)
    m = memoryview(x)
    d = x.data
    assert m == d
    mv_release(m)
    mv_release(d)

    # Make a scalar
    x = 0 ^ x(0)
    m = memoryview(x)
    d = x.data
    assert m == d
    mv_release(m)
    mv_release(d)

    # Repeat a scalar
    x = q('3#', x)
    m = memoryview(x)
    d = x.data
    assert m == d
    mv_release(m)
    mv_release(d)


@pytest.mark.parametrize('x,f,s,u', [
    # ('::', 'P', 8),
    ('0b', '?', 1, False),
    ('0x0', "B", 1, 0),
    ('0h', "h", 2, 0),
    ('0i', K_INT_CODE, 4, 0),
    ('0j', K_LONG_CODE, 8, 0),
    ('0e', "f", 4, 0.0),
    ('0f', "d", 8, 0.0),
    ('" "', "s", 1, b' '),
    ('2000.01m', K_INT_CODE, 4, 0),
    ('2000.01.01', K_INT_CODE, 4, 0),
    ('2000.01.01T00:00', "d", 8, 0),
    ('00:00', K_INT_CODE, 4, 0),
    ('00:00:00', K_INT_CODE, 4, 0),
    ('00:00:00.000', K_INT_CODE, 4, 0),
    pytest.mark.skipif("'not implemented'", ('0Ng', "16B", 16, 0)),
    # TODO: Q_VERSION >= 3
])
def test_simple_view(x, f, s, u):
    m = q(x).data
    assert m.ndim == 0
    assert m.format == f
    assert m.itemsize == s
    v = struct.unpack(f, m.tobytes())
    assert v[0] == u
    mv_release(m)

    m = q("enlist " + x).data
    assert m.ndim == 1
    assert m.shape == (1,)
    assert m.strides == (s,)
    assert m.format == f
    assert m.itemsize == s
    if _PY3K:
        try:
            v = m[0]
        except NotImplementedError:
            pass
        else:
            assert v == u
    else:
        v = struct.unpack(f, m[0])
        assert v[0] == u
    mv_release(m)


@pytest.mark.skipif('not _PY3K')
def test_enum_data(q):
    x = q('`sym?`a`b`')
    assert x.data.tolist() == [0, 1, SYM_NA]
