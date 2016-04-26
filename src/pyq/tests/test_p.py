import os
import subprocess

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
    out = subprocess.check_output([os.environ['QBIN'], str(test_p)])
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


def test_test_p_exception(tmpdir):
    p = tmpdir.join('test.p')
    p.write("""\
import sys
from pyq import q

def test(a, b):
    return a + b

q("p)test(1, 'a')")
sys.exit(0)

""")
    p = subprocess.Popen([os.environ['QBIN'], str(p)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    assert out == b''
    assert b'python\n@\ncode\n' in err
    # XXX: Why in python 3 I don't get TypeError in stderr?
