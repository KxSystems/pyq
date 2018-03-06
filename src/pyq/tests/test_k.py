from __future__ import absolute_import

import pytest
import sys
import os
import unittest
from datetime import datetime, date, time, timedelta
import math
import struct
from pyq import _k, Q_VERSION, _PY3K

if sys.maxsize == 2147483647:  # 32-bit platform
    K_INT_CODE, K_LONG_CODE = "lq"
else:
    K_INT_CODE, K_LONG_CODE = "il"


# extract _k.K class methods
for m in ('func k knk ktd err dot a1'
          ' ka kb kg kh ki kj ke kf kc ks km kd kz ku kv kt kp'
          ' ktn ktj kzz knz kpz b9 d9'
          ' B G H I J E F S K P M D N U V T xT xD').split():
    globals()[m] = getattr(_k.K, '_' + m)
del m


def q(*args):
    return k(0, *args)


q("\\e 0")  # disable q's debug on error

if Q_VERSION >= 3:
    kguid = _k.K._kguid
    UU = _k.K._UU


def kstr(x):
    return k(0, '-3!', x).inspect(b's')


class K_TestCase(unittest.TestCase):
    def assert_k_is(self, x, y):
        test = k(0, '~[%s;]' % y, x).inspect(b'g')
        if not test:
            raise self.failureException(kstr(x) + ' <> ' + y)


class AtomTestCase(K_TestCase):
    def test_ka(self):
        self.assert_k_is(ka(-_k.KB, 1), '1b')
        self.assert_k_is(ka(-_k.KJ, 1), '1j')
        self.assert_k_is(ktj(-_k.KP, 0), '2000.01.01D00:00:00.000000000')
        self.assert_k_is(ktj(-_k.KN, 0), '0D00:00:00.000000000')

    def test_kb(self):
        self.assert_k_is(kb(1), '1b')
        self.assert_k_is(kb(2 ** 70), '1b')
        self.assert_k_is(kb(True), '1b')
        self.assert_k_is(kb(0), '0b')
        self.assert_k_is(kb(False), '0b')
        self.assert_k_is(kb(None), '0b')

    def test_kg(self):
        self.assert_k_is(kg(1), '0x01')

    def test_kh(self):
        self.assert_k_is(kh(1), '1h')

    def test_ki(self):
        self.assert_k_is(ki(1), '1i')

    def test_kj(self):
        self.assert_k_is(kj(1), '1j')
        self.assert_k_is(kj(9223372036854775806), '9223372036854775806j')

    def test_ke(self):
        self.assert_k_is(ke(1), '1e')

    def test_kf(self):
        self.assert_k_is(kf(1), '1f')

    def test_kc(self):
        self.assert_k_is(kc(b'x'), '"x"')
        self.assert_k_is(kc('x'), '"x"')

    def test_ks(self):
        self.assert_k_is(ks('abc'), '`abc')

    def test_km(self):
        self.assert_k_is(km(1), '2000.02m')

    def test_kd(self):
        self.assert_k_is(kd(1), '2000.01.02')

    def test_kzz(self):
        self.assert_k_is(kzz(datetime(2000, 1, 2, 10, 11, 12, 1000)),
                         '2000.01.02T10:11:12.001')

    def test_kpz(self):
        self.assert_k_is(kpz(datetime(2000, 1, 2, 10, 11, 12, 1000)),
                         '2000.01.02D10:11:12.001000000')

    def test_knz(self):
        self.assert_k_is(knz(timedelta(100, 20, 1000)),
                         '100D00:00:20.001000000')

    def test_kz(self):
        self.assert_k_is(kz(1.5), '2000.01.02T12:00:00.000')

    def test_ku(self):
        self.assert_k_is(ku(1), '00:01')

    def test_kv(self):
        self.assert_k_is(kv(1), '00:00:01')

    def test_kt(self):
        self.assert_k_is(kt(1), '00:00:00.001')

    def test_id(self):
        x, y = ki(1), ki(1)
        self.assertNotEqual(x._id(), y._id())


class ListTestCase(K_TestCase):
    def test_kp(self):
        self.assert_k_is(kp("abc"), '"abc"')

    def test_I(self):
        self.assert_k_is(I([]), '`int$()')
        self.assert_k_is(I([1, 2]), '1 2i')

    def test_J(self):
        self.assert_k_is(J([]), '`long$()')
        self.assert_k_is(J([1, 2]), '1 2j')

    def test_F(self):
        self.assert_k_is(F([]), '`float$()')
        self.assert_k_is(F([1., 2.]), '1 2f')

    def test_S(self):
        self.assert_k_is(S([]), '`symbol$()')
        self.assert_k_is(S(['aa', 'bb']), '`aa`bb')

    def test_K(self):
        self.assert_k_is(K([]), '()')
        self.assert_k_is(K([ki(0), kf(1)]), '(0i;1f)')


class TableDictTestCase(K_TestCase):
    def test_xD(self):
        self.assert_k_is(xD(S('abc'), I(range(3))), '`a`b`c!0 1 2i')

    def test_xT(self):
        a = S('XYZ')
        b = kp('xyz')
        c = I([1, 2, 3])
        self.assert_k_is(xT(xD(S('abc'), K([a, b, c]))),
                         '([]a:`X`Y`Z;b:"xyz";c:1 2 3i)')

    def test_ktd(self):
        x = k(0, '([a:1 2 3]b:10 20 30)')
        y = '([]a:1 2 3;b:10 20 30)'
        self.assert_k_is(ktd(x), y)


