from __future__ import absolute_import
from __future__ import unicode_literals
import subprocess
import os


def test_python_q_exitcode():
    with open(os.devnull) as rnull, open(os.devnull, 'w') as wnull:
        assert subprocess.call([os.getenv('QBIN'), 'python.q',
                                '-c@', 'raise Exception'],
                               stdin=rnull, stdout=wnull, stderr=wnull) == 1
