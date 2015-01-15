from __future__ import absolute_import
import unittest, pytest
from datetime import datetime, date, time, timedelta
import sys

from pyq import _k

if sys.maxsize == 2147483647:  # 32-bit platform
    K_INT_CODE, K_LONG_CODE = "lq"
else:
    K_INT_CODE, K_LONG_CODE = "il"

PY3K = sys.hexversion >= 0x3000000

# extract _k.K class methods
for m in ('func k knk ktd err dot a1'
          ' ka kb kg kh ki kj ke kf kc ks km kd kz ku kv kt kp'
          ' ktn ktj kdd ktt kzz knz kpz b9 d9 kguid'
          ' B I J F S K D xT xD').split():
    globals()[m] = getattr(_k.K, '_' + m)
del m
q = lambda *args: k(0, *args)
q("\\e 0")  # disable q's debug on error
KXVER = int(q('.Q.k').inspect(b'f'))
if KXVER >= 3:
    kguid = _k.K._kguid


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

    def test_kb(self):
        self.assert_k_is(kb(1), '1b')

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

    def test_ks(self):
        self.assert_k_is(ks('abc'), '`abc')

    def test_km(self):
        self.assert_k_is(km(1), '2000.02m')

    def test_kd(self):
        self.assert_k_is(kd(1), '2000.01.02')

    def test_kdd(self):
        self.assert_k_is(kdd(date(2000, 1, 2)), '2000.01.02')

    def test_ktt(self):
        self.assert_k_is(ktt(time(10, 11, 12, 1000)), '10:11:12.001')

    def test_kzz(self):
        self.assert_k_is(kzz(datetime(2000, 1, 2, 10, 11, 12, 1000)), '2000.01.02T10:11:12.001')

    def test_kpz(self):
        self.assert_k_is(kpz(datetime(2000, 1, 2, 10, 11, 12, 1000)), '2000.01.02D10:11:12.001000000')

    def test_knz(self):
        self.assert_k_is(knz(timedelta(100, 20, 1000)), '100D00:00:20.001000000')

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
        l = [1, 2, 3, None]
        self.assertEqual(list(I(l)), l)

    def test_long(self):
        self.assertEqual(list(k(0, '1 2 3j')), [1, 2, 3])

    def test_date(self):
        self.assertEqual(list(k(0, '"d"$0 1 2')), [date(2000, 1, d) for d in [1, 2, 3]])
        self.assertEqual(list(k(0, '-0W 0N 0Wd')), [date(1, 1, 1), None, date(9999, 12, 31), ])

    def test_month(self):
        self.assertEqual(list(k(0, '"m"$0 1 2')), [date(2000, m, 1) for m in [1, 2, 3]])
        self.assertEqual(list(k(0, '-0W 0N 0Wm')), [date(1, 1, 1), None, date(9999, 12, 1), ])

    def test_datetime(self):
        self.assertEqual(list(k(0, '"z"$0.5 1.5 2.5')), [datetime(2000, 1, d, 12) for d in [1, 2, 3]])
        self.assertEqual(list(k(0, '-0w 0n 0wz')), [datetime(1, 1, 1), None,
                                                    datetime(9999, 12, 31, 23, 59, 59, 999999), ])

    def test_time(self):
        self.assertEqual(list(k(0, '"t"$0 1 2 0N')), [time(0, 0, 0, m * 1000) for m in range(3)] + [None])

    def test_minute(self):
        self.assertEqual(list(k(0, '"u"$0 1 2 0N')), [time(0, m, 0) for m in range(3)] + [None])

    def test_second(self):
        self.assertEqual(list(k(0, '"v"$0 1 2')), [time(0, 0, s) for s in range(3)])

    def test_symbol(self):
        l = ['a', 'b', 'c']
        self.assertEqual(list(S(l)), l)

    def test_float(self):
        l = [1.2, 2.3, 3.4]
        self.assertEqual(list(F(l)), l)

    def test_generic(self):
        l = kf(1.2), ki(2), ks('xyz')
        self.assertEqual([kstr(x) for x in K(l)],
                         [kstr(x) for x in l])

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

    if KXVER >= 3:
        def test_guid(self):
            s = '0x16151413121110090807060504030201'
            l = int(s, 16)
            self.assert_k_is(kguid(l), '0x0 sv ' + s)
            self.assertEqual([l], list(k(0, 'enlist 0x0 sv ' + s)))


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
        if KXVER >= 3:
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
        if KXVER >= 3:
            self.assertEqual(repr(ki(1)), "k('1i')")
            self.assertEqual(repr(kj(1)), "k('1')")
        else:
            self.assertEqual(repr(ki(1)), "k('1')")
            self.assertEqual(repr(kj(1)), "k('1j')")
        self.assertEqual(repr(kf(1)), "k('1f')")