class IterTestCase(K_TestCase):
    def test_bool(self):
        self.assertEqual(list(k(0, '101b')), [True, False, True])

    def test_byte(self):
        self.assertEqual(list(k(0, '0x010203')), [1, 2, 3])

    def test_char(self):
        self.assertEqual(list(kp('abc')), ['a', 'b', 'c'])

    def test_short(self):
        self.assertEqual(list(k(0, '1 2 3h')), [1, 2, 3])

    def test_int(self):
        x = [1, 2, 3, None]
        self.assertEqual(list(I(x)), x)

    def test_long(self):
        self.assertEqual(list(k(0, '1 2 3j')), [1, 2, 3])

    def test_date(self):
        self.assertEqual(list(k(0, '"d"$0 1 2')),
                         [date(2000, 1, d) for d in [1, 2, 3]])
        self.assertEqual(list(k(0, '-0W 0N 0Wd')),
                         [date(1, 1, 1), None, date(9999, 12, 31), ])

    def test_month(self):
        self.assertEqual(list(k(0, '"m"$0 1 2')),
                         [date(2000, m, 1) for m in [1, 2, 3]])
        self.assertEqual(list(k(0, '-0W 0N 0Wm')),
                         [date(1, 1, 1), None, date(9999, 12, 1), ])

    def test_datetime(self):
        self.assertEqual(list(k(0, '"z"$0.5 1.5 2.5')),
                         [datetime(2000, 1, d, 12) for d in [1, 2, 3]])
        self.assertEqual(list(k(0, '-0w 0n 0wz')), [datetime(1, 1, 1), None,
                                                    datetime(9999, 12, 31, 23,
                                                             59, 59,
                                                             999999), ])

    def test_time(self):
        self.assertEqual(list(k(0, '"t"$0 1 2 0N')),
                         [time(0, 0, 0, m * 1000) for m in range(3)] + [None])

    def test_minute(self):
        self.assertEqual(list(k(0, '"u"$0 1 2 0N')),
                         [time(0, m, 0) for m in range(3)] + [None])

    def test_second(self):
        self.assertEqual(list(k(0, '"v"$0 1 2')),
                         [time(0, 0, s) for s in range(3)])

    def test_symbol(self):
        x = ['a', 'b', 'c']
        self.assertEqual(list(S(x)), x)

    def test_float(self):
        x = [1.2, 2.3, 3.4]
        self.assertEqual(list(F(x)), x)

    def test_generic(self):
        x = kf(1.2), ki(2), ks('xyz')
        self.assertEqual([kstr(i) for i in K(x)],
                         [kstr(i) for i in x])

    def test_dict(self):
        d = k(0, '`a`b`c!1 2 3')
        self.assertEqual(list(d), list('abc'))

    def test_table(self):
        t = k(0, '([]a:`X`Y`Z;b:"xyz";c:1 2 3)')
        d = ['`a`b`c!(`X;"x";1)',
             '`a`b`c!(`Y;"y";2)',
             '`a`b`c!(`Z;"z";3)', ]
        for x, y in zip(t, d):
            self.assert_k_is(x, y)

    if Q_VERSION >= 3:
        def test_guid(self):
            s = '0x16151413121110090807060504030201'
            x = int(s, 16)
            self.assert_k_is(kguid(x), '0x0 sv ' + s)
            self.assertEqual([x], list(k(0, 'enlist 0x0 sv ' + s)))


class CallsTestCase(K_TestCase):
    def test_dot(self):
        x = k(0, '+')._dot(I([1, 2]))
        y = '3i'
        self.assert_k_is(x, y)
        self.assertRaises(_k.error, q('+')._dot, q('``'))

    def test_a0(self):
        x = k(0, '{1}')._a0()
        self.assert_k_is(x, '1')

    def test_a1(self):
        x = k(0, 'neg')._a1(ki(1))
        y = '-1i'
        self.assert_k_is(x, y)

    def test_call(self):
        f = q('{5}')
        x = ki(42)
        self.assert_k_is(f(), '5')
        self.assert_k_is(f(x), '5')
        self.assertRaises(_k.error, f, x, x)


class StrTestCase(K_TestCase):
    def test_pass(self):
        x = 'abc'
        self.assertEqual(str(ks(x)), x)
        self.assertEqual(str(kp(x)), x)
        x = b'a'
        self.assertEqual(str(kc(x)), x.decode())

    def test_misc(self):
        self.assertEqual(str(kb(1)), '1b')
        self.assertEqual(str(kh(1)), '1h')
        if Q_VERSION >= 3:
            self.assertEqual(str(ki(1)), '1i')
            self.assertEqual(str(kj(1)), '1')
        else:
            self.assertEqual(str(ki(1)), '1')
            self.assertEqual(str(kj(1)), '1j')
        self.assertEqual(str(kf(1)), '1f')


class ReprTestCase(unittest.TestCase):
    def test_pass(self):
        x = 'abc'
        self.assertEqual(repr(ks(x)), "k('`abc')")
        x = b'abc'
        self.assertEqual(repr(kp(x)), "k('\"abc\"')")
        x = b'a'
        self.assertEqual(repr(kc(x)), "k('\"a\"')")

    def test_misc(self):
        self.assertEqual(repr(kb(1)), "k('1b')")
        self.assertEqual(repr(kh(1)), "k('1h')")
        if Q_VERSION >= 3:
            self.assertEqual(repr(ki(1)), "k('1i')")
            self.assertEqual(repr(kj(1)), "k('1')")
        else:
            self.assertEqual(repr(ki(1)), "k('1')")
            self.assertEqual(repr(kj(1)), "k('1j')")
        self.assertEqual(repr(kf(1)), "k('1f')")


