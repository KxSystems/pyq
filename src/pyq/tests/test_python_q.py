from __future__ import absolute_import
from __future__ import unicode_literals
import subprocess
import os


def test_python_q_exitcode():
    assert subprocess.call([os.getenv('QBIN'), 'python.q',
                            '-c@', 'raise Exception']) == 1
