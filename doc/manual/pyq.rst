.. _pyq:

.. testsetup::

   from pyq import *
   from datetime import date, time
   import numpy
   import math
   import bisect
   import pathlib
   import operator
   import itertools
   import functools

.. testcleanup:: prec

   q.system(b"P 7")

Python for kdb+
===============

------------
Introduction
------------

Kdb+, a high-performance database system comes with a programming language (q)
that may be unfamiliar to many programmers.  PyQ lets you enjoy the power of
kdb+ in a comfortable environment provided by a mainstream programming
language.  In this guide we will assume that the reader has a working knowledge
of Python, but we will explain the q language concepts as we encounter them.

---------------
The q namespace
---------------

Meet ``q`` - your portal to kdb+.  Once you import :const:`~pyq.q` from :mod:`pyq`,
you get access to over 170 functions:

>>> from pyq import q
>>> dir(q)  # doctest: +ELLIPSIS
['abs', 'acos', 'aj', 'aj0', 'all', 'and_', 'any', 'asc', 'asin', ...]

These functions should be familiar to anyone who knows the q language and this
is exactly what these functions are: q functions repackaged so that they can be
called from Python.  Some of the q functions are similar to Python builtins or
:mod:`math` functions which is not surprising because q like Python is a complete
general purpose language.  In the following sections we will systematically draw
an analogy between q and Python functions and explain the differences between them.

The til function
----------------

Since Python does not have a language constructs to loop over integers, many
Python tutorials introduce the :func:`range` function early on.  In the q language,
the situation is similar and the function that produces a sequence of integers
is called "til". Mnemonically, ``q.til(n)`` means "Count from zero 'til *n*":

>>> q.til(10)
k('0 1 2 3 4 5 6 7 8 9')

The return value of a q function is always an instance of the class :class:`~pyq.K`
which will be described in the next chapter.  In the case of ``q.til(n)``, the result
is a :class:`~pyq.K` vector which is similar to Python list.  In fact, you can get
the Python list by simply calling the :func:`list` constructor on the q vector:

>>> list(_)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

While useful for illustrative purposes, you should avoid converting :class:`~pyq.K`
vectors to Python lists in real programs.  It is often more efficient to manipulate
:class:`~pyq.K` objects directly.  For example, unlike :func:`range`, :func:`~pyq.q.til`
does not have optional start or step arguments.  This is not necessary because you
can do arithmetic on the :class:`~pyq.K` vectors to achieve a similar result:

>>> range(10, 20, 2) == 10 + 2 * q.til(5)
True

Many q functions are designed to "map" themselves automatically over sequences passed as
arguments.  Those functions are called "atomic" and will be covered in the next section.
The :func:`~pyq.q.til` function is not atomic, but it can be mapped explicitly:

