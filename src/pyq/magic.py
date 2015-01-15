from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import pyq
from io import StringIO
from getopt import getopt

try:
    string_types = (str, unicode)
except NameError:
    string_types = (str,)

Q_NONE = pyq.q('::')


def logical_lines(lines):
    if isinstance(lines, string_types):
        lines = StringIO(lines)
    buf = []
    for line in lines:
        if buf and not line.startswith(' '):
            chunk = ''.join(buf).strip()
            if chunk:
                yield chunk
            buf[:] = []

        buf.append(line)
    chunk = ''.join(buf).strip()
    if chunk:
        yield chunk


def q(line, cell=None):
    """Run q code.

    Options:
       -l (dir|script) - pre-load database or script
       -h host:port - execute on the given host
    """
    try:
        if cell is None:
            return pyq.q(line)
        h = pyq.q
        if line:
            for opt, value in getopt(line.split(), "h:l:")[0]:
                if opt == '-l':
                    h(r"\l " + value)
                elif opt == '-h':
                    def h(chunk, _handle="`:" + value):
                        return pyq.q(_handle, pyq.kp(chunk))
        for chunk in logical_lines(cell):
            r = h(chunk)
            if r != Q_NONE:
                r.show()
    except pyq.kerr as e:
        print("'%s" % e)


def _q_formatter(x, p, _):
    p.text(x.show(output=str))


def load_ipython_extension(ipython):
    ipython.register_magic_function(q, 'line_cell')
    fmr = ipython.display_formatter.formatters['text/plain']
    fmr.for_type(pyq.K, _q_formatter)


def unload_ipython_extension(ipython):
    pass
