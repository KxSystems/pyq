from __future__ import absolute_import
from __future__ import division

import unittest
from collections import namedtuple, OrderedDict
from keyword import iskeyword

import math
import pytest
from datetime import timedelta
import os

from pyq import *
from pyq import Q_VERSION, _PY3K


q("\\e 0")  # disable q's debug on error


class TestPickle(unittest.TestCase):
    def test_roundtrip(self):
        import pickle

        data = ['1b', '1 2 3', '"abcde"',
                '(([a:""]b:0#0);`;0h)']
        for d in data:
            x = q(d)
            s = pickle.dumps(x)
            y = pickle.loads(s)
        self.assertEqual(x, y)


class TestBuiltinConversions(unittest.TestCase):
    def test_none(self):
        self.assertEqual(K(None), q("::"))

    def test_bool(self):
        self.assertEqual(K(True), q("1b"))
        self.assertEqual(K(False), q("0b"))

    def test_int(self):
        self.assertEqual(K(1), q("1"))
        self.assertRaises(OverflowError, K, 2 ** 100)

    @unittest.skipIf(_PY3K, "long and int are unified in Py3K")
    def test_long(self):
        self.assertEqual(K(1), q("1"))
        self.assertRaises(OverflowError, K, 2 ** 100)

    def test_str(self):
        self.assertEqual(K(''), q("`"))

    def test_float(self):
        self.assertEqual(K(1.0), q("1f"))
        self.assertEqual(K(float('nan')), q("0Nf"))
        self.assertEqual(K(float('inf')), q("0w"))

    def test_datetime(self):
        self.assertEqual(K(date(2000, 1, 1)),
                         q("2000.01.01"))
        self.assertEqual(K(time(0)), q("00:00t"))
        self.assertEqual(K(datetime(2000, 1, 1)),
                         q("2000.01.01D00:00:00.000000000"))
        self.assertEqual(K(timedelta(1)), q("1D"))

    def test_list(self):
        self.assertEqual(K([]), q("()"))
        self.assertEqual(K([1]), q("enlist 1"))
        self.assertEqual(K([1, 2]), q("1 2"))
        self.assertEqual(K([1, None]), q("1 0N"))

        self.assertEqual(K([1.0]), q("enlist 1f"))
        self.assertEqual(K([1.0, 2.0]), q("1 2f"))
        self.assertEqual(K([1.0, float('nan')]), q("1 0n"))

        self.assertEqual(K(['']), q("enlist`"))
        self.assertEqual(K(['a', 'b']), q("`a`b"))

        self.assertEqual(K([date(2001, 1, 1)]), q('enlist 2001.01.01'))
        self.assertEqual(K([date(2001, 1, 1), None]), q('2001.01.01 0Nd'))
        self.assertEqual(K(5 * [date(2001, 1, 1)]), q('5#2001.01.01'))

    def test_tuple(self):
        self.assertEqual(K(()), q("()"))
        t = (False, 0, 0.0, '', kp(b''), date(2000, 1, 1))
        self.assertEqual(K(t), q("(0b;0;0f;`;\"\";2000.01.01)"))


def test_dict():
    assert K({}) == q('()!()')
    assert K({'a': 1}) == q('enlist[`a]!enlist 1')


class CallTestCase(unittest.TestCase):
    def test_a0(self):
        self.assertEqual(q('{1}')(), q('1'))

    def test_a1(self):
        self.assertEqual(q('::')(1), q('1'))

    def test_a2(self):
        self.assertEqual(q('+')(1, 2), q('3'))

    def test_a3(self):
        self.assertEqual(q('?')(q('10b'), 1, 2), q('1 2'))

    def test_err(self):
        try:
            q("{'`test}", 0)
        except kerr as e:
            self.assertEqual(e.args[0], 'test')
        q("f:{'`test}")
        try:
            q("{f[x]}")(42)
        except kerr as e:
            self.assertEqual(e.args[0], 'test')


if Q_VERSION >= 3:
    class TestGUID(unittest.TestCase):
        def test_conversion(self):
            from uuid import UUID

            u = UUID('cc165d74-88df-4973-8dd1-a1f2e0765a80')
            self.assertEqual(int(K(u)), u.int)