>>> q.til.each(range(5)).show()
`long$()
,0
0 1
0 1 2
0 1 2 3

The last example requires some explanation.  First we have used the :meth:`~pyq.K.show`
method to provide a nice multi-line display of a list of vectors.  This method is
available for all :class:`~pyq.K` objects.  Second, the first line in the display shows
and empty list of type "long".  Note that unlike Python lists :class:`~pyq.K` vectors
come in different types and :func:`~pyq.q.til` returns vectors of type "long".  Finally,
the second line in the display starts with "," to emphasize that this is a vector of size
1 rather than an atom.

The :meth:`~pyq.K.each` adverb is similar to Python's :func:`map`, but is often much faster.

>>> q.til.each(range(5)) == map(q.til, range(5))
True


Atomic functions
----------------

As we mentioned in the previous section, atomic functions operate on numbers
or lists of numbers.  When given a number, an atomic function acts similarly
to its Python analogue.

Compare

>>> q.exp(1)
k('2.718282')

and

>>> math.exp(1)
2.718281828459045

.. note::

   Want to see more digits?  Set ``q`` display precision using the
   :func:`~pyq.q.system` function:

    .. doctest:: prec

       >>> q.system(b"P 16")
       k('::')
       >>> q.exp(1)
       k('2.718281828459045')

Unlike their native Python analogues, atomic ``q`` functions can operate
on sequences:

>>> q.exp(range(5))
k('1 2.718282 7.389056 20.08554 54.59815')

The result in this case is a :class:`~pyq.K` vector whose elements are
obtained by applying the function to each element of the given sequence.


Mathematical functions
^^^^^^^^^^^^^^^^^^^^^^

As you can see in the table below, most of the mathematical functions
provided by q are similar to the Python standard library functions in
the :mod:`math` module.

.. list-table:: Mathematical functions
   :header-rows: 1

   * - q
     - Python
     - Return
   * - :func:`~pyq.q.neg`
     - :func:`operator.neg`
     - the negative of the argument
   * - :func:`~pyq.q.abs`
     - :func:`abs`
     - the absolute value
   * - :func:`~pyq.q.signum`
     -
     - ±1 or 0 depending on the sign of the argument
   * - :func:`~pyq.q.sqrt`
     - :func:`math.sqrt`
     - the square root of the argument
   * - :func:`~pyq.q.exp`
     - :func:`math.exp`
     - e raised to the power of the argument
   * - :func:`~pyq.q.log`
     - :func:`math.log`
     - the natural logarithm (base e) of the argument
   * - :func:`~pyq.q.cos`
     - :func:`math.cos`
     - the cosine of the argument
   * - :func:`~pyq.q.sin`
     - :func:`math.sin`
     - the sine of the argument
   * - :func:`~pyq.q.tan`
     - :func:`math.tan`
     - the tangent of the argument
   * - :func:`~pyq.q.acos`
     - :func:`math.acos`
     - the arc cosine of the argument
   * - :func:`~pyq.q.asin`
     - :func:`math.asin`
     - the arc sine of the argument
   * - :func:`~pyq.q.atan`
     - :func:`math.atan`
     - the arc tangent of the argument
   * - :func:`~pyq.q.ceiling`
     - :func:`math.ceil`
     - the smallest integer >= the argument
   * - :func:`~pyq.q.floor`
     - :func:`math.floor`
     - the largest integer <= the argument
   * - :func:`~pyq.q.reciprocal`
     -
     - 1 divided by the argument

Other than being able to operate on lists of of numbers, q functions differ
from Python functions in a way they treat out of domain errors.

Where Python functions raise an exception,

>>> math.log(0)  # doctest: +ELLIPSIS
Traceback (most recent call last):
  ...
ValueError: math domain error

q functions return special values:

>>> q.log([-1, 0, 1])
k('0n -0w 0')


The null function
^^^^^^^^^^^^^^^^^

Unlike Python, q allows division by zero.  The reciprocal of zero is
infinity that shows up as 0w or 0W in displays.

>>> q.reciprocal(0)
k('0w')

Multiplying infinity by zero produces a null value that generally indicates
missing data

>>> q.reciprocal(0) * 0
k('0n')

Null values and infinities can also appear as a result of applying a
mathematical function to numbers outside of its domain:

>>> q.log([-1, 0, 1])
k('0n -0w 0')

The :func:`~pyq.q.null` function returns 1b (boolean true) when given a
null value and 0b otherwise.  For example, wen applied to the output of
the :func:`~pyq.q.log` function from the previous example, it returns

>>> q.null(_)
k('100b')


Aggregation functions
---------------------

Aggregation functions (also known as reduction functions) are functions that
given a sequence of atoms produce an atom.  For example,

>>> sum(range(10))
45
>>> q.sum(range(10))
k('45')

.. list-table:: Aggregation functions
   :header-rows: 1

   * - q
     - Python
     - Return
   * - :func:`~pyq.q.sum`
     - :func:`sum`
     - the sum of the elements
   * - :func:`~pyq.q.prd`
     -
     - the product of the elements
   * - :func:`~pyq.q.all`
     - :func:`all`
     - ``1b`` if all elements are nonzero, ``0b`` otherwise
   * - :func:`~pyq.q.any`
     - :func:`any`
     - ``1b`` if any of the elements is nonzero, ``0b`` otherwise
   * - :func:`~pyq.q.min`
     - :func:`min`
     - the smallest element
   * - :func:`~pyq.q.max`
     - :func:`max`
     - the largest element
   * - :func:`~pyq.q.avg`
     - :func:`statistics.mean`
     - the arithmetic mean
   * - :func:`~pyq.q.var`
     - :func:`statistics.pvariance`
     - the population variance
   * - :func:`~pyq.q.dev`
     - :func:`statistics.pstdev`
     - the square root of the population variance
   * - :func:`~pyq.q.svar`
     - :func:`statistics.variance`
     - the sample variance
   * - :func:`~pyq.q.sdev`
     - :func:`statistics.stdev`
     - the square root of the sample variance


Accumulation functions
----------------------

Given a sequence of numbers, one may want to compute not just
total sum, but all the intermediate sums as well.  In q, this
can be achieved by applying the ``sums`` function to the sequence:

>>> q.sums(range(10))
k('0 1 3 6 10 15 21 28 36 45')

.. list-table:: Accumulation functions
   :header-rows: 1

   * - q
     - Return
   * - :func:`pyq.q.sums`
     - the cumulative sums of the elements
   * - :func:`pyq.q.prds`
     - the cumulative products of the elements
   * - :func:`pyq.q.maxs`
     - the maximums of the prefixes of the argument
   * - :func:`pyq.q.mins`
     -  the minimums of the prefixes of the argument


There are no direct analogues of these functions in the Python standard
library, but the :func:`itertools.accumulate` function provides similar
functionality:

>>> list(itertools.accumulate(range(10)))
[0, 1, 3, 6, 10, 15, 21, 28, 36, 45]

Passing :func:`operator.mul`, :func:`max` or :func:`min` as the second
optional argument to :func:`itertools.accumulate`, one can get
analogues of :func:`pyq.q.prds`, :func:`pyq.q.maxs` and :func:`pyq.q.mins`.


Sliding window statistics
-------------------------

 * :func:`~pyq.q.mavg`
 * :func:`~pyq.q.mcount`
 * :func:`~pyq.q.mdev`
 * :func:`~pyq.q.mmax`
 * :func:`~pyq.q.mmin`
 * :func:`~pyq.q.msum`


Uniform functions
-----------------

Uniform functions are functions that take a list and return another list
of the same size.

 * :func:`~pyq.q.reverse`
 * :func:`~pyq.q.ratios`
 * :func:`~pyq.q.deltas`
 * :func:`~pyq.q.differ`
 * :func:`~pyq.q.next`
 * :func:`~pyq.q.prev`
 * :func:`~pyq.q.fills`


Set operations
--------------

 * :func:`~pyq.q.except_`
 * :func:`~pyq.q.inter`
 * :func:`~pyq.q.union`


Sorting and searching
---------------------

Functions :func:`~pyq.q.asc` and :func:`~pyq.q.desc` sort lists in ascending
and descending order respectively:

>>> a = [9, 5, 7, 3, 1]
>>> q.asc(a)
k('`s#1 3 5 7 9')
>>> q.desc(a)
k('9 7 5 3 1')

