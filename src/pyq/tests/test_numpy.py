from __future__ import absolute_import

try:
    import numpy
    from numpy import ma
except ImportError:
    numpy = ma = None

import pytest

import pyq
from pyq import *
from .test_k import K_INT_CODE, K_LONG_CODE

pytestmark = pytest.mark.skipif(numpy is None, reason="numpy is not installed")
SIZE_OF_PTR = pyq._k.SIZEOF_VOID_P


@pytest.mark.parametrize(('t', 'r'), [
    ('?', 'b'),
    ('h', 'h'),
    ('i', 'i'),
    ('q', 'j'),
    ('f', 'e'),
    ('d', 'f'),
])
def test_ndarray(t, r):
    a = numpy.zeros(0, t)
    assert K(a) == k('"%c"$()' % r)

    a = numpy.zeros(1, t)
    assert K(a) == k(',0' + r)


def test_ma():
    x = ma.array([1.0, 2, 3])
    assert K(x) == k('1.0 2 3')

    x = ma.masked_values([1.0, 0, 2], 0)
    assert K(x) == k('1 0n 2')

    s = ma.masked_values(0.0, 0)
    assert K(s) == k('0n')


@pytest.mark.parametrize(('n', 'k'), [
    ('int8', '0x01'),
    ('int16', '1h'),
    ('int32', '1i'),
    ('int64', '1j'),
    ('float32', '1e'),
    ('float64', '1f'),
])
def test_scalar_conversion(n, k):
    x = getattr(numpy, n)(1)
    assert K(x) == q(k)


@pytest.mark.parametrize('a', [
    '0n', '1i', '1j', '0.1f', '1e', '1h',
    '010101b',
    '0xdeadbeef',
    '0 0n 1 0n',
    '0 0N 1 0N',
    '1 2 3 0Nh',
    '0.0 0.1 0Nf',
    '"abracadabra"',
    '"s p a c e d"',
    '0.0 0.1 0Ne',
    '1 2 3 0Nj',
    '1 2 3 0Ni',
])
def test_ma_array_roundtrip(a):
    x = q(a)
    m = ma.array(x)

    assert K(m) == x


def test_ma_conversion():
    x = q('1 0N 2')
    m = ma.array(x)

    assert isinstance(m.mask, numpy.ndarray)


@pytest.mark.parametrize(
    't,char,size', [
        (1, '?', 1),
        (4, 'B', 1),
        (5, 'h', 2),
        (6, K_INT_CODE, 4),
        (7, K_LONG_CODE, 8),
        (8, 'f', 4),
        (9, 'd', 8),
        (10, 'S', 1),
        # (11, 'O', SIZE_OF_PTR)  # issue #589
        (12, K_LONG_CODE, 8),
        (13, K_INT_CODE, 4),
        (14, K_INT_CODE, 4),
        (15, 'd', 8),
        (16, K_LONG_CODE, 8),
        (17, K_INT_CODE, 4),
        (18, K_INT_CODE, 4),
        (19, K_INT_CODE, 4),
    ])
def test_empty(t, char, size):
    x = q('$[;()]', K._kh(t))
    a = numpy.array(x)

    assert a.dtype.char == char
    assert a.dtype.itemsize == size


def test_chartype():
    x = kp('abc')
    a = numpy.array(x)

    assert a.tolist() == [b'a', b'b', b'c']
    assert K(a) == x


def test_bytestype():
    x = q('0xabab')
    a = numpy.array(x)

    assert a.tolist() == [0xAB] * 2
    assert K(a) == x


@pytest.mark.xfail  # issue #591
def test_splayed_char(tmpdir):
    x = q('([]x:enlist"abc")')
    d = q('{sv[`;x,`x`]}', tmpdir)
    d.set(x)
    y = d.get.x
    a = numpy.array(y)

    assert y.inspect(b't') == 87
    assert a.dtype.char == 'S'
    assert a.tolist() == [b'a', b'b', b'c']


