from UltimateStrat.STP.Skill.sPathAxis import *
from PythonFramework.Util.Pose import Position
import math

def test_ball_on_axis():
    mock = sPathAxis()
    mock.pose = Position(0, 0)
    mock.orientation = 0
    y = True

    mock.target = Position(50, 50)
    assert mock.ball_on_axis() is True
    assert mock.ball_on_axis(y) is True

    mock.target = Position(-50, 50)
    assert mock.ball_on_axis() is True
    assert mock.ball_on_axis(y) is True

    mock.target = Position(50, 500)
    assert mock.ball_on_axis() is False
    assert mock.ball_on_axis(y) is True

    mock.target = Position(50, -50)
    assert mock.ball_on_axis(y) is True

    mock.target = Position(600, 50)
    assert mock.ball_on_axis(y) is False

def test_union():
    mock = sPathAxis()
    r1 = range(1,2)
    r2 = range(1,5)
    assert mock.union(r1, r2) is True
    r3 = range(10, 15)
    assert mock.union(r2, r3) is False

def test_path_TT():
    mock = sPathAxis()
    mock.pose = Position(0,0)
    mock.orientation = 0

    # edge case, shouldn't happen!
    mock.target = Position(0,0)
    mock.path()
    assert mock.paths == Position(0,0)

def test_path_TF():
    mock = sPathAxis()
    mock.pose = Position(0,0)
    mock.orientation = 0

    # derriere la balle, mais loin
    mock.target = Position(500, 0)
    mock.path()
    assert mock.paths == Position(90, 0)

    mock.orientation = math.pi/4
    mock.path()
    assert not mock.paths == Position(90, 0)
    assert Position(math.floor(mock.paths.x), math.floor(mock.paths.y)) == Position(63, 63)

    mock.orientation = 0

    # ROBOT_RADIUS * + BALL_RADIUS
    mock.target = Position(112, 0)
    mock.path()
    assert mock.paths == Position(1, 0)

    # Devant la balle, mais meme y
    mock.target = Position(-150, 0)
    mock.path()
    print(mock.paths)
    assert mock.paths == Position(0, -90)

    # Devant la balle, meme y, en negatif
    mock.pose = Position(-10, -10)
    mock.target = Position(-200, -10)
    mock.path()
    assert mock.paths == Position(-10, 80)

def test_path_FT():
    mock = sPathAxis()
    mock.pose = Position(0,0)
    mock.orientation = 0

    # y_axis True
    mock.pose = Position(0, 0)
    mock.target = Position(0, -200)
    mock.path()
    assert mock.paths == Position(-90, 0)

    mock.taget = Position(0, 200)
    mock.path()
    assert mock.paths == Position(-90, 0)

def test_path_FF():
    mock = sPathAxis()
    mock.pose = Position(0,0)
    mock.orientation = 0

    # on est derriere la balle
    mock.target = Position(200, 200)
    mock.path()
    assert mock.paths == Position(0, 90)

    mock.target = Position(200, 70)
    mock.path()
    assert mock.paths == Position(0, 70)

    mock.target = Position(200, -200)
    mock.path()
    assert mock.paths == Position(0, -90)

    mock.target = Position(200, -70)
    mock.path()
    assert mock.paths == Position(0, -70)

    # on est devant la balle
    mock.target = Position(-200, -200)
    mock.path()
    print(mock.paths)
    assert mock.paths == Position(-90, 0)

