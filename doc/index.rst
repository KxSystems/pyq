.. PyQ documentation master file, created by
   sphinx-quickstart on Thu Mar 24 12:35:50 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

%%%
PyQ
%%%

PyQ brings the `Python programming language`_ to the `kdb+ database`_. It allows
developers to seamlessly integrate Python and q codes in one application.
This is achieved by bringing the Python and q interpreters in the same process
so that codes written in either of the languages operate on the same data.
In PyQ, Python and q objects live in the same memory space and share the same
data.

.. _Python programming language: https://www.python.org/about
.. _kdb+ database: https://kx.com


Quick start
-----------

.. sidebar:: Install pyq

   Don't have pyq installed?  Run

   .. code-block:: bash

      $ pip install \
        -i https://pyq.enlnt.com \
        --no-binary pyq pyq

First, make sure that PyQ is :ref:`installed <install>` and :ref:`up-to-date <update>`.
Start an interactive session::

    $ pyq

Import the :const:`~pyq.q` object from :mod:`pyq` and the :class:`~datetime.date` class from the standard library
module :mod:`datetime`:

>>> from pyq import q
>>> from datetime import date

Drop to the :ref:`q) prompt <q_prompt>` and create an empty ``trade`` table::

    >>> q()  # doctest: +SKIP
    q)trade:([]date:();sym:();qty:())

Get back to the Python prompt and insert some data into the ``trade`` table::

    q)\
    >>> q.insert('trade', (date(2006,10,6), 'IBM', 200))
    k(',0')
    >>> q.insert('trade', (date(2006,10,6), 'MSFT', 100))
    k(',1')

(In the following we will skip ``q()`` and ``\`` commands that switch between ``q`` and Python.)

Display the result::

    >>> q.trade.show()
    date       sym  qty
    -------------------
    2006.10.06 IBM  200
    2006.10.06 MSFT 100

Define a function in ``q``::

    q)f:{[s;d]select from trade where sym=s,date=d}

Call the ``q`` function from python and pretty-print the result::

    >>> x = f('IBM', date(2006,10,6))
    >>> x.show()
    date       sym qty
    ------------------
    2006.10.06 IBM 200


For an enhanced interactive shell, use ``pyq`` to start IPython::

    $ pyq -m IPython

See the :ref:`ipython section <ipython>` for details.

..  toctree::
    :hidden:
    :maxdepth: 4
    :caption: Table of Contents
    :name: mastertoc

    whatsnew/4.1
    whatsnew/4.0
    install/install
    User Guide <manual/pyq>
    reference/pyq-auto
    whatsnew/changelog
    License <license/index>

Navigation
----------

* :ref:`genindex`
* :ref:`search`

