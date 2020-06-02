from __future__ import absolute_import
from __future__ import unicode_literals

import ctypes
import subprocess
import sys
import platform
import shutil
import os
import pytest
import py

pytestmark = pytest.mark.skipif(platform.system() == "Windows",
                                reason="pyq.exe is not implemented")

linux_only = pytest.mark.skipif('linux' not in sys.platform.lower(),
                                reason="requires linux")


@pytest.fixture(scope='session')
def pyq_cmd():
    try:
        subprocess.check_call(['valgrind', '--version'])
    except (OSError, subprocess.CalledProcessError):
        return ['pyq']
    else:
        return ['valgrind', '-q', 'pyq']


def test_pyq_executable_success(pyq_cmd):
    out = subprocess.check_output(pyq_cmd + ['-V'],
                                  stderr=subprocess.STDOUT)
    version = [x for x in out.splitlines() if not x.startswith(b'profiling')]
    assert version[0].startswith(b'Python')

    executable = subprocess.check_output(
        ['pyq', '-c', 'import sys; print(sys.executable)'])
    assert executable.strip().endswith(b'pyq')


def test_pyq_executable_error(pyq_cmd):
    rc = subprocess.call(pyq_cmd + ['-c', 'raise SystemExit(42)'])
    assert rc == 42


def test_pyq_executable_versions(pyq_cmd):
    stream = 'stderr' if str is bytes else 'stdout'
    p = subprocess.Popen(pyq_cmd + ['--versions'],
                         **{stream: subprocess.PIPE})
    versions = getattr(p, stream).read()
    assert b'PyQ ' in versions
    assert b'KDB+ ' in versions
    assert b'Python ' in versions


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
def test_pyq_taskset(c, r, monkeypatch, pyq_cmd):
    monkeypatch.setenv('CPUS', c)
    monkeypatch.setenv('TEST_CPUS', 'y')
    assert r == subprocess.check_output(pyq_cmd).decode()


def test_q_not_found(tmpdir, monkeypatch, pyq_cmd):
    monkeypatch.setenv('QHOME', str(tmpdir))
    monkeypatch.setenv('HOME', str(tmpdir.join('empty').ensure(dir=True)))
    monkeypatch.setenv("VIRTUAL_ENV", str(tmpdir))
    monkeypatch.setenv('PATH', str(tmpdir), prepend=':')
    tmpdir.join('pyq').mksymlinkto(sys.executable)
    p = subprocess.Popen(pyq_cmd, stderr=subprocess.PIPE)
    errors = p.stderr.read()
    rc = p.wait()
    assert rc != 0
    assert b"No such file or directory" in errors


@pytest.fixture
def q_arch(q):
    return str(q('.z.o'))


