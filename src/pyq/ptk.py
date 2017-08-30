"""Prompt toolkit

"""
from __future__ import absolute_import
from __future__ import unicode_literals

import re
from prompt_toolkit.completion import Completion
from prompt_toolkit.contrib.completers import PathCompleter
from prompt_toolkit.contrib.completers.base import Completer
from prompt_toolkit.document import Document
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import prompt
from prompt_toolkit.styles import style_from_pygments
from pygments.token import Token
from pygments.styles.monokai import MonokaiStyle as BasicStyle
from pygments.lexers import get_lexer_by_name

try:
    q_lexer = get_lexer_by_name('q')
except ValueError:
    lexer = None
else:
    from prompt_toolkit.layout.lexers import PygmentsLexer

    lexer = PygmentsLexer(type(q_lexer))
from . import q

KDB_INFO = "KDB+ %s %s" % tuple(q('.z.K,.z.k'))

style_dict = {
    # Prompt.
    Token.Generic.Prompt: '#884444',
    # Toolbar.
    Token.Toolbar: '#ffffff bg:#333333',
}


def get_bottom_toolbar_tokens(cli):
    mem = q('.Q.w', '') // 1024  # memory info in KiB
    return [(Token.Toolbar, "{0} {1.used}/{1.mphy} KiB".format(KDB_INFO, mem))]


history = InMemoryHistory()


def get_prompt_tokens(_):
    namespace = q(r'\d')
    if namespace == '.':
        namespace = ''
    return [(Token.Generic.Prompt, 'q%s)' % namespace)]


HSYM_RE = re.compile(r'.*`:([\w/.]*)$')


class QCompleter(Completer):
    """Completer for the q language"""

    def __init__(self):
        namespace = q(r'\d')
        res = q('.Q.res')
        dot_q = q('1_key .q')
        self.path_completer = PathCompleter()
        self.words_info = [(list(res), 'k'),
                           (list(dot_q), 'q'),
                           (list(q.key(namespace)), str(namespace))]

    def get_completions(self, document, complete_event):
        # Detect a file handle
        m = HSYM_RE.match(document.text_before_cursor)
        if m:
            text = m.group(1)
            doc = Document(text, len(text))
            for c in self.path_completer.get_completions(doc, complete_event):
                yield c
        else:
            # Get word/text before cursor.
            word_before_cursor = document.get_word_before_cursor(False)
            for words, meta in self.words_info:
                for a in words:
                    if a.startswith(word_before_cursor):
                        yield Completion(a, -len(word_before_cursor),
                                         display_meta=meta)


def cmdloop(self, intro=None):
    style = style_from_pygments(BasicStyle, style_dict)
    self.preloop()
    stop = None
    while not stop:
        line = prompt(get_prompt_tokens=get_prompt_tokens, lexer=lexer,
                      get_bottom_toolbar_tokens=get_bottom_toolbar_tokens,
                      history=history, style=style, true_color=True,
                      on_exit='return-none', on_abort='return-none',
                      completer=QCompleter())
        if line is None or line.strip() == r'\\':
            raise SystemExit
        else:
            line = self.precmd(line)
            stop = self.onecmd(line)
        stop = self.postcmd(stop, line)
    self.postloop()
