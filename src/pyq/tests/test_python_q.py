from __future__ import absolute_import
from __future__ import unicode_literals
import subprocess
import sys


def test_python_q_exitcode():
    assert 1 == subprocess.call([sys.executable, '-c@', 'raise Exception'])
