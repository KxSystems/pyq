# ![PyQ](img/pyq.png)  Installation


PyQ can be installed using the standard Python package management tool `pip`.

:point_right: [Installing Python Modules](https://docs.python.org/3/installing/)

To install the latest version, run the following command

```bash
pip install pyq
```

> Tip: Extras
> 
> For the best experience with PyQ, you should also install some third-party
> packages such as NumPy and IPython.  The extra packages recommended by
> the PyQ developers can be installed using the `pip install pyq[all]`
> command.


## Requirements

&nbsp; | &nbsp;
-------|---------
operating system | :fontawesome-brands-linux: Linux or :fontawesome-brands-apple: macOS 10.11+<br><br>Solaris is supported, but has not been tested recently.<br><br>:fontawesome-brands-windows: Windows is [supported as an experiment](#installing-on-windows)
kdb+ | V2.8+ :fontawesome-solid-download: [Download](https://kx.com/download/) :fontawesome-regular-hand-point-right: [Install](../../learn/install.md)
Python | 2.7 or 3.5+ :fontawesome-solid-download: [Download](https://www.python.org/downloads/)
compiler |`gcc` or `clang`


## Installing from the package repository

Use the following `pip` command to install the latest version of PyQ into your environment.

```bash
pip install pyq
```
To install another version, specify which version you would like to install:

```bash
pip install pyq==4.1.2
```


## Install from source code

Get the source code:

-   GitHub

    Clone the repository:

    ```bash
    git clone https://github.com/kxsystems/pyq.git
    ```

-   Download

    Download the source archive as a [tar file](../archive/master.tar.gz) or a [ZIP file](../archive/master.zip) and extract it.

Install the sources into your environment using Pip:

```bash
pip 0install path-to-the-source
```


## Install into a virtual environment

PyQ was designed to work inside virtual environments. You can set up your system to use different versions of Python and/or kdb+ by using separate virtual environments.

To create a virtual environment, you need to install the [virtualenv](https://virtualenv.pypa.io/en/stable/installation.html) package:

```bash
[sudo] pip install virtualenv
```

Create a new virtualenv and activate it:

```bash
virtualenv path/to/virtualenv
source path/to/virtualenv/bin/activate
```

Download [kdb+](https://kx.com/download/) and save into your `~/Downloads` folder. Extract it into `virtualenv`:

```bash
unzip ${HOME}/Downloads/macosx.zip -d ${VIRTUAL_ENV}
```

If you have a license for kdb+, create a directory for it first:

```bash
mkdir -p ${VIRTUAL_ENV}/q && unzip path/to/m64.zip -d ${VIRTUAL_ENV}/q
```

Copy your kdb+ license file to `${VIRTUAL_ENV}/q` or set the `QLIC` environment variable to the directory containing the license file and add it to the virtualenv's `activate` file:

```bash
echo "export QLIC=path/to/qlic" >> ${VIRTUAL_ENV}/bin/activate
source ${VIRTUAL_ENV}/bin/activate
```

Install PyQ:

```bash
pip install pyq
```



## Install 32-bit PyQ with 32-bit kdb+ on 64-bit CentOS&nbsp;7

> Tip: Python 2.7
> 
> This guide is for installing Python 3.6.
> 
> To use Python 2.7, replace `3.6.0` with `2.7.13` where necessary.


1.  Install the development tools and libraries to build 32-bit Python

    ```bash
    sudo yum install gcc gcc-c++ rpm-build subversion git zip unzip bzip2 \
    libgcc.i686 glibc-devel.i686 glibc.i686 zlib-devel.i686 \
    readline-devel.i686 gdbm-devel.i686 openssl-devel.i686 ncurses-devel.i686 \
    tcl-devel.i686 libdb-devel.i686 bzip2-devel.i686 sqlite-devel.i686 \
    tk-devel.i686 libpcap-devel.i686 xz-devel.i686 libffi-devel.i686
    ```

2.  Download, compile and install 32-bit Python 3.6.0 into `/opt/python3.6.i686`

    ```bash
    mkdir -p ${HOME}/Archive ${HOME}/Build
    sudo mkdir -p /opt/python3.6.i686
    curl -Ls http://www.python.org/ftp/python/3.6.0/Python-3.6.0.tgz \
      -o ${HOME}/Archive/Python-3.6.0.tgz
    tar xzvf ${HOME}/Archive/Python-3.6.0.tgz -C ${HOME}/Build
    cd ${HOME}/Build/Python-3.6.0
    export CFLAGS=-m32 LDFLAGS=-m32
    ./configure --prefix=/opt/python3.6.i686 --enable-shared
    LD_RUN_PATH=/opt/python3.6.i686/lib make
    sudo make install
    unset CFLAGS LDFLAGS
    ```

    Let’s confirm we have 32-bit Python on our 64-bit system

    ```bash
    $ uname -mip
    x86_64 x86_64 x86_64
    $ /opt/python3.6.i686/bin/python3.6 \
      -c "import platform; print(platform.processor(), platform.architecture())"
    x86_64 ('32bit', 'ELF')
    ```

    Yes, exactly what we wanted.

3.  We are going to use virtual environments, so download, extract, and install virtualenv

    ```bash
    curl -Ls https://pypi.org/packages/source/v/virtualenv/virtualenv-15.1.0.tar.gz \
      -o ${HOME}/Archive/virtualenv-15.1.0.tar.gz
    tar xzf ${HOME}/Archive/virtualenv-15.1.0.tar.gz -C ${HOME}/Build
    ```

4.  Create a 32-bit Python virtual environment; first, create a virtual environment:

    ```bash
    /opt/python3.6.i686/bin/python3.6 ${HOME}/Build/virtualenv-15.1.0/virtualenv.py \
      ${HOME}/Work/pyq3
    ```

    Enter the new virtual environment, confirm you have 32-bit Python there:

    ```bash
    (pyq3) $ source ${HOME}/Work/pyq3/bin/activate
    (pyq3) $ python -c "import struct; print(struct.calcsize('P') * 8)"
    32
    ```

5.  Download the 32-bit Linux x86 version of kdb+ from [kx.com](https://kx.com/download/) and save it as `${HOME}/Work/linux-x86.zip`.


6.  Extract and install kdb+

    ```bash
    (pyq3) $ unzip ${HOME}/Work/linux-x86.zip -d ${VIRTUAL_ENV}
    ```

7.  Install PyQ 3.8.2 or newer

    ```bash
    (pyq3) $ pip install pyq>=3.8.2
    ```

8.  Start PyQ

    ```bash
    (pyq3) $ pyq
    ```

    ```python
    >>> import platform
    >>> platform.processor()
    'x86_64'
    >>> platform.architecture()
    ('32bit', 'ELF')
    >>> from pyq import q
    >>> q.til(10)
    k('0 1 2 3 4 5 6 7 8 9')
    ```


## Install on Ubuntu 16.04

Since Python provided by Ubuntu is statically linked, shared libraries need to be installed before PyQ can be installed.

### Python 2

Install shared libraries:

```bash
sudo apt-get install libpython-dev libpython-stdlib python-pip python-virtualenv
```

Create and activate virtual environment:

```bash
python -m virtualenv -p $(which python2) py2
source py2/bin/activate
```

Install PyQ:

```bash
(py2) $ pip install pyq
```

### Python 3

Install shared libraries:

```bash
sudo apt-get install libpython3-dev libpython3-stdlib python3-pip python3-virtualenv
```

Create and activate virtual environment:

```bash
python3 -m virtualenv -p $(which python3) py3
source py3/bin/activate
```

Install PyQ:

```bash
(py3) $ pip3 install pyq
```



## Install with 32-bit kdb+ on macOS

To use PyQ with the free 32-bit kdb+ on macOS, you need a 32-bit version of Python.

> **Python installed on macOS**
> 
> MacOS Sierra and High Sierra ship with a universal version of Python 2.7.10.


### System Python 2

Install the `virtualenv` module:

```bash
pip install virtualenv
```

If your system, does not have `pip` installed, follow [`pip` installation guide](https://pip.pypa.io/en/stable/installing/).

Create and activate a virtual environment:

```bash
virtualenv ${HOME}/pyq2
source ${HOME}/pyq2/bin/activate
```

[Download kdb+](https://kx.com/download/) and save the downloaded file as `${HOME}/Downloads/macosx.zip`.

Install kdb+ and PyQ:

```bash
(pyq2) $ unzip ${HOME}/Downloads/macosx.zip -d ${VIRTUAL_ENV}
(pyq2) $ pip install pyq
```

PyQ is ready and can be launched:

```bash
(pyq2) $ pyq
```


### Brew Universal Python

To use the latest version of Python 2.7 or Python 3, install it using the package manager Homebrew.

1.  Install [Homebrew](https://brew.sh/).

1.  Install universal Python 2.7 and Python 3.6:

    ```bash
    brew install --universal sashkab/python/python27 sashkab/python/python36
    ```

1.  Install the virtualenv package.

    ```bash
    /usr/local/opt/pythonXY/bin/pythonX -mpip install -U virtualenv
    ```

    `X` is the major version of the Python; `Y` the minor, i.e. 2.7 or 3.6.

1.  Create a new virtual environment and activate it:

    ```bash
    /usr/local/opt/pythonXY/bin/pythonX -mvirtualenv -p /usr/local/opt/pythonXY/bin/pythonX ${HOME}/pyq
    source ${HOME}/pyq/bin/activate
    ```

1.  Download [kdb+ by following this link](https://kx.com/download/) and save the downloaded file as `${HOME}/Downloads/macosx.zip`.

1.  Install kdb+ and PyQ:

    ```bash
    (pyq) $ unzip ${HOME}/Downloads/macosx.zip -d ${VIRTUAL_ENV}
    (pyq) $ pip install pyq
    ```

PyQ is ready and can be launched:

```bash
(pyq2) $ pyq
```



## Install on Windows

PyQ 4.1.0 introduced **experimental support** for Windows.

Requirements are:

-   Installation should be started using the Windows Command Prompt.
-   [Visual Studio 9 for Python](http://aka.ms/vcpython27), if using Python 2.7.x.
-   [Microsoft Build Tools for Visual Studio 2017](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2017), if using Python 3.6.x
-   Ensure that kdb+ is installed under `C:\q`, or that the `QHOME` environment variable is set to the location of the kdb+ executable.

Install PyQ:

```powershell
pip install -U pyq
```

You can start PyQ by running

```powershell
c:\q\w32\q.exe python.q
```

> :warning: **Known limitation**
> 
> You will have to press `^Z` and then `Enter` key in order to get into the Python REPL.

You can run tests too: first install the required packages:

```powershell
pip install pytest pytest-pyq
```

Then run:

```powershell
set QBIN=c:\q\w32\q.exe
%QBIN% python.q -mpytest --pyargs pyq < nul
```

You can follow the latest updates on Windows support on [issue gh\#1](https://github.com/kxsystems/pyq/issues/1).


### Install the Jupyter kernel

Since we have not ported the `pyq` executable to the Windows platform yet, setting up a working PyQ environment on Windows requires several manual steps.

First, you are strongly recommended to use a dedicated Python virtual environment and install `q` in `%VIRTUAL_ENV%`. Assuming that you have downloaded `windows.zip` from [kx.com](https://kx.com/download/) into your `Downloads` folder, enter the following commands:

```powershell
python -mvenv py36
py36\Scripts\activate.bat
set QHOME=%VIRTUAL_ENV%\q
"C:\Program Files\7-Zip\7z.exe" x -y -o%VIRTUAL_ENV% %HOMEPATH%\Downloads\windows.zip
del %QHOME%\q.q
set PYTHONPATH=%VIRTUAL_ENV%\lib\site-packages
set QBIN=%QHOME%\w32\q.exe
```

Now you should be able to install `jupyter`, `pyq` and `pyq-kernel` in one command:

```powershell
pip install jupyter pyq pyq-kernel
```

Finally, to install PyQ kernel specs, run

```powershell
%QBIN% python.q -mpyq.kernel install
```
If everything is successful, you should see `pyq_3` listed in the `kernelspec` list:

```powershell
>jupyter kernelspec list
Available kernels:
  pyq_3      C:\Users\a\AppData\Roaming\jupyter\kernels\pyq_3
  python3    c:\users\a\py36\share\jupyter\kernels\python3
```

Now, start the notebook server

```powershell
jupyter-notebook
```

and select _PyQ 3_ from the _New_ menu.


_YouTube_: [What can be done in a PyQ notebook](https://youtu.be/v2UoP0l6mOw "YouTube")