.. note::

   The ```s#`` prefix that appears in the display of the output for the
   :func:`~pyq.q.asc` function indicates that the resulting vector has a
   sorted attribute set.  An attribute can be queried by calling the
   :func:`~pyq.q.attr` function or accessing the :attr:`~pyq.K.attr` property
   of the result:

   >>> s = q.asc(a)
   >>> q.attr(s)
   k('`s')
   >>> s.attr
   k('`s')

   When the :func:`~pyq.q.asc` function gets a vector with the ``s`` attribute
   set, it skips sorting and immediately returns the same vector.

Functions :func:`~pyq.q.iasc` and :func:`~pyq.q.idesc` return the indices indicating
the order in which the elements of the incoming list should be taken to make them
sorted:

>>> q.iasc(a)
k('4 3 1 2 0')

Sorted lists can be efficiently searched using :func:`~pyq.q.bin` and
:func:`~pyq.q.binr` functions.  As the names suggest, both use binary search to
locate the position the element that is equal to the search key, but in the
case when there is more than one such element, :func:`~pyq.q.binr` returns the
index of the first match while :func:`~pyq.q.bin` returns the index of the last.

>>> q.binr([10, 20, 20, 20, 30], 20)
k('1')
>>> q.bin([10, 20, 20, 20, 30], 20)
k('3')

When no matching element can be found, :func:`~pyq.q.binr` (:func:`~pyq.q.bin`)
returns the index of the position before (after) which the key can be inserted
so that the list remains sorted.

>>> q.binr([10, 20, 20, 20, 30], [5, 15, 20, 25, 35])
k('0 1 1 4 5')
>>> q.bin([10, 20, 20, 20, 30], [5, 15, 20, 25, 35])
k('-1 0 3 3 4')

In the Python standard library similar functionality is provided by the :mod:`bisect`
module.

>>> [bisect.bisect_left([10, 20, 20, 20, 30], key) for key in [5, 15, 20, 25, 35]]
[0, 1, 1, 4, 5]
>>> [-1 + bisect.bisect_right([10, 20, 20, 20, 30], key) for key in [5, 15, 20, 25, 35]]
[-1, 0, 3, 3, 4]

Note that while :func:`~pyq.q.binr` and :func:`bisect.bisect_left` return the same values,
:func:`~pyq.q.bin` and :func:`bisect.bisect_right` are off by 1.

Q does not have a named function for searching in an unsorted list because it uses the ``?``
operator for that.  We can easily expose this functionality in PyQ as follows:

>>> index = q('?')
>>> index([10, 30, 20, 40], [20, 25])
k('2 4')

Note that our home-brew ``index`` function is similar to the :meth:`list.index` method, but
it returns the one after last index when the key is not found while :meth:`list.index` raises
an exception.

>>> list.index([10, 30, 20, 40], 20)
2
>>> list.index([10, 30, 20, 40], 25)
Traceback (most recent call last):
  ...
ValueError: 25 is not in list

If you are not interested in the index, but only want to know whether the keys can be found in
a list, you can use the :func:`~pyq.q.in_` function:

>>> q.in_([20, 25], [10, 30, 20, 40])
k('10b')

.. note::

   The :func:`q.in_ <pyq.q.in_>` function has a trailing underscore because otherwise it would
   conflict with the Python :keyword:`in`.


From Python to kdb+
-------------------

You can pass data from Python to kdb+ by
assigning to ``q`` attributes.  For example,

>>> q.i = 42
>>> q.a = [1, 2, 3]
>>> q.t = ('Python', 3.5)
>>> q.d = {'date': date(2012, 12, 12)}
>>> q.value.each(['i', 'a', 't', 'd']).show()
42
1 2 3
(`Python;3.5)
(,`date)!,2012.12.12