class TestOrderedDict(unittest.TestCase):
    def test_conversion(self):
        import collections

        odict = getattr(collections, 'OrderedDict', None)
        if odict is None:
            self.skipTest("no OrderedDict in collections")
        od = odict([('a', 1.0), ('b', 2.0)])
        self.assertEqual(K(od), q('`a`b!1 2f'))
        self.assertEqual(K(odict()), q('()!()'))


def test_seu():
    t = q('([]a:5 8 9 4;b:4 3 2 4)')
    assert t.select('a', by='b') == k('(+(,`b)!,2 3 4)!+(,`a)!,(,9;,8;5 4)')
    assert t.select('a', where='b>c', c=3) == k('+(,`a)!,5 4')
    assert t.select('a', where='a<c', by='b', c=7) == k(
        '(+(,`b)!,,4)!+(,`a)!,,5 4')
    assert t.select('a,b,c', where='a>b', c=[2, 3, 4]) == k(
        '+`a`b`c!(5 8 9;4 3 2;2 3 4)')

    t = q('([]a:5 8 9 4;b:4 3 2 4)')
    assert t.exec_('a', by='b') == k('2 3 4!(,9;,8;5 4)')
    assert t.exec_('a', where='b>c', c=3) == [5, 4]

    t = q('([]a:5 8 9 4;b:4 3 2 4)')
    assert t.update('a:sum a', by='b') == k('+`a`b!(9 8 9 9;4 3 2 4)')
    assert t.update('a:a+b', where='a>c', c=8) == k('+`a`b!(5 8 11 4;4 3 2 4)')
    assert t.update('a:b-c,b:b+c', where='a=b', c=10) == k(
        '+`a`b!(5 8 9 -6;4 3 2 14)')


def test_select_list():
    t = q('([]a:1 2 3;b:4 5 6)')
    assert t.select(['b', 'a']).cols == ['b', 'a']
    assert t.select(['b'], by=['a']).key.cols == ['a']
    assert t.select(['b'], where=['a<3', 'a>1']).b == [5]


def test_getattr():
    assert q("([a:1 2 3]b:10 20 30)").b == k('10 20 30')

    t = q("2013.12.16T10:12:44.053")

    assert t.hh == k('10i')
    assert t.date == k('2013.12.16')
    assert t.mm == k('12i')
    assert t.second == k('10:12:44')
    # assert t.ss == k('44i')   # Conflicts with .q.ss

    with pytest.raises(AttributeError) as e:
        x = q("2013.12.16T10:12:44").hours
    assert e.typename == 'AttributeError'


def test_q_setattr():
    q.xyz = 1
    assert q('xyz') == 1

    q.x = [1, 2]
    assert q('x~1 2')


def test_q_delattr():
    q.x = q.y = q.z = 5
    del q.x, q.y, q.z

    with pytest.raises(AttributeError):
        q.x


def test_bool():
    assert K([True, False, False]) == q('100b')


# 574
def test_ss():
    haystack = q.string('baa')
    needle = q.string('aa')
    assert haystack.ss(needle) == [1]

    t = q('01:02:03')
    assert t.ss == q("3i")


def test_K_getattr():
    x = q('`a`b!41 42')

    assert x.b == 42


def test_compare():
    assert K(1) < K(2)
    assert K(2) > K(1)
    assert K(2) <= K(2)
    assert K(1) >= K(1)


def test_compare_mixed():
    assert K(2) > 1
    assert 1 < K(2)


def test_compare_notimplemented():
    with pytest.raises(NotImplementedError):
        K([1, 2]) < K([2, 3])
    with pytest.raises(NotImplementedError):
        K(1) < K([1, 2])


def test_xor_as_fill():
    x = q('1 0N')
    assert K(2) ^ x == [1, 2]
    assert 2 ^ x == [1, 2]
    assert [1, 2] ^ x == [1, 2]


def test_xor_as_coalesce():
    x = q('([a:0 1 2]b:0 10 20)')
    y = q('([a:1 2 3]b:11 0N 31)')
    r = x ^ y

    assert r.b == [0, 11, 20, 31]


def test_arith_unary():
    assert +K(1) == 1
    assert +q('(1 2;3 4)') == q('(1 3;2 4)')

    assert -K(1) == -1

    assert ~K(True) == False  # noqa
    assert ~K([False, True]) == [True, False]


