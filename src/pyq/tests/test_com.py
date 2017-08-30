from __future__ import absolute_import
import pytest

from pyq import K, kerr, Q_OS
# See #942
from pyq.conftest import kdb_server

WIN = Q_OS.startswith('w')


def test_connection(q, kdb_server):
    c = kdb_server
    assert c('.z.K') == q('.z.K')


def test_async_call(kdb_server):
    c = -kdb_server
    c(K.string("x:42"))
    assert kdb_server('x') == 42


def test_closed_connection(kdb_server):
    cmd = K.string("exit 0")
    with pytest.raises(kerr) as info:
        kdb_server(cmd)
    msg = info.value.args[0]
    if WIN:
        assert msg.startswith('rcv.')
    else:
        assert msg == 'close'
