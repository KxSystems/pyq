.. _install:

Installation
============

OS Support
----------

PyQ has been tested and is supported on Linux and OS X 10.10 or later.

PyQ has support for Solaris, but has not been tested recently.

Windows is not supported yet.

Prerequisites
-------------

* `kdb+ 3.1 <https://kx.com/purchasesoftware.php>`_ or later;
* Python 2.7, or 3.4 or later;
* GNU make, gcc or clang.

Using pip
---------

Use following pip command to install PyQ into your environment.

::

    pip install -i https://pyq.enlnt.com --no-binary pyq pyq

You can specify which version you would like to install:

::

    pip install -i https://pyq.enlnt.com --no-binary pyq pyq==3.8


Using source code
-----------------

1. Get the source code:

    * You can clone the repository

         ::

            git clone https://github.com/enlnt/pyq.git

    * Download the `tar file <https://github.com/enlnt/pyq/archive/master.tar.gz>`_:: or  `zip file <https://github.com/enlnt/pyq/archive/master.zip>`_:: and extract it.

2. You can now install into your environment:

    ::

        $ python setup.py install

