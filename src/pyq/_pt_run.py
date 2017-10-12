from __future__ import print_function
import sys
import os

try:
    import ptpython.entry_points.run_ptpython as ptp
except ImportError:
    if hasattr(sys, '_called_from_test'):
        raise
    print('Cannot import ptpython. Try',
          '    pip install ptpython', sep='\n')
    raise SystemExit(1)

from pyq import q, kerr


def console_size(fd=1):
    try:
        import fcntl
        import termios
        import struct
    except ImportError:
        size = os.getenv('LINES', 25), os.getenv('COLUMNS', 80)
    else:
        size = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
                                               b'1234'))
    return size


def run(q_prompt=False):
    lines, columns = console_size()
    q(r'\c %d %d' % (lines, columns))
    if len(sys.argv) > 1:
        try:
            q(r'\l %s' % sys.argv[1])
        except kerr as e:
            print(e)
            raise SystemExit(1)
        else:
            del sys.argv[1]
    if q_prompt:
        q()
    ptp.run()