Note that Python objects are automatically converted to kdb+ form when they are
assigned in the ``q`` namespace, but when they are retrieved, Python gets a
"handle" to kdb+ data.

For example, passing an ``int`` to ``q`` results in

>>> q.i
k('42')

If you want a Python integer instead, you have to convert explicitly

>>> int(q.i)
42

This will be covered in more detail in the next section.

You can also create kdb+ objects by calling ``q`` functions that are also
accessible as ``q`` attributes.  For example,

>>> q.til(5)
k('0 1 2 3 4')

Some q functions don't have names because q uses special characters.
For example, to generate random data in q you should use the ``?``
function (operator).  While PyQ does not supply a Python name for ``?``,
you can easily add it to your own toolkit:

>>> rand = q('?')

And use it as you would any other Python function

>>> x = rand(10, 2)  # generates 10 random 0's or 1's (coin toss)

From kdb+ to Python
-------------------

In many cases your data is already stored in kdb+ and PyQ philosophy is
that it should stay there.  Rather than converting kdb+ objects to Python,
manipulating Python objects and converting them back to kdb+, PyQ lets
you work directly with kdb+ data as if it was already in Python.

For example, let us retrieve the release date from kdb+:

>>> d1 = q('.z.k')

add 30 days to get another date

>>> d2 = d1 + 30

and find the difference in whole weeks

>>> (d2 - d1) % 7
k('2')

Note that the result of operations are (handles to) kdb+ objects.  The only
exceptions to this rule are indexing and iteration over simple kdb+ vectors.
These operations produce Python scalars

>>> list(q.a)
[1, 2, 3]
>>> q.a[-1]
3

In addition to Python operators, one invoke q functions on kdb+ objects
directly from Python using convenient attribute access / method call syntax.

For example

>>> q.i.neg.exp.log.mod(5)
k('3f')

Note that the above is equivalent to

>>> q.mod(q.log(q.exp(q.neg(q.i))), 5)
k('3f')

but shorter and closer to ``q`` syntax

>>> q('(log exp neg i)mod 5')
k('3f')

The difference being that in q, functions are applied right to left, by in PyQ
left to right.

Finally, if q does not provide the function that you need, you can unleash the
full power of numpy or scipy on your kdb+ data.

>>> numpy.log2(q.a)  # doctest: +SKIP
array([ 0.       ,  1.       ,  1.5849625])

Note that the result is a numpy array, but you can redirect the output back to
kdb+.  To illustrate this, create a vector of 0s in kdb+

>>> b = q.a * 0.0  # doctest: +SKIP

and call a numpy function on one kdb+ object redirecting the output to another:

>>> numpy.log2(q.a, out=numpy.asarray(b)) # doctest: +SKIP

The result of a numpy function is now in the kdb+ object

>>> b              # doctest: +SKIP
k('0 1 1.584963')


Working with files
------------------

Kdb+ uses unmodified host file system to store data and therefore q has
excellent support for working with files.  Recall that we can send Python
objects to kdb+ by simply assigning them to a :data:`q` attribute:

>>> q.data = range(10)

This code saves 10 integers in kdb+ memory and makes a global variable ``data``
available to kdb+ clients, but it does not save the data in any persistent storage.
To save ``data`` is a file "data", we can simply call the :func:`pyq.q.save <q.save>`
function as follows:

>>> q.save('data')
k('`:data')

Note that the return value of the :func:`pyq.q.save <q.save>` function is a :class:`K`
symbol that is formed by prepending ':' to the file name.  Such symbols are known as
file handles in q.  Given a file handle the kdb+ object stored in the file can be obtained
by accessing the ``value`` property of the file handle:

>>> _.value
k('0 1 2 3 4 5 6 7 8 9')

Now we can delete the data from memory

>>> del q.data

and load it back from the file using the :func:`pyq.q.load <q.load>` function:

>>> q.load('data')
k('`data')
>>> q.data
k('0 1 2 3 4 5 6 7 8 9')

:func:`pyq.q.save <q.save>` and :func:`pyq.q.load <q.load>` functions can also
take a :class:`pathlib.Path` object

>>> data_path = pathlib.Path('data')
>>> q.save(data_path)
k('`:data')
>>> q.load(data_path)
k('`data')

It is not necessary to assign data to a global variable before saving it to a
file.  We can save our 10 integers directly to a file using the
:func:`pyq.q.set <q.set>` function

>>> q.set(':0-9', range(10))
k('`:0-9')

and read it back using the :func:`pyq.q.set <q.get>` function

>>> q.get(_)
k('0 1 2 3 4 5 6 7 8 9')

---------
K objects
---------

The q language has has atoms (scalars), lists, dictionaries, tables and functions.  In PyQ,
kdb+ objects of any type appear as instances of class :class:`~pyq.K`.  To tell the underlying
kdb+ type, one can access the :attr:`~pyq.K.type` property to obtain a type code.  For example,

