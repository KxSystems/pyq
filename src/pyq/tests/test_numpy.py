from __future__ import absolute_import

try:
    import numpy
    from numpy import ma
except ImportError:
    numpy = ma = None

import pytest

import pyq
from pyq import *
from pyq import _PY3K, Q_VERSION
from .test_k import K_INT_CODE, K_LONG_CODE

SYM_NA = int(K.int.na if Q_VERSION < 3.6 else K.long.na)

pytestmark = pytest.mark.skipif(numpy is None, reason="numpy is not installed")
SIZE_OF_PTR = pyq._k.SIZEOF_VOID_P

SIMPLE_DTYPES = 'bool uint8 int16 int32 int64 float32 float64'.split()
# TODO: Add support for the "Y" unit.  What to do with ps and as?
# TIME_UNITS = 'Y M W D h m s ms us ns ps as'.split()
TIME_UNITS = 'M W D h m s ms us ns'.split()
DATETIME_DTYPES = ['datetime64[%s]' % unit for unit in TIME_UNITS]
TIMEDELTA_DTYPES = ['timedelta64[%s]' % unit for unit in TIME_UNITS if
                    unit != 'M']


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
        (12, 'M', 8),
        (13, 'M', 8),
        (14, 'M', 8),
        # (15, 'M', 8),  # datetime
        (16, 'm', 8),
        (17, 'm', 8),
        (18, 'm', 8),
        (19, 'm', 8),
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


@pytest.mark.skipif("pyq.Q_VERSION < 3")
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

    a = numpy.array(['2001-01-01T00Z'], dtype='M8[ns]')
    assert K(a) == q('enlist 2001.01.01D00')

    a = numpy.array(['2001-01-01T00Z'], dtype='M8[h]')
    assert K(a) == q('enlist 2001.01.01D00')

    a = numpy.array(['2001-01-01T00Z'], dtype='M8[m]')
    assert K(a) == q('enlist 2001.01.01D00')

    a = numpy.array(['2001-01-01T00Z'], dtype='M8[s]')
    assert K(a) == q('enlist 2001.01.01D00')

    a = numpy.array(['2001-01-01T00Z'], dtype='M8[ms]')
    assert K(a) == q('enlist 2001.01.01D00')

    a = numpy.array(['2001-01-01T00Z'], dtype='M8[us]')
    assert K(a) == q('enlist 2001.01.01D00')


def test_datetime64_scalar():
    a = numpy.array('2001-01-01', dtype='M8')
    assert K(a) == q('2001.01.01')

    a = numpy.datetime64(1, 'Y')
    assert K(a) == q('1971.01m')

    a = numpy.datetime64(1, 'M')
    assert K(a) == q('1970.02m')

    a = numpy.datetime64(1, 'W')
    assert K(a) == q('1970.01.08')

    a = numpy.array('2001-01-01T00Z', dtype='M8[ns]')
    assert K(a) == q('2001.01.01D00')

    a = numpy.array('2001-01-01T00Z', dtype='M8[h]')
    assert K(a) == q('2001.01.01D00')

    a = numpy.array('2001-01-01T00Z', dtype='M8[m]')
    assert K(a) == q('2001.01.01D00')

    a = numpy.array('2001-01-01T00Z', dtype='M8[s]')
    assert K(a) == q('2001.01.01D00')

    a = numpy.array('2001-01-01T00Z', dtype='M8[ms]')
    assert K(a) == q('2001.01.01D00')

    a = numpy.array('2001-01-01T00Z', dtype='M8[us]')
    assert K(a) == q('2001.01.01D00')


def test_timedelta64_vector():
    a = numpy.array([1, 2, 3], dtype='m8[s]')
    assert K(a) == q('"n"$ 1 2 3 * 1000000000j')

    a = numpy.array([1, 2, 3], dtype='m8[ms]')
    assert K(a) == q('"n"$ 1 2 3 * 1000000j')

    a = numpy.array([1, 2, 3], dtype='m8[us]')
    assert K(a) == q('"n"$ 1 2 3 * 1000j')

    a = numpy.array([1, 2, 3], dtype='m8[ns]')
    assert K(a) == q('"n"$ 1 2 3j')


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
    a = numpy.asarray(x.data)
    a.tolist() == [0, 1, 2]


@pytest.mark.parametrize('data, dtype, kstr', [
    ([1, 0, 1], bool, '101b'),
    ([1, 2, 3], 'h', '1 2 3h'),
    ([1, 2, 3], 'i', '1 2 3i'),
    ([1, 2, 3], 'q', '1 2 3j'),
    ([1, 2, 3], 'f', '1 2 3e'),
    ([1, 2, 3], 'd', '1 2 3f'),
])
def test_from_array_struct(data, dtype, kstr):
    a = numpy.array(data, dtype)
    x = K._from_array_struct(a.__array_struct__)
    assert x == q(kstr)