class JoinTestCase(K_TestCase):
    def test_any(self):
        x = ktn(0, 0)
        x._ja(ktj(101, 0))
        x._ja(ktj(101, 0))
        self.assert_k_is(x, '(::; ::)')

    def test_bool(self):
        x = q('10b')
        x._ja(True)
        y = '101b'
        self.assert_k_is(x, y)

    def test_byte(self):
        x = q('0x0102')
        x._ja(3)
        y = '0x010203'
        self.assert_k_is(x, y)

    def test_short(self):
        x = q('1 2h')
        x._ja(3)
        x._ja(-1)
        y = '1 2 3 -1h'
        self.assert_k_is(x, y)

    def test_int(self):
        x = q('1 2')
        x._ja(3)
        x._ja(-1)
        y = '1 2 3 -1'
        self.assert_k_is(x, y)

    def test_long(self):
        x = q('1 2j')
        x._ja(3)
        x._ja(-1)
        y = '1 2 3 -1j'
        self.assert_k_is(x, y)

    def test_real(self):
        x = q('1 2e')
        x._ja(3)
        x._ja(-1)
        y = '1 2 3 -1e'
        self.assert_k_is(x, y)

    def test_float(self):
        x = q('1 2f')
        x._ja(3)
        x._ja(-1)
        y = '1 2 3 -1f'
        self.assert_k_is(x, y)

    def test_str(self):
        x = q('"ab"')
        x._ja(b'c')
        y = '"abc"'
        self.assert_k_is(x, y)

    def test_sym(self):
        x = q('`a`b')
        x._ja(b'c')
        y = '`a`b`c'
        self.assert_k_is(x, y)


@pytest.mark.parametrize('f', [
    B, I, J, F, S, K,
])
def test_ja_errors(f):
    x = f([])
    with pytest.raises(TypeError):
        x._ja({})


@pytest.mark.parametrize('x', [
    "0x0102", "0 0h", "0 0e", '""',
])
def test_ja_errors_2(x):
    x = q(x)
    with pytest.raises(TypeError):
        x._ja({})


def test_ja_errors_3():
    x = kp("")
    with pytest.raises(TypeError):
        x._ja(b'aa')
    x = q('0x0102')
    with pytest.raises(OverflowError):
        x._ja(258)
    with pytest.raises(OverflowError):
        x._ja(-1)
    x = q('::')
    with pytest.raises(NotImplementedError):
        x._ja(0)


@pytest.mark.parametrize('f', [
    B, I, J, F, S, K,
])
def test_ja_overflow_errors(f):
    x = f([])
    with pytest.raises(TypeError):
        x._ja([])


@pytest.mark.parametrize('t', [
    'h', 'i', 'j', 'e', 'f'
])
def test_ja_none(t):
    x = q('"%s"$()' % t)
    x._ja(None)
    assert eq(x, q('enlist 0N' + t))


@pytest.mark.parametrize('t, x, y', [
    ('h', 2 ** 16, '0Wh'),
    ('i', 2 ** 32, '0Wi'),
    ('j', 2 ** 64, '0Wj'),
    ('h', - 2 ** 16, '-0Wh'),
    ('i', - 2 ** 32, '-0Wi'),
    ('j', - 2 ** 64, '-0Wj'),
    ('e', 1e40, '0We'),
    ('e', -1e40, '-0We'),
])
def test_ja_inf(t, x, y):
    a = q('"%s"$()' % t)
    a._ja(x)
    assert eq(a, q('enlist ' + y))


class ErrorTestCase(unittest.TestCase):
    def test_simple(self):
        self.assertRaises(_k.error, q, "1+`")
        self.assertRaises(_k.error, q("1+"), ks(''))
        self.assertRaises(_k.error, q("+"), ki(1), ks(''))

    def test_nested(self):
        self.assertRaises(_k.error, q, "{{{'`xyz}0}0}", ki(0))


class ArrayStructTestCase(unittest.TestCase):
    def test_type(self):
        for x in [q('1 2 3'), q('1')]:
            s = x.__array_struct__
            if _PY3K:
                self.assertEqual(type(s).__name__, 'PyCapsule')
            else:
                self.assertEqual(type(s).__name__, 'PyCObject')

    def test_error(self):
        x = q('()!()')
        self.assertRaises(AttributeError, lambda: x.__array_struct__)


class SerializationTestCase(K_TestCase):
    def test_b9(self):
        self.assert_k_is(b9(0, kb(1)), '0x010000000a000000ff01')
        self.assert_k_is(b9(0, kc(b'a')), '0x010000000a000000f661')
        self.assert_k_is(b9(0, kg(1)), '0x010000000a000000fc01')
        self.assert_k_is(b9(0, ki(1)), '0x010000000d000000fa01000000')
        self.assert_k_is(b9(0, kj(1)), '0x0100000011000000f90100000000000000')
        self.assert_k_is(b9(0, kp(b'')), '0x010000000e0000000a0000000000')

    def test_d9(self):
        self.assert_k_is(d9(q('0x010000000a000000ff00')), "0b")