>>> vector = q.til(5); scalar = vector.first
>>> vector.type
k('7h')
>>> scalar.type
k('-7h')

Basic vector types have type codes in the range 1 through 19 and their elements have the type
code equal to the negative of the vector type code.  For the basic vector types, one can also
get a human readable type name by accessing the :attr:`~pyq.K.key` property:

>>> vector.key
k('`long')

To get the same from a scalar – convert it to a vector first:

>>> scalar.enlist.key
k('`long')

.. list-table:: Basic data types
   :header-rows: 1

   * - Code
     - Kdb+ type
     - Python type
   * - 1
     - ``boolean``
     - :class:`bool`
   * - 2
     - ``guid``
     - :class:`uuid.UUID`
   * - 4
     - ``byte``
     -
   * - 5
     - ``short``
     -
   * - 6
     - ``int``
     -
   * - 7
     - ``long``
     - :class:`int`
   * - 8
     - ``real``
     -
   * - 9
     - ``float``
     - :class:`float`
   * - 10
     - ``char``
     - :class:`bytes` (*)
   * - 11
     - ``symbol``
     - :class:`str`
   * - 12
     - ``timestamp``
     -
   * - 13
     - ``month``
     -
   * - 14
     - ``date``
     - :class:`datetime.date`
   * - 16
     - ``timespan``
     - :class:`datetime.timedelta`
   * - 17
     - ``minute``
     -
   * - 18
     - ``second``
     -
   * - 19
     - ``time``
     - :class:`datetime.time`

(*) Unlike other Python types mentioned in the table above, :class:`bytes` instances get converted
to a vector type:

>>> K(b'x')
k(',"x"')
>>> q.type(_)
k('10h')

There is no scalar character type in Python, so in order to create a :class:`~pyq.K` character scalar,
one will need to use a typed constructor:

>>> K.char(b'x')
k('"x"')

Typed constructors are discussed in the next section.


Constructors and casts
----------------------

As we have seen in the previous chapter, it is often not necessary to construct :class:`~pyq.K`
objects explicitly because they are automatically created whenever a Python object is passed
to a q function.  This is done by passing the Python object to the default :class:`~pyq.K`
constructor.

For example, if you need to pass a type long atom to a q function, you can use a Python
:class:`int` instead, but if a different integer type is required, you will need to create
it explicitly:

>>> K.short(1)
k('1h')

Since empty list does not know the element type, passing ``[]`` to the default :class:`~pyq.K`
constructor produces a generic (type ``0h``) list:

>>> K([])
k('()')
>>> q.type(_)
k('0h')

To create an empty list of a specific type -- pass ``[]`` to one of the named constructors:

>>> K.time([])
k('`time$()')

.. list-table:: :class:`~pyq.K` constructors
   :header-rows: 1

   * - Constructor
     - Accepts
     - Description
   * - :meth:`K.boolean`
     - :class:`int`, :class:`bool`
     - logical type ``0b`` is false and ``1b`` is true.
   * - :meth:`byte`
     - :class:`int`, :class:`bytes`
     - 8-bit bytes
   * - :meth:`short`
     - :class:`int`
     - 16-bit integers
   * - :meth:`int`
     - :class:`int`
     - 32-bit integers
   * - :meth:`long`
     - :class:`int`
     - 64-bit integers
   * - :meth:`real`
     - :class:`int`, :class:`float`
     - 32-bit floating point numbers
   * - :meth:`float`
     - :class:`int`, :class:`float`
     - 32-bit floating point numbers
   * - :meth:`char`
     - :class:`str`, :class:`bytes`
     - 8-bit characters
   * - :meth:`symbol`
     - :class:`str`, :class:`bytes`
     - interned strings
   * - :meth:`timestamp`
     - :class:`int` (nanoseconds), :class:`~datetime.datetime`
     - date and time
   * - :meth:`month`
     - :class:`int` (months), :class:`~datetime.date`
     - year and month
   * - :meth:`date`
     - :class:`int` (days), :class:`~datetime.date`
     - year, month and day
   * - :meth:`datetime`
     -
     - deprecated
   * - :meth:`timespan`
     - :class:`int` (nanoseconds), :class:`~datetime.timedelta`
     - duration in nanoseconds
   * - :meth:`minute`
     - :class:`int` (minutes), :class:`~datetime.time`
     - duration or time of day in minutes
   * - :meth:`second`
     - :class:`int` (seconds), :class:`~datetime.time`
     - duration or time of day in seconds
   * - :meth:`time`
     - :class:`int` (milliseconds), :class:`~datetime.time`
     - duration or time of day in milliseconds

The typed constructors can also be used to access infinities an missing values
of the given type:

>>> K.real.na, K.real.inf
(k('0Ne'), k('0we'))

If you already have a :class:`~pyq.K` object and want to convert it to a different
type, you can access the property named after the type name.  For example,

