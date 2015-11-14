from UltimateStrat.STP.Skill.sPathAxis import *
from RULEngine.Util.Pose import Position
import math
from nose.tools import *

RADIUS = 111
DEAD_DELTA = 850

def test_union():
    mock = sPathAxis()
    r1 = range(1,2)
    r2 = range(1,5)
    assert mock.union(r1, r2) is True
    r3 = range(10, 15)
    assert mock.union(r2, r3) is False

def test_kx():
    mock = sPathAxis()
    a = Position(0, 0)
    b = Position(5, 0)
    angle = 0
    assert mock.kx(a, b, angle) == 5
    angle = math.pi/4
    r = mock.kx(a, b, angle)
    assert r == 7

    angle = math.pi/2
    r = mock.kx(a, b, angle)
    assert r == 0

    angle = (2*math.pi/3)
    r = mock.kx(a, b, angle)
    assert r == 0

    angle = -math.pi/2
    r = mock.kx(a, b, angle)
    assert r == 0

def test_ky():
    mock = sPathAxis()
    a = Position(0, 0)
    b = Position(0, 5)
    angle = math.pi/2
    r = mock.ky(a, b, angle)
    assert r == 5

    angle = math.pi/4
    r = mock.ky(a, b, angle)
    assert r == 7

    angle = 0
    r = mock.ky(a, b, angle)
    assert r == 0

    angle = math.pi
    r = mock.ky(a, b, angle)
    assert r == 0

    angle = -math.pi
    r = mock.ky(a, b, angle)
    assert r == 0

def test_radf():
    mock = sPathAxis()
    f = math.cos
    r = 5
    angle = 0
    a = mock.radf(f, r, angle)
    assert a == 5

    angle = math.pi/2
    a = mock.radf(f, r, angle)
    assert a == 0

    f = math.sin
    angle = 0
    a = mock.radf(f, r, angle)
    assert a == 0

    angle = math.pi/2
    a = mock.radf(f, r, angle)
    assert a == 5

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
    mock.target = Position(RADIUS+DEAD_DELTA+1, 0)
    mock.path()
    print(mock.paths)
    assert mock.paths == Position(DEAD_DELTA+1, 0)

    # Devant la balle, mais meme y
    mock.target = Position(-RADIUS-DEAD_DELTA-1, 0)
    mock.path()
    print(mock.paths)
    assert mock.paths == Position(0, -222)

    # Devant la balle, meme y, en negatif
    mock.pose = Position(-10, -10)
    mock.target = Position(-200, -10)
    mock.path()
    print(mock.paths)
    assert mock.paths == Position(-10, -10)

def test_path_FT():
    mock = sPathAxis()
    mock.pose = Position(0,0)
    mock.orientation = 0

    # y_axis True
    mock.pose = Position(0, 0)
    mock.target = Position(250, RADIUS+DEAD_DELTA+1)
    mock.path()
    print(mock.paths)
    assert mock.paths == Position(0, RADIUS+DEAD_DELTA+1)
    t = 0 - RADIUS - DEAD_DELTA - 1
    mock.target = Position(250, t)
    mock.path()
    print(mock.paths)
    assert mock.paths == Position(0, -RADIUS-DEAD_DELTA-1)

def test_path_FF():
    mock = sPathAxis()
    mock.pose = Position(0,0)
    mock.orientation = 0

    mock.target = Position(1000, 1000)
    mock.path()
    a = mock.paths
    assert a == Position(889, 0)
    mock.pose = mock.paths
    mock.path()
    a = mock.paths
    assert a == Position(889, 1000)
