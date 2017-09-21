.. _install:

Installation
============

PyQ can be installed using the standard Python package management tool - pip.
See `Installing Python Modules <https://docs.python.org/3/installing>`_ for details.
To install the latest version, run the following command

::

    $ pip install -i https://pyq.enlnt.com --no-binary pyq pyq

.. _pre:

Prerequisites
-------------

OS Support
..........


PyQ has been tested and is supported on Linux and macOS 10.11 or later.

PyQ has support for Solaris, but has not been tested recently.

Windows is not supported yet.

Required Software
.................

* `kdb+ 2.8 <https://kx.com/discover/>`_ or later;
* Python 2.7, or 3.5 or later;
* GNU make, gcc or clang.

Installing from the package repository
--------------------------------------

Use following pip command to install the latest version of PyQ into your environment.

::

    $ pip install -i https://pyq.enlnt.com --no-binary pyq pyq

To install another version, specify which version you would like to install:

::

    $ pip install -i https://pyq.enlnt.com --no-binary pyq pyq==3.8


Installing from source code
---------------------------

1. Get the source code using one of the following:

    * Clone the Github repository

         ::

            $ git clone https://github.com/enlnt/pyq.git

    * Download the source archive as a `tar file <https://github.com/enlnt/pyq/archive/master.tar.gz>`_
      or a `zip file <https://github.com/enlnt/pyq/archive/master.zip>`_ and extract it.

2. Install the sources into your environment using pip::

        $ pip install <path to the source>



Installing PyQ into a virtual environment
-----------------------------------------

PyQ was designed to work inside virtual environments.
You can setup your system to use different versions of Python and/or kdb+ by using separate virtual environments.

In order to create a virtual environment, you need to install the `virtualenv <https://virtualenv.pypa.io/en/stable/installation/>`_ package:

::

    $ [sudo] pip install virtualenv

Create a new virtualenv and activate it:

::

    $ virtualenv path/to/virtualenv
    $ source path/to/virtualenv/bin/activate

Download `kdb+ <https://kx.com/download/>`_ and save into your ``~/Downloads`` folder. Extract it into virtualenv:

::

    $ unzip ${HOME}/Downloads/macosx.zip -d ${VIRTUAL_ENV}

If you have licensed version of the kdb+, you should create directory for it first:

::

    $ mkdir -p ${VIRTUAL_ENV}/q && unzip path/to/m64.zip -d ${VIRTUAL_ENV}/q

Copy your kdb+ license file to ``${VIRTUAL_ENV}/q`` or set the ``QLIC`` environment variable to the directory
containing the license file and add it to the virtualenv's ``activate`` file:

::

    $ echo "export QLIC=path/to/qlic" >> ${VIRTUAL_ENV}/bin/activate
    $ source ${VIRTUAL_ENV}/bin/activate

Install PyQ:

::

    $ pip install -i https://pyq.enlnt.com --no-binary pyq pyq


.. _update:

.. include:: update.rst

.. include:: centos32on64.rst

.. include:: ubuntu.rst

.. include:: macos.rst
