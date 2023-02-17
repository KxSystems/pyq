# ![PyQ](img/pyq.png) PyQ user guide



PyQ lets you enjoy the power of kdb+ in a comfortable environment provided by a mainstream programming language. In this guide we will assume that the reader has a working knowledge of Python, but we will explain the q language concepts as we encounter them.


## The q namespace

Meet `q` – your portal to kdb+. Once you import `q` from `pyq`, you get access to over 170 functions:

```python
>>> from pyq import q
>>> dir(q)
['abs', 'acos', 'aj', 'aj0', 'all', 'and_', 'any', 'asc', 'asin', ...]
```

These functions should be familiar to anyone who knows the q language and this is exactly what these functions are: q functions repackaged so that they can be called from Python. Some of the q functions are similar to Python built-ins or math functions, which is not surprising because q, like Python, is a complete general-purpose language. In the following sections we will systematically draw an analogy between q and Python functions and explain the differences between them.


### The `til` function

Since Python does not have language constructs to loop over integers, many Python tutorials introduce the `range()` function early on. In the q language, the situation is similar and the function that produces a sequence of integers is called `til`. Mnemonically, `q.til(n)` means _count from zero until n_.

```python
>>> q.til(10)
k('0 1 2 3 4 5 6 7 8 9')
```

The return value of a q function is always an instance of the class `K`, which will be described in the next chapter. In the case of `q.til(n)`, the result is a `K` vector, which is similar to a Python list. In fact, you can get the Python list simply by calling the `list()` constructor on the q vector.

```python
>>> list(_)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

While useful for illustrative purposes, you should avoid converting `K` vectors to Python lists in real programs. It is often more efficient to manipulate `K` objects directly. For example, unlike `range()`, `til()` does not have optional start or step arguments. This is not necessary because you can do arithmetic on the `K` vectors to achieve a similar result.

```python
>>> range(10, 20, 2) == 10 + 2 * q.til(5)
True
```

Many q functions are designed to ‘map’ themselves automatically over sequences passed as arguments. Those functions are called _atomic_ and will be covered in the next section. The `til()` function is not atomic, but it can be mapped explicitly.

```python
>>> q.til.each(range(1,5)).show()
,0
0 1
0 1 2
0 1 2 3
```

The last example requires some explanation.  First we have used the `show()` method to provide a nice multi-line display of a list of vectors. This method is available for all `K` objects. Second, the first line in the display shows an empty list of type _long_. Note that, unlike Python lists, `K` vectors come in different types, and `til()` returns vectors of type _long_. Finally, the second line in the display starts with `,` to emphasize that this is a vector of length 1 rather than an atom.

The `each()` adverb is similar to Python’s `map()`, but is often much faster.

```python
>>> q.til.each(range(5)) == map(q.til, range(5))
True
```


### Atomic functions

As we mentioned in the previous section, atomic functions operate on numbers or lists of numbers. When given a number, an atomic function acts similarly to its Python analogue.

Compare

```python
>>> q.exp(1)
k('2.718282')
```

to

```python
>>> math.exp(1)
2.718281828459045
```

Want to see more digits? Set `q`’s display precision using the `system()` function:

```python
>>> q.system(b"P 16")
k('::')
>>> q.exp(1)
k('2.718281828459045')
```

Unlike their native Python analogues, atomic `q` functions can operate on sequences:

```python
>>> q.exp(range(5))
k('1 2.718282 7.389056 20.08554 54.59815')
```

The result in this case is a `K` vector whose elements are obtained by applying the function to each element of the given sequence.


#### Mathematical functions

As you can see in the table below, most of the mathematical functions provided by q are similar to the Python standard library functions in the `math` module.

q                                   | Python           | Return
------------------------------------|------------------|---------------------------------------
[`neg()`](../../ref/neg.md)         | [`operator.neg()`](https://docs.python.org/3.6/library/operator.html#operator.neg)  | the negative of the argument
[`abs()`](../../ref/abs.md)         | [`abs()`](https://docs.python.org/3.6/library/functions.html#abs)                   | the absolute value
[`signum()`](../../ref/signum.md)   |                                                                                     | ±1 or 0 depending on the sign of the argument
[`sqrt()`](../../ref/sqrt.md)       | [`math.sqrt()`](https://docs.python.org/3.6/library/math.html#math.sqrt)            | the square root of the argument
[`exp()`](../../ref/exp.md)         | [`math.exp()`](https://docs.python.org/3.6/library/math.html#math.exp)              | _e_ raised to the power of the argument
[`log()`](../../ref/log.md))        | [`math.log()`](https://docs.python.org/3.6/library/math.html#math.log)              | the natural logarithm (base e) of the argument
[`cos()`](../../ref/cos.md)         | [`math.cos()`](https://docs.python.org/3.6/library/math.html#math.cos)              | the cosine of the argument
[`sin()`](../../ref/sin.md)         | [`math.sin()`](https://docs.python.org/3.6/library/math.html#math.sin)              | the sine of the argument
[`tan()`](../../ref/tan.md)         | [`math.tan()`](https://docs.python.org/3.6/library/math.html#math.tan)              | the tangent of the argument
[`acos()`](../../ref/cos.md#acos)   | [`math.acos()`](https://docs.python.org/3.6/library/math.html#math.acos)            | the arc cosine of the argument
[`asin()`](../../ref/sin.md#asin)   | [`math.asin()`](https://docs.python.org/3.6/library/math.html#math.asin)            | the arc sine of the argument
[`atan()`](../../ref/tan.md#atan)   | [`math.atan()`](https://docs.python.org/3.6/library/math.html#math.atan)            | the arc tangent of the argument
[`ceiling()`](../../ref/ceiling.md) | [`math.ceil()`](https://docs.python.org/3.6/library/math.html#math.ceil)            | the smallest integer &ge; the argument
[`floor()`](../../ref/floor.md)     | [`math.floor()`](https://docs.python.org/3.6/library/math.html#math.floor)          | the largest integer &le; the argument
[`reciprocal()`](https://pyq.enlnt.com/reference/pyq-auto.html#pyq.q.reciprocal) |                                        | 1 divided by the argument

Other than being able to operate on lists of numbers, q functions differ from Python functions in the way they treat out-of-domain errors.

Where Python functions raise an exception,

```python
>>> math.log(0)
Traceback (most recent call last):
...
ValueError: math domain error
```

q functions return special values:

```python
>>> q.log([-1, 0, 1])
k('0n -0w 0')
```


#### The null function

Unlike Python, q allows division by zero. The reciprocal of zero is infinity, which shows up as `0w` or `0W` in displays.

```python
>>> q.reciprocal(0)
k('0w')
```

Multiplying infinity by zero produces a null value that generally indicates missing data

```python
>>> q.reciprocal(0) * 0
k('0n')
```

Null values and infinities can also appear as a result of applying a mathematical function to numbers outside of its domain:

```python
>>> q.log([-1, 0, 1])
k('0n -0w 0')
```

The `null()` function returns `1b` (boolean true) when given a null value and `0b` otherwise. For example, when applied to the output of the `log()` function from the previous example, it returns

```python
>>> q.null(_)
k('100b')
```


### Aggregation functions

Aggregation functions (also known as _reduction_ functions) are functions that given a sequence of atoms produce an atom. For example,

```python
>>> sum(range(10))
45
>>>  q.sum(range(10))
k('45')
```

q        | Python                   | Return
---------|--------------------------|-------------------------------------------------------
`sum()`  | `sum()`                  | the sum of the elements
`prd()`  |                          | the product of the elements
`all()`  | `all()`                  | `1b` if all elements are nonzero, `0b` otherwise
`any()`  | `any()`                  | `1b `if any of the elements is nonzero, `0b` otherwise
`min()`  | `min()`                  | the smallest element
`max()`  | `max()`                  | the largest element
`avg()`  | `statistics.mean()`      | the arithmetic mean
`var()`  | `statistics.pvariance()` | the population variance
`dev()`  | `statistics.pstdev()`    | the square root of the population variance
`svar()` | `statistics.variance()`  | the sample variance
`sdev()` | `statistics.stdev()`     | the square root of the sample variance



### Accumulation functions

Given a sequence of numbers, one may want to compute not just the sum total, but all the intermediate sums as well. In q, this can be achieved by applying the `sums` function to the sequence:

```python
>>> q.sums(range(10))
k('0 1 3 6 10 15 21 28 36 45')
```

q        | Return
---------|---------------------------------------------
`sums()` | the cumulative sums of the elements
`prds()` | the cumulative products of the elements
`maxs()` | the maximums of the prefixes of the argument
`mins()` | the minimums of the prefixes of the argument

There are no direct analogues of these functions in the Python standard library, but the `itertools.accumulate()` function provides similar functionality:

```python
>>> list(itertools.accumulate(range(10)))
[0, 1, 3, 6, 10, 15, 21, 28, 36, 45]
```

Passing `operator.mul()`, `max()` or `min()` as the second optional argument to `itertools.accumulate()`, one can get analogues of `q.prds()`, `q.maxs()` and `q.mins()`.


### Sliding window statistics

-    `mavg()`
-    `mcount()`
-    `mdev()`
-    `mmax()`
-    `mmin()`
-    `msum()`


### Uniform functions

Uniform functions are functions that take a list and return another list of the same size.

-   `reverse()`
-   `ratios()`
-   `deltas()`
-   `differ()`
-   `next()`
-   `prev()`
-   `fills()`


### Set operations

-   `except_()`
-   `inter()`
-   `union()`


### Sorting and searching

Functions `asc()` and `desc()` sort lists in ascending and descending order respectively:

```python
>>> a = [9, 5, 7, 3, 1]
>>> q.asc(a)
k('`s#1 3 5 7 9')
>>> q.desc(a)
k('9 7 5 3 1')
```

**Sorted attribute**

> The `s#` prefix that appears in the display of the output for the `asc()` function indicates that the resulting vector has a _sorted_>  attribute set. An attribute can be queried by calling the `attr()` function or accessing the `attr` property of the result:
> 
> ```python
> >>> s = q.asc(a) 
> >>> q.attr(s) k('s')
> >>> s.attr
> k('s')
> ```
> 
> When the`asc()` function gets a vector with the `s` attribute set, it skips sorting and immediately returns the same vector.