try:
    from numpy import array
except ImportError:
    pass
else:
    class NumPyTestCase(unittest.TestCase):
        def test_scalar(self):
            x = ki(0)
            self.assertEquals(array(x).shape, ())


def eq(a, b):
    return q('~', a, b).inspect(b'g')


def test_B():
    x = B([])
    assert eq(x, q('0#0b'))

    x = B([True])
    assert eq(x, q('1#1b'))

    x = B([True, False])
    assert eq(x, q('10b'))

    with pytest.raises(TypeError):
        B(True, '')


@pytest.mark.parametrize("k,x", [
    ('1 2', [1, 2]),
    ('`a`b', ['a', 'b']),
    ('1 2e', [1., 2.]),
])
def test_as_sequence(k, x):
    a = q(k)
    b = list(a)
    assert len(a) == len(b)
    assert a[0] == b[0]
    assert b == x


@pytest.mark.parametrize("k,n", [
    ('1 2', 2),
    ('`a`b', 2),
    ('`a`b!1 2', 2),
    ('([]a:1 2;b:0;c:0)', 2),
    ('([]a:1 2)', 2),
    ('([a:1 2]b:10 20)', 2),
    ('0#([a:1 2]b:10 20)', 0),
    ('0', 1),
    ('{}', 1),
])
def test_length(k, n):
    assert len(q(k)) == n


def test_k_methods():
    assert _k.ymd(2000, 1, 1) == 0
    assert _k.ymd(1970, 1, 1) == -10957
    assert _k.dj(0) == 20000101
    assert _k.dj(-10957) == 19700101


def test_jv():
    x = q('1 2')
    y = q('3 4')
    x._jv(y)
    assert eq(x, q('1 2 3 4'))
    assert y.inspect(b'r') == 0
    with pytest.raises(TypeError):
        x._jv(1)


@pytest.mark.parametrize("k,py", [
    ('-0Wd', date(1, 1, 1)),
    ('0Nd', None),
    ('0Wd', date(9999, 12, 31)),
    ('2014.06.06', date(2014, 6, 6)),
    ('1828.09.09', date(1828, 9, 9)),
])
def test_date(k, py):
    x = q('enlist ' + k)
    assert x[0] == py


def test_errors_type():
    with pytest.raises(_k.error) as e:
        q('`+1')
    assert e.value.args[0] == 'type'

    with pytest.raises(TypeError):
        ktd(None)

    with pytest.raises(TypeError):
        ka(None, None)

    with pytest.raises(TypeError):
        dot(None, None)

    with pytest.raises(TypeError):
        a1(None, None)

    with pytest.raises(TypeError):
        ktn(None, None)

    # with pytest.raises(TypeError):
    #     q('{}')(None)

    with pytest.raises(TypeError):
        k(None)


@pytest.mark.parametrize('f', [
    G, H, I, J, E, F, S, K, P, M, D, N, U, V, T,
])
def test_sequence_conversion_errors(f):
    with pytest.raises(TypeError):
        f(None)
    with pytest.raises(TypeError):
        f([()])


@pytest.mark.parametrize('f', [
    ka, kg, kh, ki, kj, ke, kf, kc, ks, km, kd, kz, ku, kv, kt, kp,
    kzz, knz, kpz, b9, d9,
])
def test_scalar_conversion_errors(f):
    with pytest.raises(TypeError):
        f([])


@pytest.mark.parametrize('f,x', [
    (G, 1), (I, 1), (J, 1), (F, 1.0), (S, ''),
])
def test_sequence_mixed_type_errors(f, x):
    with pytest.raises(TypeError):
        f([x, ()])


def test_errors_ktd():
    with pytest.raises(TypeError):
        ktd(None)
    x = ki(0)
    with pytest.raises(_k.error):
        ktd(x)
    # Check that ktd does not leak refs of failure.
    assert x._r == 0


def test_errors_ka():
    with pytest.raises(TypeError):
        ka(None, None)


def test_errors_dot():
    with pytest.raises(TypeError):
        dot(None, None)
    f = ktj(101, 0)  # ::
    with pytest.raises(TypeError):
        dot(f, None)


def test_errors_a1():
    with pytest.raises(TypeError):
        a1(None, None)


def test_errors_ktn():
    with pytest.raises(TypeError):
        ktn(None, None)


# def test_errors_q_arg0():
#     with pytest.raises(TypeError):
#         q('{}')(None)


def test_errors_k():
    with pytest.raises(TypeError):
        k(None)
    with pytest.raises(TypeError):
        k(0, None)
    with pytest.raises(TypeError):
        k(0, ':', None)


def test_errors_K():
    with pytest.raises(TypeError):
        _k.K()


def test_errors_ymd():
    with pytest.raises(TypeError):
        _k.ymd()


def test_errors_dj():
    with pytest.raises(TypeError):
        _k.dj()


def test_errors_I():
    assert eq(I([2 ** 32]), q('1#0Wi'))
    assert eq(I([2 ** 64]), q('1#0Wi'))


def test_errors_J():
    assert eq(J([2 ** 64]), q('1#0Wj'))
    assert eq(J([2 ** 64 + 1]), q('1#0Wj'))


@pytest.mark.parametrize('f', [
    ka, kg, kh, ki, kj, ke, kf, kc, ks, km, kd, kz, ku, kv, kt, kp,
    kzz, knz, kpz, b9, d9, xD, xT, kzz,
] + ([kguid] if Q_VERSION >= 3 else []))
def test_misc_conversion_errors(f):
    with pytest.raises(TypeError):
        f([])


