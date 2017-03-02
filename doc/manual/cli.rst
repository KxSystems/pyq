---------
q) prompt
---------

While in PyQ, you can drop to emulated kdb+ Command Line Interface (CLI). Here is how:

Start pyq::

    $ pyq
    >>> from pyq import q

Enter kdb+ CLI::

    >>> q()
    q)t:([]a:til 5; b:10*til 5)
    q)t
    a b
    ----
    0 0
    1 10
    2 20
    3 30
    4 40

Exit back to Python::

    q)\
    >>> print("Back to Python")
    Back to Python

Or you can exit back to shell::

    q)\\
    $
