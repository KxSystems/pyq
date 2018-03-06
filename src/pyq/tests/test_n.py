from __future__ import absolute_import
import pytest

_n = pytest.importorskip('pyq._n')
numpy = _n.numpy

pytestmark = pytest.mark.skipif(
    [int(n) for n in numpy.__version__.split('.', 2)[:2]] < [1, 11],
    reason="numpy>=1.11 is not installed")


@pytest.fixture
def q_types(q):
    return q("{{key x$()}'[x t]!`short$t:where not null x}.Q.t")


@pytest.mark.parametrize('unit', [
    'Y', 'M'])
def test_get_unit(unit):
    a = numpy.empty([1], dtype='M8[%s]' % unit)
    assert unit == _n.get_unit(a)


def test_get_unit_error():
    a = numpy.zeros(0)
    with pytest.raises(TypeError):
        _n.get_unit(a)


@pytest.mark.parametrize('unit,x,y', [
    ('Y', '2001.01.01', '2001'),
    ('M', '2001.01.01', '2001-01'),
    ('D', '2001.01.01', '2001-01-01'),
    ('W', '1970.02.05', '1970-02-05'),
    ('h', '2001.01.01D01',
     '2001-01-01 01'),
    ('m', '2001.01.01D01:02',
     '2001-01-01 01:02:03.123456789'),
    ('s', '2001.01.01D01:02:03.123456789',
     '2001-01-01 01:02:03.123456789'),
    ('ns', '2001.01.01D01:02:03.123456789',
     '2001-01-01 01:02:03.123456789'),
    ('ps', '2001.01.01D01:02:03.123456789',
     '2001-01-01 01:02:03.123456789'),
])
def test_k2a_date(q, unit, x, y):
    dtype = 'M8[%s]' % unit
    a = numpy.empty([1], dtype)
    x = q(x).enlist
    _n.k2a(a, x)
    assert numpy.array_equiv(a, numpy.array([y], dtype))


def test_array(q):
    x = q('([]d:"d"$0 1;t:"t"$0 1)')
    a = _n.array(x)
    assert x.d == a['d']


def test_symbol_enum_mix(q):
    x = q('(`sym?`a`b;`x`y)')
    a = _n.array(x)
    assert a.tolist() == [['a', 'b'], ['x', 'y']]


def test_issue_615(q):
    x = q('0#`')
    a = _n.array(x)
    assert a.dtype == numpy.dtype('O')
