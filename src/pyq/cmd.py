from __future__ import absolute_import, print_function
from __future__ import unicode_literals

import cmd as _cmd

from . import q, kerr, Q_OS

try:
    from . import ptk
except ImportError:
    ptk = None

q('.py.pcc:`s#0 5 20f!32 33 31')
_prompt_color = q('{.py.pcc 100*(%)over system["w"]1 5}')
_prompt_namespace = q('{?[ns~`.;`;ns:system"d"]}')
if Q_OS.startswith('w'):
    def _colorize(_, prompt):
        return prompt
else:
    def _colorize(code, prompt):
        return "\001\033[%d;1m\002%s\001\033[0m\002" % (code, prompt)


class Cmd(_cmd.Cmd, object):
    _prompt = 'q{ns})'

    @property
    def prompt(self):
        code = _prompt_color()
        prompt = self._prompt.format(ns=_prompt_namespace())
        return _colorize(code, prompt)

    def precmd(self, line):
        if line.startswith('help'):
            if not q("`help in key`.q"):
                try:
                    q("\\l help.q")
                except kerr:
                    return '-1"no help available - install help.q"'
        if line == 'help':
            line += "`"
        return line

    def onecmd(self, line):
        if line == '\\':
            return True
        elif line == 'EOF':
            print('\r', end='')
            return True
        else:
            try:
                v = q(line)
            except kerr as e:
                print("'%s" % e.args[0])
            else:
                if v != q('::'):
                    v.show()
            return False

    if ptk:
        cmdloop = ptk.cmdloop
