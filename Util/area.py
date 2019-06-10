# Under MIT License, see LICENSE.txt
import math as m


# Question
from Util import Position


def is_inside_circle(position, center, radius):
    # Parameters assertions
    assert isinstance(position, Position)
    assert isinstance(center, Position)
    assert isinstance(radius, (int, float))
    assert radius >= 0

    return (position - center).norm < radius


def is_outside_circle(position, center, radius):
    return not is_inside_circle(position, center, radius)


def stay_inside_circle(position, center, radius):
    # Parameters assertions
    if is_inside_circle(position, center, radius):
        return Position(position.x, position.y)
    pos_angle = (position - center).angle
    pos_x = radius * m.cos(pos_angle) + center.x
    pos_y = radius * m.sin(pos_angle) + center.y
    return Position(pos_x, pos_y)


def stay_outside_circle(position, center, radius):
    # Parameters assertions
    if is_outside_circle(position, center, radius):
        return Position(position.x, position.y)
    pos_angle = (position - center).angle
    pos_x = radius * m.cos(pos_angle) + center.x
    pos_y = radius * m.sin(pos_angle) + center.y
    return Position(pos_x, pos_y)
