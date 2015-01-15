"""Python interface to the Q language

The following examples are adapted from the "Kdb+ Database and Language Primer"
by Dennis Shasha <http://kx.com/q/d/primer.htm>

>>> y = q('`aaa`bbbdef`c'); y[0]
'aaa'

Unlike in Q, in python function call syntax uses '()' and
indexing uses '[]':
>>> z = q('(`abc; 10 20 30; (`a; `b); 50 60 61)')
>>> z(2, 0)
k('`a')
>>> z[q('0 2')] # XXX: Should be able to write this as z[0,2]
k('(`abc;`a`b)')


Dictionaries

>>> fruitcolor = q('`cherry`plum`tomato!`brightred`violet`brightred')
>>> fruitcolor['plum']
k('`violet')
>>> fruitcolor2 = q('`grannysmith`plum`prune!`green`reddish`black')
>>> q(',', fruitcolor, fruitcolor2)
k('`cherry`plum`tomato`grannysmith`prune!`brightred`reddish`brightred`green`black')

Tables from Dictionaries

>>> d = q('`name`salary! (`tom`dick`harry;30 30 35) ')
>>> e = q.flip(d)
>>> e[1]
k('`name`salary!(`dick;30)')
>>> q('{select name from x}', e)
k('+(,`name)!,`tom`dick`harry')
>>> q('{select sum salary from x}', e).salary
k(',95')

>>> e2 = q.xkey('name', e)
>>> q('+', e2, e2)
k('(+(,`name)!,`tom`dick`harry)!+(,`salary)!,60 60 70')
>>> q.keys(e2)
k(',`name')
>>> q.cols(e2)
k('`name`salary')

Temporal Primitives

>>> x = datetime(2004,7,3,16,35,24,980000)
>>> K(x)
k('2004.07.03D16:35:24.980000000')
>>> K(x.date()), K(x.time())
(k('2004.07.03'), k('16:35:24.980'))
>>> K(timedelta(200,200,200))
k('200D00:03:20.000200000')
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

__version__ = '3.7'
__metaclass__ = type
import os

try:
    import numpy as _np
except ImportError:
    _np = None

QVER = os.environ.get('QVER')
del os
PY3K = str is not bytes  # don't want to import sys
# Q sets QVER environment variable to communicate its version info to
# python. If it is not set - most likely you are attempting to run
# _PyQ under regular python.
if QVER is None:
    raise NotImplementedError("loading PyQ in stock python is not implemented")
_mod = '_k' + QVER
_k = __import__('pyq.' + _mod, level=0)
_k = getattr(_k, _mod)
from datetime import datetime, date, time, timedelta

# Starting with version 3.0, q default integer type is 64 bit.  Thus
# '1' now means '1j' rather than '1i'.  This messes up doctests. To
# fix this problem, _ij dict is introduced below.  We use the same
# mechanism to apply Py3K fixes.
if QVER[0] >= '3':
    _ij = dict(i='i', j='')
else:
    _ij = dict(i='', j='j')
_ij['b'] = repr(bytes())[-3:-2]  # 'b' in py3k, '' otherwise
_int_types = (int, ) if PY3K else (int, long)

if PY3K:
    _ij['_'] = ''
    _ij['div'] = 'truediv'
else:
    def _print(*args):
        for a in args:
            print(a, end=' ')
        print()

    _ij['_'] = '_'
    _ij['div'] = 'div'
__doc__ += """
Input/Output

