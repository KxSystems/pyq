from __future__ import print_function
import sys
try:
    import ptpython.entry_points.run_ptpython as ptp
except ImportError:
    if hasattr(sys, '_called_from_test'):
        raise
    print('Cannot import ptpython. Try',
          '    pip install ptpython', sep='\n')
    raise SystemExit(1)

from pyq import q, kerr


def run(q_prompt=False):
    if len(sys.argv) > 1:
        try:
            q(r'\l %s' % sys.argv[1])
        except kerr:
            pass
        else:
            del sys.argv[1]
    if q_prompt:
        q()
    ptp.run()
