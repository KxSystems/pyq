-----------------
Numeric Computing
-----------------

.. testsetup:: *

   import numpy
   from datetime import date, time, datetime, timedelta
   trades = q('([]sym:`a`a`b`b;time:09:31 09:33 09:32 09:35;size:100 300 200 100)')

NumPy is the fundamental package for scientific computing in Python.  NumPy shares
common APL ancestry with q and can often operate directly on :class:`~pyq.K` objects.


Primitive data types
--------------------

There are eighteen primitive data types in kdb+, eight of those closely match their
NumPy analogues and will be called "simple types" in this section.  Simple
types consist of booleans, bytes, characters, integers of three different
sizes, and floating point numbers of two sizes.  Seven kdb+ types are dealing with
dates, times and durations.  Similar data types are available in recent versions
of NumPy, but they differ from kdb+ types in many details.  Finally, kdb+ symbol,
enum and guid types have no direct analogue in NumPy.


.. list-table:: Primitive kdb+ data types as NumPy arrays
   :widths: 3 10 10 10 30
   :header-rows: 1

   * - No.
     - kdb+ type
     - array type
     - raw
     - description
   * - 1
     - boolean
     - bool\_
     - bool\_
     - Boolean (True or False) stored as a byte
   * - 2
     - guid
     - uint8 (x16)
     - uint8 (x16)
     - Globally unique 16-byte identifier
   * - 4
     - byte
     - uint8
     - uint8
     - Byte (0 to 255)
   * - 5
     - short
     - int16
     - int16
     - Signed 16-bit integer
   * - 6
     - int
     - int32
     - int32
     - Signed 32-bit integer
   * - 7
     - long
     - int64
     - int64
     - Signed 64-bit integer
   * - 8
     - real
     - float32
     - float32
     - Single precision 32-bit float
   * - 9
     - float
     - float64
     - float64
     - Double precision 64-bit float
   * - 10
     - char
     - S1
     - S1
     - (byte-)string
   * - 11
     - symbol
     - str
     - P
     - Strings from a pool
   * - 12
     - timestamp
     - datetime64[ns]
     - int64
     - Date and time with nanosecond resolution
   * - 13
     - month
     - datetime64[M]
     - int32
     - Year and month
   * - 14
     - date
     - datetime64[D]
     - int32
     - Date (year, month, day)
   * - 16
     - timespan
     - timedelta64[ns]
     - int64
     - Time duration in nanoseconds
   * - 17
     - minute
     - datetime64[m]
     - int32
     - Time duration (or time of day) in minutes
   * - 18
     - second
     - datetime64[s]
     - int32
     - Time duration (or time of day) in seconds
   * - 19
     - time
     - datetime64[ms]
     - int32
     - Time duration (or time of day) in milliseconds
   * - 20+
     - enum
     - str
     - int32
     - Enumerated strings


Simple types
^^^^^^^^^^^^

Kdb+ atoms and vectors of the simple types (booleans, characters, integers and floats) can
be viewed as 0- or 1-dimensional NumPy arrays.  For example,

>>> x = K.real([10, 20, 30])
>>> a = numpy.asarray(x)
>>> a.dtype
dtype('float32')

Note that ``a`` in the example above is not a copy of ``x``.  It is an array view
into the same data:

>>> a.base.obj
k('10 20 30e')

If you modify ``a``, you modify x as well:

>>> a[:] = 88
>>> x
k('88 88 88e')


Dates, times and durations
^^^^^^^^^^^^^^^^^^^^^^^^^^

An age old question of when to start counting calendar years did not get
any easier in the computer age.  Python standard :class:`~datetime.date`
starts at

>>> date.min
datetime.date(1, 1, 1)

more commonly known as

>>> date.min.strftime('%B %d, %Y')   # doctest: +SKIP
'January 01, 0001'

and this date is considered to be day 1

>>> date.min.toordinal()
1

Note that according to the Python calendar the world did not exist before
that date:

>>> date.fromordinal(0)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: ordinal must be >= 1

At the time of this writing,

>>> date.today().toordinal()  # doctest: +SKIP
736335