>>> import os
>>> r,w = os.pipe()
>>> h = K(w)(kp("xyz"))
>>> os.read(r, 100)
{b}'xyz'
>>> os.close(r); os.close(w)
""".format(**_ij)

kerr = _k.error


class K_call_proxy:
    def __get__(self, obj, objtype):
        if obj is None:
            return self
        if obj.inspect(b't') == 100:
            return obj._call_lambda
        return obj._call


class K(_k.K):
    """a handle to q objects

    >>> k('2005.01.01 2005.12.04')
    k('2005.01.01 2005.12.04')

    Iteration over simple lists produces python objects
    >>> list(q("`a`b`c`d"))
    ['a', 'b', 'c', 'd']

    Iteration over q tables produces q dictionaries
    >>> list(q("([]a:`x`y`z;b:1 2 3)"))
    [k('`a`b!(`x;1)'), k('`a`b!(`y;2)'), k('`a`b!(`z;3)')]

    Iteration over a q dictionary iterates over its key
    >>> list(q('`a`b!1 2'))
    ['a', 'b']

    as a consequence, iteration over a keyed table is the same as
    iteration over its key table
    >>> list(q("([a:`x`y`z]b:1 2 3)"))
    [k('(,`a)!,`x'), k('(,`a)!,`y'), k('(,`a)!,`z')]

    Callbacks into python
    >>> def f(x, y):
    ...     return x + y
    >>> q('{[f]f(1;2)}', f)
    k('3')"""
    if not PY3K:
        __doc__ += """

    Buffer protocol:
    >>> x = kp('xxxxxx')
    >>> import os; r,w = os.pipe()
    >>> os.write(w, 'abcdef') == os.fdopen(r).readinto(x)
    True
    >>> os.close(w); x
    k('"abcdef"')"""
    __doc__ += """

    Array protocol:
    >>> ','.join([k(x).__array_typestr__
    ...  for x in ('0b;0x00;0h;0i;0j;0e;0.0;" ";`;2000.01m;2000.01.01;'
    ...            '2000.01.01T00:00:00.000;00:00;00:00:00;00:00:00.000')
    ...  .split(';')])
    '<b1,<u1,<i2,<i4,<i8,<f4,<f8,<S1,|O%d,<i4,<i4,<f8,<i4,<i4,<i4'
    """ % _k.SIZEOF_VOID_P

    try:
        import numpy
    except ImportError:
        pass
    else:
        del numpy
        if _k.SIZEOF_VOID_P == 4:
            dtypes = dict(i_dtype='', j_dtype=', dtype=int64')
        else:
            dtypes = dict(i_dtype=', dtype=int32', j_dtype='')
        __doc__ += """
    Numpy support
    ---------------

    >>> from numpy import asarray, array
    >>> asarray(k("1010b"))
    array([ True, False,  True, False], dtype=bool)

    >>> asarray(k("0x102030"))
    array([16, 32, 48], dtype=uint8)

    >>> asarray(k("0 1 2h"))
    array([0, 1, 2], dtype=int16)

    >>> asarray(k("0 1 2i"))
    array([0, 1, 2]{i_dtype})

    >>> asarray(k("0 1 2j"))
    array([0, 1, 2]{j_dtype})

    >>> asarray(k("0 1 2e"))
    array([ 0.,  1.,  2.], dtype=float32)

    >>> asarray(k("0 1 2.0"))
    array([ 0.,  1.,  2.])

    Date-time data-types expose their underlying data:

    >>> asarray(k(",2000.01m"))
    array([0]{i_dtype})

    >>> asarray(k(",2000.01.01"))
    array([0]{i_dtype})

    >>> asarray(k(",2000.01.01T00:00:00.000"))
    array([ 0.])

   """.format(**dtypes)
        del dtypes
    try:
        import Numeric
    except ImportError:
        pass
    else:
        del Numeric
        __doc__ += """
    Numeric support
    ---------------

    >>> from Numeric import asarray, array
    >>> asarray(k("1 2 3h"))
    array([1, 2, 3],'s')
    >>> K(array([1, 2, 3], 'd'))
    k('1 2 3f')

    K scalars behave like Numeric scalars
    >>> asarray([1,2,3]) + asarray(k('0.5'))
    array([ 1.5,  2.5,  3.5])
    >>> K(array(1.5))
    k('1.5')
    """
    __doc__ += """
    Low level interface
    -------------------

    The K type provides a set of low level functions that are similar
    to the C API provided by the k.h header. The C API functions that
    return K objects in C are implemented as class methods that return
    instances of K type.

    Atoms:
    >>> K._kb(True), K._kg(5), K._kh(42), K._ki(-3), K._kj(2**40), K._ke(3.5)
    (k('1b'), k('0x05'), k('42h'), k('-3{i}'), k('1099511627776{j}'), k('3.5e'))

    >>> K._kf(1.0), K._kc(b'x'), K._ks('xyz')
    (k('1f'), k('"x"'), k('`xyz'))

    >>> K._kd(0), K._kz(0.0), K._kt(0)
    (k('2000.01.01'), k('2000.01.01T00:00:00.000'), k('00:00:00.000'))


    Tables and dictionaries:
    >>> x = K._xD(k('`a`b`c'), k('1 2 3')); x, K._xT(x)
    (k('`a`b`c!1 2 3'), k('+`a`b`c!1 2 3'))

    Keyed table:
    >>> t = K._xD(K._xT(K._xD(k(",`a"), k(",1 2 3"))),
    ...           K._xT(K._xD(k(",`b"), k(",10 20 30"))))
    >>> K._ktd(t)
    k('+`a`b!(1 2 3;10 20 30)')

    """.format(**_ij)
    # Lighten the K objects by preventing the automatic creation of
    # __dict__ and __weakref__ for each instance.
    __slots__ = ()

    def __new__(cls, x):
        try:
            return _k.K.__new__(cls, x)
        except NotImplementedError:
            pass
        try:
            array_struct = x.__array_struct__
        except AttributeError:
            pass
        else:
            try:
                k = K._from_array_interface(array_struct, x)
            # TODO: Unsupported formats should raise NotImplementedError
            except ValueError:
                fields = [f for f, t in x.dtype.descr]
                k = q('!', list(fields), [K(x[f]) for f in fields])
                if x.ndim:
                    k = k.flip
            try:
                mask = x.mask
            except AttributeError:
                return k
            else:
                return q("{?[y;((),x)0N;x]}", k, mask)
        c = converters[type(x)]
        return c(x)

    def __reduce_ex__(self, proto):
        x = self._b9(-1, self)
        b = memoryview(x).tobytes()
        return (d9, (b,))

    def _call(self, *args):
        """call the k object

        Arguments are automatically converted to appropriate k objects
        >>> k('+')(date(1999,12,31), 2)
        k('2000.01.02')

        Strings are converted into symbols, use kp to convert to char
        vectors:
        >>> f = k('::')
        >>> [f(x) for x in ('abc', kp('abc'))]
        [k('`abc'), k('"abc"')]

        """
        return super(K, self).__call__(*map(K, args))

    def _call_lambda(self, *args, **kwds):
        """call the k lambda

        >>> f = q('{[a;b]a-b}')
        >>> assert f(1,2) == f(1)(2) == f(b=2)(1) == f(b=2,a=1)
        >>> f(1,a=2)
        Traceback (most recent call last):
        ...
        TypeError: {[a;b]a-b} got multiple values for argument 'a'
        """
        if not kwds:
            return self._call(*args)
        names = self._k(0, '{(value x)1}', self)
        kargs = [nil] * len(names)
        l = len(args)
        kargs[:l] = args
        for i, n in enumerate(names):
            v = kwds.get(n)
            if v is not None:
                if i >= l:
                    kargs[i] = v
                else:
                    raise TypeError("%s got multiple values for argument '%s'"
                                    % (self, n))
        return self._call(*(kargs or ['']))

    __call__ = K_call_proxy()

    def __getitem__(self, x):
        """
        >>> k("10 20 30 40 50")[k("1 3")]
        k('20 40')
        >>> k("`a`b`c!1 2 3")['b']
        k('2')
        """
        try:
            return _k.K.__getitem__(self, x)
        except TypeError:
            pass
        try:
            start, stop, step = x.indices(len(self))
        except AttributeError:
            i = K(x)
        else:
            if step != 0:
                i = start + step * q.til((stop - start) // step)
            else:
                raise ValueError('slice step cannot be zero')

        return self._k(0, "@", self, i)

    def __getattr__(self, a):
        """table columns can be accessed via dot notation

        >>> q("([]a:1 2 3; b:10 20 30)").a
        k('1 2 3')
        """
        t = self.inspect(b't')
        if t == 98:
            return self._k(0, '{x`%s}' % a, self)

        if t == 99:
            if self._k(0, "{11h~type key x}", self):
                return self._k(0, '{x`%s}' % a, self)

            return self._k(0, '{(0!x)`%s}' % a, self)

        if 12 <= abs(t) < 20:
            try:
                return self._k(0, "`%s$" % a, self)
            except _k.error:
                pass

        raise AttributeError(a)

    def __int__(self):
        """converts K scalars to python int

        >>> [int(q(x)) for x in '1b 2h 3 4e `5 6.0 2000.01.08'.split()]
        [1, 2, 3, 4, 5, 6, 7]
        """
        t = self.inspect(b't')
        if t >= 0:
            raise TypeError("cannot convert non-scalar to int")
        return int(self.inspect(fields[-t]))

    __long__ = __int__

    def __float__(self):
        """converts K scalars to python float

        >>> [float(q(x)) for x in '1b 2h 3 4e `5 6.0 2000.01.08'.split()]
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        """
        t = self.inspect(b't')
        if t >= 0:
            raise TypeError("cannot convert non-scalar to float")
        return float(self.inspect(fields[-t]))

    def __nonzero__(self):
        t = self.inspect(b't')
        if t < 0:
            if t == -11:
                return bool(str(self))
            else:
                return self.inspect(fields[-t]) != 0

        return len(self) > 0

    __bool__ = __nonzero__

    def __index__(self):
        t = self.inspect(b't')
        if -5 >= t >= -7:
            return int(self)
        raise TypeError("Only scalar short/int/long K objects can be converted to an index")

    def __eq__(self, other):
        """
        >>> K(1) == K(1)
        True
        >>> K(1) == None
        False
        """
        try:
            other = K(other)
        except KeyError:
            return False
        return bool(k('~')(self, other))

    def __ne__(self, other):
        """
        >>> K(1) != K(2)
        True
        """
        return bool(k('~~')(self, other))

    def __contains__(self, item):
        """membership test

        >>> 1 in q('1 2 3')
        True

        >>> 'abc' not in q('(1;2.0;`abc)')
        False
        """
        if self.inspect(b't'):
            x = q('in', item, self)
        else:
            x = q('{sum x~/:y}', item, self)
        return bool(x)

    def __get__(self, client, cls):
        """allow K objects use as descriptors"""
        if client is None or not isinstance(client, _k.K):
            return self
        return self._a1(client)

    def keys(self):
        """returns q('key', self)

        Among other uses, enables interoperability between q and
        python dicts.
        >>> dict(q('`a`b!1 2'))
        {'a': k('1'), 'b': k('2')}
        >>> d = {}; d.update(q('`a`b!1 2'))
        >>> list(sorted(d.items()))
        [('a', k('1')), ('b', k('2'))]

        An elegant idiom to unpack q tables:
        >>> u = locals().update
        >>> for r in q('([]a:`x`y`z;b:1 2 3;c:"XYZ")'):
        ...     u(r); a, b, c
        (k('`x'), k('1'), k('"X"'))
        (k('`y'), k('2'), k('"Y"'))
        (k('`z'), k('3'), k('"Z"'))
        """
        return self._k(0, 'key', self)

    def show(self, start=0, geometry=None, output=None):
        """pretty-print data to the console

        (similar to q.show, but uses python stdout by default)

        >>> x = q('([k:`x`y`z]a:1 2 3;b:10 20 30)')
        >>> x.show()  # doctest: +NORMALIZE_WHITESPACE
        k| a b
        -| ----
        x| 1 10
        y| 2 20
        z| 3 30

        the first optional argument, 'start' specifies the first row to be
        printed (negative means from the end):
        >>> x.show(2)  # doctest: +NORMALIZE_WHITESPACE
        k| a b
        -| ----
        z| 3 30

        >>> x.show(-2)  # doctest: +NORMALIZE_WHITESPACE
        k| a b
        -| ----
        y| 2 20
        z| 3 30

        the geometry is the height and width of the console
        >>> x.show(geometry=[4,6])
        k| a..
        -| -..
        x| 1..
        ..

        """
        if output is None:
            import sys

            output = sys.stdout

        if geometry is None:
            geometry = q.value(kp("\\c"))
        else:
            geometry = self._I(geometry)

        if start < 0:
            start += q.count(self)

        r = self._show(geometry, start)

        if isinstance(output, type):
            return output(r)
        try:
            output.write(r)
        except TypeError:
            output.write(str(r))

    # See issue #665
    def decode(self, encoding='utf-8', errors='strict'):
        return bytes(self).decode(encoding, errors)

    def _seu(self, what, columns, by, where, kwds):
        args = [self]
        anames = ['self']
        if kwds:
            extra = sorted(kwds.keys())
            args.extend(kwds[name] for name in extra)
            anames.extend(extra)

        if not isinstance(columns, str):
            columns = ','.join(str(x) for x in columns)
        query = "{[%s]%s %s " % (';'.join(anames), what, columns)
        if by:
            if not isinstance(by, str):
                by = ','.join(str(x) for x in by)
            query += " by " + by
        query += " from self"
        if where:
            if not isinstance(where, str):
                where = ','.join(str(x) for x in where)
            query += " where " + where
        query += '}'

        return q(query, *args)

    def select(self, columns=(), by=(), where=(), **kwds):
        """select from self

        >>> t = q('([]a:1 2 3; b:10 20 30)')
        >>> t.select('a', where='b > 20').show()
        a
        -
        3
        """
        return self._seu('select', columns, by, where, kwds)

    def exec_(self, columns=(), by=(), where=(), **kwds):
        """exec from self

        >>> t = q('([]a:1 2 3; b:10 20 30)')
        >>> t.exec_('a', where='b > 10').show()
        2 3
        """
        return self._seu('exec', columns, by, where, kwds)

    def update(self, columns=(), by=(), where=(), **kwds):
        """update from self

        >>> t = q('([]a:1 2 3; b:10 20 30)')
        >>> t.update('a*2', where='b > 20').show()  # doctest: +NORMALIZE_WHITESPACE
        a b
        ----
        1 10
        2 20
        6 30
        """
        return self._seu('update', columns, by, where, kwds)

    @property
    def ss(self):
        if self.inspect(b't') == 10:
            return q.ss(self)
        return q('`ss$', self)

    if _np is not None:
        @property
        def _mask(self):
            return _np.asarray(self.null)

    __doc__ += """
    Q objects can be used in Python arithmetic expressions

    >>> x,y,z = map(K._ki, (1,2,3))
    >>> {_}print(x + y, x * y, z/y, x|y, x&y, abs(-z))  #doctest: +NORMALIZE_WHITESPACE
    3{i} 2{i} 1.5 2{i} 1{i} 3{i}

    Mixing Q objects with python numbers is allowed
    >>> 1/q('1 2 4')
    k('1 0.5 0.25')
    >>> q.til(5)**2
    k('0 1 4 9 16f')
    """.format(**_ij)

    def __format__(self, fmt):
        if fmt:
            return format(self._pys(), fmt)
        return str(self)


def _genmethods(cls):
    from keyword import iskeyword

    K._show = q('{` sv .Q.S[y;z;x]}')

    for spec, verb in [('add', '+'), ('sub', '-'), ('rsub', '{y-x}'), ('mul', '*'),
                       ('pow', 'xexp'), ('rpow', '{y xexp x}'),
                       ('xor', '^'), ('rxor', '{y^x}'),
                       ('truediv', '%'), ('rtruediv', '{y%x}'),
                       ('floordiv', 'div'), ('rfloordiv', '{y div x}'),
                       ('and', '&'), ('or', '|'),
                       ('mod', 'mod'), ('rmod', '{y mod x}'), ('invert', 'not'),
                       ('pos', '{@[flip;x;x]}'), ('neg', '-:'), ('abs', 'abs')]:
        setattr(cls, '__%s__' % spec, K._k(0, verb))

    for spec in 'add mul and or'.split():
        setattr(cls, '__r%s__' % spec, getattr(cls, '__%s__' % spec))

    q_builtins = ['avg', 'last', 'sum', 'prd', 'min', 'max', 'exit', 'getenv', 'abs', 'sqrt',
                  'log', 'exp', 'sin', 'asin', 'cos', 'acos', 'tan', 'atan', 'enlist',
                  'within', 'like', 'bin', 'ss', 'insert', 'wsum', 'wavg', 'div', 'xexp', 'setenv', 'binr']
    q_builtins.extend(f for f in K._k(0, '.q') if not hasattr(cls, f))
    for x in q_builtins:
        if not hasattr(cls, x):
            setattr(cls, (x + '_' if iskeyword(x) else x), K._k(0, x))

    def cmp_op(op):
        def dunder(self, other):
            other = K(other)
            if self.inspect(b't') < 0 and other.inspect(b't') < 0:
                return bool(q(op, self, other))
            else:
                raise NotImplementedError

        return dunder

    for spec, verb in [('gt', '>'), ('lt', '<'), ('ge', '>='), ('le', '<=')]:
        setattr(cls, '__%s__' % spec, cmp_op(verb))


def d9(x):
    """like K._d9, but takes python bytes"""
    return K._d9(K._kp(x))

#          01234567890123456789
fields = b" g@ ghijefgsjiifjiii"
if PY3K:
    fields = [bytes([_x]) for _x in fields]


def k(m, *args):
    return K._k(0, 'k)' + m, *map(K, args))


class _Q(object):
    def __init__(self):
        object.__setattr__(self, '_cmd', None)

    def __call__(self, m=None, *args):
        try:
            return K._k(0, m, *map(K, args))
        except TypeError:
            if m is not None:
                raise
            if self._cmd is None:
                from .cmd import Cmd
                object.__setattr__(self, '_cmd', Cmd())
            self._cmd.cmdloop()

    def __getattr__(self, attr):
        k = K._k
        try:
            return k(0, attr.rstrip('_'))
        except kerr:
            pass
        raise AttributeError(attr)

    def __setattr__(self, attr, value):
        self("@[`.;;:;]", attr, value)

    def __delattr__(self, attr):
        k = K._k
        k(0, "delete %s from `." % attr)


__doc__ += """
Q variables can be accessed as attributes of the 'q' object:
>>> q.test = q('([]a:1 2i;b:`x`y)')
>>> sum(q.test.a)
3
>>> del q.test
"""
q = _Q()
nil = q('(value +[;0])1')

show = K.show

datetimetok = K._kzz
__doc__ += """
datetimetok converts python datetime to k (DEPRECATED)

