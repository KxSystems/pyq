.. PyQ documentation master file, created by
   sphinx-quickstart on Thu Mar 24 12:35:50 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
============

PyQ provides seamless integration of Python and Q code. It brings Python and Q interpretors in the same
process and allows code written in either of the languages to operate on the same data. In PyQ, Python and
Q objects live in the same memory space and share the same data.



Quickstart
----------

First, make sure that PyQ is :ref:`installed <install>` and :ref:`up-to-date <update>`.

Start interactive session:

::

    $ pyq
    >>> from pyq import q
    >>> from datetime import date

Create an empty table:

::

    >>> q.trade = q('([]date:();sym:();qty:())')

Insert sample data:

::

    >>> q.insert('trade', (date(2006,10,6), 'IBM', 200))
    k(',0')
    >>> q.insert('trade', (date(2006,10,6), 'MSFT', 100))
    k(',1')

Display the result:

::

    >>> q.trade.show()
    date       sym  qty
    -------------------
    2006.10.06 IBM  200
    2006.10.06 MSFT 100

Define a parameterized query:

::

    >>> query = q('{[s;d]select from trade where sym=s,date=d}')

Run a query:

::

    >>> query('IBM', date(2006,10,6))
    k('+`date`sym`qty!(,2006.10.06;,`IBM;,200)')

Pretty print the result:

::

    >>> query('IBM', date(2006,10,6)).show()
    date       sym qty
    ------------------
    2006.10.06 IBM 200





Table of Contents
-----------------

..  toctree::
    :titlesonly:
    :maxdepth: 4

    install
    update
    pyq
    jupyter
    cli
    centos32on64
    CHANGES
    license

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

