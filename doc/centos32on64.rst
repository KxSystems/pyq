Installing 32-bit PyQ with the free 32-bit kdb+ on 64-bit CentOS 7
==================================================================

1. Install development tools and libraries required to build 32-bit Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


::

    $ sudo yum install gcc gcc-c++ rpm-build subversion git zip unzip bzip2 wget
    $ sudo yum install libgcc.i686 glibc-devel.i686 glibc.i686 zlib-devel.i686 readline-devel.i686 \
      gdbm-devel.i686 openssl-devel.i686 ncurses-devel.i686 tcl-devel.i686 libdb-devel.i686 bzip2-devel.i686 \
      sqlite-devel.i686 tk-devel.i686 libpcap-devel.i686 xz-devel.i686 libffi-devel.i686


2. Download, compile and install the 32-bit version of Python 2.7.12
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We are going to install Python 2.7.12 into `/opt/python2.i686`.

::

    $ mkdir -p ${HOME}/Archive ${HOME}/Build
    $ sudo mkdir -p /opt/python2.i686
    $ wget http://www.python.org/ftp/python/2.7.12/Python-2.7.12.tgz -O ${HOME}/Archive/Python-2.7.12.tgz
    $ tar xzvf ${HOME}/Archive/Python-2.7.12.tgz -C ${HOME}/Build
    $ cd ${HOME}/Build/Python-2.7.12
    $ export CFLAGS=-m32 LDFLAGS=-m32
    $ ./configure --prefix=/opt/python2.i686 --enable-shared | tee c.log
    $ LD_RUN_PATH=/opt/python2.i686/lib make | tee m.log
    $ sudo make install |tee i.log
    $ unset CFLAGS LDFLAGS

Let's confirm we've got 32-bit Python on our 64-bit system:

::

    $ uname -mip
    x86_64 x86_64 x86_64
    $ /opt/python2.i686/bin/python -c "import platform; print(platform.processor(), platform.architecture())"
    ('x86_64', ('32bit', 'ELF'))

Yes, it is exactly what we desired.

3. Install virtualenv into Python installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We are going to use virtualenv. Let's install it together with pip, setuptools and wheel into Python installation to make things easier.

::

    $ sudo /opt/python2.i686/bin/python -mensurepip
    $ sudo /opt/python2.i686/bin/python -mpip install -U pip setuptools virtualenv wheel


4. Create 32-bit Python virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create virtual environment:

::

    $ /opt/python2.i686/bin/virtualenv ${HOME}/Work/pyq


Define `QHOME` in the new virtuale nvironment:

::

    $ echo 'export QHOME=${VIRTUAL_ENV}/q' >> ${HOME}/Work/pyq/bin/activate


Enter virtualenvironment we've just created, confirm we've got 32-bit Python in it:

::

    $ source ${HOME}/Work/pyq/bin/activate
    $ python -c "import struct; print(struct.calcsize('P') * 8)"
    32

5. Download the 32-bit Linux x86 version of kdb+ from kx.com
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download `kdb+ by following this link <http://kx.com/software-download.php>`_.

Save downloaded file as  `${HOME}/Work/linux-x86.zip`.

6. Extract kdb+ and install PyQ
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extract downloaded file:

::

    $ unzip ${HOME}/Work/linux-x86.zip -d ${VIRTUAL_ENV}


Install PyQ (note, PyQ 3.8.2 or newer required):

::

    $ pip install -i https://pyq.enlnt.com --no-binary pyq pyq>=3.8.2


6. Use PyQ
~~~~~~~~~~

Start PyQ:

::

    $ pyq
    >>> import platform
    >>> platform.processor()
    'x86_64'
    >>> platform.architecture()
    ('32bit', 'ELF')
    >>> from pyq import q
    >>> q.til(10)
    k('0 1 2 3 4 5 6 7 8 9')
