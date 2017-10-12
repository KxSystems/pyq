Installing PyQ on Ubuntu 16.04
------------------------------

Since Python provided by Ubuntu is statically linked, shared libraries need to be installed before PyQ can be installed.

Python 2
........

Install shared libraries:

.. code-block:: bash

    $ sudo apt-get install libpython-dev libpython-stdlib python-pip python-virtualenv


Create and activate virtual environment:

.. code-block:: bash

    $ python -m virtualenv -p $(which python2) py2
    $ source py2/bin/activate


Install PyQ:

.. code-block:: bash

    (py2) $ pip install pyq


Python 3
........

Install shared libraries:

.. code-block:: bash

    $ sudo apt-get install libpython3-dev libpython3-stdlib python3-pip python3-virtualenv


Create and activate virtual environment:

.. code-block:: bash

    $ python3 -m virtualenv -p $(which python3) py3
    $ source py3/bin/activate


Install PyQ:

.. code-block:: bash

    (py3) $ pip3 install pyq

