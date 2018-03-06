from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import itertools
from datetime import datetime, date, time
from collections import Mapping as _Mapping

try:
    import __builtin__
except ImportError:
    import builtins as __builtin__
import sys
import os

try:
    import numpy as _np
except ImportError:
    _np = None

try:
    from ._k import K as _K, error as kerr, Q_VERSION, Q_DATE, Q_OS
except ImportError:
    if 'python' in os.path.basename(sys.executable).lower():
        import platform
        message = "Importing pyq from stock python is not supported. "
        if platform.system() == 'Windows':
            message += "Run path\\to\\q.exe python.q."
        else:
            message += "Use pyq executable."
        raise ImportError(message)
    raise

try:
    from .version import version as __version__
except ImportError:
    __version__ = 'unknown'

__metaclass__ = type

# Convenience constant to select code branches according to Q_VERSION
_KX3 = Q_VERSION >= 3

_PY3K = sys.hexversion >= 0x3000000

# List of q builtin functions that are not defined in .q.
# NB: This is similar to .Q.res, but excludes non-function constructs
# such as "do", "if", "select" etc. We also exclude the "exit" function
# because it is rarely safe to use it to exit from pyq.
_Q_RES = ['abs', 'acos', 'asin', 'atan', 'avg', 'bin',  'cor', 'cos',
          'cov', 'dev', 'div', 'ema', 'enlist', 'exp', 'getenv', 'in',
          'insert', 'last', 'like', 'log', 'max', 'min', 'prd', 'reval',
          'scov', 'sdev', 'setenv', 'sin', 'sqrt', 'ss', 'sum', 'svar',
          'tan', 'var', 'wavg', 'within', 'wsum', 'xexp']

if _KX3 and Q_DATE >= date(2012, 7, 26):
    # binr was introduced in kdb+3.0 2012.07.26
    _Q_RES.append('binr')

if Q_VERSION >= 3.6:
    _Q_RES.append('hopen')


