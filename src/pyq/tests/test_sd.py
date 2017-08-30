from __future__ import absolute_import
import subprocess
import os
import pytest
from pyq import _k
import platform

WIN = platform.system() == "Windows"

TEST_SD = """\
p)import os
p)import sys
p)from pyq import _k
p)def f(d):
    x = os.read(d, 1)
    print(x.decode())
    sys.stdout.flush()
    _k.sd0(d)
p)r,w = os.pipe()
p)_k.sd1(r, f)
p)os.write(w, b'X')
"""

TEST_SD_ERROR = """\
p)from pyq import _k
p)r,w = os.pipe()
p)_k.sd1(r, None)
p)os.write(w, b'X')
"""


@pytest.mark.skipif(WIN, reason="This test hangs on Windows.")
def test_sd(tmpdir):
    qbin = os.environ['QBIN']
    test = tmpdir.join('test_sd.q')
    test.write(TEST_SD)
    with open(os.devnull) as devnull:
        assert b'X\n' == subprocess.check_output([qbin, str(test)],
                                                 stdin=devnull)


@pytest.mark.skipif(WIN, reason="This test hangs on Windows.")
def test_callback_error(tmpdir):
    qbin = os.environ['QBIN']
    test = tmpdir.join('test_sd.q')
    test.write(TEST_SD_ERROR)
    with open(os.devnull) as devnull:
        p = subprocess.Popen([qbin, str(test)],
                             stdin=devnull, stderr=subprocess.PIPE)
        out, err = p.communicate()
    assert b'py' in err


def test_sd1_error():
    with pytest.raises(ValueError):
        _k.sd1(-1, None)
