--------------
Enhanced shell
--------------

If you have ipython installed in your environment, you can run an
interactive IPython shell as follows::

        $ pyq -m IPython


For a better experience, load ``pyq.magic`` extension::

    In [1]: %load_ext pyq.magic


This makes K objects display nicely in the output and gives
you access to the PyQ-specific IPython magic commands:

Line magic ``%q``::

    In [2]: %q ([]a:til 3;b:10*til 3)
    Out[2]:
    a b
    ----
    0 0
    1 10
    2 20

Cell magic ``%%q``::

        In [4]: %%q
           ....: a: exec a from t where b=20
           ....: b: exec b from t where a=2
           ....: a+b
           ....:
        Out[4]: ,22

You can pass following options to the ``%%q`` cell magic:

| -l (dir|script)
|     pre-load database or script
| -h host:port
|     execute on the given host
| -o var
|     send output to a variable named var
| -i var1, .., varN
|     input variables
| -1
|     redirect stdout
| -2
|     redirect stderr