class JoinTestCase(K_TestCase):
    def test_byte(self):
        x = q('0x0102')
        x._ja(3)
        y = '0x010203'
        self.assert_k_is(x, y)

    def test_short(self):
        x = q('1 2h')
        x._ja(3)
        y = '1 2 3h'
        self.assert_k_is(x, y)

    def test_int(self):
        x = q('1 2')
        x._ja(3)
        y = '1 2 3'
        self.assert_k_is(x, y)

    def test_long(self):
        x = q('1 2j')
        x._ja(3)
        y = '1 2 3j'
        self.assert_k_is(x, y)

    def test_real(self):
        x = q('1 2e')
        x._ja(3)
        y = '1 2 3e'
        self.assert_k_is(x, y)

    def test_float(self):
        x = q('1 2f')
        x._ja(3)
        y = '1 2 3f'
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
        x._ja(None)

@pytest.mark.parametrize('f', [
    B, I, J, F, S, K,
])
def test_ja_errors(f):
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
    @pytest.mark.skipif(PY3K, reason="WIP")
    def test_type(self):
        for x in [q('1 2 3'), q('1')]:
            s = x.__array_struct__
            if PY3K:
                self.assertEqual(type(s).__name__, 'PyCapsule')
            else:
                self.assertEqual(type(s).__name__, 'PyCObject')

    def test_error(self):
        x = q('()!()')
        self.assertRaises(AttributeError, lambda: x.__array_struct__)


try:
    memoryview
except NameError:
    pass
else:
    import struct

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
                ('0Ng', "16B", 16, 0),
            ])
    def test_simple_view(x, f, s, u):
        m = memoryview(q(x))
        assert m.ndim == 0
        assert m.format == f
        assert m.itemsize == s
        v = struct.unpack(f, m.tobytes())
        assert v[0] == u
        m = memoryview(q("enlist " + x))
        assert m.ndim == 1
        assert m.shape == (1,)
        assert m.strides == (s,)
        assert m.format == f
        assert m.itemsize == s
        if PY3K:
            try:
                v = m[0]
            except NotImplementedError:
                pass
            else:
                assert v == u
        else:
            v = struct.unpack(f, m[0])
            assert v[0] == u


class SerializationTestCase(K_TestCase):
    def test_b9(self):
        self.assert_k_is(b9(-1, kb(1)), '0x010000010a000000ff01')
        self.assert_k_is(b9(-1, kc(b'a')), '0x010000010a000000f661')
        self.assert_k_is(b9(-1, kg(1)), '0x010000010a000000fc01')
        self.assert_k_is(b9(-1, ki(1)), '0x010000010d000000fa01000000')
        self.assert_k_is(b9(-1, kj(1)), '0x0100000111000000f90100000000000000')
        self.assert_k_is(b9(-1, kp(b'')), '0x01000001120000000a000000000000000000')

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


