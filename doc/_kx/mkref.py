# A script to generate reference manual entries for q functions

import py
from pyq import q
from collections import defaultdict


Q_FUNC_DOC = """\
.. py:function:: q.{name}

   {short}{doc}

   See also `{qname} on code.kx.com <http://code.kx.com/wiki/Reference/{qname}>`_.


"""


K_METH_DOC = """\
.. py:method:: K.{name}

   {short}

   For details, see :func:`q.{name} <pyq.q.{name}>` and `{qname} on code.kx.com
   <http://code.kx.com/wiki/Reference/{qname}>`_.


"""

DOC = defaultdict(str)

DOC['abs'] = """\

   The abs function computes the absolute value of its argument. Null is returned if the argument is null.

   >>> q.abs([-1, 0, 1, None])
   k('1 0 1 0N')

"""

script_dir = py.path.local(__file__).dirpath()
ref_dir = script_dir / '..' / 'reference'
q_func_rst = ref_dir / 'q-funcs.rst'
k_meth_rst = ref_dir / 'K-meths.rst'
code_dump = script_dir / 'code.dump'
kx_docs = code_dump.load()

#  Fix links
fixes = {'aj0': 'aj', 'binr': 'bin'}

with q_func_rst.open('w') as f, k_meth_rst.open('w') as g:
    for name in sorted(dir(q)):
        qname = name.rstrip('_')
        qname = fixes.get(name, qname)
        desc = kx_docs.get(qname)
        if isinstance(desc, tuple):
            short = desc[1]
        else:
            short = 'The %s function.' % qname
        f.write(Q_FUNC_DOC.format(name=name, short=short, qname=qname, doc=DOC[name]))
        g.write(K_METH_DOC.format(name=name, short=short, qname=qname))
