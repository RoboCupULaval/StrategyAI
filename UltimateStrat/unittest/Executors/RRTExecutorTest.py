from nose.tools import *
from StrategyIA.UltimateStrat.Executor.RRTExecutor import *

def test_norm():
    a = (4, 5)
    b = (1, 1)
    assert norm(a, b) == 5
