#! /usr/bin/env q
PYVER:"2.7"
PYSO:`py
SOEXT:".so\000"
lib:"libpython",PYVER,SOEXT

args:{$["@"~last x;-1_x;x]} each .z.x
py:PYSO 2:(`py;3)
`QVER setenv string floor .Q.k
r:py[`pyq^`$getenv`PYTHONEXECUTABLE;args;lib]
exit r
\\
