from __future__ import absolute_import
from __future__ import unicode_literals
import subprocess
import sys

import pytest

linux_only = pytest.mark.skipif(sys.platform != 'linux2', reason="requires linux")


def test_pyq_executable_success():
    version = subprocess.check_output(['pyq', '-V'], stderr=subprocess.STDOUT)
    assert version.startswith(b'Python')

    executable = subprocess.check_output(['pyq', '-c', 'import sys; print(sys.executable)'])
    assert executable.strip().endswith(b'pyq')


def test_pyq_executable_error():
    rc = subprocess.call(['pyq', '-c', 'raise SystemExit(42)'])
    assert rc == 42


@linux_only
@pytest.mark.parametrize('c, r', [
    ('0', 'n = 1\n0 \n'),
    ('1', 'n = 1\n1 \n'),
    ('1-2', 'n = 2\n1 2 \n'),
    ('1-3', 'n = 3\n1 2 3 \n'),
    ('1-4', 'n = 4\n1 2 3 4 \n'),
    ('1-5', 'n = 5\n1 2 3 4 5 \n'),
    ('1-6', 'n = 6\n1 2 3 4 5 6 \n'),
    ('1-7', 'n = 7\n1 2 3 4 5 6 7 \n'),
    ('1-8', 'n = 8\n1 2 3 4 5 6 7 8 \n'),
    ('1,3,5,7', 'n = 4\n1 3 5 7 \n'),
    ('2-4,8', 'n = 4\n2 3 4 8 \n'),
    ('0,4-8', 'n = 6\n0 4 5 6 7 8 \n'),
    ('0-3,4,7-8', 'n = 7\n0 1 2 3 4 7 8 \n'),
    ('0-3,4,7,10', 'n = 7\n0 1 2 3 4 7 10 \n'),
    ('x', 'n = 1\n0 \n'),
    ('0, 1, 2', 'n = 3\n0 1 2 \n'),
    ('0 , 1', 'n = 2\n0 1 \n'),
    ('0 ,1', 'n = 2\n0 1 \n'),
])
def test_pyq_taskset(c, r, monkeypatch):
    monkeypatch.setenv('CPUS', c)
    monkeypatch.setenv('TEST_CPUS', 'y')
    assert r == subprocess.check_output(['pyq'])