def test_reference_leaks():
    x = q('1 2 3')
    n = q('\\w')[0]
    s = str(x)
    assert n == q('\\w')[0]
    r = repr(x)
    assert n == q('\\w')[0]
    test_errors_I()
    assert n == q('\\w')[0]
    test_errors_J()
    assert n == q('\\w')[0]


def test_ktd_reference_leak():
    x = q('([a:1 2]b:3 4)')
    ktd(x)
    assert x.inspect(b'r') == 0


def test_xD_reference_leak():
    x = q('1 2 3')
    y = q('5 6 7')
    xD(x, y)
    assert x.inspect(b'r') == 0
    assert y.inspect(b'r') == 0


def test_func():
    def f(x, y):
        return y

    kf = func(f)
    x = q('1 2j')

    assert eq(kf(x), kj(2))


@pytest.mark.parametrize('x,r', [
    (1, '1'),
    (3.14, '3.14'),
    (None, '::'),
    (True, '1b'),
    (False, '0b')
])
def test_func_values(x, r):
    def f():
        return x

    kf = func(f)
    assert eq(kf(ktn(0, 0)), q(r))


@pytest.mark.parametrize('x,e', [
    ([], 'py2k'),
    (2 ** 65, 'OverflowError'),
])
def test_func_errors(x, e):
    def f():
        return x

    kf = func(f)
    with pytest.raises(_k.error) as info:
        kf(ktn(0, 0))
        assert info.value.args[0] == e


def test_ktn():
    x = ktn(_k.KF, 3)
    assert x.inspect(b't') == _k.KF
    assert x.inspect(b'n') == 3


@pytest.mark.parametrize("k,py", [
    ('::', None),
    ('1b', True),
    ('0b', False),
    ('42', 42),
    ('3.14', 3.14),
    ('2001.01.01', date(2001, 1, 1)),
    ('2001.01.01D0', datetime(2001, 1, 1)),
    ('0D01:02:03.456789',
     timedelta(hours=1, minutes=2, seconds=3, microseconds=456789)),
    ('`xyz', 'xyz'),
])
def test_constructor(k, py):
    x = _k.K(py)
    assert eq(q(k), x)


@pytest.mark.skipif("sys.version_info >= (3,0)")
def test_constructor_long():
    x = eval('42L')
    assert eq(_k.K(x), q('42'))


@pytest.mark.parametrize('x', list('zmtuvd'))  # nyi - np
def test_temporal_none(x):
    assert q('enlist 0N' + x)[0] is None


def test_inspect():
    x = q("`s#1 2")
    assert x.inspect(b'u') == 1


def test_enlist():
    for n in range(1, 8):
        args = [kc(b'x')] + [ki(0)] * n
        x = q('enlist', *args)
        y = knk(len(args), *args)
        # TODO: figure out why simple == comparison fails
        assert str(x) == str(y)
        errargs = [None] + args[1:]
        with pytest.raises(TypeError):
            q('enlist', *errargs)
        with pytest.raises(TypeError):
            knk(len(errargs), *errargs)


@pytest.mark.parametrize('x, y', [
    ('"abc"', '"xxx"'),
    ('1 2 3h', '0 0 0h'),
    ('1 2 3i', '0 0 0i'),
    ('1 2 3', '0 0 0'),
])
def test_buffer_protocol(tmpdir, x, y):
    x = q(x)
    y = q(y)
    p = tmpdir.join('x')
    with p.open('wb') as f:
        f.write(x)
    with p.open() as f:
        if _PY3K:
            f = f.buffer
        f.readinto(y)

    assert eq(x, y)


def test_charbuffer(tmpdir):
    x = q('"abc"')
    p = tmpdir.join('x')
    with p.open('w') as f:
        if _PY3K:
            f = f.buffer
        f.write(x)

    assert p.read() == 'abc'


def test_charbuffer_error(tmpdir):
    x = q('1 2 3j')
    p = tmpdir.join('x')
    with p.open('w') as f:
        if _PY3K:
            f = f.buffer
            f.write(x)
            f.close()
            assert struct.unpack("qqq", p.read_binary()) == (1, 2, 3)
        else:
            with pytest.raises(TypeError):
                f.write(x)


def test_iter():
    x = q('0')
    with pytest.raises(TypeError):
        iter(x)

    x = q('1 2')
    i = iter(x)
    assert list(i) == [1, 2]


@pytest.mark.parametrize('Y, M, D, h, m, s, u', [
    (1970, 1, 1, 0, 0, 0, 123000),
    (2015, 1, 13, 20, 27, 25, 926000),
])
def test_datetime_conversion(Y, M, D, h, m, s, u):
    d = datetime(Y, M, D, h, m, s, u)
    x = q('enlist', kzz(d))
    assert x[0] == d


def test_errmsg():  # Issue #737
    with pytest.raises(ValueError) as e:
        F([1., ''])
    assert 'float' in e.value.args[0]


@pytest.mark.parametrize('x,y', [
    ('0b', False),
    ('1b', True),
    ('"x"', 'x'),
    ('0x00', 0),
    ('0h', 0),
    ('0i', 0),
    ('0', 0),
    ('0e', 0.0),
    ('0f', 0.0),
    ('0Wj-1', 9223372036854775806),
])
def test_pys(x, y):
    k = q(x)
    s = k._pys()
    assert s == y
    assert type(s) is type(y)


