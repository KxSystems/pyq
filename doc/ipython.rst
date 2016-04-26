.. _ipython:

IPython Magic
=============

PyQ provides a Jupyter extension for accessing kdb+ from IPython.

In Jupyter notebook or the IPython Command Line Interface you can load PyQ's magic:

$ pyq -mIPython
In [1]: %load_ext pyq.magic


Then you get access to two magics:

* Line magic:

    ::

        In [2]: %q t:([]a:til 3;b:10*til 3)

        In [3]: %q show t
        a b
        ----
        0 0
        1 10
        2 20

* Cell magic:

    ::

        In [4]: %%q
           ....: a: exec a from t where b=20
           ....: b: exec b from t where a=2
           ....: a+b
           ....:
        Out[4]: ,22

You can pass following options to cell magic:

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