def test_arith_binary():
    assert K(1) + 2 == 1 + K(2) == 1 + 2
    assert K(1) - 2 == 1 - K(2) == 1 - 2
    assert K(1) * 2 == 1 * K(2) == 1 * 2
    assert K(1) / 2 == 1 / K(2) == 1 / 2
    assert K(1) // 2 == 1 // K(2) == 1 // 2
    assert K(1) % 2 == 1 % K(2) == 1 % 2
    assert K(2) ** 3 == 2 ** K(3) == 2. ** 3
    assert abs(-K(1)) == 1


def test_python_keywords():
    x = K(True)
    assert x.and_(False) == False  # noqa
    assert x.or_(False) == True  # noqa

    x = K([1, 2, 3])
    assert x.except_(2) == [1, 3]

    q.except_([1, 2], [2, 3]) == [1]


def test_dict_conversion():
    x = q("`a`b!1 2")

    assert dict(x) == {'a': 1, 'b': 2}


def test_keyed_table():
    x = q("([a:1 2]b:10 20)")
    assert len(x) == 2


@pytest.mark.parametrize('e', [
    '(::;1)',
    '00b',
    '0 0',
    '1 2!3 4',
    '([]x:0 0)',
    '([x:0 0]y:1 1)',
])
def test_convertion_to_bool_vector(e):
    x = q(e)
    assert x
    assert not q('0#', x)


@pytest.mark.parametrize('t,f', zip(
    ['1b', '0x1', '1e', '1i', '1j', '0p', '1n', '`s'],
    ['0b', '0x0', '0e', '0i', '0j', '0', '0*1n', '`'],
))
def test_convertion_to_bool_scalar(t, f):
    assert q(t)
    assert not q(f)


def test_show_str():
    x = K(1)
    assert x.show(0, (1, 2), output=str) == '1' + os.linesep
    assert x.show(output=str) == '1' + os.linesep


def test_show_capture(capsys):
    x = K(1)
    x.show(0, (1, 2))
    out, _ = capsys.readouterr()
    assert out == '1' + os.linesep


def test_show_start():
    t = q("([]til 10)")
    assert t.show(5, (20, 20), str) == t.show(-5, (20, 20), str) == """\
x
-
5
6
7
8
9
""".replace('\n', os.linesep)


@pytest.mark.parametrize('x,fmt,r', [
    ('2001.01.01', '{:%Y-%m-%d}', '2001-01-01'),
    ('2001.01.01T12', '{:%Y-%m-%d %H}', '2001-01-01 12'),
    ('2001.01m', '{:%Y-%m}', '2001-01'),
    ('12t', '{:%H}', '12'),
    ('12:00', '{:%H}', '12'),
    ('12:01:02', '{:%H%M%S}', '120102'),
    ('`xyz', '{:4s}', 'xyz '),
    ('1b', '{:d}', '1'),
    ('10000i', '{:,}', '10,000'),
    ('10000j', '{:,}', '10,000'),
    ('3.14e', '{:.1f}', '3.1'),
    ('3.14f', '{:.1f}', '3.1'),
    ('"Z"', '{:2s}', 'Z '),
    ('0xef', '{:x}', 'ef'),
    ('::', '{}', '::'),
])
def test_format(x, fmt, r):
    assert fmt.format(q(x)) == r


@pytest.mark.parametrize('x, r', [
    ('2001.01.01', date(2001, 1, 1)),
    ('2001.01m', date(2001, 1, 1)),
    ('1900.12m', date(1900, 12, 1)),
    ('20t', time(20, 0)),
    ('20:01', time(20, 1)),
    ('20:01:01', time(20, 1, 1)),
    ('20:01:01.007', time(20, 1, 1, 7000)),
])
def test_pys(x, r):
    assert q(x)._pys() == r


@pytest.mark.parametrize('t', ['h', 'i', 'j'])
def test_index_good(t):
    x = [1, 2, 3]
    i = q('1' + t)
    assert x[i] == 2


def test_index_bad():
    x = [1, 2, 3]
    with pytest.raises(TypeError):
        x[K(1.5)]


def test_coverters_buffer0():
    if _PY3K:
        assert K(b'abc') == k('"abc"')
    else:
        assert K(buffer('abc')) == k('"abc"')


def test_nil_str():
    assert str(nil) == '::'


def test_nil_repr():
    assert repr(nil) == "k('::')"


def test_nil_show():
    nil.show(output=str) == '::\n'
    x = q('last value +[;]')
    x.show(output=str) == '::\n'


