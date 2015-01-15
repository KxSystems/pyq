import pytest

@pytest.yield_fixture
def q():
    """clean and restore q's global namespace"""
    from pyq import q as _q

    ns = _q.value('.')
    _q("delete from `.")

    yield _q

    _q.set('.', ns)
