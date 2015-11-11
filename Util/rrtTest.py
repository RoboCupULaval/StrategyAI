from nose.tools import *
from StrategyIA.Util.rrt import *

def test_init():
    a = Tree((24, 75))
    assert a.data == (24, 75)

@raises(TypeError)
def test_init_exception():
    a = Tree(None)
