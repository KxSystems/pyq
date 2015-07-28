PYVER:"2.7"
SOEXT:".so\000"
PSO:`p
lib:"libpython",PYVER,SOEXT
PYTHON:"python.py"

`QVER setenv$_.Q.k
\d .p
@[`.[`PSO]2:(`i;1);`. `lib]
e:{e0 x,"\000";}
\d .
p)import sys, os
p)from pyq import q
p)sys.executable = str(q.PYTHON)
p)script = str(q(".z.f"))
p)sys.argv = [script] + [str(a) for a in  q(".z.x")]
p)sys.modules['__main__'].__file__ = script
p)sys.path.insert(0, os.path.dirname(script))
p)del sys, os, script