def test_decode():
    x = q('"abc"')
    assert x.decode() == 'abc'
    # tester that decode works with the output of _show()
    x = q.til(5)
    r = x._show([100, 100], 0)
    assert r.decode() == x.show(0, [100, 100], str)


def test_descriptor():
    class X(K):
        square = q('{x*x}')

    x = X(2)
    assert x.square == 4

    # See issue #644
    class N(object):
        square = q('{x*x}')

    n = N()
    assert n.square(2) == 4


def test_conversion_error_in_eq():
    assert not K(1) == object()


@pytest.mark.parametrize('cls, args', [
    (str, []),
    (int, []),
    (float, []),
    (date, [2000, 1, 1]),
    (time, []),
    (list, ([[1], [2, 3]],))
])
def test_list_conversion(cls, args):
    x = cls(*args)
    assert K([x])[0] == x


def test_nested_list_conversion():
    x = [[1, 2, 3],
         ['a', 'b'],
         [[1, 1], [2, 2]], ]
    assert K(x) == q("(1 2 3;`a`b;(1 1; 2 2))")


if not _PY3K:
    def test_getitem_long():
        x = q('1 2 3f')
        assert isinstance(x[long(1)], float)


def test_nested_tuple_conversion():
    x = (1, (2, 3.14))
    assert K(x) == q("(1;(2;3.14))")


@pytest.mark.parametrize("start, stop, stride, size", [
    (None, None, None, 5),
    (None, 1, -1, 5),
    (1, 5, 2, 10),
    (8, 2, -2, 10),
])
def test_slice(start, stop, stride, size):
    x = q.til(size)
    y = list(range(size))
    assert x[start:stop:stride] == y[start:stop:stride]

    d = q('!', x, x)
    s = d[start:stop:stride]
    assert s.key == s.value == y[start:stop:stride]


def test_slice_error():
    x = q.til(1)
    with pytest.raises(ValueError):
        x = x[1:2:0]
    assert x == [0]


@pytest.mark.parametrize("start, stop, stride", [
    (2, 1, 2),
    (1, 2, -1),
])
def test_empty_slice(start, stop, stride):
    x = q.til(10)
    assert x[start:stop:stride].count == 0


@pytest.mark.parametrize('cls', ['int', 'float'])
def test_scalar_conversion_error(cls):
    x = q('1 2')
    with pytest.raises(TypeError):
        eval(cls)(x)


def test_unicode():
    assert K(u'abc') == u'abc'
    assert K([u'abc']) == [u'abc']


def test_q_error():
    with pytest.raises(TypeError):
        q(1)


def test_q_cmdloop(monkeypatch):
    called = [0]

    def cmdloop(self):
        called[0] += 1

    from ..cmd import Cmd
    monkeypatch.setattr(Cmd, 'cmdloop', cmdloop)
    q()
    assert called[0]


def test_contains():
    assert 1 in q('1 2 3')
    assert 'abc' in q('(1;2.0;`abc)')


def test_scalar_conversions():
    x = K(1)
    assert float(x) == 1
    assert int(x) == 1


def test_call():
    f = q('{x-y}')
    assert f(1, 2) == f(y=2, x=1) == f(y=2)(1) == -1
    with pytest.raises(TypeError):
        f(1, x=1)


def test_issue_715():
    t = q("([]a:til 3)")
    assert t[2].value == [2]


@pytest.mark.skipif(_PY3K, reason="No 'long' type in Python 3.x")
def test_list_of_long():
    x = eval("[1L, 2L]")
    assert K(x) == [1, 2]
    x = eval("[1, 2L]")
    assert K(x) == [1, 2]
    x = eval("[1L, 2]")
    assert K(x) == [1, 2]


def test_q_dir(q):
    assert 'exp' in dir(q)
    q.foo = 42
    assert 'foo' in dir(q)


@pytest.mark.skipif(not _PY3K, reason="exec is a keyword in Python <3")
def test_plain_exec():
    t = q('([]a:1 2)')
    assert eval('t.exec("a")') == [1, 2]


def python_function(x, y):
    return x + y


def python_date():
    return date(2000, 1, 1)


def python_error():
    raise ValueError


