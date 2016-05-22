Under MIT License, see LICENSE.txt
from nose.tools import *
from StrategyIA.Util.rrt import *

def test_init():
    a = Tree((24, 75))
    assert a.data == (24, 75)

@raises(TypeError)
def test_init_exception():
    a = Tree(None)
    a = Tree(true)
    a = Tree(4)

def test_add():
    a = Tree((24, 75))
    a.add((13, 42))
    assert len(a.childs) == 1

def test_find_nearest():
    a = Tree((24, 75))
    path = (50, 50)
    assert a.find_nearest(path) == (24, 75)
    a.add((49, 51))
    assert a.find_nearest(path) == (49, 51)

def test_find():
    a = Tree((24, 75));
    assert a == a.find((24, 75))
    b = (13, 42)
    a.add(b)
    c = Tree(b)
    assert c == a.find(b)
    assert a.find((99, 99)) is None

def test_get_all_nodes():
    a = Tree((24, 75))
    b = ((1, 2))
    c = ((13, 42))
    a.add(b)
    a.add(c)
    assert a.get_all_nodes() == [Tree((24, 75)), Tree((1, 2)), Tree((13, 42))]

def test_eq():
    a = Tree((24, 75))
    b = Tree((24, 75))
    assert a == b
    c = Tree((13, 13))
    d = Tree((13, 13))
    assert c == d
    assert not c == a

def test_lt():
    a = Tree((24, 75))
    b = Tree((24, 75))
    c = Tree((10, 75))
    d = Tree((24, 60))
    assert not a < b
    assert not b < a
    assert c < a
    assert d < a

def test_le():
    a = Tree((24, 75))
    b = Tree((10, 75))
    c = Tree((24, 75))

    assert b <= a
    assert c <= a

def test_gt():
    a = Tree((24, 75))
    b = Tree((99, 99))
    assert b > a

def test_ge():
    a = Tree((24, 75))
    b = Tree((99, 99))
    c = Tree((24, 75))

    assert b >= a and c >= a

def test_ne():
    a = Tree((24, 75))
    b = Tree((13, 42))
    assert a != b

def test_str():
    a = Tree((24, 75))
    s = "(24, 75)\n"
    assert str(a) == s