Functions `iasc()` and `idesc()` return the indices indicating the order in which the items of the incoming list should be arranged to be sorted.

```python
>>> q.iasc(a)
k('4 3 1 2 0')
```

Sorted lists can be searched efficiently using the `bin()` and `binr()` functions. As their names suggest, both use binary search to locate the position of an item equal to the search key; but where there is more than one such element, `binr()` returns the index of the first match while `bin()` returns the index of the last.

```python
>>> q.binr([10, 20, 20, 20, 30], 20)
k('1')
>>> q.bin([10, 20, 20, 20, 30], 20)
k('3')
```

When no item matches, `binr()` (`bin()`) returns the index of the position before (after) which the key can be inserted so that the list remains sorted.

```python
>>> q.binr([10, 20, 20, 20, 30], [5, 15, 20, 25, 35])
k('0 1 1 4 5')
>>> q.bin([10, 20, 20, 20, 30], [5, 15, 20, 25, 35])
k('-1 0 3 3 4')
```

In the Python standard library similar functionality is provided by the `bisect` module.

```python
>>> [bisect.bisect_left([10, 20, 20, 20, 30], key) for key in [5, 15, 20, 25, 35]]
[0, 1, 1, 4, 5]
>>> [-1 + bisect.bisect_right([10, 20, 20, 20, 30], key) for key in [5, 15, 20, 25, 35]]
[-1, 0, 3, 3, 4]
```

Note that while `binr()` and `bisect.bisect_left()` return the same values, `bin()` and `bisect.bisect_right()` are off by 1.

Q does not have a named function for searching an unsorted list because it uses the `?` operator for that. We can easily expose this functionality in PyQ as follows:

```python
>>> index = q('?')
>>> index([10, 30, 20, 40], [20, 25])
k('2 4')
```
Note that our home-brewed `index` function resembles the `list.index()` method, but it returns the one-after-last index when the key is not found, where `list.index()` raises an exception.

```python
>>> list.index([10, 30, 20, 40], 20)
2
>>> list.index([10, 30, 20, 40], 25)
Traceback (most recent call last):
  ...
ValueError: 25 is not in list
```

If you are not interested in the index, but want to know only whether the keys can be found in a list, you can use the `in_()` function:

```python
>>> q.in_([20, 25], [10, 30, 20, 40])
k('10b')
```