def test_call_python_function_success(q):
    q.f = python_function
    assert q('f(1;2)') == 3
    q.g = math.log
    assert q('g enlist 1') == 0.0
    q.d = python_date
    assert q('d()') == q('2000.01.01')


def test_call_python_function_error(q):
    q.f = python_function
    with pytest.raises(kerr) as e:
        q('f(1;`)')
    assert e.value.args[0] == 'type'
    q.e = python_error
    with pytest.raises(kerr) as e:
        q('e()')
    assert e.value.args[0] == 'ValueError'
    # Invalid use of call_python_object
    call_python_object = q.f.value[0]
    with pytest.raises(kerr) as e:
        call_python_object(None, None, None)
    assert 'type error' in str(e.value)


def test_versions(capsys):
    versions()
    out = capsys.readouterr()[not _PY3K]
    assert 'PyQ' in out


def test_attr_complete():
    # Test that q and K have all expected attributes
    all_names = q('distinct .Q.res,1_key`.q')
    not_expected = {'if', 'do', 'while', 'from', 'delete', 'exit'}
    if not _PY3K:
        not_expected.add('exec')
    for name in all_names:
        if name not in not_expected:
            if iskeyword(name):
                name += '_'
            assert hasattr(K, name)
    not_expected.update({'exec', 'select', 'delete', 'update'})
    for name in all_names:
        if name not in not_expected:
            if iskeyword(name):
                name += '_'
            assert hasattr(q, name)


@pytest.mark.parametrize("a, b, result", [
    ('1 2 3', '1', '2'),
    ('{x+1}', '1', '2'),
])
def test_matmul(a, b, result):
    a, b, result = map(q, [a, b, result])

    def mm(x, y):
        return eval('x @ y') if sys.version_info >= (3, 5) else x.__matmul__(y)

    assert result == mm(a, b)


def test_rmatmul():
    def rmm(x, y):
        return eval('x @ y') if sys.version_info >= (3, 5) else y.__rmatmul__(
            x)

    assert rmm([1, 2], K(1)) == 2


def test_casts(q):
    x = q.til(5)
    assert x.short == q('$', 'short', x)


def test_constructors():
    x = K.long([])
    assert x == q('$', 'long', ())


@pytest.mark.parametrize("x,y", [
    ('', '""'),
    ('a', ',"a"'),
    ([], '()'),
    (['abc'], ',"abc"'),
    ([['abc']], ',,"abc"'),
    ([['abc'], 'def'], '(,"abc";"def")')
])
def test_string_constructor(x, y):
    assert K.string(x) == k(y)


def test_string_constructor_error():
    x = [None]
    x[0] = x  # Makes a self-referencing list
    with pytest.raises(RuntimeError):
        K.string(x)


def test_table_cols_priority():
    # Plain table
    t = +q('`date`time`char!', ())
    assert t.date._t == t.time._t == t.char._t == 0
    # Keyed table
    t = q('1!', t)
    assert t.date._t == t.time._t == t.char._t == 0


def test_dict_key_priority():
    d = q('`string`date`time`char!1 2 3 4')
    assert d.string == 1
    assert d.date == 2
    assert d.time == 3
    assert d.char == 4


@pytest.mark.parametrize('char, name', [
    ('h', 'short'),
    ('i', 'int'),
    ('j', 'long'),
    ('e', 'real'),
    ('f', 'float'),
    ('c', 'char'),
    ('p', 'timestamp'),
    ('m', 'month'),
    ('d', 'date'),
    ('z', 'datetime'),
    ('n', 'timespan'),
    ('u', 'minute'),
    ('v', 'second'),
    ('t', 'time'),
])
def test_special_values(q, char, name):
    assert getattr(K, name).inf == q('0W' + char)
    assert getattr(K, name).na == q('0N' + char)


@pytest.mark.skipif("Q_VERSION < 3")
def test_guid_na():
    x = K.guid.na
    assert x.null
    assert x == q('0Ng')


@pytest.mark.parametrize('type_name', [
    'boolean',
    pytest.mark.skipif("Q_VERSION < 3", 'guid'),
    'short',
    'int',
    'long',
    'real',
    'float',
    'char',
    'symbol',
    'timestamp',
    'month',
    'date',
    # 'datetime',  - not implemented
    'timespan',
    'minute',
    'second',
    'time',
])
def test_empty_list(type_name):
    constructor = getattr(K, type_name)
    x = constructor([])
    assert x.count == 0
    assert x.key == type_name


