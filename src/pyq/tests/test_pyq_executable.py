from __future__ import absolute_import
from __future__ import unicode_literals

import subprocess
import sys

import pytest

linux_only = pytest.mark.skipif('linux' not in sys.platform.lower(), reason="requires linux")


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
    assert r == subprocess.check_output(['pyq']).decode()


def test_q_not_found(tmpdir, monkeypatch):
    q_home = str(tmpdir)
    monkeypatch.setenv('QHOME', q_home)
    p = subprocess.Popen(['pyq'], stderr=subprocess.PIPE)
    errors = p.stderr.readlines()
    assert errors[0].startswith(q_home.encode())


@pytest.fixture
def q_arch():
    path = ''  # Make PyCharm happy
    if sys.platform.startswith('linux'):
        path = 'l64'
    elif sys.platform.startswith('darwin'):
        path = 'm32'
    return path


def test_q_venv0(tmpdir, monkeypatch, q_arch):
    # QHOME not set, $VIRTUAL_ENV/q present with q executable
    monkeypatch.setenv("VIRTUAL_ENV", tmpdir)
    monkeypatch.delenv("QHOME")
    venv = tmpdir.join('q')
    venv.join('python.q').ensure()
    q_exe = venv.join(q_arch, 'q')
    q_exe.write("#/usr/bin/env\necho 'pass'", ensure=True)
    q_exe.chmod(0o755)
    p = subprocess.Popen(['pyq'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = p.stderr.readlines()
    assert err == []
    out = p.stdout.readlines()
    assert out[0].strip() == b'pass'


def test_q_venv1(tmpdir, monkeypatch):
    # QHOME not set, $VIRTUAL_ENV/q present, but no q executable
    monkeypatch.setenv("VIRTUAL_ENV", tmpdir)
    monkeypatch.delenv("QHOME")
    venv = tmpdir.join('q', 'python.q').ensure()
    p = subprocess.Popen(['pyq'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = p.stderr.readlines()
    assert err[0].startswith(venv.dirname.encode())


def test_q_venv2(tmpdir, monkeypatch, q_arch):
    # QHOME not set, VIRTUAL_ENV not set, HOME set to tempdir
    monkeypatch.setenv("HOME", tmpdir)
    monkeypatch.delenv("QHOME")
    monkeypatch.delenv("VIRTUAL_ENV")

    q_exe = tmpdir.join('q', q_arch, 'q')
    q_exe.write("#/usr/bin/env\necho 'pass'", ensure=True)
    q_exe.chmod(0o755)

    p = subprocess.Popen(['pyq'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.readlines()
    err = p.stderr.readlines()
    assert out[0].strip() == b'pass'
    assert err == []
