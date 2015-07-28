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


def test_test_p(tmpdir):
    test_p = tmpdir.join('test.p')
    test_p.write(TEST_P)
    out = subprocess.check_output([os.environ['QBIN'], str(test_p)])
    assert b'ok' in out
