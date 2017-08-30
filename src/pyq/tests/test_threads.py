from __future__ import absolute_import
import subprocess
import threading
from pyq import _k
import os
import sys


def test_m9_in_thread():
    def call_m9():
        _k.m9()

    thread = threading.Thread(target=call_m9)
    thread.start()
    thread.join()


if sys.version_info >= (3, ):
    MT_PEACH_CODE = "from threading import get_ident"
else:
    MT_PEACH_CODE = "from thread import get_ident"

MT_PEACH_CODE += """
q.f = get_ident
q)exit"i"$%d<>count distinct {f()} peach til 10
"""


def test_mt_peach(tmpdir):
    n = 4  # number of slave threads for peach
    qbin = os.getenv('QBIN')
    script = tmpdir.join('x.p')
    script.write(MT_PEACH_CODE % n)
    subprocess.check_call([qbin, script.strpath, '-s', str(n), '-q'])
