from __future__ import unicode_literals
from ..magic import q as qmag, logical_lines


def test_q_magic_cell(capsys):
    qmag('', """\
a:1 2 3
b:3 2 1
a + b
""")
    assert capsys.readouterr()[0] == "4 4 4\n"


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


def test_q_magic_cell_2(capsys):
    script = """\
f:{x +  / to be continued
 y}

f[5;6]
"""
    qmag('', script)
    assert capsys.readouterr()[0] == "11\n"


def test_q_magic_cell_3(tmpdir, monkeypatch, capsys):
    monkeypatch.chdir(tmpdir)
    script1 = tmpdir.join("script-1.q")
    script2 = tmpdir.join("script-2.q")
    script1.write("x:1")
    script2.write("x:2")

    qmag("-l script-1.q -l script-2.q", "x")
    assert capsys.readouterr()[0] == "2\n"