def test_q_venv0(tmpdir, monkeypatch, q_arch, pyq_cmd):
    # QHOME not set, $VIRTUAL_ENV/q present with q executable
    monkeypatch.setenv("VIRTUAL_ENV", str(tmpdir))
    monkeypatch.delenv("QHOME")
    venv = tmpdir.join('q')
    venv.join('python.q').ensure()
    q_exe = venv.join(q_arch, 'q')
    q_exe.write("#!/usr/bin/env bash\necho 'pass'", ensure=True)
    q_exe.chmod(0o755)
    p = subprocess.Popen(pyq_cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    err = p.stderr.readlines()
    assert err == []
    out = p.stdout.readlines()
    assert out[0].strip() == b'pass'


def test_q_venv1(tmpdir, monkeypatch, pyq_cmd):
    # QHOME not set, $VIRTUAL_ENV/q present, but no q executable
    monkeypatch.setenv("VIRTUAL_ENV", str(tmpdir))
    monkeypatch.setenv("HOME", str(tmpdir.join("empty").ensure(dir=True)))
    monkeypatch.delenv("QHOME")
    monkeypatch.setenv('PATH', str(tmpdir), prepend=':')
    py.path.local(sys.executable).copy(tmpdir.join('pyq'), mode=True)
    qhome = tmpdir.join('q').ensure(dir=True)
    p = subprocess.Popen(pyq_cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    err = p.stderr.read()
    out = p.stdout.read()
    rc = p.wait()
    assert out == b''
    assert qhome.dirname.encode() in err
    assert rc != 0


def test_q_venv2(tmpdir, monkeypatch, q_arch, pyq_cmd):
    # QHOME not set, VIRTUAL_ENV not set, HOME set to tempdir
    monkeypatch.setenv("HOME", str(tmpdir))
    monkeypatch.delenv("QHOME")
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    monkeypatch.setenv('PATH', str(tmpdir), prepend=':')
    py.path.local(sys.executable).copy(tmpdir.join('pyq'), mode=True)

    q_exe = tmpdir.join('q', q_arch, 'q')
    q_exe.write("#!/usr/bin/env bash\necho 'pass'", ensure=True)
    q_exe.chmod(0o755)

    p = subprocess.Popen(pyq_cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out = p.stdout.readlines()
    err = p.stderr.readlines()
    assert out[0].strip() == b'pass'
    assert err == []
    assert p.wait() == 0


def test_q_venv3(tmpdir, monkeypatch, q_arch, pyq_cmd):
    # QHOME not set, VIRTUAL_ENV not set, q is next to bin/pyq
    monkeypatch.delenv("QHOME")
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    bindir = tmpdir.join('bin')
    bindir.ensure(dir=1)
    monkeypatch.setenv('PATH', str(bindir), prepend=':')
    py.path.local(sys.executable).copy(bindir.join('pyq'), mode=True)

    q_exe = tmpdir.join('q', q_arch, 'q')
    q_exe.write("#!/usr/bin/env bash\necho 'pass'", ensure=True)
    q_exe.chmod(0o755)

    p = subprocess.Popen(pyq_cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out = p.stdout.readlines()
    err = p.stderr.readlines()
    assert out[0].strip() == b'pass'
    assert err == []
    assert p.wait() == 0


def test_pyq_trace(pyq_cmd):
    output = subprocess.check_output(pyq_cmd + ['--pyq-trace', '-c', '0'])
    assert b"pyq trace is on" in output


def test_pyq_preload(tmpdir, q, pyq_cmd):
    db = tmpdir.join('db')
    q.x = q.til(3)
    q.save(db.join('x'))
    output = subprocess.check_output(pyq_cmd + [
        str(db), "-c", "from pyq import q; print(q.x)"])
    assert output == b"0 1 2\n"


def test_p__file__0(tmpdir, pyq_cmd):
    p = tmpdir.join('test.py')
    p.write("print(__file__)")
    out = subprocess.check_output(pyq_cmd + [str(p)])
    assert out.strip().endswith(str(p).encode())


def test_broken_q(tmpdir, monkeypatch, q_arch, pyq_cmd):
    # QHOME not set, $VIRTUAL_ENV/q present with a broken q executable
    monkeypatch.setenv("VIRTUAL_ENV", str(tmpdir))
    monkeypatch.delenv("QHOME")
    q_exe = tmpdir.join('q', q_arch, 'q')
    q_exe.ensure()
    q_exe.chmod(0o422)
    with open(os.devnull, 'w')as null:
        p = subprocess.Popen(pyq_cmd, stdout=null, stderr=subprocess.PIPE)
        assert (str(q_exe) + ':') in p.stderr.read().decode()


@pytest.mark.parametrize('message,stock', [
    ('standalone python', True),
    ('', False),
]
                         )
def test_stock_python(monkeypatch, message, stock):
    if stock:
        monkeypatch.setattr(ctypes, 'CDLL', lambda x: None)
    monkeypatch.setitem(sys.modules, 'pyq._k', None)
    monkeypatch.delitem(sys.modules, 'pyq', raising=False)

    with pytest.raises(ImportError) as exc:
        __import__('pyq')

    if stock:
        assert message in exc.value.args[0]


def test_dash_dash(pyq_cmd):
    # NB: -P is q command line option to set display precision
    output = subprocess.check_output(pyq_cmd + ['-c', r'print(q(r"\P"))',
                                                '--', '-P', '10'])
    assert b'10' in output


@pytest.mark.parametrize('option, message', [
    ('qhome', b'QHOME='),
    ('qarch', b'QARCH='),
    ('qbin', b'QBIN='),
])
def test_print_options(option, message):
    output = subprocess.check_output(['pyq', '--pyq-' + option])
    assert message in output
    value = 'xyz'
    output = subprocess.check_output(['pyq', '--pyq-' + option,
                                      '--pyq-' + option + '=' + value])
    assert (message + value.encode()) in output


@pytest.mark.skipif("not hasattr(shutil, 'which')")
def test_run_with_absolute_path():
    abs_path = shutil.which('pyq')
    out = subprocess.check_output([abs_path, '-c',
                                   'import sys;print(sys.executable)'])
    assert os.stat(out.strip().decode()) == os.stat(abs_path)


@pytest.mark.skipif("not hasattr(shutil, 'which')")
def test_run_with_relative_path(monkeypatch):
    abs_path = shutil.which('pyq')
    monkeypatch.chdir(os.path.dirname(abs_path))
    out = subprocess.check_output(['./pyq', '-c',
                                   'import sys;print(sys.executable)'])
    assert os.stat(out.strip().decode()) == os.stat(abs_path)


@pytest.mark.skipif("not hasattr(shutil, 'which')")
def test_run_with_single_dir_in_path(monkeypatch):
    abs_path = shutil.which('pyq')
    monkeypatch.setenv('PATH', os.path.dirname(abs_path))
    out = subprocess.check_output(['pyq', '-c',
                                   'import sys;print(sys.executable)'])
    assert os.stat(out.strip().decode()) == os.stat(abs_path)
