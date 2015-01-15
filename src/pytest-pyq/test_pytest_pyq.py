def test_q1(q):
    assert q.get('.').count == 0
    q.foo = 42
    assert q.get('.').count == 1

def test_q2(q):
    assert q.get('.').count == 0