>>> datetimetok(datetime(2006,5,3,2,43,25,999000))
k('2006.05.03T02:43:25.999')
"""

datetok = K._kdd
__doc__ += """
datetok converts python date to k (DEPRECATED)

>>> datetok(date(2006,5,3))
k('2006.05.03')

"""

timetok = K._ktt
__doc__ += """
timetok converts python time to k (DEPRECATED)

>>> timetok(time(12,30,0,999000))
k('12:30:00.999')

"""


def _ni(x):
    r = q('()')
    append = q(',')
    for i in x:
        r = append(r, K(i))
    return r


_X = {K: K._K, str: K._S, int: (K._I if QVER[0] < '3' else K._J),
      float: K._F, date: K._D, time: _ni, datetime: _ni, bool: K._B}


def listtok(x):
    if x:
        return _X[type(x[0])](x)
    return K._ktn(0, 0)

_X[list] = lambda x: K([K(i) for i in x])

__doc__ += """
listtok converts python list to k

>>> listtok([])
k('()')

Type is determined by the type of the first element of the list
>>> listtok(list("abc"))
k('`a`b`c')
>>> listtok([1,2,3])
k('1 2 3')
>>> listtok([0.5,1.0,1.5])
k('0.5 1 1.5')

All elements must have the same type for conversion
>>> listtok([0.5,'a',5])
Traceback (most recent call last):
  ...
