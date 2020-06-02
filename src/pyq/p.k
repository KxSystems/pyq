\l pyq-config.q
q)(`:./pyq 2:(`p_init;2))[.pyq.python_dll;.pyq.pyq_executable,"\000"]
/ We use function composition to suppress back-traces
/ from lambda.  Note that parentheses are required.
.p.e:('[.pyq.e;],[;"\000"])
p)import sys, os
p)from pyq import q
p)script = q("{$[x~`python.q;`;x]}.z.f")
p)if script:
    sys.argv = [str(script)] + [str(a) for a in q(".z.x")]
    sys.modules['__main__'].__file__ = str(script)
    sys.path.insert(0, os.path.dirname(str(script)))
p)del sys, os, script
