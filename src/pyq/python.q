#! /usr/bin/env q
VER:"3.9"
PYVER:"2.7"
PYSO:`py
SOEXT:".so\000"
lib:"libpython",PYVER,SOEXT

args:{$["@"~last x;-1_x;x]} each .z.x
if[$[count args;"--versions" in args;0b];args:("-c";"import pyq; pyq.versions()")]
py:PYSO 2:(`py;3)
`QVER setenv string floor .Q.k
r:py[`pyq^`$getenv`PYTHONEXECUTABLE;args;lib]
exit r
