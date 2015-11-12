from UltimateStrat.Executor.PFAxisExecutor import *
from PythonFramework.Util.Position import Position

def test_init():
    assert False

def test_exec():
    assert False

def test_ballx():
    mock = PFAxisExecutor(None)
    mock.pose = Position(0, 0)
    mock.orientation = 0

    mock.target = Position(50, 50)
    assert mock.is_ball_x() is True

    mock.target = Position(-50, 50)
    assert mock.is_ball_x() is True

    mock.target = Position(50, 400)
    assert mock.is_ball_x() is False

def test_bally():
    assert False
