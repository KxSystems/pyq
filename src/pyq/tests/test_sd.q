p)import os
p)import sys
p)from pyq import _k
p)def f(d):
    x = os.read(d, 1)
    print(x.decode())
    sys.stdout.flush()
    _k.sd0(d)
p)r,w = os.pipe()
p)_k.sd1(r, None)
p)os.write(w, b'X')