def test_symbol_list():
    x = K(['a'])
    a = numpy.array(x)
    assert numpy.array_equiv(a, ['a'])

    x = K(['a'] * 3)
    a = numpy.array(x, 'O')
    assert a[0] is a[1] is a[2] == 'a'


def test_settitem():
    a = numpy.array([1])
    a[0] = K(2)
    assert a[0] == 2


def test_issue652():
    a = numpy.array([(q('1h'), q('1i'), q('1j'))], dtype='h,i,q')
    assert a.dtype == numpy.dtype('h,i,q')


def test_datetime64_vector():
    a = numpy.array(['2001-01-01'] * 3, dtype='M8')
    assert K(a) == q('3#2001.01.01')


def test_datetime64_scalar():
    a = numpy.array('2001-01-01', dtype='M8')
    assert K(a) == q('2001.01.01')

    a = numpy.datetime64(1, 'Y')
    assert K(a) == q('1971.01m')

    a = numpy.datetime64(1, 'M')
    assert K(a) == q('1970.02m')

    a = numpy.datetime64(1, 'W')
    assert K(a) == q('1970.01.08')

    # a = numpy.array('2001-01-01T00', dtype='M8[ms]')
    # assert K(a) == q('2001.01.01')


def test_timedelta64_vector():
    a = numpy.array([1, 2, 3], dtype='m8[s]')
    assert K(a) == q('"n"$ 1 2 3 * 1000000000')

    a = numpy.array([1, 2, 3], dtype='m8[ms]')
    assert K(a) == q('"n"$ 1 2 3 * 1000000')

    a = numpy.array([1, 2, 3], dtype='m8[us]')
    assert K(a) == q('"n"$ 1 2 3 * 1000')

    a = numpy.array([1, 2, 3], dtype='m8[ns]')
    assert K(a) == q('"n"$ 1 2 3')


def test_timedelta64_scalar():
    a = numpy.timedelta64(1, 'W')
    assert K(a) == q('7D00:00:00')

    a = numpy.timedelta64(1, 'D')
    assert K(a) == q('1D00:00:00')

    a = numpy.timedelta64(1, 'h')
    assert K(a) == q('0D01:00:00')

    a = numpy.timedelta64(1, 'm')
    assert K(a) == q('0D00:01:00')

    a = numpy.timedelta64(1, 's')
    assert K(a) == q('0D00:00:01')

    a = numpy.timedelta64(1, 'ms')
    assert K(a) == q('0D00:00:00.001')

    a = numpy.timedelta64(1, 'us')
    assert K(a) == q('0D00:00:00.000001')

    a = numpy.timedelta64(1, 'ns')
    assert K(a) == q('0D00:00:00.000000001')


def test_record_arrays():
    a = numpy.array([(date(2001, 1, 1), 1, 3.14),
                     (date(2001, 1, 2), 2, 2.78), ],
                    dtype=[('date', 'M8[D]'), ('num', 'i2'), ('val', 'f')])
    t = K(a)
    assert t.date == q('2001.01.01 2001.01.02')
    assert t.num == q('1 2h')
    assert t.val == q('3.14 2.78e')

    r = K(a[0])
    assert r == q("`date`num`val!(2001.01.01;1h;3.14e)")


def test_unsupported_dtype_errors():
    with pytest.raises(TypeError):
        a = numpy.array('abc', dtype='S3')
        K(a)


@pytest.mark.parametrize('e', ['sym', 'other'])
def test_enum_conversion(q, e):
    x = q('`%s?`a`b`c' % e)
    a = numpy.asarray(x)
    a.tolist() == [0, 1, 2]


def test_numpy_in_versions(capsys):
    versions()
    out = capsys.readouterr()[not PY3K]
    assert 'NumPy' in out


def test_no_dtype():

    class NoDtype(numpy.ndarray):
        """A helper class to test error branches"""

        @property
        def dtype(self):
            raise AttributeError('intentional error')

    x = NoDtype([0], dtype='M8[D]')
    with pytest.raises(AttributeError) as info:
        K(x)
    assert 'intentional error' in str(info.value)