@pytest.mark.parametrize("k,l", [
    ('1 2', [1, 2]),
    ('`a`b', ['a', 'b']),
    ('1 2e', [1., 2.]),
])
def test_as_sequence(k, l):
    a = q(k)
    b = list(a)
    assert len(a) == len(b)
    assert a[0] == b[0]
    assert b == l


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

    with pytest.raises(TypeError):
        q('{}')(None)

    with pytest.raises(TypeError):
        k(None)


@pytest.mark.parametrize('f', [
    B, I, J, F, S, K,
])
def test_sequence_conversion_errors(f):
    with pytest.raises(TypeError):
        f(None)
    with pytest.raises(TypeError):
        f([()])


@pytest.mark.parametrize('f', [
    ka, kb, kg, kh, ki, kj, ke, kf, kc, ks, km, kd, kz, ku, kv, kt, kp,
    kzz, knz, kpz, b9, d9,
])
def test_scalar_conversion_errors(f):
    with pytest.raises(TypeError):
        f([])

@pytest.mark.parametrize('f,x', [
    (B, 1), (I, 1), (J, 1), (F, 1.0), (S, ''),
])
def test_sequence_mixed_type_errors(f, x):
    with pytest.raises(TypeError):
        f([x, ()])

def test_errors_ktd():
    with pytest.raises(TypeError):
        ktd(None)


def test_errors_ka():
    with pytest.raises(TypeError):
        ka(None, None)


def test_errors_dot():
    with pytest.raises(TypeError):
        dot(None, None)


def test_errors_a1():
    with pytest.raises(TypeError):
        a1(None, None)


def test_errors_ktn():
    with pytest.raises(TypeError):
        ktn(None, None)


def test_errors_q_arg0():
    with pytest.raises(TypeError):
        q('{}')(None)


def test_errors_k():
    with pytest.raises(TypeError):
        k(None)


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
    with pytest.raises(OverflowError):
        I([2 ** 32])

    with pytest.raises(OverflowError):
        I([2 ** 64])


def test_errors_J():
    with pytest.raises(OverflowError):
        J([2 ** 64])


@pytest.mark.parametrize('f', [
    B, I, J, F, S, K, D,
])
def test_sequence_conversion_errors(f):
    with pytest.raises(TypeError):
        f(None)
    with pytest.raises(TypeError):
        f([()])


@pytest.mark.parametrize('f', [
    ka, kb, kg, kh, ki, kj, ke, kf, kc, ks, km, kd, kz, ku, kv, kt, kp,
    kzz, knz, kpz, b9, d9, xD, xT, kdd, kzz, kguid, ktt,
])
def test_misc_conversion_errors(f):
    with pytest.raises(TypeError):
        f([])


@pytest.mark.parametrize('f,x', [
    (B, 1), (I, 1), (J, 1), (F, 1.0), (S, ''),
])
def test_sequence_mixed_type_errors(f, x):
    with pytest.raises(TypeError):
        f([x, ()])


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
    x = q('1 2')

    assert eq(kf(x), kj(2))


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
    ('0D01:02:03.456789', timedelta(hours=1, minutes=2, seconds=3, microseconds=456789)),
    ('`xyz', 'xyz'),
])
def test_constructor(k, py):
    x = _k.K(py)
    assert eq(q(k), x)


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
    ('"d"$1 2 3', '"d"$0 0 0'),
])
def test_buffer_protocol(tmpdir, x, y):
    x = q(x)
    y = q(y)
    p = tmpdir.join('x')
    with p.open('wb') as f:
        f.write(x)
    with p.open() as f:
        if PY3K:
            f = f.buffer
        f.readinto(y)

    assert eq(x, y)


def test_charbuffer(tmpdir):
    x = q('"abc"')
    p = tmpdir.join('x')
    with p.open('w') as f:
        if PY3K:
            f = f.buffer
        f.write(x)

    assert p.read() == 'abc'


def test_charbuffer_error(tmpdir):
    x = q('1 2 3')
    p = tmpdir.join('x')
    with p.open('w') as f:
        if PY3K:
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