>>> x = q.til(5)
>>> x.date
k('2000.01.01 2000.01.02 2000.01.03 2000.01.04 2000.01.05')



Operators
---------

Both Python and q provide a rich system of operators.  In PyQ, :class:`~pyq.K` objects
can appear in many Python expressions where they often behave as native Python objects.

Most operators act on :class:`~pyq.K` instances as namesake q functions.  For example:

>>> K(1) + K(2)
k('3')

The if statement and boolean operators
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Python has three boolean operators ``or``, ``and`` and ``not`` and :class:`~pyq.K`
objects can appear in boolean expressions.  The result of boolean expressions depends
on how the objects are tested  in Python if statements.

All :class:`~pyq.K` objects can be tested for "truth". Similarly to
the Python numeric types and sequences, :class:`~pyq.K` atoms of numeric types are true
is they are not zero and vectors are true if they are non-empty.

Atoms of non-numeric types follow different rules.  Symbols test true except for the empty
symbol; characters and bytes tested true except for the null character/byte; guid, timestamp,
and (deprecated) datetime types always test as true.

Functions test as true except for the monadic pass-through function:

>>> q('::') or q('+') or 1
k('+')

Dictionaries and tables are treated as sequences: they are true if non-empty.

Note that in most cases how the object test does not change when Python native types
are converted to :class:`~pyq.K`:

>>> objects = [None, 1, 0, True, False, 'x', '', {1:2}, {}, date(2000, 1, 1)]
>>> [bool(o) for o in objects]
[False, True, False, True, False, True, False, True, False, True]
>>> [bool(K(o)) for o in objects]
[False, True, False, True, False, True, False, True, False, True]

One exception is the Python :class:`~datetime.time` type.  Starting with version 3.5 all
:class:`~datetime.time` instances test as true, but ``time(0)`` converts to
``k('00:00:00.000')`` which tests false:

>>> [bool(o) for o in (time(0), K(time(0)))]
[True, False]

.. note::

   Python changed the rule for ``time(0)`` because :class:`~datetime.time` instances
   can be timezone aware and because they do not support addition making 0 less than
   special.  Neither of those arguments apply to ``q`` time, second or minute data
   types which behave more like :class:`~datetime.timedelta`.

Arithmetic operations
^^^^^^^^^^^^^^^^^^^^^

Python has the four familiar arithmetic operators ``+``, ``-``, ``*`` and ``/`` as well as
less common ``**`` (exponentiation), ``%`` (modulo) and ``//`` (floor division).  PyQ
maps those operators to q "verbs" as follows

===============   ======  =======
Operation         Python   q
===============   ======  =======
addition          ``+``   ``+``
subtraction       ``-``   ``-``
multiplication    ``*``   ``*``
true division     ``/``   ``%``
exponentiation    ``**``  ``xexp``
floor division    ``//``  ``div``
modulo            ``%``   ``mod``
===============   ======  =======

:class:`~pyq.K` objects can be freely mixed with Python native types in arithmetic expressions
and the result is a :class:`~pyq.K` object in most cases:

>>> q.til(10) % 3
k('0 1 2 0 1 2 0 1 2 0')

A notable exception occurs when the modulo operator is used for string formatting

>>> "%.5f" % K(3.1415)
'3.14150'

Unlike python sequences, :class:`~pyq.K` lists behave very similar to atoms: arithmetic
operations act element-wise on them.

Compare

>>> [1, 2] * 5
[1, 2, 1, 2, 1, 2, 1, 2, 1, 2]

and

>>> K([1, 2]) * 5
k('5 10')

or

>>> [1, 2] + [3, 4]
[1, 2, 3, 4]

and

>>> K([1, 2]) + [3, 4]
k('4 6')


The flip (``+``) operator
^^^^^^^^^^^^^^^^^^^^^^^^^

The unary ``+`` operator acts as :func:`~pyq.q.flip` function on :class:`~pyq.K`
objects.  Applied to atoms, it has no effect:


>>> +K(0)
k('0')

but it can be used to transpose a matrix:

>>> m = K([[1, 2], [3, 4]])
>>> m.show()
1 2
3 4
>>> (+m).show()
1 3
2 4

or turn a dictionary into a table:

>>> d = q('!', ['a', 'b'], m)
>>> d.show()
a| 1 2
b| 3 4
>>> (+d).show()
a b
---
1 3
2 4

Bitwise operators
^^^^^^^^^^^^^^^^^

Python has six bitwise operators: ``|``, ``^``, ``&``, ``<<``,
``>>``, and ``~``.  Since there are no bitwise operations in q,
PyQ redefines them as follows:

+------------+--------------------------------+----------+
| Operation  | Result                         | Notes    |
+============+================================+==========+
| ``x | y``  | element-wise maximum of        | (1)      |
|            | *x*  and *y*                   |          |
+------------+--------------------------------+----------+
| ``x ^ y``  | *y* with null elements filled  | (2)      |
|            | with *x*                       |          |
+------------+--------------------------------+----------+
| ``x & y``  | element-wise minimum of        | (1)      |
|            | *x* and *y*                    |          |
+------------+--------------------------------+----------+
| ``x << n`` | *x* shifted left by *n*        |          |
|            | elements                       | (3)      |
+------------+--------------------------------+----------+
| ``x >> n`` | *x* shifted right by *n*       |          |
|            | elements                       | (3)      |
+------------+--------------------------------+----------+
| ``~x``     | a boolean vector with 1's for  |          |
|            | zero elements of *x*           |          |
+------------+--------------------------------+----------+

Notes:

(1)
   For boolean vectors, ``|`` and ``&`` are also element-wise *or* and
   *and* operations.

(2) For Python integers, the result of ``x ^ y`` is the bitwise exclusive
    or.  There is no similar operation in ``q``, but for boolean vectors
    exclusive or is equivalent to q ``<>`` (not equal).

(3)
   Negative shift counts result in a shift in the opposite direction to
   that indicated by the operator: ``x >> -n`` is the same as ``x << n``.

Minimum and maximum
"""""""""""""""""""

Minimum and maximum operators are ``&`` and ``|`` in q.  PyQ maps similar
looking Python bitwise operators to the corresponding q ones:

>>> q.til(10) | 5
k('5 5 5 5 5 5 6 7 8 9')
>>> q.til(10) & 5
k('0 1 2 3 4 5 5 5 5 5')

The ``^`` operator
""""""""""""""""""

Unlike Python where caret (``^``) is the binary xor operator, q defines it
to denote the `fill`_ operation that replaces null values in the right argument
with the left argument.  PyQ follows the q definition:

>>> x = q('1 0N 2')
>>> 0 ^ x
k('1 0 2')

.. _fill: http://code.kx.com/wiki/Reference/Caret

The ``@`` operator
^^^^^^^^^^^^^^^^^^

Python 3.5 introduced the ``@`` operator that can be used by user types.  Unlike
numpy that defines ``@`` as the matrix multiplication operator, PyQ uses ``@``
for function application and composition:

>>> q.log @ q.exp @ 1
k('1f')


Adverbs
-------

Adverbs in q are somewhat similar to Python decorators.  They act on functions and
produce new functions.  The six adverbs are summarized in the table below.


.. list-table:: Adverbs
   :header-rows: 1

   * - PyQ
     - q
     - Description
   * - :meth:`K.each`
     - ``'``
     - map or case
   * - :meth:`K.over`
     - ``/``
     - reduce
   * - :meth:`K.scan`
     - ``\``
     - accumulate
   * - :meth:`K.prior`
     - ``':``
     - each-prior
   * - :meth:`K.sv`
     - ``/:``
     - each-right or scalar from vector
   * - :meth:`K.vs`
     - ``\:``
     - each-left or vector from scalar

The functionality provided by the first three adverbs is similar to functional
programming features scattered throughout Python standard library.  Thus ``each``
is similar to :func:`map`.  For example, given a list of lists of numbers

>>> data = [[1, 2], [1, 2, 3]]

One can do

>>> q.sum.each(data)
k('3 6')

or

>>> list(map(sum, [[1, 2], [1, 2, 3]]))
[3, 6]

and get similar results.

The ``over`` adverb is similar to the :func:`functools.reduce` function.  Compare

>>> q(',').over(data)
k('1 2 1 2 3')

and

>>> functools.reduce(operator.concat, data)
[1, 2, 1, 2, 3]


Finally, the ``scan`` adverb is similar to the :func:`itertools.accumulate` function.

>>> q(',').scan(data).show()
1 2
1 2 1 2 3

>>> for x in itertools.accumulate(data, operator.concat):
...     print(x)
...
[1, 2]
[1, 2, 1, 2, 3]


Each
^^^^

The ``each`` adverb serves double duty in q.  When it is applied to a function, it
returns a new function that expects lists as arguments and maps the original function
over those lists.  For example, we can write a "daily return" function in q that
takes yesterday's price as the first argument (x), today's price as the second (y) and
dividend as the third (z) as follow:

>>> r = q('{(y+z-x)%x}')  # Recall that % is the division operator in q.

and use it to compute returns from a series of prices and dividends using ``r.each``:

>>> p = [50.5, 50.75, 49.8, 49.25]
>>> d = [.0, .0, 1.0, .0]
>>> r.each(q.prev(p), p, d)
k('0n 0.004950495 0.0009852217 -0.01104418')

When the ``each`` adverb is applied to an integer vector, it turns the vector v into an
n-ary function that for each i-th argument selects its v[i]-th element. For example,

>>> v = q.til(3)
>>> v.each([1, 2, 3], 100, [10, 20, 30])
k('1 100 30')

Note that scalars passed to ``v.each`` are treated as infinitely repeated values. Vector
arguments must all be of the same length.


Over and scan
^^^^^^^^^^^^^

