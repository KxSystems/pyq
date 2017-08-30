Installing PyQ on macOS
-----------------------

In order to use PyQ with the free 32-bit kdb+ on macOS, you need a 32-bit version of Python. Out of the box,
macOS Sierra and High Sierra come with a universal version of Python 2.7.10.

System Python 2
...............

Install virtualenv module:

.. code-block:: bash

    $ pip install virtualenv

If your system, does not have pip installed, follow `pip installation guide <https://pip.pypa.io/en/stable/installing/>`_.

Create and activate virtual environment:

.. code-block:: bash

    $ virtualenv ${HOME}/pyq2
    $ source ${HOME}/pyq2/bin/activate

Download `kdb+ by following this link <https://kx.com/download/>`_ and save the downloaded file as `${HOME}/Downloads/macosx.zip`.

Install kdb+ and PyQ:

.. code-block:: bash

    (pyq2) $ unzip ${HOME}/Downloads/macosx.zip -d ${VIRTUAL_ENV}
    (pyq2) $ pip install -i https://pyq.enlnt.com --no-binary pyq pyq

PyQ is ready and can be launched:

.. code-block:: bash

    (pyq2) $ pyq

Brewing Universal Python
........................

If you would like to use latest version of the Python 2.7 or Python 3, you will need to install it
using package manager `Homebrew <https://brew.sh/>`_.

1. Install Homebrew. Installation instructions are available at `Homebrew's website <https://brew.sh/>`_.
2. Install universal Python 2.7 and Python 3.6:

.. code-block:: bash

    $ brew install --universal sashkab/python/python27 sashkab/python/python36

3. Install virtualenv package.

.. code-block:: bash

    $ /usr/local/opt/pythonXY/bin/pythonX -mpip install -U virtualenv

`X` is major version of the Python, `Y` - minor, i.e. 2.7 or 3.6.

4. Create new virtual environment and activate it:

.. code-block:: bash

    $ mkvirtualenv -p /usr/local/opt/pythonXY/bin/pythonX ${HOME}/pyq
    $ source ${HOME}/pyq/bin/activate

5. Download `kdb+ by following this link <https://kx.com/download/>`_ and save the downloaded file as `${HOME}/Downloads/macosx.zip`.

6. Install kdb+ and PyQ:

.. code-block:: bash

    (pyq) $ unzip ${HOME}/Downloads/macosx.zip -d ${VIRTUAL_ENV}
    (pyq) $ pip install -i https://pyq.enlnt.com --no-binary pyq pyq

PyQ is ready and can be launched:

.. code-block:: bash

    (pyq2) $ pyq
