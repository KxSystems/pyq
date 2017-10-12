from __future__ import absolute_import
import os
import sys
import subprocess
import platform
import pytest

WIN = platform.system() == "Windows"

TEST_P = """\
import sys
from pyq import q
def test():
    pass
assert len(sys.argv) == len(q(".z.x")) + 1, "test argv"
q("p)print('ok')")
sys.exit(0)
"""


def test_test_p0(tmpdir):
    test_p = tmpdir.join('test.p')
    test_p.write(TEST_P)
    with open(os.devnull) as null:
        out = subprocess.check_output([os.environ['QBIN'], str(test_p)],
                                      stderr=subprocess.PIPE, stdin=null)
    assert b'ok' in out


def test_test_p_multiple_arugments(tmpdir):
    p = tmpdir.join('test.p')
    p.write("""\
import sys
from pyq import q

def test(a, b, c):
    return a + b + c

q("p)print('ok' if test(1, 2, 3) else 'fail')")
sys.exit(0)
""")
    out = subprocess.check_output([os.environ['QBIN'], str(p)])
    assert b'ok' in out


@pytest.mark.skipif(WIN, reason="This test hangs on Windows.")
def test_test_p_exception(tmpdir):
    p = tmpdir.join('test.q')
    p.write("p)1+'a'")
    p = subprocess.Popen([os.environ['QBIN'], str(p)], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    assert out == b''
    traceback = b'''\
Traceback (most recent call last):
  File "<string>", line 1, in <module>
TypeError: unsupported operand type(s) for +: 'int' and 'str'
'''
    assert traceback in err


def test_p__file__qbin(tmpdir):
    p = tmpdir.join('test.p')
    p.write("import sys\nprint(__file__)\nsys.exit(0)")
    with open(os.devnull) as null:
        out = subprocess.check_output([os.environ['QBIN'], str(p)],
                                      stderr=subprocess.PIPE, stdin=null)
    assert out.strip().endswith(str(p).encode())
