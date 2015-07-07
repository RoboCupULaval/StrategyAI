from ..Util.Position import Position
from ..Util.geometry import *
import math as m

__author__ = 'jbecirovski'

# Question
def isInsideSquare(position, X_TOP, X_BOTTOM, Y_LEFT, Y_RIGHT):
    # Parameters assertions
    assert(isinstance(position, Position))
    assert(isinstance(X_TOP, (int, float)))
    assert(isinstance(X_BOTTOM, (int, float)))
    assert(isinstance(Y_LEFT, (int, float)))
    assert(isinstance(Y_RIGHT, (int, float)))
    assert(X_TOP > X_BOTTOM)
    assert(Y_RIGHT > Y_LEFT)

    if not X_TOP < position.x < X_BOTTOM:
        return False
    if not Y_LEFT < position.y < Y_RIGHT:
        return False
    return True

def isInsideCircle(position, center, radius):
    # Parameters assertions
    assert(isinstance(position, Position))
    assert(isinstance(center, Position))
    assert(isinstance(radius, (int, float)))
    assert(radius >= 0)

    if distance(position, center) < radius:
        return True
    else:
        return False

def isOutsideSquare(position, X_TOP, X_BOTTOM, Y_LEFT, Y_RIGHT):
    return not isInsideSquare(position, X_TOP, X_BOTTOM, Y_LEFT, Y_RIGHT)

def isOutsideCircle(position, center, radius):
    return not isInsideCircle(position, center, radius)

# Reform
def stayInsideSquare(position, X_TOP, X_BOTTOM, Y_LEFT, Y_RIGHT):
    # Parameters assertions
    assert(isinstance(position, Position))
    assert(isinstance(X_TOP, (int, float)))
    assert(isinstance(X_BOTTOM, (int, float)))
    assert(isinstance(Y_LEFT, (int, float)))
    assert(isinstance(Y_RIGHT, (int, float)))
    assert(X_TOP > X_BOTTOM)
    assert(Y_RIGHT > Y_LEFT)

    if isInsideSquare(position, X_TOP, X_BOTTOM, Y_LEFT, Y_RIGHT):
        return Position(position.x, position.y)
    else:
        pos_x = position.x
        pos_y = position.y

        if pos_x > X_TOP:
            pos_x = X_TOP
        elif pos_x < X_BOTTOM:
            pos_x = X_BOTTOM

        if pos_y > Y_RIGHT:
            pos_y = Y_RIGHT
        elif pos_y < Y_LEFT:
            pos_y = Y_LEFT

        return Position(pos_x, pos_y)

def stayInsideCircle(position, center, radius):
    # Parameters assertions
    if isInsideCircle(position, center, radius):
        return Position(position.x, position.y)
    else:
        pos_angle = m.radians(angle(center, position))
        pos_x = radius * m.cos(pos_angle)
        pos_y = radius * m.sin(pos_angle)
        return Position(pos_x, pos_y)


def stayOutsideSquare(position, X_TOP, X_BOTTOM, Y_LEFT, Y_RIGHT):
    # Parameters assertions
    assert(isinstance(position, Position))
    assert(isinstance(X_TOP, (int, float)))
    assert(isinstance(X_BOTTOM, (int, float)))
    assert(isinstance(Y_LEFT, (int, float)))
    assert(isinstance(Y_RIGHT, (int, float)))
    assert(X_TOP > X_BOTTOM)
    assert(Y_RIGHT > Y_LEFT)

    if isOutsideSquare(position, X_TOP, X_BOTTOM, Y_LEFT, Y_RIGHT):
        return Position(position.x, position.y)
    else:
        pos_x = position.x
        pos_y = position.y

        if pos_x < X_TOP:
            pos_x = X_TOP
        elif pos_x > X_BOTTOM:
            pos_x = X_BOTTOM

        if pos_y < Y_RIGHT:
            pos_y = Y_RIGHT
        elif pos_y > Y_LEFT:
            pos_y = Y_LEFT

        return Position(pos_x, pos_y)

def stayOutsideCircle(position, center, radius):
    # Parameters assertions
    if isOutsideCircle(position, center, radius):
        return Position(position.x, position.y)
    else:
        pos_angle = m.radians(angle(center, position))
        pos_x = radius * m.cos(pos_angle)
        pos_y = radius * m.sin(pos_angle)
        return Position(pos_x, pos_y)