def test_pys_vector():
    x = q('1 2')
    with pytest.raises(TypeError):
        x._pys()


def test_pys_nyi():
    # Timestamp conversion is not implemented to
    # avoid the loss of precision.
    x = ka(-_k.KP, 0)
    with pytest.raises(NotImplementedError):
        x._pys()


def test_getitem_neg():
    x = I([0, 1, 2, 3])
    assert x[-2] == 2


@pytest.mark.parametrize('i', [-5, 4, 10])
def test_getitem_out_of_range(i):
    x = I([0, 1, 2, 3])
    with pytest.raises(IndexError):
        x[i]


def test_getitem_nyi():
    x = q('0N 0Np')
    with pytest.raises(NotImplementedError):
        x[0]


@pytest.mark.parametrize('x', "hijmdvut")
def test_getitem_none(x):
    x = q('enlist 0N' + x)
    assert x[0] is None


# XXX: This is commented out because it induces failures
# in unrelated tests.  TODO: investigate whether additional
# cleanup is needed upon a connection error.
# def test_connection_error():
#    with pytest.raises(OSError):
#        k(-1, "")

def test_issue_796():
    x = J([1])
    assert type(x[0]) is int


@pytest.mark.skipif('_PY3K')
def test_issue_796_long():
    maxint = sys.maxint
    if maxint == 2 ** 31 - 1:
        x = J([maxint, -maxint - 1, maxint + 1, -maxint - 2])
        assert [type(i) for i in x] == [int, int, long, long]
    else:
        x = J([maxint - 1, -maxint + 1])
        assert [type(i) for i in x] == [int, int]


def test_okx():
    x = kb(0)
    b = b9(0, x)
    assert _k.okx(b)


@pytest.mark.parametrize('b', [None, kb(0)])
def test_okx_errors(b):
    with pytest.raises(TypeError):
        _k.okx(b)


@pytest.mark.parametrize('attr,value', [
    ('r', 0),
    ('t', 100),
])
def test_int_attr(attr, value):
    x = q('{}')
    a = getattr(x, '_' + attr)
    assert isinstance(a, int)
    assert a == value


# Atoms and vectors
# q) .Q.t
# " bg xhijefcspmdznuvts"
# num ch name       atom    vector
# --------------------------------
# 1   b  boolean    kb       B
# 2   g  guid       kguid    -
# 4   x  byte       kg       -
# 5   h  short      kh       -
# 6   i  int        ki       I
# 7   j  long       kj       J
# 8   e  real       ke       -
# 9   f  float      kf       F
# 10  c  char       kc       kp
# 11  s  symbol     ks       S
# 12  p  timestamp  knz      -
# 13  m  month      km       -
# 14  d  date       kd       D
# 15  z  datetime   kz       -
# 16  n  timespan   kpz      -
# 17  u  minute     ku       -
# 18  v  second     kv       -
# 19  t  time       kt       -
# 11  s  symbol     ks       -

def test_byte_list():
    x = G([])
    assert x._t == _k.KG
    x = G([None, 1])
    assert eq(x, q('0x0001'))


@pytest.mark.parametrize('ch, num', [
    ("H", 5),
    ("I", 6),
    ("J", 7),
])
def test_integer_list(ch, num):
    vec = getattr(_k.K, '_%s' % ch)
    # Empty list - check the type
    x = vec([])
    assert x._t == num
    # List with a missing value
    x = vec([None, 0])
    assert eq(x, q('0N 0' + ch.lower()))


@pytest.mark.parametrize('ch, num', [
    ("E", 8),
    ("F", 9),
])
def test_float_list(ch, num):
    vec = getattr(_k.K, '_%s' % ch)
    # Empty list - check the type
    x = vec([])
    assert x.inspect(b't') == num
    # List with special values
    inf = float('inf')
    nan = float('nan')
    x = vec([0.0, -0.0, inf, -inf, nan])
    assert x[0] == 0.0
    assert math.copysign(1.0, x[1]) < 0
    assert math.isinf(x[2]) and x[2] > 0
    assert math.isinf(x[3]) and x[3] < 0
    assert math.isnan(x[4])


def test_timestamp_list():
    x = P([])
    assert x._t == _k.KP
    d = date(2000, 1, 1)
    x = P([None, d])
    assert eq(x, q('0N 2000.01.01D0'))
    dt = datetime(2000, 1, 1, 12, 34, 56, 789)
    x = P([None, dt])
    assert eq(x, q('0N 2000.01.01D12:34:56.000789'))


def test_month_list():
    x = M([])
    assert x._t == _k.KM
    d = date(2000, 1, 1)
    x = M([None, d])
    assert eq(x, q('0N 2000.01m'))
    dt = datetime(2000, 1, 1, 12, 34, 56, 789)
    x = M([None, dt])
    assert eq(x, q('0N 2000.01m'))


def test_timespan_list():
    x = N([])
    assert x._t == _k.KN
    d = timedelta(1, 2, 3)
    x = N([None, d, timedelta.max, timedelta.min])
    assert eq(x, q('0N 1D00:00:02.000003 0W -0Wn'))


def test_minute_list():
    x = U([])
    assert x._t == _k.KU
    t = time(1, 2, 3, 4000)
    x = U([None, t])
    assert eq(x, q('0N 01:02'))


