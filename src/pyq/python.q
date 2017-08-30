#! /usr/bin/env q
\l p.k
\d .p
args:{$["@"~last x;-1_x;x]} each .z.x
if[$[count args;"--versions" in args;0b];args:("-c";"import pyq; pyq.versions()")]
run:py`$pyq_executable
\d .
/ Try loading args[0]
if[not 0~@[system;"l ",first .p.args;0];.p.args _: 0]
if[`python.q~last` vs hsym .z.f;exit .p.run .p.args]
