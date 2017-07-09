# Under MIT License, see LICENSE.txt
from ..Util.Position import Position
from ..Util.geometry import *
import math as m
from ..Util.constant import *

__author__ = 'RoboCupULaval'


# Question
def isInsideSquare(position, Y_TOP, Y_BOTTOM, X_LEFT, X_RIGHT):
    # Parameters assertions
    assert(isinstance(position, Position))
    assert(isinstance(Y_TOP, (int, float)))
    assert(isinstance(Y_BOTTOM, (int, float)))
    assert(isinstance(X_LEFT, (int, float)))
    assert(isinstance(X_RIGHT, (int, float)))
    assert(Y_TOP > Y_BOTTOM)
    assert(X_RIGHT > X_LEFT)

    if not Y_BOTTOM < position.y < Y_TOP:
        return False
    if not X_LEFT < position.x < X_RIGHT:
        return False
    return True


def is_inside_circle(position, center, radius):
    # Parameters assertions
    assert(isinstance(position, Position))
    assert(isinstance(center, Position))
    assert(isinstance(radius, (int, float)))
    assert(radius >= 0)

    if (position - center).norm() < radius:
        return True
    else:
        return False


def isOutsideSquare(position, X_TOP, X_BOTTOM, Y_LEFT, Y_RIGHT):
    return not isInsideSquare(position, X_TOP, X_BOTTOM, Y_LEFT, Y_RIGHT)


def isOutsideCircle(position, center, radius):
    return not is_inside_circle(position, center, radius)


# Reform
def stayInsideSquare(position, Y_TOP, Y_BOTTOM, X_LEFT, X_RIGHT):
    # Parameters assertions
    assert(isinstance(position, Position))
    assert(isinstance(Y_TOP, (int, float)))
    assert(isinstance(Y_BOTTOM, (int, float)))
    assert(isinstance(X_LEFT, (int, float)))
    assert(isinstance(X_RIGHT, (int, float)))
    assert(Y_TOP > Y_BOTTOM)
    assert(X_RIGHT > X_LEFT)

    if isInsideSquare(position, Y_TOP, Y_BOTTOM, X_LEFT, X_RIGHT):
        return Position(position.x, position.y)
    else:
        pos_x = position.x
        pos_y = position.y

        if pos_y > Y_TOP:
            pos_y = Y_TOP
        elif pos_y < Y_BOTTOM:
            pos_y = Y_BOTTOM

        if pos_x > X_RIGHT:
            pos_x = X_RIGHT
        elif pos_x < X_LEFT:
            pos_x = X_LEFT

        return Position(pos_x, pos_y)


def stayInsideCircle(position, center, radius):
    # Parameters assertions
    if is_inside_circle(position, center, radius):
        return Position(position.x, position.y)
    else:
        pos_angle = (position - center).angle()
        pos_x = radius * m.cos(pos_angle) + center.x
        pos_y = radius * m.sin(pos_angle) + center.y
        return Position(pos_x, pos_y)


def stayOutsideSquare(position, Y_TOP, Y_BOTTOM, X_LEFT, X_RIGHT):
    # Parameters assertions
    assert(isinstance(position, Position))
    assert(isinstance(Y_TOP, (int, float)))
    assert(isinstance(Y_BOTTOM, (int, float)))
    assert(isinstance(X_LEFT, (int, float)))
    assert(isinstance(X_RIGHT, (int, float)))
    assert(Y_TOP > Y_BOTTOM)
    assert(X_RIGHT > X_LEFT)

    if isOutsideSquare(position, Y_TOP, Y_BOTTOM, X_LEFT, X_RIGHT):
        return Position(position.x, position.y)
    else:
        pos_x = position.x
        pos_y = position.y

        if pos_y < Y_TOP:
            pos_y = Y_TOP
        elif pos_y > Y_BOTTOM:
            pos_y = Y_BOTTOM

        if pos_x < X_RIGHT:
            pos_x = X_RIGHT
        elif pos_x > X_LEFT:
            pos_x = X_LEFT

        return Position(pos_x, pos_y)


def stayOutsideCircle(position, center, radius):
    # Parameters assertions
    if isOutsideCircle(position, center, radius):
        return Position(position.x, position.y)
    else:
        pos_angle = get_angle(center, position)
        pos_x = radius * m.cos(pos_angle) + center.x
        pos_y = radius * m.sin(pos_angle) + center.y
        return Position(pos_x, pos_y)
