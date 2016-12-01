from __future__ import division
from __future__ import absolute_import
import unittest
import pytest

from pyq import *

q("\\e 0")  # disable q's debug on error
KXVER = int(q('.Q.k'))
PY3K = str is not bytes


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

    @unittest.skipIf(PY3K, "long and int are unified in Py3K")
    def test_long(self):
        self.assertEqual(K(1), q("1j"))
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
            self.assertEqual(str(e), 'test')
        q("f:{'`test}")
        try:
            q("{f[x]}")(42)
        except kerr as e:
            self.assertEqual(str(e), 'test')


if KXVER >= 3:
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
    assert t.select('a', where='a<c', by='b', c=7) == k('(+(,`b)!,,4)!+(,`a)!,,5 4')
    assert t.select('a,b,c', where='a>b', c=[2, 3, 4]) == k('+`a`b`c!(5 8 9;4 3 2;2 3 4)')

    t = q('([]a:5 8 9 4;b:4 3 2 4)')
    assert t.exec_('a', by='b') == k('2 3 4!(,9;,8;5 4)')
    assert t.exec_('a', where='b>c', c=3) == [5, 4]

    t = q('([]a:5 8 9 4;b:4 3 2 4)')
    assert t.update('a:sum a', by='b') == k('+`a`b!(9 8 9 9;4 3 2 4)')
    assert t.update('a:a+b', where='a>c', c=8) == k('+`a`b!(5 8 11 4;4 3 2 4)')
    assert t.update('a:b-c,b:b+c', where='a=b', c=10) == k('+`a`b!(5 8 9 -6;4 3 2 14)')


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


#574
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

    assert ~K(True) == False
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
    assert x.and_(False) == False
    assert x.or_(False) == True

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
    ['1b', '0x1', '1e', '1i', '1j', '1p', '1n', '`s'],
    ['0b', '0x0', '0e', '0i', '0j', '0p', '0*1n', '`'],
))
def test_convertion_to_bool_scalar(t, f):
    assert q(t)
    assert not q(f)


def test_show_str():
    x = K(1)
    assert x.show(0, (1, 2), output=str) == '1\n'
    assert x.show(output=str) == '1\n'


def test_show_capture(capsys):
    x = K(1)
    x.show(0, (1, 2))
    out, _ = capsys.readouterr()
    assert out == '1\n'


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
"""


@pytest.mark.parametrize('x,fmt,r', [
    ('2001.01.01', '{:%Y-%m-%d}',  '2001-01-01'),
    ('2001.01.01T12', '{:%Y-%m-%d %H}',  '2001-01-01 12'),
    ('2001.01m', '{:%Y-%m}',  '2001-01'),
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
])
def test_format(x, fmt, r):
    assert fmt.format(q(x)) == r


@pytest.mark.parametrize('x, r', [
    ('2001.01.01', date(2001, 1, 1)),
    ('2001.01m', date(2001, 1, 1)),
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
    if PY3K:
        assert K(b'abc') == k('"abc"')
    else:
        assert K(buffer('abc')) == k('"abc"')


def test_nil_str():
    assert str(nil) == '::'


def test_nil_repr():
    assert repr(nil) == "k('::')"


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


if not PY3K:
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


def test_call_proxy():
    assert isinstance(K.__call__, K_call_proxy)


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


@pytest.mark.skipif(PY3K, reason="No 'long' type in Python 3.x")
def test_list_of_long():
    x = eval("[1L, 2L]")
    assert K(x) == [1, 2]
    x = eval("[1, 2L]")
    assert K(x) == [1, 2]
    x = eval("[1L, 2]")
    assert K(x) == [1, 2]


def test_versions(capsys):
    versions()
    out = capsys.readouterr()[not PY3K]
    assert 'PyQ' in out