class K(_K):
    """proxies for kdb+ objects

    >>> q('2005.01.01 2005.12.04')
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
    k('3')

    Buffer protocol

    The following session illustrates how buffer protocol implemented by
    K objects can be used to write data from Python streams directly yo kdb+.

    Create a list of chars in kdb+

    >>> x = kp('xxxxxx')

    Open a pair of file descriptors

    >>> r, w = os.pipe()

    Write 6 bytes to the write end

    >>> os.write(w, b'abcdef')
    6

    Read from the read-end into x

    >>> f = os.fdopen(r, mode='rb')
    >>> f.readinto(x)
    6

    Now x contains the bytes that were sent through the pipe

    >>> x
    k('"abcdef"')

    Close the descriptors and the stream

    >>> os.close(w); f.close()

    Low level interface

    The K type provides a set of low level functions that are similar
    to the C API provided by the `k.h header <http://kx.com/q/c/c/k.h>`_.
    The C API functions that return K objects in C are implemented as
    class methods that return instances of K type.

    Atoms

    >>> K._kb(True), K._kg(5), K._kh(42), K._ki(-3), K._kj(2**40)
    (k('1b'), k('0x05'), k('42h'), k('-3i'), k('1099511627776'))

    >>> K._ke(3.5), K._kf(1.0), K._kc(b'x'), K._ks('xyz')
    (k('3.5e'), k('1f'), k('"x"'), k('`xyz'))

    >>> K._kd(0), K._kz(0.0), K._kt(0)
    (k('2000.01.01'), k('2000.01.01T00:00:00.000'), k('00:00:00.000'))


    Tables and dictionaries

    >>> x = K._xD(k('`a`b`c'), k('1 2 3')); x, K._xT(x)
    (k('`a`b`c!1 2 3'), k('+`a`b`c!1 2 3'))

    Keyed table

    >>> t = K._xD(K._xT(K._xD(k(",`a"), k(",1 2 3"))),
    ...           K._xT(K._xD(k(",`b"), k(",10 20 30"))))
    >>> K._ktd(t)
    k('+`a`b!(1 2 3;10 20 30)')

    """
    # Lighten the K objects by preventing the automatic creation of
    # __dict__ and __weakref__ for each instance.
    __slots__ = ()

    # Helper methods for use in C implementation of __new__

    def _set_mask(self, mask):
        return q("{?[y;((),x)0N;x]}", self, mask)

    @classmethod
    def _from_record_array(cls, x):
        fields = [f for f, t in x.dtype.descr]
        k = q('!', list(fields), [K(x[f]) for f in fields])
        if x.ndim:
            k = k.flip
        return k

    @classmethod
    def _from_sequence(cls, x, elm=None):
        r = cls._ktn(0, 0)
        g = iter(x)
        try:
            i = next(g)
        except StopIteration:
            return r
        en = _K_k(0, 'enlist')
        r._ja(en)
        if elm is None:
            elm = cls
        for i in itertools.chain([i], g):
            i = elm(i)
            # Symbols and lists require special treatment
            if i._t in (-11, 11, 0):
                i = i.enlist
            r._ja(i)
        return r.eval

    @classmethod
    def _convert(cls, x):
        for t in type(x).mro():
            c = converters.get(t)
            if c is not None:
                return c(x)
        return cls._from_sequence(x)

    def __reduce_ex__(self, proto):
        x = self._b9(1, self)
        b = memoryview(x).tobytes()
        return (d9, (b,))

    def __getitem__(self, x):
        """
        >>> k("10 20 30 40 50")[k("1 3")]
        k('20 40')
        >>> k("`a`b`c!1 2 3")['b']
        2
        """
        try:
            return _K.__getitem__(self, x)
        except (TypeError, NotImplementedError):
            pass
        try:
            start, stop, step = x.indices(len(self))
        except AttributeError:
            i = K(x)
            if self._t == 99 and i._t < 0:
                return self.value[self._k(0, "?", self.key, i)]
            else:
                return self._k(0, "@", self, i)

        if step == 1:
            return self._k(0, "sublist", self._J([start, stop - start]), self)
        # NB: .indices() cannot return step=0.
        i = start + step * q.til(max(0, (stop - start) // step))

        return self._k(0, "{$[99=type x;(key[x]y)!value[x]y;x y]}", self, i)

    def __getattr__(self, a):
        """table columns can be accessed via dot notation

        >>> q("([]a:1 2 3; b:10 20 30)").a
        k('1 2 3')
        """
        t = self._t
        if t == 98:
            return self._k(0, '{x`%s}' % a, self)

        if t == 99:
            if self._k(0, "{11h~type key x}", self):
                if a == 'items':
                    # NB: Workaround for a bug in OrderedDict in Python 3.5.
                    # See http://bugs.python.org/issue27576 for details.
                    raise AttributeError
                return self._k(0, '{x`%s}' % a, self)

            return self._k(0, '{(0!x)`%s}' % a, self)

        if 12 <= abs(t) < 20:
            try:
                return self._k(0, "`%s$" % a, self)
            except kerr:
                pass

        raise AttributeError(a)

    _fields = b" g@ ghijefgsjiifjiii"
    if _PY3K:
        _fields = [bytes([_x]) for _x in _fields]

    def __int__(self):
        """converts K scalars to python int

        >>> [int(q(x)) for x in '1b 2h 3 4e `5 6.0 2000.01.08'.split()]
        [1, 2, 3, 4, 5, 6, 7]
        """
        t = self._t
        if t >= 0:
            raise TypeError("cannot convert non-scalar to int")
        return int(self.inspect(self._fields[-t]))

    __long__ = __int__

    def __float__(self):
        """converts K scalars to python float

        >>> [float(q(x)) for x in '1b 2h 3 4e `5 6.0 2000.01.08'.split()]
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        """
        t = self._t
        if t >= 0:
            raise TypeError("cannot convert non-scalar to float")
        return float(self.inspect(self._fields[-t]))

    def __index__(self):
        t = self._t
        if -5 >= t >= -7:
            return int(self)
        raise TypeError("Only scalar short/int/long K objects "
                        "can be converted to an index")

    # Strictly speaking, this is only needed for Python 3.x, but
    # there is no harm if this is defined and not used in Python 2.x.
    def __bytes__(self):
        t = self._t
        if -5 >= t >= -7:
            return bytes(int(self))
        if 0 < abs(t) < 11:
            if abs(t) == 2:
                # A work-around while .data is not implemented for guid type
                from uuid import UUID
                x = q('(),', self)  # ensure that x is a list
                return b''.join(UUID(int=i).bytes for i in x)
            return bytes(self.data)
        raise BufferError("k object of type %d" % t)

    def __eq__(self, other):
        """
        >>> K(1) == K(1)
        True
        >>> K(1) == None
        False
        """
        try:
            other = K(other)
        except TypeError:
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
        if self._t:
            x = q('in', item, self)
        else:
            x = q('{sum x~/:y}', item, self)
        return bool(x)

    def keys(self):
        """returns q('key', self)

        Among other uses, enables interoperability between q and
        python dicts.

        >>> from collections import OrderedDict
        >>> OrderedDict(q('`a`b!1 2'))
        OrderedDict([('a', 1), ('b', 2)])
        >>> d = {}; d.update(q('`a`b!1 2'))
        >>> list(sorted(d.items()))
        [('a', 1), ('b', 2)]
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
        printed (negative means from the end)

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

        >>> x.show(geometry=[4, 6])
        k| a..
        -| -..
        x| 1..
        ..

        """
        if output is None:
            output = sys.stdout

        if geometry is None:
            geometry = q.value(kp("\\c"))
        else:
            geometry = self._I(geometry)

        if start < 0:
            start += q.count(self)

        # Make sure nil is not passed to a q function
        if self._id() != nil._id():
            r = self._show(geometry, start)
        else:
            r = '::\n'

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
        >>> t.update('a*2',
        ...          where='b > 20').show()  # doctest: +NORMALIZE_WHITESPACE
        a b
        ----
        1 10
        2 20
        6 30
        """
        return self._seu('update', columns, by, where, kwds)

    @property
    def ss(self):
        if self._t == 10:
            return q.ss(self)
        return q('`ss$', self)

    if _np is not None:
        @property
        def _mask(self):
            return _np.asarray(self.null)

        from ._n import array as __array__

        __array_priority__ = 20

    __doc__ += """
    K objects can be used in Python arithmetic expressions

    >>> x, y, z = map(K, (1, 2, 3))
    >>> print(x + y, x * y,
    ...       z/y, x|y, x&y, abs(-z))  #doctest: +NORMALIZE_WHITESPACE
    3 2 1.5 2 1 3

    Mixing K objects with python numbers is allowed

    >>> 1/q('1 2 4')
    k('1 0.5 0.25')
    >>> q.til(5)**2
    k('0 1 4 9 16f')
    """

    def __format__(self, fmt):
        if fmt:
            return format(self._pys(), fmt)
        return str(self)

    def __sizeof__(self):
        return object.__sizeof__(self) + int(self._sizeof())

    def __fspath__(self):
        """Return the file system path representation of the object."""
        if self._t != -11:  # symbol
            raise TypeError
        sym = str(self)
        if not sym.startswith(':'):
            raise TypeError
        return sym[1:]

    def __complex__(self):
        """Called to implement the built-in function complex()."""
        if self._t != 99 or self.key != ['re', 'im']:
            return complex(float(self))
        return complex(float(self.re), float(self.im))


if _PY3K:
    setattr(K, 'exec', K.exec_)


def _q_builtins():
    from keyword import iskeyword

    # Allow _q_builtins() to be called before q is defined
    def q(x):
        return K._k(0, x)

    kver = q('.z.K').inspect(b'f')
    names = _Q_RES + list(q("1_key[.q]except`each`over`scan"))
    if kver < 3.4:
        # ema is present since kdb+3.4
        q(r'.q.ema:{first[y]("f"$1-x)\x*y}')
    if kver < 3.3:
        # restricted eval was added in 3.3
        q(r'.q.reval:eval')

    if kver < 3.0:
        for new in ['scov', 'svar', 'sdev']:
            names.remove(new)

    pairs = []
    for x in names:
        attr = x
        if iskeyword(x):
            attr += '_'
        pairs.append((attr, q(x)))

    return pairs


def _genmethods(cls, obj):
    q('\l pyq-operators.q')
    cls._show = q('{` sv .Q.S[y;z;x]}')
    cls._sizeof = q('.p.sizeof')
    for spec, verb in [
        ('add', '+'), ('sub', '-'), ('rsub', '{y-x}'),
        ('mul', '*'), ('pow', 'xexp'), ('rpow', '{y xexp x}'),
        ('xor', '^'), ('rxor', '{y^x}'),
        ('truediv', '%'), ('rtruediv', '{y%x}'),
        ('floordiv', 'div'), ('rfloordiv', '{y div x}'),
        ('and', '&'), ('or', '|'),
        ('mod', 'mod'), ('rmod', '{y mod x}'), ('invert', 'not'),
        ('pos', '{@[flip;x;x]}'), ('neg', '-:'), ('abs', 'abs'),
        # x @ y - composition if y is a function, x[y] otherwise.
        ('matmul', "{$[100>type y;x y;'[x;y]]}"),
        ('rmatmul', "{$[100>type x;y x;'[y;x]]}"),
    ]:
        setattr(cls, '__%s__' % spec, q(verb))

    for spec in 'add mul and or'.split():
        setattr(cls, '__r%s__' % spec, getattr(cls, '__%s__' % spec))

    for x, f in _q_builtins():
        if not hasattr(cls, x):
            setattr(cls, x, f)
            obj.__dict__[x] = f

    def cmp_op(op):
        def dunder(self, other):
            other = K(other)
            if self._t < 0 and other._t < 0:
                return bool(q(op, self, other))
            else:
                raise NotImplementedError

        return dunder

    for spec, verb in [('gt', '>'), ('lt', '<'), ('ge', '>='), ('le', '<=')]:
        setattr(cls, '__%s__' % spec, cmp_op(verb))

    # Shift operators
    for x in ['', 'r']:
        for y in 'lr':
            op = x + y + 'shift'
            setattr(cls, '__%s__' % op, q('.p.' + op))


def d9(x):
    """like K._d9, but takes python bytes"""
    return K._d9(K._kp(x))


def k(m, *args):
    return K._k(0, 'k)' + m, *map(K, args))


class _Q(object):
    """a portal to kdb+"""

    def __init__(self):
        object.__setattr__(self, '_cmd', None)
        object.__setattr__(self, '_q_names',
                           [name for name, _ in _q_builtins()])

    def __call__(self, m=None, *args):
        """Execute q code."""
        try:
            return K._k(0, m, *map(K, args))
        except TypeError:
            if m is not None:
                raise
            if self._cmd is None:
                from .cmd import Cmd
                object.__setattr__(self, '_cmd', Cmd())
            self._cmd.cmdloop()

    def __getattr__(self, attr, _k=K._k):
        try:
            return _k(0, attr.rstrip('_'))
        except kerr:
            pass
        raise AttributeError(attr)

    def __setattr__(self, attr, value):
        self("@[`.;;:;]", attr, value)

    def __delattr__(self, attr):
        k = K._k
        k(0, "delete %s from `." % attr)

    def __dir__(self):
        return self._q_names + list(self.key('.'))


q = _Q()
nil = q('(value +[;0])1')

show = K.show


def _ni(x):
    r = q('()')
    append = q(',')
    for i in x:
        r = append(r, K(i))
    return r


_X = {K: K._K, str: K._S, int: (K._J if _KX3 else K._I),
      float: K._F, date: K._D, time: _ni, datetime: _ni, bool: K._B}


def _listtok(x):
    if x:
        for i in x:
            if i is not None:
                break
        c = _X.get(type(i))
        if c is not None:
            try:
                return c(x)
            except (TypeError, ValueError):
                pass
        return K._from_sequence(x)
    return K._ktn(0, 0)


_X[list] = lambda x: K([K(i) for i in x])


def _tupletok(x):
    try:
        fields = x._fields
    except AttributeError:
        return K._from_sequence(x)
    else:
        return K._xD(K(fields), K._from_sequence(x))


kp = K._kp

converters = {
    list: _listtok,
    tuple: _tupletok,
    type(lambda: 0): K._func,
    type(sum): K._func,
    dict: lambda x: K._xD(K(x.keys()), K(x.values())),
    complex: lambda z: K._xD(K._S(['re', 'im']), K._F([z.real, z.imag])),
}

if _PY3K:
    converters[bytes] = K._kp
else:
    converters[unicode] = K._ks
    _X[unicode] = lambda x: K([i.encode() for i in x])
    _X[long] = (K._J if _KX3 else K._I)
try:
    converters[buffer] = K._kp
except NameError:
    buffer = str


###############################################################################
# Lazy addition of converters
###############################################################################
lazy_converters = {'uuid': [('UUID', lambda u: K._kguid(u.int))],
                   'py._path.local': [('LocalPath',
                                       lambda p: q.hsym(p.strpath))],
                   'pathlib': [('PurePath', lambda p: K(':' + str(p)))],
                   }

lazy_converters['pathlib2'] = lazy_converters['pathlib']


# If module is already loaded, register converters for its classes
# right away.
def _pre_register_converters():
    for name, pairs in lazy_converters.items():
        mod = sys.modules.get(name)
        if mod is not None:
            for cname, conv in pairs:
                converters[getattr(mod, cname)] = conv


_pre_register_converters()
del _pre_register_converters

# Replace builtin import to add lazy registration logic
_imp = __builtin__.__import__


def __import__(name, globals={}, locals={}, fromlist=[], level=[-1, 0][_PY3K],
               _imp=_imp, _c=converters, _lc=lazy_converters):
    m = _imp(name, globals, locals, fromlist, level)
    pairs = _lc.get(name)
    if pairs is not None:
        _c.update((getattr(m, cname), conv) for cname, conv in pairs)
    return m


__builtin__.__import__ = __import__
###############################################################################

_genmethods(K, q)
del _genmethods, _imp


def versions():
    stream = sys.stdout if _PY3K else sys.stderr
    print('PyQ', __version__, file=stream)
    if _np is not None:
        print('NumPy', _np.__version__, file=stream)
    print('KDB+ %s (%s) %s' % tuple(q('.z.K,.z.k,.z.o')), file=stream)
    print('Python', sys.version, file=stream)


###############################################################################
# Casts and constructors
###############################################################################
def _gendescriptors(cls, string_types=(type(b''), type(u''))):
    cls._Z = NotImplemented
    if Q_VERSION < 3:
        cls._UU = cls._kguid = NotImplemented
    types = [
        # code, char, name, vector, scalar
        (1, 'b', 'boolean', cls._B, cls._kb),
        (2, 'g', 'guid', cls._UU, cls._kguid),
        (4, 'x', 'byte', cls._G, cls._kg),
        (5, 'h', 'short', cls._H, cls._kh),
        (6, 'i', 'int', cls._I, cls._ki),
        (7, 'j', 'long', cls._J, cls._kj),
        (8, 'e', 'real', cls._E, cls._ke),
        (9, 'f', 'float', cls._F, cls._kf),
        (11, 's', 'symbol', cls._S, cls._ks),
        (12, 'p', 'timestamp', cls._P, cls._kpz),
        (13, 'm', 'month', cls._M, cls._km),
        (14, 'd', 'date', cls._D, cls._kd),
        (15, 'z', 'datetime', cls._Z, cls._kz),
        (16, 'n', 'timespan', cls._N, cls._knz),
        (17, 'u', 'minute', cls._U, cls._ku),
        (18, 'v', 'second', cls._V, cls._kv),
        (19, 't', 'time', cls._T, cls._kt),
    ]

    class Desc:
        def __init__(self, code, char, name, vector, scalar):
            self.code = cls._kh(code)
            self.char = char
            self.name = name
            self.vector = vector
            self.scalar = scalar

        def make_constructor(self):
            def constructor(x):
                # If x is already K - check the type and either
                # pass it through or cast to the type needed.
                if isinstance(x, K):
                    if x.type.abs == self.code:
                        return x
                    else:
                        return cls._k(0, '$', self.code, x)
                if isinstance(x, _Mapping):
                    return cls._xD(cls(x.keys()), constructor(x.values()))
                try:
                    return self.vector(x)
                except TypeError:
                    pass
                try:
                    return self.scalar(x)
                except TypeError:
                    return cls._from_sequence(x, constructor)

            constructor.__name__ = 'K.' + self.name
            if self.code > 4 and int(self.code) != 11:
                constructor.inf = q('0W' + self.char)
                constructor.na = q('0N' + self.char)
            elif self.name == 'guid':
                constructor.na = q('0Ng')

            return constructor

        def __get__(self, instance, owner):
            if instance is None:
                return self.make_constructor()
            # Make sure dict keys and table columns have priority over casts
            name = self.name
            if instance._t == 98 and name in instance.cols:
                return instance[name]
            if instance._t == 99:  # keyed table or dict
                key = instance.key
                if key._t == 11 and name in key:
                    return instance[name]
                if key._t == 98 and name in instance.cols:
                    return instance.exec_(name)

            return cls._k(0, '$', self.code, instance)

    for code, char, name, vector, scalar in types:
        setattr(cls, name, Desc(code, char, name, vector, scalar))

    # Special case: string
    def make_strings(x):
        if isinstance(x, string_types):
            return cls._kp(x)
        if isinstance(x, _Mapping):
            return cls._xD(cls(x.keys()), make_strings(x.values()))
        return cls._from_sequence(x, make_strings)

    class StringDesc:
        def __get__(self, instance, owner):
            if instance is None:
                return make_strings
            # NB: As a reserved word, "string" cannot be a column name but
            # can be a key in a dictionary
            if instance._t == 99:
                key = instance.key
                if key._t == 11 and 'string' in key:
                    return instance['string']

            return cls._k(0, 'string', instance)

    cls.string = StringDesc()

    # Special case: char (like string, but may return a scalar char.)
    def make_chars(x):
        if isinstance(x, str):
            x = x.encode('utf8')
        if isinstance(x, bytes):
            if len(x) == 1:
                return cls._kc(x)
            else:
                return cls._kp(x)
        if isinstance(x, _Mapping):
            return cls._xD(cls(x.keys()), make_chars(x.values()))
        if not x:
            return cls._kp('')
        return cls._from_sequence(x, make_chars)

    make_chars.inf = q('0Wc')
    make_chars.na = q('0Nc')

    class CharDesc:
        def __get__(self, instance, owner):
            if instance is None:
                return make_chars
            # Make sure dict keys and table columns have priority over casts
            name = 'char'
            if instance._t == 98 and name in instance.cols:
                return instance[name]
            if instance._t == 99:  # keyed table or dict
                key = instance.key
                if key._t == 11 and name in key:
                    return instance[name]
                if key._t == 98 and name in instance.cols:
                    return instance.exec_(name)

            return cls._k(0, '`char$', instance)

    cls.char = CharDesc()


_gendescriptors(K)
del _gendescriptors


def _genadverbs(cls):
    adverbs = [
        'each',   # '
        'over',   # /
        'scan',   # \
        'prior',  # ':
        'sv',     # /: - each-right
        'vs',     # \: - each-left
     ]
    for i, a in enumerate(adverbs):
        x = cls._ktj(103, i)
        setattr(cls, a, x)


_genadverbs(K)
del _genadverbs


# Traceback support
_K_k = K._k
_K_call = K.__call__


def _set_excepthook(origexcepthook):
    def excepthook(exctype, value, traceback):
        origexcepthook(exctype, value, traceback)
        a = value.args
        if exctype is kerr and len(a) > 1:
            sbt = _K_k(0, '.Q.sbt', a[1])
            print("kdb+ backtrace:\n%s" % sbt,
                  file=sys.stderr, end='')

    sys.excepthook = excepthook


_val = q.value
_enl = q.enlist


def _trp_k(cls_, h, m, *args):
    if h != 0:
        return cls_._k(h, m, args)
    f = cls_._trp(_val, K._knk(1, kp(m)))
    if args:
        return cls_._trp(f, K(args))
    else:
        return f


def _trp_call(*args, **kwds):
    f = args[0]
    args = args[1:]
    if f.type < 100:
        return _K_call(f, *args, **kwds)
    if kwds:
        args = f._callargs(*args, **kwds)
    if not args:
        args = [None]
    args = K._knk(len(args), *map(K, args))
    return f._trp(args)


if 'PYQ_BACKTRACE' in os.environ and q('.z.K >= 3.5'):
    _set_excepthook(sys.excepthook)
    K._k = classmethod(_trp_k)
    K.__call__ = _trp_call