!!! note "Trailing underscore"

    The `q.in_`  function has a trailing underscore because otherwise it would conflict with the Python keyword `in`.


### From Python to kdb+

You can pass data from Python to kdb+ by assigning to `q` attributes. For example,

```python
>>> q.i = 42
>>> q.a = [1, 2, 3]
>>> q.t = ('Python', 3.5)
>>> q.d = {'date': date(2012, 12, 12)}
>>> q.value.each(['i', 'a', 't', 'd']).show()
42
1 2 3
(`Python;3.5)
(,`date)!,2012.12.12
```

Note that Python objects are automatically converted to kdb+ form when they are assigned in the `q` namespace, but when they are retrieved, Python gets a ‘handle’ to kdb+ data.

For example, passing an `int` to `q` results in

```python
>>> q.i
k('42')
```

If you want a Python integer instead, you have to convert explicitly.

```python
>>> int(q.i)
42
```

This will be covered in more detail in the next section.

You can also create kdb+ objects by calling `q` functions that are also accessible as `q` attributes. For example,

```python
>>> q.til(5)
k('0 1 2 3 4')
```

Some q functions don’t have names because q uses special characters. For example, to generate random data in q you should use the `?` operator. While PyQ does not supply a Python name for `?`, you can easily add it to your own toolkit:

```python
>>> rand = q('?')
```

And use it as you would any other Python function

```python
>>> x = rand(10, 2) # generates 10 random 0s or 1s (coin toss)
```


### From kdb+ to Python

In many cases your data is already stored in kdb+, and PyQ philosophy is that it should stay there. Rather than converting kdb+ objects to Python, manipulating Python objects and converting them back to kdb+, PyQ lets you work directly with kdb+ data as if it were already in Python.

For example, let us retrieve the release date from kdb+:

```python
>>> d1 = q('.z.k')
```

add 30 days to get another date

```python
>>> d2 = d1 + 30
```

and find the difference in whole weeks

```python
>>> (d2 - d1) % 7
k('2')
```

Note that the result of operations are (handles to) kdb+ objects. The only exceptions to this rule are indexing and iteration over simple kdb+ vectors. These operations produce Python scalars

```python
>>> list(q.a)
[1, 2, 3]
>>> q.a[-1]
3
```

In addition to Python operators, one invokes q functions on kdb+ objects directly from Python using the convenient attribute access / method call syntax.

For example

```python
>>> q.i.neg.exp.log.mod(5)
k('3f')
```

Note that the above is equivalent to

```python
>>> q.mod(q.log(q.exp(q.neg(q.i))), 5)
k('3f')
```

but shorter and closer to `q` syntax

```python
>>> q('(log exp neg i)mod 5')
k('3f')
```

The difference being that in q, functions are applied right to left, but in PyQ left to right.

Finally, if q does not provide the function you need, you can unleash the full power of numpy or scipy on your kdb+ data.

```python
>>> numpy.log2(q.a)
array([ 0.       , 1.        ,  1.5849625])
```

Note that the result is a numpy array, but you can redirect the output back to kdb+. To illustrate this, create a vector of 0s in kdb+

```python
>>> b = q.a * 0.0
```

and call a numpy function on one kdb+ object, redirecting the output to another:

```python
>>> numpy.log2(q.a, out=numpy.asarray(b))
```

The result of a numpy function is now in the kdb+ object.

```python
>>> b
k('0 1 1.584963')
```


### Working with files

Kdb+ uses the unmodified host file system to store data and therefore q has excellent support for working with files. Recall that we can send Python objects to kdb+ simply by assigning them to a `q` attribute:

```python
>>> q.data = range(10)
```

This code saves 10 integers in kdb+ memory and makes a global variable `data` available to kdb+ clients, but it does not save the data in any persistent storage. To save `data` as a file `data`, we can simply call the `pyq.q.save` function as follows:

```python
>>> q.save('data')
k(':data')
```

Note that the return value of the `pyq.q.save` function is a `K` symbol that is formed by pre-pending `:` to the file name. Such symbols are known as _file handles_ in q. Given a file handle, the kdb+ object stored in the file can be obtained by accessing the `value` property of the file handle.

```python
>>> _.value
k('0 1 2 3 4 5 6 7 8 9')
```

Now we can delete the data from memory

```python
>>> del q.data
```

and load it back from the file using the `pyq.q.load` function:

```python
>>> q.load('data')
k('data')
>>> q.data
k('0 1 2 3 4 5 6 7 8 9')
```

`pyq.q.save` and `pyq.q.load` functions can also take a `pathlib.Path` object

```python
>>> data_path = pathlib.Path('data')
>>> q.save(data_path)
k('`:data')
>>> q.load(data_path)
k('`data')
>>> data_path.unlink()
```

It is not necessary to assign data to a global variable before saving it to a file. We can save our 10 integers directly to a file using the `pyq.q.set` function

```python
>>> q.set(':0-9', range(10))
k(':0-9')
```

and read it back using the `pyq.q.get` function

```python
>>> q.get(_)
k('0 1 2 3 4 5 6 7 8 9')
```

```python
>>> pathlib.Path('0-9').unlink()
```


## K objects

The q language has has atoms (scalars), lists, dictionaries, tables and functions. In PyQ, kdb+ objects of any type appear as instances of class `K`. To tell the underlying kdb+ type, one can access the `type` property to obtain a type code. For example,

```python
>>> vector = q.til(5); scalar = vector.first
>>> vector.type
k('7h')
>>> scalar.type
k('-7h')
```

Basic vector types have type codes in the range 1 through 19 and their elements have the type code equal to the negative of the vector type code. For the basic vector types, one can also get a human-readable type name by accessing the `key` property.

```python
>>> vector.key k('long')
```

To get the same from a scalar, convert it to a vector first.

```python
>>> scalar.enlist.key
k('long')
```

code | kdb+ type   | Python type
-----|-------------|-------------------
1    | `boolean`   | [`bool`](https://docs.python.org/3.6/library/functions.html#bool)
2    | `guid`      | [`uuid.UUID`](https://docs.python.org/3.6/library/uuid.html#uuid.UUID)
4    | `byte`      |
5    | `short`     |
6    | `int`       |
7    | `long`      | [`int`](https://docs.python.org/3.6/library/functions.html#int)
8    | `real`      |
9    | `float`     | [`float`](https://docs.python.org/3.6/library/functions.html#float)
10   | `char`      | [`bytes`](https://docs.python.org/3.6/library/functions.html#bytes) (*)
11   | `symbol`    | [`str`](https://docs.python.org/3.6/library/stdtypes.html#str)
12   | `timestamp` | 
13   | `month`     |
14   | `date`      | [`datetime.date`](https://docs.python.org/3.6/library/datetime.html#datetime.date)
16   | `timespan`  | [`datetime.timedelta`](https://docs.python.org/3.6/library/datetime.html#datetime.timedelta)
17   | `minute`    |
18   | `second`    |
19   | `time`      | [`datetime.time`](https://docs.python.org/3.6/library/datetime.html#datetime.time)


(\*) Unlike other Python types mentioned in the table above, `bytes` instances get converted to a vector type.

```python
>>> K(b'x')
k(',"x"')
>>> q.type(_)
k('10h')
```

There is no scalar character type in Python, so to create a `K` character scalar, use a typed constructor:

```python
>>> K.char(b'x')
k('"x"')
```

Typed constructors are discussed in the next section.


### Constructors and casts

As we have seen in the previous chapter, it is seldom necessary to construct `K` objects explicitly, because they are created automatically whenever a Python object is passed to a q function. This is done by passing the Python object to the default `K` constructor.

For example, if you need to pass a long atom to a q function, you can use a Python int instead, but if a different integer type is required, you will need to create it explicitly.

```python
>>> K.short(1)
k('1h')
```

Since an empty list does not know its type, passing `[]` to the default `K` constructor produces a generic (type `0h`) list.

```python
>>> K([])
k('()')
>>> q.type(_)
k('0h')
```

To create an empty list of a specific type, pass `[]` to one of the named constructors.

```python
>>> K.time([])
k('`time$()')
```

constructor   | accepts                          | description
--------------|----------------------------------|-----------------------------------------------
`K.boolean()` | [`int`](https://docs.python.org/3.6/library/functions.html#int "in Python V3.6"), [`bool`](https://docs.python.org/3.6/library/functions.html#bool "in Python V3.6")               | logical type `0b` is false and `1b` is true
`byte()`      | [`int`](https://docs.python.org/3.6/library/functions.html#int "in Python V3.6"), [`bytes`](https://docs.python.org/3.6/library/functions.html#bytes "in Python V3.6")                              | 8-bit bytes
`short()`     | [`int`](https://docs.python.org/3.6/library/functions.html#int "in Python V3.6")                                                                                                                    | 16-bit integers
`int()`       | [`int`](https://docs.python.org/3.6/library/functions.html#int "in Python V3.6")                                                                                                                    | 32-bit integers
`long()`      | [`int`](https://docs.python.org/3.6/library/functions.html#int "in Python V3.6")                                                                                                                    | 64-bit integers
`real()`      | [`int`](https://docs.python.org/3.6/library/functions.html#int "in Python V3.6"), [`float`](https://docs.python.org/3.6/library/functions.html#float "in Python V3.6")                              | 32-bit floating point numbers
`float()`     | [`int`](https://docs.python.org/3.6/library/functions.html#int "in Python V3.6"), [`float`](https://docs.python.org/3.6/library/functions.html#float "in Python V3.6")                              | 32-bit floating point numbers
`char()`      | [`str`](https://docs.python.org/3.6/library/stdtypes.html#str "in Python V3.6"), [`bytes`](https://docs.python.org/3.6/library/functions.html#bytes "in Python V3.6")                               | 8-bit characters
`symbol()`    | [`str`](https://docs.python.org/3.6/library/stdtypes.html#str "in Python V3.6"), [`bytes`](https://docs.python.org/3.6/library/functions.html#bytes "in Python V3.6")                               | interned strings
`timestamp()` | [`int`](https://docs.python.org/3.6/library/functions.html#int "in Python V3.6") (nanoseconds), [`datetime`](https://docs.python.org/3.6/library/datetime.html#datetime.datetime "in Python V3.6")  | date and time
`month()`     | [`int`](https://docs.python.org/3.6/library/functions.html#int "in Python V3.6") (months), [`date`](https://docs.python.org/3.6/library/datetime.html#datetime.date "in Python V3.6")               | year and month
`date()`      | [`int`](https://docs.python.org/3.6/library/functions.html#int "in Python V3.6") (days), [`date`](https://docs.python.org/3.6/library/datetime.html#datetime.date "in Python V3.6")                 | year, month and day
`datetime()`  |                                                                                                                                                                                                     | (deprecated)
`timespan()`  | [`int`](https://docs.python.org/3.6/library/functions.html#int "in Python V3.6") (nanoseconds), [`timedelta`](https://docs.python.org/3.6/library/datetime.html#datetime.timedelta "in Python V3.6")| duration in nanoseconds
`minute()`    | [`int`](https://docs.python.org/3.6/library/functions.html#int "in Python V3.6") (minutes), [`time`](https://docs.python.org/3.6/library/datetime.html#datetime.time "in Python V3.6")              | duration or time of day in minutes
`second()`    | [`int`](https://docs.python.org/3.6/library/functions.html#int "in Python V3.6") (seconds), [`time`](https://docs.python.org/3.6/library/datetime.html#datetime.time "in Python V3.6")              | duration or time of day in seconds
`time()`      | [`int`](https://docs.python.org/3.6/library/functions.html#int "in Python V3.6") (milliseconds), [`time`](https://docs.python.org/3.6/library/datetime.html#datetime.time "in Python V3.6")         | duration or time of day in milliseconds

The typed constructors can also be used to access infinities and missing values of the given type.

```python
>>> K.real.na, K.real.inf
(k('0Ne'), k('0we'))
```

If you already have a `K` object and want to convert it to a different type, you can access the property named after the type name. For example,

```python
>>> x = q.til(5)
>>> x.date
k('2000.01.01 2000.01.02 2000.01.03 2000.01.04 2000.01.05')
```


### Operators

Both Python and q provide a rich system of operators. In PyQ, `K` objects can appear in many Python expressions where they often behave as native Python objects.

Most operators act on `K` instances as namesake q functions. For example:

```python
>>> K(1) + K(2)
k('3')
```


#### The if statement and boolean operators

Python has three boolean operators `or`, `and` and `not` and `K` objects can appear in boolean expressions. The result of a boolean expression depends on how the objects are tested in Python if-statements.

All `K` objects can be tested for ‘truth’. Similarly to the Python numeric types and sequences, `K` atoms of numeric types are true if they are not zero, and vectors are true if they are non-empty.

Atoms of non-numeric types follow different rules. Symbols test true except for the empty symbol; characters and bytes tested true except for the null character/byte; guid, timestamp, and (deprecated) datetime types always test as true.

Functions test as true, except for the monadic pass-through function:

```python
>>> q('::') or q('+') or 1
k('+')
```

Dictionaries and tables are treated as sequences: they are true if non-empty.

Note that in most cases how the object test does not change when Python native types are converted to `K`:

```python
>>> objects = [None, 1, 0, True, False, 'x', '', {1:2}, {}, date(2000, 1, 1)]
>>> [bool(o) for o in objects]
[False, True, False, True, False, True, False, True, False, True]
>>>[bool(K(o)) for o in objects]
[False, True, False, True, False, True, False, True, False, True]
```

One exception is the Python `time` type. Starting with version 3.5 all `time` instances test as true, but `time(0)` converts to `k('00:00:00.000')` which tests false:

```python
>>> [bool(o) for o in (time(0), K(time(0)))]
[True, False]
```

> Note: Python changed the rule for `time(0)` because `time` instances can be timezone-aware and because they do not support addition, making 0 less than special. Neither of those arguments apply to `q` time, second or minute data types which behave more like `timedelta`.


#### Arithmetic operations

Python has the four familiar arithmetic operators `+`, `-`, `*` and `/` as well as less common `**` (exponentiation), `%` (modulo) and `//` (floor division). PyQ maps those to q operators as follows

| operation      | Python | q      |
|----------------|:------:|:------:|
| addition       | `+`    | `+`    |
| subtraction    | `-`    | `-`    |
| multiplication | `*`    | `*`    |
| true division  | `/`    | `%`    |
| exponentiation | `**`   | `xexp` |
| floor division | `//`   | `div`  |
| modulo         | `%`    | `mod`  |

`K` objects can be freely mixed with Python native types in arithmetic expressions and the result is a `K` object in most cases:

```python
>>> q.til(10) % 3
k('0 1 2 0 1 2 0 1 2 0')
```

A notable exception occurs when the modulo operator is used for string formatting.

```python
>>> "%.5f" % K(3.1415)
'3.14150'
```

Unlike Python sequences, `K` lists behave very similarly to atoms: arithmetic operations act item-wise on them.

Compare

```python
>>> [1, 2] * 5
[1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
```

and

```python
>>> K([1, 2]) * 5
k('5 10')
```

or

```python
>>> [1, 2] + [3, 4]
[1, 2, 3, 4]
```

and

```python
>>> K([1, 2]) + [3, 4]
k('4 6')
```


#### The flip (`+`) operator

The unary `+` operator acts as the `flip()` function on `K` objects. Applied to atoms, it has no effect:

```python
>>> +K(0)
k('0')
```

but it can be used to transpose a matrix:

```python
>>> m = K([[1, 2], [3, 4]])
>>> m.show()
1 2
3 4
>>> (+m).show()
1 3
2 4
```

or turn a dictionary into a table:

```python
>>> d = q('!', ['a', 'b'], m)
>>> d.show()
a| 1 2
b| 3 4
>>> (+d).show()
a b
---
1 3
2 4
```


#### Bitwise operators

Python has six bitwise operators: `|`, `^`, `&`, `<<`, `>>`, and `~`. Since there are no bitwise operations in q, PyQ redefines them as follows:

operation | result                                             | note
:--------:|----------------------------------------------------| :---:
`x | y`   | element-wise maximum of `x` and `y`                | 1
`x ^ y`   | `y` with null elements filled with `x`             | 2
`x & y`   | element-wise minimum of `x` and `y`                | 1
`x << n`  | `x` shifted left by `n` elements                   | 3
`x >> n`  | `x` shifted right by `n` elements                  | 3
`~x`      | a boolean vector with 1s for zero elements of `x`  |

Notes:

1.   For boolean vectors, `|` and `&` are also item-wise _or_ and _and_ operations.

2.   For Python integers, the result of `x^y` is the bitwise exclusive
_or_. There is no similar operation in `q`, but for boolean vectors _exclusive or_ is equivalent to q `<>` (_not equal_).

3.   Negative shift counts result in a shift in the opposite direction to that indicated by the operator: `x >> -n` is the same as `x << n`.


##### Minimum and maximum

Minimum and maximum operators are `&` and `|` in q. PyQ maps similar-looking Python bitwise operators to the corresponding q ones:

```python
>>> q.til(10) | 5
k('5 5 5 5 5 5 6 7 8 9')
>>> q.til(10) & 5
k('0 1 2 3 4 5 5 5 5 5')
```


##### The `^` operator

Unlike Python, where caret (`^`) is the binary _xor_ operator, q defines it to denote the [fill](../../ref/fill.md) operation that replaces null values in the right argument with the left argument. PyQ follows the q definition:

```python
>>> x = q('1 0N 2') >>> 0 ^ x
k('1 0 2')
```


#### The `@` operator

Python 3.5 introduced the `@` operator, which can be used by user types. Unlike NumPy that defines `@` as the matrix-multiplication operator, PyQ uses `@` for function application and composition:

```python
>>> q.log @ q.exp @ 1
k('1f')
```


### Iterators

Iterators (formerly _adverbs_) in q are somewhat similar to Python decorators. They act on functions and produce new functions. The six iterators are summarized in the table below.

PyQ         | q    | description
------------|------|--------------------------------
`K.each()`  | `'`  | map or case
`K.over()`  | `/`  | reduce
`K.scan()`  | `\`  | accumulate
`K.prior()` | `':` | Each Prior
`K.sv()`    | `/:` | Each Right or scalar from vector
`K.vs()`    | `\:` | Each Left or vector from scalar

The functionality provided by the first three iterators is similar to functional programming features scattered throughout Python standard library.
Thus `each` is similar to [`map()`](https://docs.python.org/3.6/library/functions.html#map "in Python V3.6").
For example, given a list of lists of numbers

```python
>>> data = [[1, 2], [1, 2, 3]]
```

One can do

```python
>>> q.sum.each(data)
k('3 6')
```

or

```python
>>> list(map(sum, [[1, 2], [1, 2, 3]]))
[3, 6]
```

and get similar results.

The `over` iterator is similar to the [`functools.reduce()`](https://docs.python.org/3.6/library/functools.html#functools.reduce "in Python V3.6") function. Compare

```python
>>> q(',').over(data)
k('1 2 1 2 3')
```

and

```python
>>> functools.reduce(operator.concat, data)
[1, 2, 1, 2, 3]
```

Finally, the `scan` iterator is similar to the [`itertools.accumulate()`](https://docs.python.org/3.6/library/itertools.html#itertools.accumulate  "in Python V3.6") function.

```python
>>> q(',').scan(data).show()
1 2
1 2 1 2 3
```

```python
>>> for x in itertools.accumulate(data, operator.concat):
... print(x)
...
[1, 2] [1, 2, 1, 2, 3]
```


#### Each

The Each iterator serves double duty in q. When it is applied to a **function**, it derives a new [function](https://code.kx.com/q/ref/iterators) that expects lists as arguments and maps the original function over those lists. For example, we can write a ‘daily return’ function in q that takes yesterday’s price as the first argument `x`, today’s price as the second `y`, and dividend as the third `z` as follows:

```python
>>> r = q('{(y+z-x)%x}') # Recall that % is the division operator in q.
```

and use it to compute returns from a series of prices and dividends using `r.each`:

```python
>>> p = [50.5, 50.75, 49.8, 49.25]
>>> d = [.0, .0, 1.0, .0]
>>> r.each(q.prev(p), p, d)
k('0n 0.004950495 0.0009852217 -0.01104418')
```

When the Each iterator is applied to an **integer vector**, it derives a n-ary function that for each `i`<sup>th</sup> argument selects its `v[i]`<sup>th</sup> element. For example,

```python
>>> v = q.til(3)
>>> v.each([1, 2, 3], 100, [10, 20, 30])
k('1 100 30')
```

:point_right: 
[Case](https://code.kx.com/q/ref/maps#case) iterator

Note that atoms passed to `v.each` are treated as infinitely repeated values. Vector arguments must all be of the same length.


#### Over and scan

Given a function `f`, the derived functions `f.over` and `f.scan` are similar as both apply `f` repeatedly, but `f.over` returns only the final result, while `f.scan` returns all intermediate values as well.

For example, recall that the Golden Ratio can be written as a continued fraction as follows:

$$\phi = 1+\frac{1}{1+\frac{1}{1+\cdots}}$$

or equivalently as the limit of the sequence that can be obtained by starting with 1 and repeatedly applying the function

$$f(x) = 1+\frac{1}{x}$$

The numerical value of the Golden Ratio can be found as

$$\phi = \frac{1+\sqrt{5}}{2} \approx 1.618033988749895$$

```python
>>> phi = (1+math.sqrt(5)) / 2
>>> phi
1.618033988749895
```

Function $f$ can be written in q as follows:

```python
>>> f = q('{1+reciprocal x}')
```

and

```python
>>> f.over(1.)
k('1.618034')
```

indeed yields a number recognizable as the Golden Ratio. If instead of `f.over`, we compute `f.scan`, we will get the list of all convergents.

```python
>>> x = f.scan(1.)
>>> len(x)
32
```

Note that `f.scan` (and `f.over`) stop calculations when the next iteration yields the same value and indeed `f` applied to the last value returns the same value:

```python
>>> f(x.last) == x.last
True
```

which is close to the value computed using the exact formula

```python
>>> math.isclose(x.last, phi)
True
```

The number of iterations can be given explicitly by passing two arguments to `f.scan` or `f.over`:

```python
>>> f.scan(10, 1.)
k('1 2 1.5 1.666667 1.6 1.625 1.615385 1.619048 1.617647 1.618182 1.617978')
>>> f.over(10, 1.)
k('1.617978')
```

This is useful when you need to iterate a function that does not converge.

Continuing with the Golden Ratio theme, define a function

```python
>>> f = q('{(last x;sum x)}')
```

that, given a pair of numbers, returns another pair made out of the last and the sum of the numbers in the original pair. Iterating this function yields the Fibonacci sequence

```python
>>> x = f.scan(10,[0, 1])
>>> q.first.each(x)
k('0 1 1 2 3 5 8 13 21 34 55')
```

and the ratios of consecutive Fibonacci numbers form the sequence of Golden Ratio convergents that we have seen before:

```python
>>> q.ratios(_)
k('0 0w 1 2 1.5 1.666667 1.6 1.625 1.615385 1.619048 1.617647')
```


#### Each Prior

In the previous section we saw a function `ratios()` that takes a vector and returns the ratios between adjacent items. A similar function `deltas()` returns the differences between adjacent items.

```python
>>> q.deltas([1, 3, 2, 5])
k('1 2 -1 3')
```

These functions are in fact implemented in q by applying the `prior` iterator to the division (`%`) and subtraction functions respectively.

```python
>>> q.ratios == q('%').prior and q.deltas == q('-').prior
True
```

In general, for any binary function $f$ and a vector $v$

$$f.prior(v)=(f(v_1, v_0), f(v_2, v_1), ⋯)$$


#### Keywords `vs` and `sv`

> **`vs` and `sv`**
> 
> `K.vs` and `K.sv` correspond to q’s `vs` and `sv` and _also_ behave as the iterators Each Left and Each Right.

Of all the q keywords, these two have the most cryptic names and offer some non-obvious features.

To illustrate how `vs` and `sv` modify binary functions, let’s give a Python name to the q `,` operator:

```python
>>> join = q(',')
```

Suppose you have a list of file names

```python
>>> name = K.string(['one', 'two', 'three'])
```

and an extension

```python
>>> ext = K.string(".py")
```

You want to append the extension to each name on your list. If you naively call `join` on `name` and `ext`, the result will not be what you might expect:

```python
>>> join(name, ext)
k('("one";"two";"three";".";"p";"y")')
```

This happened because `join` treated `ext` as a list of characters rather than an atomic string and created a mixed list of three strings followed by three characters. What we need is to tell `join` to treat its first argument as a vector and the second as a scalar and this is exactly what the `vs` adverb will achieve:

```python
>>> join.vs(name, ext)
k('("one.py";"two.py";"three.py")')
```

The mnemonic rule is "vs" = "vector, scalar". (_Scalar_ is a synonym for _atom_.) Now, if you want to prepend a directory name to each resulting file, you can use the `sv` attribute:

```python
>>> d = K.string("/tmp/")
>>> join.sv(d, _)
k('("/tmp/one.py";"/tmp/two.py";"/tmp/three.py")')
```


### Input/output

```python
>>> import os
>>> r, w = os.pipe()
>>> h = K(w)(kp("xyz"))
>>> os.read(r, 100)
b'xyz'
>>> os.close(r); os.close(w)
```

Q variables can be accessed as attributes of the `q` object:

```python
>>> q.t = q('([]a:1 2i;b:xy)')
>>> sum(q.t.a)
3
>>> del q.t
```


## Numeric computing

NumPy is the fundamental package for scientific computing in Python. NumPy shares APL ancestry with q and can often operate directly on `K` objects.


### Primitive data types

There are eighteen primitive data types in kdb+. Eight closely match their NumPy analogues and will be called _simple types_ in this section. Simple types consist of booleans, bytes, characters, integers of three different sizes, and floating point numbers of two sizes. Seven kdb+ types  represent dates, times and durations. Similar data types are available in recent versions of NumPy, but they differ from kdb+ types in many details. Finally, kdb+ symbol, enum and guid types have no direct analogue in NumPy.

No  | kdb+ type | array type      | raw         | description
:--:|-----------|-----------------|-------------|-----------------------------------------------
1   | boolean   | bool_           | bool_       | Boolean (True or False) stored as a byte
2   | guid      | uint8 (x16)     | uint8 (x16) | Globally unique 16-byte identifier
4   | byte      | uint8           | uint8       | Byte (0 to 255)
5   | short     | int16           | int16       | Signed 16-bit integer
6   | int       | int32           | int32       | Signed 32-bit integer
7   | long      | int64           | int64       | Signed 64-bit integer
8   | real      | float32         | float32     | Single-precision 32-bit float
9   | float     | float64         | float64     | Double-precision 64-bit float
10  | char      | S1              | S1          | (byte-)string
11  | symbol    | str             | P           | Strings from a pool
12  | timestamp | datetime64[ns]  | int64       | Date and time with nanosecond resolution
13  | month     | datetime64[M]   | int32       | Year and month
14  | date      | datetime64[D]   | int32       | Date (year, month, day)
16  | timespan  | timedelta64[ns] | int64       | Time duration in nanoseconds
17  | minute    | datetime64[m]   | int32       | Time duration (or time of day) in minutes
18  | second    | datetime64[s]   | int32       | Time duration (or time of day) in seconds
19  | time      | datetime64[ms]  | int32       | Time duration (or time of day) in milliseconds
20+ | enum      | str             | int32       | Enumerated strings


#### Simple types

Kdb+ atoms and vectors of the simple types (booleans, characters, integers and floats) can be viewed as 0- or 1-dimensional NumPy arrays. For example,

```python
>>> x = K.real([10, 20, 30])
>>> a = numpy.asarray(x)
>>> a.dtype
dtype('float32')
```

Note that `a` in the example above is not a copy of `x`. It is an array view into the same data:

```python
>>> a.base.obj
k('10 20 30e')
```

If you modify `a`, you modify `x` as well:

```python
>>> a[:] = 88
>>> x
k('88 88 88e')
```


#### Dates, times and durations

The age-old question of when to start counting calendar years did not get any easier in the computer age. Python standard `date` starts at

```python
>>> date.min
datetime.date(1, 1, 1)
```

more commonly known as

```python
>>> date.min.strftime('%B %d, %Y')
'January 01, 0001'
```

and this date is considered to be day 1

```python
>>> date.min.toordinal()
1
```

Note that, according to the Python calendar, the world did not exist before that date:

```python
>>> date.fromordinal(0)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: ordinal must be >= 1
```

At the time of this writing,
```python
>>> date.today().toordinal()
736335
```

The designer of kdb+ made the more practical choice: date 0 is January 1, 2000. As a result, in PyQ we have

```python
>>> K.date(0)
k('2000.01.01')
```

and

```python
>>> (-2 + q.til(5)).date
k('1999.12.30 1999.12.31 2000.01.01 2000.01.02 2000.01.03')
```

Similarly, the 0 timestamp was chosen to be midnight of the day 0

```python
>>> K.timestamp(0)
k('2000.01.01D00:00:00.000000000')
```

With NumPy, however the third choice was made. Bowing to the UNIX tradition, NumPy took midnight of January 1, 1970 as the zero mark on its timescales.

```python
>>> numpy.array([0], 'datetime64[D]')
array(['1970-01-01'], dtype='datetime64[D]')
>>> numpy.array([0], 'datetime64[ns]')
array(['1970-01-01T00:00:00.000000000'], dtype='datetime64[ns]')
```

PyQ automatically adjusts the epoch when converting between NumPy arrays and `K` objects.

```python
>>> d = q.til(2).date
>>> a = numpy.array(d)
>>> d
k('2000.01.01 2000.01.02')
>>> a
array(['2000-01-01', '2000-01-02'], dtype='datetime64[D]')
>>> K(a)
k('2000.01.01 2000.01.02')
```

This convenience comes at the cost of copying the data.

```python
>>> a[0] = 0
>>> a array(['1970-01-01', '2000-01-02'], dtype='datetime64[D]')
>>> d
k('2000.01.01 2000.01.02')
```

To avoid such copying, `K` objects can expose their raw data to `numpy`.

```python
>>> b = numpy.asarray(d.data)
>>> b.tolist()
[0, 1]
```

Arrays created this way share their data with the underlying `K` objects. Any change to the array is reflected in kdb+.

```python
>>> b[:] += 42
>>> d
k('2000.02.12 2000.02.13')
```


#### Characters, strings and symbols

Text data appears in kdb+ as character atoms and strings or as symbols and enumerations. Character strings are compatible with the NumPy "bytes" type:

```python
>>> x = K.string("abc")
>>> a = numpy.asarray(x)
>>> a.dtype.type
<class 'numpy.bytes_'>
```

In the example above, data is shared between the kdb+ string `x` and the NumPy array `a`:

```python
>>> a[:] = 'x'
>>> x
k('"xxx"')
```


### Nested lists

Kdb+ does not have a datatype representing multi-dimensional contiguous arrays. In PyQ, a multi-dimensional NumPy array becomes a nested list when passed to `q` functions or converted to `K` objects. For example,

```python
>>> a = numpy.arange(12, dtype=float).reshape((2,2,3))
>>> x = K(a)
>>> x
k('((0 1 2f;3 4 5f);(6 7 8f;9 10 11f))')
```

Similarly, kdb+ nested lists of regular shape, become multi-dimensional NumPy arrays when passed to `numpy.array()`:

```python
>>> numpy.array(x)
array([[[ 0., 1., 2.],
        [ 3., 4., 5.]],

        [[ 6., 7., 8.],
         [ 9., 10., 11.]]])
```

Moreover, many NumPy functions can operate directly on kdb+ nested lists, but they internally create a contiguous copy of the data

```python
>>> numpy.mean(x, axis=2)
array([[ 1., 4.],
       [ 7., 10.]])
```


### Tables and dictionaries

Unlike kdb+, NumPy does not implement column-wise tables. Instead it has record arrays that can store table-like data row by row. PyQ supports two-way conversion between kdb+ tables and NumPy record arrays:

```python
>>> trades.show()
sym time  size
--------------
a   09:31 100
a   09:33 300
b   09:32 200
b   09:35 100
```

```python
>>> numpy.array(trades)
array([('a', datetime.timedelta(0, 34260), 100),
       ('a', datetime.timedelta(0, 34380), 300),
       ('b', datetime.timedelta(0, 34320), 200),
       ('b', datetime.timedelta(0, 34500), 100)],
      dtype=[('sym', 'O'), ('time', '<m8[m]'), ('size', '<i8')])
```


## Enhanced shell

If you have IPython installed in your environment, you can run an interactive IPython shell as follows:

```bash
pyq -m IPython
```

or use the `ipyq` script.

For a better experience, load the `pyq.magic` extension:

```python
In [1]: %load_ext pyq.magic
```

This makes K objects display nicely in the output and gives you access to the PyQ-specific IPython magic commands:

Line magic `%q`:

```python
In [2]: %q ([]a:til 3;b:10*til 3)
Out[2]:
a b
----
0 0
1 10
2 20
```

Cell magic `%%q`:

```python
In [4]: %%q
   ....: a: exec a from t where b=20
   ....: b: exec b from t where a=2
   ....: a+b
   ....:
Out[4]: ,22
```

You can pass following options to the `%%q` cell magic:

option              | effect
--------------------|--------------------------------------
`-l (dir|script)`   | pre-load database or script
`-h host:port`      | execute on the given host
`-o var`            | send output to a variable named `var`
`-i var1, .., varN` | input variables
`-1`                | redirect stdout
`-2`                | redirect stderr


## q) prompt

While in PyQ, you can drop in to an emulated kdb+ Command-Line Interface (CLI). Here is how:

Start PyQ:

```python
$ pyq
>>> from pyq import q
```

Enter kdb+ CLI:

```q
>>> q()
q)t:([]a:til 5; b:10*til 5)
q)t
a b
----
0 0
1 10
2 20
3 30
4 40
```

Exit back to Python:

```python
q)\
>>> print("Back to Python")
Back to Python
```

Or you can exit back to the shell:

```q
q)\\
$
```


## Calling Python from kdb+

Kdb+ is designed as a platform for multiple programming languages. 
Installing PyQ gives access to the p language, where "p" stands for "Python". In addition, PyQ provides a mechanism for exporting Python functions to q where they can be called as native q functions.


### The p language

To access Python from the `q)` prompt, simply start the line with the `p)` prefix and continue with the Python statement/s. Since the standard `q)` prompt does not allow multi-line entries, you are limited to what can be written in one line and need to separate Python statements with semicolons.

```python
q)p)x = 42; print(x)
42
```

The `p)` prefix can also be used in q scripts. In this case, multi-line Python statements can be used provided additional lines start with one or more spaces. For example, with the following code in `hello.q`

```q
p)def f():
      print('Hello')
p)f()
```

we get

```bash
$ q hello.q -q
Hello
```

If your script contains more Python code than q, you can avoid sprinkling it with `p)`s by placing the code in a file with `.p` extension. Thus instead of `hello.q` described above, we can write the following code in `hello.p`

```python
def f():
    print('Hello')
f()
q.exit(0)
```

and run it the same way:

```bash
$ q hello.p -q
Hello
```

It is recommended that any substantial amount of Python code be placed in regular Python modules or packages, with only top-level entry points imported and called in q scripts.


### Exporting Python functions to q

As we have seen in the previous section, calling Python by evaluating `p)` expressions has several limitations. For tighter integration between q and Python, PyQ supports exporting Python functions to q. Once exported, Python functions appear in q as unary functions that take a single argument that should be a list. For example, we can make Python’s `%`-formatting available in q as follows:

```python
>>> def fmt(f, x):
...     return K.string(str(f) % x)
>>> q.fmt = fmt
```

Now, calling the `fmt` function from q will pass the argument list to Python and return the result back to q:

```q
q)fmt("%10.6f";acos -1)
"  3.141593"
```

<!-- Python functions exported to q should return a `K` object or an instance of one of the simple scalar types: [`None`](https://docs.python.org/3.6/library/constants.html#None "(in Python v3.6)"), [`bool`](https://docs.python.org/3.6/library/functions.html#bool "(in Python v3.6)"), [`int`](https://docs.python.org/3.6/library/functions.html#int "(in Python v3.6)"), [`float`](https://docs.python.org/3.6/library/functions.html#float "(in Python v3.6)") or [`str`](https://docs.python.org/3.6/library/stdtypes.html#str "(in Python v3.6)") which are automatically converted to q `::`, boolean, long, float or symbol respectively.
 -->

When a Python function is called from q, the returned Python objects are automatically converted to q. Any type accepted by the `K()` constructor can be successfully converted. For example, the `numpy.eye` function returns a 2-D array with 1s on the diagonal and 0s elsewhere. It can be called from q as follows:

```q
q)p)import numpy
q)p)q.eye = numpy.eye
q)eye 3 4 1
0 1 0 0
0 0 1 0
0 0 0 1
```

Exported functions are called from q by supplying a single argument that contains a list of objects to be passed to the Python functions as `K`-valued arguments.

To pass a single argument to an exported function, it has to be enlisted. For example,

```q
q)p)q.erf = math.erf
q)erf enlist 1
0.8427008
```
