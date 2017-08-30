from __future__ import absolute_import
from __future__ import unicode_literals
from ..magic import q as qmag, logical_lines


def test_q_magic_cell():
    r = qmag('', """\
a:1 2 3
b:3 2 1
a + b
""")
    assert r == [4] * 3


def test_q_magic_line():
    r = qmag('a:1 2 3;b:3 2 1;a + b')
    assert r == [4, 4, 4]


def test_logical_lines():
    script = """\
f:{a:x + y
   neg a}
f[5;6]
"""
    ll = logical_lines(script)
    assert next(ll) == "f:{a:x + y\n   neg a}"
    assert next(ll) == "f[5;6]"


def test_q_magic_cell_2():
    script = """\
f:{x +  / to be continued
 y}

f[5;6]
"""
    assert 11 == qmag('', script)


def test_q_magic_cell_3(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    script1 = tmpdir.join("script-1.q")
    script2 = tmpdir.join("script-2.q")
    script1.write("x:1")
    script2.write("x:2")

    x = qmag("-l script-1.q -l script-2.q", "x")
    assert x == 2


def test_q_magic_output(q):
    ns = {}
    qmag('-o x', "42", ns)
    assert ns['x'] == 42

    qmag('-o q.x', "42")
    assert q.x == 42


def test_q_magic_input():
    ns = dict(x=1, y=2)
    r = qmag('-i x,y', "x+y", ns)
    assert r == 3