@pytest.mark.parametrize('type_name', [
    # 'boolean',
    # pytest.mark.skipif("Q_VERSION < 3", 'guid'),
    'short',
    'int',
    'long',
    'real',
    'float',
    'timestamp',
    'month',
    'date',
    # 'datetime',  - not implemented
    'timespan',
    'minute',
    'second',
    'time',
])
def test_from_range(type_name):
    constructor = getattr(K, type_name)
    x = constructor(range(2))
    assert list(x.long) == [0, 1]
    assert x.key == type_name


@pytest.mark.parametrize('type_name', [
    'short',
    'int',
    'long',
    # 'real',
    # 'float',
    'timestamp',
    'month',
    'date',
    # 'datetime',  - not implemented
    'timespan',
    'minute',
    'second',
    'time',
])
def test_special_values(type_name):
    constructor = getattr(K, type_name)
    big_number = 2 ** 100
    x = constructor([-big_number, None, big_number])
    assert x.first == -constructor.inf
    assert x.last == constructor.inf
    assert x(1) == constructor.na


def test_interned():
    x = K('aaa')
    assert str(x) is str(x)
    x = K(['aaa'] * 5)
    assert x[0] is x[-1]


def test_strings_constructor():
    assert K.string(b'') == K.string(u'') == q('""')
    assert K.string([b'bytes', u'unicode', 'whatever']) == q(
        '("bytes";"unicode";"whatever")'
    )


@pytest.mark.parametrize('x, n, result', [
    ('1111b', 2, '1100b'),
    ('til 5', 3, '3 4 0N 0N 0N'),
])
def test_lshift(x, n, result):
    x, result = map(q, [x, result])
    assert (x << n) == (x >> -n) == result
    assert (x.enlist << n) == (x.enlist >> -n) == result.enlist


@pytest.mark.parametrize('x, n, result', [
    ('1111b', 2, '0011b'),
    ('til 5', 3, '0N 0N 0N 0 1'),
])
def test_rshift(x, n, result):
    x, result = map(q, [x, result])
    assert (x >> n) == (x << -n) == result
    assert (x.enlist >> n) == (x.enlist << -n) == result.enlist


def test_rlshift():
    assert ([1, 2, 3] << K(2)) == q('3 0N 0N')


def test_rrshift():
    assert ([1, 2, 3] >> K(2)) == q('0N, 0N 1')


BASE_SIZE = object.__sizeof__(K([]))


@pytest.mark.parametrize('x, n', [
    ('0b', 9),
    pytest.mark.skipif("Q_VERSION < 3", ('0Ng', 24)),
    ('0x0', 9),
    ('0h', 10),
    ('0i', 12),
    ('0j', 16),
    ('0e', 12),
    ('0f', 16),
])
def test_scalar_sizeof(q, x, n):
    x = q(x)
    assert BASE_SIZE + n == x.__sizeof__()


@pytest.mark.skipif("Q_VERSION < 3")
@pytest.mark.parametrize('x, n32, n64', [
    ('1 2!3 4', 88, 96),
    ('([]a:1 2)', 116, 136),
    ('+', 24, 24),
])
def test_misc_sizeof(q, x, n32, n64):
    n = n32 if q('.z.o like"?32"') else n64
    x = q(x)
    assert BASE_SIZE + n == x.__sizeof__()