TypeError: K._F: 2-nd item is not an int

"""

tupletok = lambda x: K._K(K(i) for i in x)

__doc__ += """
tupletok converts python tuple to k

Tuples are converted to general lists, strings in tuples are
converted to char lists.

>>> tupletok((kp("insert"), 't', (1, "abc")))
k('("insert";`t;(1;`abc))')
"""

kp = K._kp

converters = {
    list: listtok,
    tuple: tupletok,
    type(lambda: 0): K._func,
    dict: lambda x: K._xD(K(x.keys()), K(x.values()))
}

if PY3K:
    converters[bytes] = K._kp
    converters[dict] = lambda x: K._xD(K(list(x.keys())), K(list(x.values())))

try:
    converters[buffer] = K._kp
except NameError:
    buffer = str
    pass

###############################################################################
# Lazy addition of converters
###############################################################################
lazy_converters = {'uuid': [('UUID', lambda u: K._kguid(u.int))],
                   'collections': [('OrderedDict', lambda x:
                   q("{![;].(flip x)}",
                     K._K(K(i) for i in x.items())))],
                   'py._path.local': [('LocalPath', lambda p: q.hsym(p.strpath))]
}

try:
    import __builtin__
except ImportError:
    import builtins as __builtin__
import sys

# If module is already loaded, register converters for its classes
# right away.
for name, pairs in lazy_converters.items():
    mod = sys.modules.get(name)
    if mod is not None:
        for cname, conv in pairs:
            converters[getattr(mod, cname)] = conv
# Replace builtin import to add lazy registration logic
_imp = __builtin__.__import__


def __import__(name, globals={}, locals={}, fromlist=[], level=[-1, 0][PY3K],
               _imp=_imp, _lc=lazy_converters):
    m = _imp(name, globals, locals, fromlist, level)
    pairs = _lc.get(name)
    if pairs is not None:
        converters.update((getattr(m, cname), conv)
                          for cname, conv in pairs)
    return m


__builtin__.__import__ = __import__
###############################################################################

__test__ = {}
try:
    from numpy import array
except ImportError:
    pass
else:
    __test__["array interface (vector)"] = """
    >>> K._from_array_interface(array([1, 0, 1], bool).__array_struct__)
    k('101b')
    >>> K._from_array_interface(array([1, 2, 3], 'h').__array_struct__)
    k('1 2 3h')
    >>> K._from_array_interface(array([1, 2, 3], 'i').__array_struct__)
    k('1 2 3{i}')
    >>> K._from_array_interface(array([1, 2, 3], 'q').__array_struct__)
    k('1 2 3{j}')
    >>> K._from_array_interface(array([1, 2, 3], 'f').__array_struct__)
    k('1 2 3e')
    >>> K._from_array_interface(array([1, 2, 3], 'd').__array_struct__)
    k('1 2 3f')
    """.format(**_ij)
    __test__["array interface (scalar)"] = """
    >>> K._from_array_interface(array(1, bool).__array_struct__)
    k('1b')
    >>> K._from_array_interface(array(1, 'h').__array_struct__)
    k('1h')
    >>> K._from_array_interface(array(1, 'i').__array_struct__)
    k('1{i}')
    >>> K._from_array_interface(array(1, 'q').__array_struct__)
    k('1{j}')
    >>> K._from_array_interface(array(1, 'f').__array_struct__)
    k('1e')
    >>> K._from_array_interface(array(1, 'd').__array_struct__)
    k('1f')
    """.format(**_ij)

_genmethods(K)
del _genmethods, _ij
