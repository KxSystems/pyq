def test_version():
    from pyq import __version__ as v

    assert v != 'unknown'