@pytest.mark.skipif('not _PY3K')
@pytest.mark.parametrize('x, b', [
    ('"abc"', b'abc'),
    ('5', 5 * b'\0'),
    ('0x010203', bytes([1, 2, 3])),
    ('1 2 3h', b'\x01\x00\x02\x00\x03\x00'),
    ('`aaa', BufferError),
    ('`a`a`a', BufferError),
    # Atoms
    ('0b', b'\0'),
    ('1b', b'\1'),
    pytest.mark.skipif("Q_VERSION < 3 or not _PY3K", ('0Ng', 16 * b'\0')),
    ('0x42', b'\x42'),
    ('0h', b''),
    ('0i', b''),
    ('0j', b''),
    ('0e', 4 * b'\0'),
    ('0f', 8 * b'\0'),
    ('"a"', b'a'),
    ('`', BufferError),
    ('0Np', BufferError),
    ('0Nm', BufferError),
    ('0Nd', BufferError),
    ('0Nn', BufferError),
    ('0Nu', BufferError),
    ('0Nv', BufferError),
    ('0Nt', BufferError),
    # Lists
    ('2#0b', 2 * b'\0'),
    ('2#1b', 2 * b'\1'),
    pytest.mark.skipif("Q_VERSION < 3 or not _PY3K",
                       ('2#0Ng', 2 * 16 * b'\0')),
    ('2#0x42', 2 * b'\x42'),
    ('2#0h', 2 * 2 * b'\0'),
    ('2#0i', 2 * 4 * b'\0'),
    ('2#0j', 2 * 8 * b'\0'),
    ('2#0e', 2 * 4 * b'\0'),
    ('2#0f', 2 * 8 * b'\0'),
    ('2#"a"', 2 * b'a'),
    ('2#`', BufferError),
    ('2#0Np', BufferError),
    ('2#0Nm', BufferError),
    ('2#0Nd', BufferError),
    ('2#0Nn', BufferError),
    ('2#0Nu', BufferError),
    ('2#0Nv', BufferError),
    ('2#0Nt', BufferError),
    # Other types
    ('()', BufferError),
    ('()!()', BufferError),
    ('([]a:1 2)', BufferError),
])
def test_bytes_from_k(x, b):
    x = q(x)
    if type(b) is bytes:
        assert b == bytes(x)
    else:
        with pytest.raises(b):
            bytes(x)


def test_from_sequence():
    assert K(range(3)) == q.til(3)


@pytest.mark.parametrize('x, r', [
    ([], '()'),
    ([None, 1], '0N 1'),
    ([1, ''], '(1;`)'),
    (['', ['']], '(`;,`)'),
    (['', [['']]], '(`;,,`)'),
    (['', [[['']]]], '(`;,,,`)'),
    ([[1, 2], ['a', 'b']], '(1 2;`a`b)'),
])
def test_list_conversions(x, r):
    assert k(r) == K(x)


@pytest.mark.parametrize('x, r', [
    ((), '()'),
    ((0, None), '(0;::)'),
    ((0,), ',0'),
    ((1, 2), '1 2'),
    (((1, 2), 3), '(1 2;3)'),
])
def test_tuple_conversions(x, r):
    assert k(r) == K(x)


@pytest.mark.parametrize('x, i, r', [
    ('`a`b!1 2', 'a', 1),
    ('1 2!`a`b', 1, 'a'),
])
def test_dict_getitem(x, i, r):
    x = q(x)
    y = x[i]
    assert y == r
    assert type(y) is type(r)


def test_mro_conversion():
    class D(dict):
        pass

    assert K(D()) == q('()!()')


def test_namedtuple_conversion():
    Point = namedtuple('Point', 'x,y')
    p = Point(1, 2)
    assert K(p) == q('`x`y!1 2')


@pytest.mark.skipif("not hasattr(os, 'fspath')")
def test_fspath():
    x = q.hsym('foo')
    assert os.fspath(x) == 'foo'
    with pytest.raises(TypeError):
        os.fspath(q.til(0))
    with pytest.raises(TypeError):
        os.fspath(K(''))


def test_str_enum(q):
    a = q("`sym?`a`b")
    assert str(a.first) == 'a'
    b = q("`xxx?`x`y")
    assert str(b.last) == 'y'
    del q.sym
    assert str(a.first) == '0' if Q_VERSION < 3 else '0i'
    q.sym = ['a']
    assert str(a.last) == ''


def test_complex():
    z = 1 + 2j
    x = K(z)
    assert x.im == z.imag
    assert x.re == z.real
    assert x == z
    assert complex(x) == z
    assert complex(K(42)) == 42


def test_long_clip_inf():
    nj = int(K.long.na)
    assert K.long(range(nj - 3, nj + 3)) == q(
        '-0W -0W -0W -0W -0W -9223372036854775806j')


@pytest.mark.parametrize('a, x', [
    ('each', "'"),
    ('over', "/"),
    ('scan', "\\"),
    ('prior', "':"),
    ('sv', "/:"),
    ('vs', "\:"),
])
def test_adverb(a, x):
    adverb = getattr(K, a)
    assert adverb == q("(%s)" % x)


