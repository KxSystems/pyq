from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import pyq
from io import StringIO
from getopt import getopt
import sys

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


def q(line, cell=None, _ns=None):
    """Run q code.

    Options:
       -l (dir|script) - pre-load database or script
       -h host:port - execute on the given host
       -o var - send output to a variable named var.
       -i var1,..,varN - input variables
    """
    if _ns is None:
        _ns = vars(sys.modules['__main__'])
    input = output = None
    preload = []
    try:
        if cell is None:
            r = pyq.q(line)
        else:
            h = pyq.q('0i')
            if line:
                for opt, value in getopt(line.split(), "h:l:o:i:")[0]:
                    if opt == '-l':
                        preload.append(value)
                    elif opt == '-h':
                        h = pyq.K(str(':' + value))
                    elif opt == '-o':
                        output = str(value)  # (see #673)
                    elif opt == '-i':
                        input = str(value).split(',')
            r = None
            for script in preload:
                h(pyq.kp(r"\l " + script))
            if input is not None:
                for chunk in logical_lines(cell):
                    func = "{[%s]%s}" % (';'.join(input), chunk)
                    args = tuple(_ns[i] for i in input)
                    r = h((pyq.kp(func),) + args)
            else:
                for chunk in logical_lines(cell):
                    r = h(pyq.kp(chunk))
    except pyq.kerr as e:
        print("'%s" % e)
    else:
        if output is not None:
            if output.startswith('q.'):
                pyq.q('@[`.;;]', output[2:], r)
            else:
                _ns[output] = r
        else:
            if r != Q_NONE:
                return r


def _q_formatter(x, p, _):
    x_show = x.show(output=str)
    p.text(x_show.strip())


def load_ipython_extension(ipython):
    ipython.register_magic_function(q, 'line_cell')
    fmr = ipython.display_formatter.formatters['text/plain']
    fmr.for_type(pyq.K, _q_formatter)


def unload_ipython_extension(ipython):
    pass
