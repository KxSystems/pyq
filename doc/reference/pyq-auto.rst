.. testsetup::

   from pyq import *
   from datetime import date
   import numpy

Reference Manual
----------------

(This section is generated from the PyQ source code.  You can access most of this
material using pydoc or the built-in help method.)

.. currentmodule:: pyq

.. autosummary::

   K
   q


class K
.......

.. autoclass:: K
   :members: exec, select, show, update, __call__, __getitem__,
              __getattr__, __int__, __float__, __eq__, __contains__, __get__, keys


.. include:: K-meths.rst

namespace q
...........

.. data:: q

.. automethod:: q.__call__

   When called without arguments in an interactive session, ``q()``
   presents a ``q)`` prompt where user can interact with kdb+ using
   q language commands.

   The first argument to that may be given to ``q()`` should be a string
   containing a q language expression.  If that expression evaluates to
   a function, the arguments to this function can be provided as additional
   arguments to ``q()``.

   For example, the following passes a list and a number to the q ``?`` (find)
   function:

   >>> q('?', [1, 2, 3], 2)
   k('1')

Q functions
...........

.. include:: q-funcs.rst

.. .. automodule:: pyq
   :members: k, d9, kp
   :exclude-members: q, K


.. autoexception:: kerr

