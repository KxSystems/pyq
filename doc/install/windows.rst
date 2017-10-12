Experimental support for Windows
--------------------------------

PyQ 4.1.0 introduced experimental support for Windows.

Requirements are:

- Installation should be started using Windows Command Prompt.
- `Visual Studio 9 for Python`_, if using Python 2.7.x.
- `Microsoft Build Tools for Visual Studio 2017`_, if using Python 3.6.x
- Ensure kdb+ is installed under ``C:\q`` or the ``QHOME`` environment variable is set to the location of the kdb+ executable.

.. _Visual Studio 9 for Python: http://aka.ms/vcpython27
.. _Microsoft Build Tools for Visual Studio 2017: https://www.visualstudio.com/downloads/#build-tools-for-visual-studio-2017

Install PyQ:

.. code-block:: batch

    pip install -U pyq

You can start PyQ by running

.. code-block:: text

    c:\q\w32\q.exe python.q

.. note::

    You will have to press ``^Z`` and then ``Enter`` key in order to get into Python REPL. This is known limitation of this version.

You can run tests too: first install required packages:

.. code-block:: batch

    pip install pytest pytest-pyq

Then run:

.. code-block:: text

    set QBIN=c:\q\w32\q.exe
    %QBIN% python.q -mpytest --pyargs pyq < nul

You can follow latest updates on Windows support on `issue gh#1`_.

 .. _issue gh#1: https://github.com/enlnt/pyq/issues/1



Installing Jupyter kernel
.........................


Since we have not ported the ``pyq`` executable to the Windows platform yet, setting up a working PyQ environment
on Windows requires several manual steps.

First, it is strongly recommended to use a dedicated Python virtual environment and install ``q`` in ``%VIRTUAL_ENV%``.
Assuming that you have downloaded ``windows.zip`` from `<https://kx.com/download/>`_ in your ``Downloads`` folder, enter the following commands:

.. code-block:: batch

    python -mvenv py36
    py36\Scripts\activate.bat
    set QHOME=%VIRTUAL_ENV%\q
    "C:\Program Files\7-Zip\7z.exe" x -y -o%VIRTUAL_ENV% %HOMEPATH%\Downloads\windows.zip
    del %QHOME%\q.q
    set PYTHONPATH=%VIRTUAL_ENV%\lib\site-packages
    set QBIN=%QHOME%\w32\q.exe

Now you should be able to install jupyter, pyq and pyq-kernel in one command

.. code-block:: batch

    pip install jupyter pyq pyq-kernel

Finally, to install pyq kernel specs, run

.. code-block:: batch

    %QBIN% python.q -mpyq.kernel install

If everything is successful, you should see pyq_3 listed in the kernelspec list:

.. code-block:: text

    >jupyter kernelspec list
    Available kernels:
      pyq_3      C:\Users\a\AppData\Roaming\jupyter\kernels\pyq_3
      python3    c:\users\a\py36\share\jupyter\kernels\python3

Now, start the notebook server

.. code-block:: batch

    jupyter-notebook

and select "PyQ 3" from the "New" menu.

For examples of what can be done in a PyQ notebook, please see `presentation <https://youtu.be/v2UoP0l6mOw>`_.
