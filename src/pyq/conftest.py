from __future__ import absolute_import
import os

import pytest
import subprocess


def pytest_configure(config):
    import sys
    sys._called_from_test = True


def pytest_unconfigure(config):
    import sys
    del sys._called_from_test


@pytest.fixture(autouse=True)
def add_array(doctest_namespace):
    try:
        from numpy import array
    except ImportError:
        pass
    else:
        doctest_namespace['array'] = array


@pytest.fixture(autouse=True)
def add_dt(doctest_namespace):
    from datetime import datetime, date, time, timedelta
    doctest_namespace['datetime'] = datetime
    doctest_namespace['date'] = date
    doctest_namespace['time'] = time
    doctest_namespace['timedelta'] = timedelta


@pytest.fixture
def kdb_server(q, tmpdir):
    """Starts a kdb server and yields connection handle"""
    prog = os.getenv('QBIN')
    script = tmpdir.join('srv.q')
    script.write("""\
p:1024;while[0~@[system;"p ",string p;0];p+:1];-1 string p;
""")
    with open(os.devnull) as devnull:
        process = subprocess.Popen([prog, script.strpath],
                                   stdout=subprocess.PIPE,
                                   stdin=devnull)
        c = None
        try:
            line = process.stdout.readline()
            port = int(line.strip())
            c = q.hopen(port)
            c(q('".z.pc:{exit 0}"'))  # stop server on port close
            yield c
        finally:
            if c is not None:
                q.hclose(c)
            process.stdout.close()
            process.wait()