def test_second_list():
    x = V([])
    assert x._t == _k.KV
    t = time(1, 2, 3, 4000)
    x = V([None, t])
    assert eq(x, q('0N 01:02:03'))


def test_time_list():
    x = T([])
    assert x._t == _k.KT
    t = time(1, 2, 3, 4000)
    x = T([None, t])
    assert eq(x, q('0N 01:02:03.004'))


@pytest.mark.skipif("Q_VERSION < 3")
def test_guid_list():
    x = UU([])
    assert x._t == _k.UU
    x = UU([None, 0x01020304050607080910111213141516])
    assert str(x) == ('00000000-0000-0000-0000-000000000000 '
                      '01020304-0506-0708-0910-111213141516')


@pytest.mark.parametrize("t", "bxhijefcnuvt")
def test_false_scalar(t):
    x = q('"%c"$0' % t)
    assert not x


@pytest.mark.parametrize("t", "bxhijefcpmdznuvt")
def test_true_scalar(t):
    x = q('"%c"$1' % t)
    assert x


@pytest.mark.parametrize("x,r", [
    ('`', False),
    ('`a', True),
    ('::', False),
    ('{}', True),
    ('+', True),
    ('neg', True),
    ('raze', True),
    ('()!()', False),
    ('1 2!3 4', True),
    ('flip`a`b!()', False),
    ('([]a:1 2)', True),
    ('([k:1 2]a:1 2)', True),
    ('1!flip`a`b!()', False),
])
def test_k_bool(x, r):
    x = q(x)
    assert r == bool(x)


def test_k_bool_of_enum():
    q("sym:`a`b`c")
    x = q("`sym$`a")
    assert x
    x = q("`sym$`")
    assert not x


def test_enum_getitem():
    q("sym:`a`b`c")
    x = q('`sym$`a`')
    assert x[0] == 'a'
    assert x[1] == ''
    with pytest.raises(IndexError):
        x[2]
    # Test short enum domain vector
    q("sym:1#sym")
    assert x[1] == ''


@pytest.mark.skipif("Q_VERSION < 3")
def test_setm():
    assert _k.setm(1) == 0
    assert _k.setm(0) == 1
    assert _k.setm(0) == 0
    with pytest.raises(TypeError):
        _k.setm('')


@pytest.mark.skipif("Q_VERSION < 3")
def test_m9():
    # For now just check that m9() exists.
    # Note that m9() can only be called from
    # a separate thread before its termination.
    assert _k.m9


@pytest.mark.parametrize("x, n", [
    ("()", 0),
    ("1 2", 2),
    ("()!()", 2),
])
def test_attr_n(x, n):
    x = q(x)
    assert n == x._n


@pytest.mark.skipif("Q_VERSION >= 3.6")
def test_date_range():
    min_date = date(1709, 1, 1)
    max_date = date(2290, 12, 31)
    one_day = timedelta(1)
    result = q('-0W 1709.01.01 1709.01.02 2290.12.30 2290.12.31 0Wd')
    assert eq(D([min_date - one_day, min_date, min_date + one_day,
                 max_date - one_day, max_date, max_date + one_day]),
              result)
    # Demonstrate that q bails on the out of range dates
    with pytest.raises(_k.error):
        d1 = min_date - one_day
        # We cannot use strftime here because in Python 2.7 it only
        # works for dates after 1900.
        q("%d.%d.%d" % (d1.year, d1.month, d1.day))
    with pytest.raises(_k.error):
        d2 = max_date + one_day
        q(d2.strftime('%Y.%m.%d'))

    # Test scalar conversions
    assert eq(_k.K(d1), q('-0Wd'))
    assert eq(_k.K(d2), q('0Wd'))
    assert eq(_k.K(min_date), q('1709.01.01'))
    assert eq(_k.K(max_date), q('2290.12.31'))


def test_issue_870():
    datetimes = [datetime(2100, 1, 1), datetime(2200, 1, 1)]
    result = q('2100.01.01D00:00:00.000000000 2200.01.01D00:00:00.000000000')
    assert eq(P(datetimes), result)


@pytest.mark.skipif("Q_VERSION >= 3.6")
def test_month_range():
    dates = map(date,
                [1708, 1709, 2290, 2291],
                [12, 1, 12, 1], [1] * 4)
    result = q('-0W 1709.01 2290.12 0Wm')
    assert eq(M(dates), result)


def test_timestamp_range():
    min_datetime = datetime(1709, 1, 1)
    over_datetime = datetime(2291, 1, 1)
    eps = datetime.resolution
    datetimes = [min_datetime - eps, min_datetime,
                 over_datetime - eps, over_datetime]
    result = q(
        '-0W 1709.01.01D00:00:00.000000000 2290.12.31D23:59:59.999999000 0Wp')
    assert eq(P(datetimes), result)


@pytest.mark.skipif("Q_VERSION < 3.6")
def test_date_and_month_extremes():
    dates = [date.min, date.max]
    assert eq(M(dates), q('0001.01 9999.12m'))
    assert eq(D(dates), q('0001.01.01 9999.12.31'))


@pytest.mark.parametrize("t,f", [
    ("boolean", "?"),
    ("byte", "B"),
    ("short", "h"),
    ("int", K_INT_CODE),
    ("long", K_LONG_CODE),
    ("real", "f"),
    ("float", "d"),
    ("char", "s"),
    ("symbol", "P"),
    ("timestamp", K_LONG_CODE),
    ("timespan", K_LONG_CODE),
    ("date", K_INT_CODE),
    ("minute", K_INT_CODE),
    ("second", K_INT_CODE),
    ("datetime", "d"),
])
def test_data_attribute(t, f):
    x = q('$', ks(t), ktn(0, 0))
    assert x.data.format == f