The designer of kdb+ made a more practical choice for date 0 to be
January 1, 2000.  As a result, in PyQ we have

>>> K.date(0)
k('2000.01.01')

and

>>> (-2 + q.til(5)).date
k('1999.12.30 1999.12.31 2000.01.01 2000.01.02 2000.01.03')

Similarly, the 0 timestamp was chosen to be at midnight of the day 0

>>> K.timestamp(0)
k('2000.01.01D00:00:00.000000000')

NumPy, however the third choice was made.  Kowtowing to the UNIX tradition,
NumPy took midnight of January 1, 1970 as the zero mark on its timescales.

>>> numpy.array([0], 'datetime64[D]')
array(['1970-01-01'], dtype='datetime64[D]')
>>> numpy.array([0], 'datetime64[ns]')
array(['1970-01-01T00:00:00.000000000'], dtype='datetime64[ns]')

PyQ will automatically adjust the epoch when converting between NumPy arrays
and :class:`~pyq.K` objects.

>>> d = q.til(2).date
>>> a = numpy.array(d)
>>> d
k('2000.01.01 2000.01.02')
>>> a
array(['2000-01-01', '2000-01-02'], dtype='datetime64[D]')
>>> K(a)
k('2000.01.01 2000.01.02')

This convenience comes at a cost of copying the data

>>> a[0] = 0
>>> a
array(['1970-01-01', '2000-01-02'], dtype='datetime64[D]')
>>> d
k('2000.01.01 2000.01.02')

To avoid such copying, :class:`~pyq.K` objects can expose their raw data
to numpy:

>>> b = numpy.asarray(d.data)
>>> b.tolist()
[0, 1]

Arrays created this way share their data with the underlying :class:`~pyq.K`
objects.  Any change to the array is reflected in kdb+.

>>> b[:] += 42
>>> d
k('2000.02.12 2000.02.13')


Characters, strings and symbols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Text data appears in kdb+ as character atoms and strings or as symbols
and enumerations.  Character strings are compatible with NumPy "bytes"
type:

>>> x = K.string("abc")
>>> a = numpy.asarray(x)
>>> a.dtype.type
<class 'numpy.bytes_'>

In the example above, data is shared between the kdb+ string **x** and NumPy
array **a**:

>>> a[:] = 'x'
>>> x
k('"xxx"')



Nested lists
------------

Kdb+ does not have a data type representing multi-dimensional contiguous arrays.
In PyQ, a multi-dimensional NumPy array becomes a nested list when passed to ``q``
functions or converted to :class:`~pyq.K` objects.  For example,

>>> a = numpy.arange(12, dtype=float).reshape((2,2,3))
>>> x = K(a)
>>> x
k('((0 1 2f;3 4 5f);(6 7 8f;9 10 11f))')

Similarly, kdb+ nested lists of regular shape, become multi-dimensional NumPy arrays
when passed to :func:`numpy.array`:

>>> numpy.array(x)
array([[[  0.,   1.,   2.],
        [  3.,   4.,   5.]],
<BLANKLINE>
       [[  6.,   7.,   8.],
        [  9.,  10.,  11.]]])

Moreover, many NumPy functions can operate directly on kdb+ nested lists, but
they internally create a contiguous copy of the data

>>> numpy.mean(x, axis=2)
array([[  1.,   4.],
       [  7.,  10.]])


Tables and dictionaries
-----------------------

Unlike kdb+ NumPy does not implement column-wise tables.  Instead it has record arrays
that can store table-like data row by row.  PyQ supports two-way conversion between kdb+
tables and NumPy record arrays:

>>> trades.show()  # doctest: +NORMALIZE_WHITESPACE
sym time  size
--------------
a   09:31 100
a   09:33 300
b   09:32 200
b   09:35 100

>>> numpy.array(trades)  # doctest: +NORMALIZE_WHITESPACE
array([('a', datetime.timedelta(0, 34260), 100),
       ('a', datetime.timedelta(0, 34380), 300),
       ('b', datetime.timedelta(0, 34320), 200),
       ('b', datetime.timedelta(0, 34500), 100)],
      dtype=[('sym', 'O'), ('time', '<m8[m]'), ('size', '<i8')])
