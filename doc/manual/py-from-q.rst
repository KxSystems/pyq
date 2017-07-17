------------------------
Calling Python from KDB+
------------------------

KDB+ is designed as a platform for multiple programming languages.  Out of the
box, it comes with q and K distributes variant of ANSI SQL as the
`"s)" language`_.  Installing pyq gives access to the "p)" language, where "p"
obviously stands for "Python".  In addition, PyQ provides a mechanism for
exporting Python functions to q where they can be called as native q functions.

.. _"s)" language: https://a.kx.com/q/s.k


The "p" language
----------------

To access Python from the ``q)`` prompt, simply start the line with the ``p)``
prefix and follow with the Python statement(s). Since the standard ``q)``
prompt does not allow multi-line entries, you are limited to what can be
written in one line and need to separate python statements with semicolons.

::

    q)p)x = 42; print(x)
    42

The ``p)`` prefix can also be used in q scripts.  In this case, multi-line
python statements can be used as long as additional lines start with one or
more spaces.  For example, with the following code in hello.q

::

   p)def f():
         print('Hello')
   p)f()


we get

::

    $ q hello.q -q
    Hello

If your script contains more python code than q, you can avoid sprinkling
it with ``p)``'s by placing the code in a file with .p extension.  Thus
instead of hello.q described above, we can write the following code in
hello.p

::

    def f():
        print('Hello')
    f()
    q.exit(0)

and run it the same way::

    $ q hello.p -q
    Hello


It is recommended that any substantial amount of Python code be placed in
regular python modules or packages with only top level entry points imported
and called in q scripts.

Exporting Python functions to q
-------------------------------

As we have seen in the previous section, calling python by evaluating "p)"
expressions has several limitations.  For tighter integration between q and
Python, pyq supports exporting Python functions to q.  Once exported, python
functions appear in q as monadic functions that take a single argument that
should be a list.  For example, we can make Python's ``%``-formatting
available in q as follows:

>>> def fmt(f, x):
...     return K.string(str(f) % x)
>>> q.fmt = fmt

Now, calling the ``fmt`` function from q will pass the argument list to Python
and return the result back to q:

::

    q)fmt("%10.6f";acos -1)
    "  3.141593"


Python functions exported to q should return a :class:`~pyq.K` object or an instance
of one of the simple scalar types: :data:`None`, :class:`bool`, :class:`int`,
:class:`float` or :class:`str` which are automatically converted to q ``::``, boolean,
long, float or symbol respectively.

Exported functions are called from q by supplying a single argument that contains a
list of objects to be passed to the Python functions as :class:`~pyq.K`-valued arguments.

.. note::

   To pass a single argument to an exported function, it has to be enlisted.  For example,

::

   q)p)q.erf = math.erf
   q)erf enlist 1
   0.8427008
