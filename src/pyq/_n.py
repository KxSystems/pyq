"""A helper module for interfacing with numpy

Numpy has four date units

Code	Meaning	Time span (relative)	Time span (absolute)
Y	year	+/- 9.2e18 years	[9.2e18 BC, 9.2e18 AD]
M	month	+/- 7.6e17 years	[7.6e17 BC, 7.6e17 AD]
W	week	+/- 1.7e17 years	[1.7e17 BC, 1.7e17 AD]
D	day	+/- 2.5e16 years	[2.5e16 BC, 2.5e16 AD]

And nine time units:

Code	Meaning	Time span (relative)	Time span (absolute)
h	hour	+/- 1.0e15 years	[1.0e15 BC, 1.0e15 AD]
m	minute	+/- 1.7e13 years	[1.7e13 BC, 1.7e13 AD]
s	second	+/- 2.9e12 years	[ 2.9e9 BC, 2.9e9 AD]
ms	millisecond	+/- 2.9e9 years	[ 2.9e6 BC, 2.9e6 AD]
us	microsecond	+/- 2.9e6 years	[290301 BC, 294241 AD]
ns	nanosecond	+/- 292 years	[ 1678 AD, 2262 AD]
ps	picosecond	+/- 106 days	[ 1969 AD, 1970 AD]
fs	femtosecond	+/- 2.6 hours	[ 1969 AD, 1970 AD]
as	attosecond	+/- 9.2 seconds	[ 1969 AD, 1970 AD]


kdb+ has four datetime-like types

num char q-type     c-type
12  "p"  timestamp  int64_t
13  "m"  month      int32_t
14  "d"  date       int32_t
15  "z"  datetime   double

And four timedelta-like types

16  "n"  timespan   int64_t
17  "u"  minute     int32_t
18  "v"  second     int32_t
19  "t"  time       int32_t
"""
from __future__ import absolute_import

from datetime import date

import numpy

K_DATE_SHIFT = date(2000, 1, 1).toordinal() - date(1970, 1, 1).toordinal()
K_STAMP_SHIFT = K_DATE_SHIFT * 24 * 60 * 60 * 10 ** 9


def get_unit(a):
    typestr = a.dtype.str
    i = typestr.find('[')
    if i == -1:
        raise TypeError("Expected a datetime64 array, not %s", a.dtype)
    return typestr[i + 1: -1]


_SCALE = {
    'W': ('floor_divide', 7 * 24 * 60 * 60 * 10 ** 9),
    'D': ('floor_divide', 24 * 60 * 60 * 10 ** 9),
    'h': ('floor_divide', 60 * 60 * 10 ** 9),
    'm': ('floor_divide', 60 * 10 ** 9),
    's': ('floor_divide', 10 ** 9),
    'ms': ('floor_divide', 10 ** 6),
    'us': ('floor_divide', 10 ** 3),
    'ns': (None, None),
    'ps': ('multiply', 10 ** 3),
    'fs': ('multiply', 10 ** 6),
    'as': ('multiply', 10 ** 9),
}

_UNIT = {
    'D': ('date', K_DATE_SHIFT, None, None),
    'Y': ('year', -1970, None, None),
    'W': ('date', K_DATE_SHIFT, 'floor_divide', 7),
    'M': ('month', 30 * 12, None, None),
    'h': ('timestamp', K_STAMP_SHIFT, 'floor_divide', 60 * 60 * 10 ** 9),
    'm': ('timestamp', K_STAMP_SHIFT, 'floor_divide', 60 * 10 ** 9),
    's': ('timestamp', K_STAMP_SHIFT, 'floor_divide', 10 ** 9),
    'ns': ('timestamp', K_STAMP_SHIFT, None, None),
    'ps': ('timestamp', K_STAMP_SHIFT, 'multiply', 1000),
}

_DTYPES = [
    "O",        # 0
    "?",        # 1 - boolean
    "16B",      # 2 - guid
    None,       # 3 - unused
    "B",        # 4 - byte
    "h",        # 5 - short
    "i",        # 6 - int
    "q",        # 7 - long
    "f",        # 8 - real
    "d",        # 9 - float
    "S1",      # 10 - char
    "O",       # 11 - symbol
    "M8[ns]",  # 12 - timestamp
    "M8[M]",   # 13 - month
    "M8[D]",   # 14 - date
    None,      # 15 - datetime (unsupported)
    "m8[ns]",  # 16 - timespan
    "m8[m]",   # 17 - minute
    "m8[s]",   # 18 - second
    "m8[ms]",  # 19 - time
    "O",       # 20 - `sym$
]


def dtypeof(x):
    t = abs(x._t)
    if t < 20:
        return _DTYPES[t]
    return 'O'


def k2a(a, x):
    """Rescale data from a K object x to array a.

    """
    func, scale = None, 1
    t = abs(x._t)
    # timestamp (12), month (13), date (14) or datetime (15)
    if 12 <= t <= 15:
        unit = get_unit(a)
        attr, shift, func, scale = _UNIT[unit]
        a[:] = getattr(x, attr).data
        a += shift
    # timespan (16), minute (17), second (18) or time (19)
    elif 16 <= t <= 19:
        unit = get_unit(a)
        func, scale = _SCALE[unit]
        a[:] = x.timespan.data
    else:
        a[:] = list(x)

    if func is not None:
        func = getattr(numpy, func)
        a[:] = func(a.view(dtype='i8'), scale)


def array(self, dtype=None):
    t = self._t
    # timestamp (12) through last enum (76)
    if 11 <= t < 77:
        dtype = dtypeof(self)
        a = numpy.empty(len(self), dtype)
        k2a(a, self)
        return a
    # table (98)
    if t == 98:
        if dtype is None:
            dtype = list(zip(self.cols, (dtypeof(c) for c in self.flip.value)))
        dtype = numpy.dtype(dtype)
        a = numpy.empty(int(self.count), dtype)
        for c in dtype.fields:
            k2a(a[c], self[c])
        return a
    return numpy.array(list(self), dtype)