Given a function ``f``, ``f.over`` and ``f.scan`` adverbs are similar as both
apply ``f`` repeatedly, but ``f.over`` only returns the final result, while
``f.scan`` returns all intermediate values as well.

For example, recall that the Golden Ratio can be written as a continued fraction
as follows

.. math::

   \phi = 1+\frac{1}{1+\frac{1}{1+\cdots}}

or equivalently as the limit of the sequence that can be obtained by starting with
:math:`1` and repeatedly applying the function

.. math::

   f(x) = 1+\frac{1}{1+x}

The numerical value of the Golden Ratio can be found as

.. math::

   \phi = \frac{1+\sqrt{5}}{2} \approx 1.618033988749895

>>> phi = (1+math.sqrt(5)) / 2
>>> phi
1.618033988749895

Function :math:`f` can be written in q as follows:

>>> f = q('{1+reciprocal x}')

and

>>> f.over(1.)
k('1.618034')

indeed yields a number recognizable as the Golden Ratio.  If instead of ``f.over``,
we compute ``f.scan``, we will get the list of all convergents.

>>> x = f.scan(1.)
>>> len(x)
32

Note that ``f.scan`` (and ``f.over``) stop calculations when the next iteration
yields the same value and indeed ``f`` applied to the last value returns the same
value:

>>> f(x.last) == x.last
True

which is close to the value computed using the exact formula

>>> math.isclose(x.last, phi)
True

The number of iterations can be given explicitly by passing two arguments to
``f.scan`` or ``f.over``:

>>> f.scan(10, 1.)
k('1 2 1.5 1.666667 1.6 1.625 1.615385 1.619048 1.617647 1.618182 1.617978')
>>> f.over(10, 1.)
k('1.617978')

This is useful when you need to iterate a function that does not converge.

Continuing with the Golden Ratio theme, let's define a function

>>> f = q('{(last x;sum x)}')

that given a pair of numbers returns another pair made out of the last and
the sum of the numbers in the original pair.  Iterating this function yields
the Fibonacci sequence

>>> x = f.scan(10,[0, 1])
>>> q.first.each(x)
k('0 1 1 2 3 5 8 13 21 34 55')

and the ratios of consecutive Fibonacci numbers form the sequence of Golden Ratio
convergents that we have seen before:

>>> q.ratios(_)
k('0 0w 1 2 1.5 1.666667 1.6 1.625 1.615385 1.619048 1.617647')


Each previous
^^^^^^^^^^^^^

In the previous section we have seen a function :func:`~pyq.K.ratios` that takes
a vector and produces the ratios of the adjacent elements.  A similar function
called :func:`~pyq.K.deltas` produces the differences between the adjacent
elements:

>>> q.deltas([1, 3, 2, 5])
k('1 2 -1 3')

These functions are in fact implemented in q by applying the ``prior`` adverb to
the division (``%``) and subtraction functions respectively:

>>> q.ratios == q('%').prior and q.deltas == q('-').prior
True

In general, for any binary function :math:`f` and a vector :math:`v`

.. math::

   \mbox{f.prior}(v) = (f(v_1, v_0), \, f(v_2, v_1), \,\cdots)



Adverbs vs and sv
^^^^^^^^^^^^^^^^^

Of all adverbs, these two have the most cryptic names and offer some non-obvious features.

To illustrate how vs and sv modify binary functions, lets give a Python name to the q ``,``
operator:

>>> join = q(',')

Suppose you have a list of file names

>>> name = K.string(['one', 'two', 'three'])

and an extension

>>> ext = K.string(".py")


You want to append the extension to each name on your list.  If you naively call ``join`` on
``name`` and ``ext``, the result will not be what you might expect:

>>> join(name, ext)
k('("one";"two";"three";".";"p";"y")')

This happened because ``join`` treated ``ext`` as a list of characters rather than an atomic
string and created a mixed list of three strings followed by three characters.  What we need
is to tell ``join`` to treat its first argument as a vector and the second as a scalar and
this is exactly what the ``vs`` adverb will achieve:

>>> join.vs(name, ext)
k('("one.py";"two.py";"three.py")')

The mnemonic rule is "vs" = "vector, scalar".  Now, if you want to prepend a directory name
to each resulting file, you can use the ``sv`` attribute:

>>> d = K.string("/tmp/")
>>> join.sv(d, _)
k('("/tmp/one.py";"/tmp/two.py";"/tmp/three.py")')




Input/Output
------------

>>> import os
>>> r, w = os.pipe()
>>> h = K(w)(kp("xyz"))
>>> os.read(r, 100)
b'xyz'
>>> os.close(r); os.close(w)

Q variables can be accessed as attributes of the 'q' object:

>>> q.t = q('([]a:1 2i;b:`x`y)')
>>> sum(q.t.a)
3
>>> del q.t

.. _numpy:

.. include:: numpy.rst

.. _ipython:

.. include:: jupyter.rst

.. _q_prompt:

.. include:: cli.rst

.. _p_lang:

.. include:: py-from-q.rst
