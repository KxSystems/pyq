#! /usr/bin/env q
\d .p
PYVER:"2.7"
PYSO:`py
SOEXT:".so\000"
lib:"libpython",PYVER,SOEXT

args:{$["@"~last x;-1_x;x]} each .z.x
if[$[count args;"--versions" in args;0b];args:("-c";"import pyq; pyq.versions()")]
py:PYSO 2:(`py;3)
run:py[`pyq^`$getenv`PYTHONEXECUTABLE;;lib]
\d .
/ Try loading args[0]
if[not 0~@[system;"l ",first .p.args;0];.p.args _: 0]
if[`python.q~last` vs hsym .z.f;exit .p.run .p.args]