def test_call_with_keywords():
    f = q.neg
    assert f(x=1) == -1
    f = q('+')
    assert f(y=2) == f(nil, 2)
    f = q('{z}')
    g = f(1, 2)
    assert g(z=3) == 3
    each = q("(')")
    f_each = each(f=f)
    g_each = f_each(x=1, y=2)
    assert g_each(z=[10, 20]) == [10, 20]
    f = q('{[a;b]a-b}')
    assert f(1, 2) == f(1)(2) == f(b=2)(1) == f(b=2, a=1)


def test_char_cast():
    x = q('0x4142')
    assert x.char == K.char('AB')


def test_bpo_issue27576_workaround():
    x = q('(0#`)!()')
    with pytest.raises(AttributeError):
        x.items


def test_constructor_as_cast():
    x = K.short(2)
    assert K.short(x) is x
    assert K.long(x) == q('2j')


def test_construct_nested():
    x = [1, [2, 3], [[4]]]
    assert K.long(x) == q('(1j;2 3j;enlist enlist 4j)')
    c = ["c", "ab", [""]]
    assert K.char(c) == q('("c";"ab";enlist"")')
    assert K.string(c) == q('(enlist"c";"ab";enlist"")')


def test_cast_string():
    x = K(10)
    assert x.string == q('"10"')


def test_too_deep():
    x = []
    x.append(x)
    with pytest.raises(RuntimeError):
        K.char(x)


@pytest.mark.skipif("q('.z.K') < 3.4")
def test_vector_from_scalar():
    ymd = q.vs([10000, 100, 100])
    assert ymd(20170124) == [2017, 1, 24]
    tobytes = K.byte(0).vs
    assert tobytes(2 ** 63 - 1) == q('0x7fffffffffffffff')
    split = q.vs('')
    _, x = split(':a/b/c')
    assert x == 'c'
    assert split('a.b.c') == q('`a`b`c')


def test_scalar_from_vector():
    ymd = q.sv([10000, 100, 100])
    assert ymd([2017, 1, 24]) == 20170124


@pytest.mark.parametrize('type_name', [
    'boolean',
    'short',
    'int',
    'long',
    'real',
    'float',
    'timestamp',
    'month',
    'date',
    'datetime',
    'timespan',
    'minute',
    'second',
    'time',
])
def test_scalar_from_zero(type_name):
    cons = getattr(K, type_name)
    z = cons(0)
    assert int(z) == 0


def test_boolean_constructor(q):
    x = K.boolean([None, {}, 10])
    assert x == q('(0b;()!`boolean$();1b)')


def test_issue_875(q):
    x = q("`sym?`x")
    n = q("`sym$`")
    # Test error condition
    value = q.value
    try:
        q(".q.value:{'error}")
        with pytest.raises(kerr):
            bool(x)
    finally:
        q.set('.q.value', value)
    # Test deleted domain vector case
    del q.sym
    assert x
    assert not n


def test_typed_from_mapping(q):
    x = OrderedDict([('a', 0), ('b', 1)])
    assert K.boolean(x) == q('`a`b!01b')
    x = OrderedDict([('a', "x"), ('b', "y")])
    assert K.string(x) == q('`a`b!(enlist"x";enlist"y")')
    assert K.char(x) == q('`a`b!"xy"')


def test_issue_923(q):
    assert K([0.0, '', 0]) == q('(0f;`;0)')
    assert K([0, '', 0.0]) == q('(0;`;0f)')


@pytest.mark.skipif("Q_VERSION < 3.5")
def test_trp_k():
    from pyq import _trp_k
    with pytest.raises(kerr) as info:
        _trp_k(K, 0, "{x+y}", K(0), K(''))
    assert info.value.args[0] == 'type'
    assert info.value.args[1].type == K.short(0)


@pytest.mark.skipif("Q_VERSION < 3.5")
def test_trp_call():
    from pyq import _trp_call
    f = q('{x+y}')
    with pytest.raises(kerr) as info:
        _trp_call(f, 0, '')
    assert info.value.args[0] == 'type'
    assert info.value.args[1].type == K.short(0)


@pytest.mark.parametrize("x, sp", [
    (nil, True),
    ([nil], True),
    ([1, nil], True),
    ([1, nil, 2], True),
    ([1, 2], False),
    ([], False),
    (0, False)
])
def test_sp(x, sp):
    if isinstance(x, list):
        x = K._knk(len(x), *[K(a) for a in x])
    else:
        x = K(x)

    assert x._sp() == sp