def test_from_array_struct_errors():
    with pytest.raises(TypeError):
        K._from_array_struct()
    # XXX: Shouldn't this be a TypeError?
    with pytest.raises(ValueError):
        K._from_array_struct(None)
    # XXX: Shouldn't this be a NotImplementedError?
    # a = numpy.zeros((1, 1))
    # with pytest.raises(ValueError):
    #     K._from_array_struct(a.__array_struct__)
    a = numpy.array(['', None], 'O')
    # XXX: Shouldn't this be a TypeError?
    with pytest.raises(ValueError):
        K._from_array_struct(a.__array_struct__)


def test_numpy_in_versions(capsys):
    versions()
    out = capsys.readouterr()[not _PY3K]
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


@pytest.mark.parametrize('kstr, typestr', zip(
    ('0b;0x00;0h;0i;0j;0e;0.0;" ";`;2000.01m;2000.01.01;'
     '2000.01.01T00:00:00.000;00:00;00:00:00;00:00:00.000').split(';'),
    ('<b1,<u1,<i2,<i4,<i8,<f4,<f8,<S1,'
     '|O%d,<i4,<i4,<f8,<i4,<i4,<i4' % SIZE_OF_PTR).split(',')))
def test_array_typestr(kstr, typestr):
    x = q(kstr)
    assert x.__array_typestr__ == typestr


def test_there_and_back_again(q):
    x = q.til(10)
    a = numpy.asarray(x)
    y = K(a)
    assert x is y


def test_table_to_array():
    t = q('([]a:1 2;b:"xy")')
    a = numpy.array(t)
    assert a.tolist() == [(1, b'x'),
                          (2, b'y')]


@pytest.mark.parametrize('dtype',
                         SIMPLE_DTYPES + TIMEDELTA_DTYPES + DATETIME_DTYPES)
def test_table_to_array_all_types(dtype):
    c = numpy.zeros(1, dtype)
    t = +q('!', ['c'], (c,))
    a = numpy.asarray(t)
    assert a.dtype.names == ('c',)
    assert numpy.array_equiv(c, a['c'])


@pytest.mark.skipif("q('.z.K') < 3")
@pytest.mark.parametrize('dtype', SIMPLE_DTYPES)
def test_2d(dtype):
    a = numpy.zeros((2, 3), dtype)
    x = K(a)
    y = K(a.flatten())
    assert x.raze == y


@pytest.mark.skipif("q('.z.K') < 3.4")
@pytest.mark.parametrize('dtype', SIMPLE_DTYPES)
def test_3d(dtype):
    a = numpy.zeros((2, 3, 2), dtype)
    x = K(a)
    y = K(a.flatten())
    assert x.raze.raze == y


@pytest.mark.parametrize('dtype', SIMPLE_DTYPES)
def test_0d(dtype):
    a = numpy.ones((), dtype)
    x = K(a)
    assert x.enlist[0] == 1


def test_enum_to_array(q):
    x = q('`sym?`a`b')
    a = numpy.array(['a', 'b'], dtype=object)
    assert numpy.array_equiv(x, a)


@pytest.mark.skipif("q('.z.K') < 3.4")
@pytest.mark.parametrize('dtype', SIMPLE_DTYPES)
def test_2d_roundtrip(dtype):
    a = numpy.zeros((3, 2), dtype)
    x = K(a)
    b = numpy.array(x)
    assert numpy.array_equiv(a, b)


def test_priority():
    a = numpy.arange(2)
    b = q.til(2)
    assert isinstance(a + b, K)
    assert isinstance(b + a, K)


class A(object):
    @property
    def __array_struct__(self):
        raise TypeError


def test_broken_array_struct():
    with pytest.raises(TypeError):
        K(A())


def test_broken_mask():
    class B(object):
        a = numpy.zeros(0)

        @property
        def __array_struct__(self):
            return self.a.__array_struct__

        @property
        def mask(self):
            raise TypeError

    with pytest.raises(TypeError):
        K(B())


def test_strided_nd():
    a = numpy.zeros((2, 2, 2))
    with pytest.raises(ValueError):
        K(a.diagonal())


def test_0d_str():
    a = numpy.array('x', 'O')
    assert K(a) == 'x'


def test_call_python(q):
    def f():
        return numpy.array([1.0, 2.0])
    q.f = f
    assert q("f()") == [1.0, 2.0]


def test_enum_to_numpy(q):
    x = q('`sym?`a`b`')
    assert numpy.asarray(x.data).tolist() == [0, 1, SYM_NA]
