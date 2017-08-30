Installing 32-bit PyQ with the free 32-bit kdb+ and Python 3.6 on 64-bit CentOS 7
---------------------------------------------------------------------------------

.. note::

    This guide was designed for installing Python 3.6. If you're looking to
    use Python 2.7, you can follow this guide by replacing ``3.6.0`` with ``2.7.13``
    where necessary.



1. Install development tools and libraries required to build 32-bit Python
..........................................................................

.. code-block:: bash

    $ sudo yum install gcc gcc-c++ rpm-build subversion git zip unzip bzip2 \
      libgcc.i686 glibc-devel.i686 glibc.i686 zlib-devel.i686 \
      readline-devel.i686 gdbm-devel.i686 openssl-devel.i686 ncurses-devel.i686 \
      tcl-devel.i686 libdb-devel.i686 bzip2-devel.i686 sqlite-devel.i686 \
      tk-devel.i686 libpcap-devel.i686 xz-devel.i686 libffi-devel.i686


2. Download, compile and install the 32-bit version of Python 3.6.0
...................................................................

We are going to install Python 3.6 into ``/opt/python3.6.i686``:

.. code-block:: bash

    $ mkdir -p ${HOME}/Archive ${HOME}/Build
    $ sudo mkdir -p /opt/python3.6.i686
    $ curl -Ls http://www.python.org/ftp/python/3.6.0/Python-3.6.0.tgz \
      -o ${HOME}/Archive/Python-3.6.0.tgz
    $ tar xzvf ${HOME}/Archive/Python-3.6.0.tgz -C ${HOME}/Build
    $ cd ${HOME}/Build/Python-3.6.0
    $ export CFLAGS=-m32 LDFLAGS=-m32
    $ ./configure --prefix=/opt/python3.6.i686 --enable-shared
    $ LD_RUN_PATH=/opt/python3.6.i686/lib make
    $ sudo make install
    $ unset CFLAGS LDFLAGS

Let's confirm we have a 32-bit Python on our 64-bit system:

.. code-block:: bash

    $ uname -mip
    x86_64 x86_64 x86_64
    $ /opt/python3.6.i686/bin/python3.6 \
      -c "import platform; print(platform.processor(), platform.architecture())"
    x86_64 ('32bit', 'ELF')

Yes, it is exactly what we desired.

3. Install virtualenv into Python installation
..............................................

We are going to use virtual environments, download and extract virtualenv package:

.. code-block:: bash

    $ curl -Ls https://pypi.org/packages/source/v/virtualenv/virtualenv-15.1.0.tar.gz \
      -o ${HOME}/Archive/virtualenv-15.1.0.tar.gz
    $ tar xzf ${HOME}/Archive/virtualenv-15.1.0.tar.gz -C ${HOME}/Build

4. Create 32-bit Python virtual environment
...........................................

Create a virtual environment:

.. code-block:: bash

    $ /opt/python3.6.i686/bin/python3.6 ${HOME}/Build/virtualenv-15.1.0/virtualenv.py \
      ${HOME}/Work/pyq3

Enter the virtual environment that we created, confirm that we have a 32-bit Python there:

.. code-block:: bash

    (pyq3) $ source ${HOME}/Work/pyq3/bin/activate
    (pyq3) $ python -c "import struct; print(struct.calcsize('P') * 8)"
    32

5. Download the 32-bit Linux x86 version of kdb+ from kx.com
............................................................

Download `kdb+ by following this link <https://kx.com/download/>`_.

Save downloaded file as  `${HOME}/Work/linux-x86.zip`.

6. Extract kdb+ and install PyQ
...............................

Extract downloaded file:

.. code-block:: bash

    (pyq3) $ unzip ${HOME}/Work/linux-x86.zip -d ${VIRTUAL_ENV}


Install PyQ (note, PyQ 3.8.2 or newer required):

.. code-block:: bash

    (pyq3) $ pip install -i https://pyq.enlnt.com --no-binary pyq pyq>=3.8.2


6. Use PyQ
..........

Start PyQ:

.. code-block:: bash

    (pyq3) $ pyq

.. code-block:: python

    >>> import platform
    >>> platform.processor()
    'x86_64'
    >>> platform.architecture()
    ('32bit', 'ELF')
    >>> from pyq import q
    >>> q.til(10)
    k('0 1 2 3 4 5 6 7 8 9')