def test_data_attribute_error():
    x = q('::')
    with pytest.raises(AttributeError):
        x.data


def test_n_attribute_error():
    x = ki(0)
    with pytest.raises(AttributeError):
        x._n


@pytest.mark.parametrize('x,m,r', [
    ('1j', 't', -7),
    # pytest.mark.skipif("Q_VERSION < 3", ('1', 'a', 3)),
    # -- unpredictable values
    pytest.mark.skipif("Q_VERSION < 3", ('1', 'm', 0)),
    ('"x"', 'c', b'x'),
    ('enlist 0x42', 'G', 0x42),
    ('enlist 42h', 'H', 42),
    ('enlist 42i', 'I', 42),
    ('enlist 42j', 'J', 42),
    ('enlist 42e', 'E', 42.),
    ('enlist 42f', 'F', 42.),
])
def test_inspect(x, m, r):
    x = q(x)
    if m.isupper():
        assert x.inspect(m, 0) == r
    else:
        assert x.inspect(m) == r


def test_inspect_error():
    x = ki(0)
    with pytest.raises(TypeError):
        x.inspect(42)


def test_a1_error():
    x = ki(0)
    with pytest.raises(TypeError):
        x._a1(None)


def test_str_error():
    x = q('`sym?`x')
    value = q('value')
    q(".q.value:{'`error}")
    try:
        with pytest.raises(_k.error):
            str(x)
    finally:
        q('set', ks('.q.value'), value)


def test_call_kw_error():
    f = q('::')
    with pytest.raises(TypeError):
        f(a=None)
    f = q('{[a;b]a-b}')
    with pytest.raises(TypeError):
        f(1, a=2)
    with pytest.raises(TypeError):
        f(1, 2, z=3)


def test_data_attr_errors():
    # Empty list
    x = ktn(0, 0)
    with pytest.raises(BufferError):
        x.data
    # Scalar in generic list
    x = knk(2, ki(0), kj(0))
    with pytest.raises(BufferError):
        x.data
    # Size varies
    x = knk(2, I([]), I([0]))
    with pytest.raises(BufferError):
        x.data


def test_kb_error():
    class X:
        def __index__(self):
            raise ValueError

    x = X()
    with pytest.raises(ValueError):
        kb(x)
    with pytest.raises(ValueError):
        B([x])

    with pytest.raises(TypeError):
        kb(0.0)


@pytest.mark.parametrize("f, u, o, r", [
    ('kg', -1, 256, OverflowError),
    ('kh', -2 ** 15 - 1, 2 ** 15 + 1, '0Wh'),
    ('ki', -2 ** 31 - 1, 2 ** 31 + 1, '0Wi'),
    ('ke', -1e200, 1e200, '0We'),
    ('kf', -float('inf'), float('inf'), '0w'),
    ('kd', -2 ** 31 - 1, 2 ** 31 + 1, '0Wd'),
    pytest.mark.skipif('Q_VERSION >= 3.6', ('kd', date.min, date.max, '0Wd')),
    ('km', -2 ** 31 - 1, 2 ** 31 + 1, '0Wm'),
    ('ku', -2 ** 31 - 1, 2 ** 31 + 1, '0Wu'),
    ('kv', -2 ** 31 - 1, 2 ** 31 + 1, '0Wv'),
    ('kpz', -2 ** 63 - 1, 2 ** 63 + 1, '0Wp'),
    ('knz', -2 ** 63 - 1, 2 ** 63 + 1, '0Wn'),
])
def test_scalar_overflow(f, u, o, r):
    f = getattr(_k.K, '_' + f)
    if isinstance(r, type):
        for v in [u, o]:
            with pytest.raises(r):
                f(v)
    else:
        s = q('-' + r)
        r = q(r)
        assert eq(f(u), s)
        assert eq(f(o), r)


def test_repr():
    assert repr(ktj(101, 1)) == "k('+:')"


def test_kj_error():
    class X:
        def __index__(self):
            return ''

    x = X()
    with pytest.raises(TypeError):
        kj(x)


def test_kc():
    assert eq(kc('a'), q('"a"'))
    assert eq(kc(b'a'), q('"a"'))
    with pytest.raises(TypeError):
        kc({})
    with pytest.raises(TypeError):
        kc('ab')
    with pytest.raises(TypeError):
        kc(b'ab')


@pytest.mark.skipif("Q_VERSION < 3.5")
def test_trp():
    f = q('{x+y}')
    args = q('(1;`)')
    with pytest.raises(_k.error) as info:
        f._trp(args)
    a = info.value.args
    assert a[0] == 'type'
    bt = q('sublist', q('0 1'), a[1])
    sbt = q('.Q.sbt', bt)
    assert str(sbt) == (
        '  [3]  {x+y}\n'
        '         ^\n').replace('\n', os.linesep)


def test_callargs():
    f = q('{x+y}')
    assert f._callargs(1, y=2) == (1, 2)


@pytest.mark.parametrize('x', ['0Wt', '-0Wt'])
def test_inf_time_pys(x):
    x = q(x)
    with pytest.raises(OverflowError):
        x._pys()
