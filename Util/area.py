# Under MIT License, see LICENSE.txt
import math as m


# Question
from Util import Position


# noinspection PyPep8Naming
def is_inside_square(position, y_top, y_bottom, x_left, x_right):
    # Parameters assertions
    assert isinstance(position, Position)
    assert isinstance(y_top, (int, float))
    assert isinstance(y_bottom, (int, float))
    assert isinstance(x_left, (int, float))
    assert isinstance(x_right, (int, float))
    assert y_top > y_bottom
    assert x_right > x_left

    if not y_bottom < position.y < y_top:
        return False
    if not x_left < position.x < x_right:
        return False
    return True


def is_inside_circle(position, center, radius):
    # Parameters assertions
    assert isinstance(position, Position)
    assert isinstance(center, Position)
    assert isinstance(radius, (int, float))
    assert radius >= 0

    return (position - center).norm < radius


# noinspection PyPep8Naming
def is_outside_square(position, x_top, x_bottom, y_left, y_right):
    return not is_inside_square(position, x_top, x_bottom, y_left, y_right)


# noinspection PyPep8Naming
def is_outside_circle(position, center, radius):
    return not is_inside_circle(position, center, radius)


# Reform
# noinspection PyPep8Naming
def stay_inside_square(position, y_top, y_bottom, x_left, x_right):
    # Parameters assertions
    assert isinstance(position, Position)
    assert isinstance(y_top, (int, float))
    assert isinstance(y_bottom, (int, float))
    assert isinstance(x_left, (int, float))
    assert isinstance(x_right, (int, float))
    assert y_top > y_bottom
    assert x_right > x_left

    if is_inside_square(position, y_top, y_bottom, x_left, x_right):
        return Position(position.x, position.y)
    else:
        pos_x = position.x
        pos_y = position.y

        if pos_y > y_top:
            pos_y = y_top
        elif pos_y < y_bottom:
            pos_y = y_bottom

        if pos_x > x_right:
            pos_x = x_right
        elif pos_x < x_left:
            pos_x = x_left

        return Position(pos_x, pos_y)


# noinspection PyPep8Naming
def stay_inside_circle(position, center, radius):
    # Parameters assertions
    if is_inside_circle(position, center, radius):
        return Position(position.x, position.y)
    pos_angle = (position - center).angle
    pos_x = radius * m.cos(pos_angle) + center.x
    pos_y = radius * m.sin(pos_angle) + center.y
    return Position(pos_x, pos_y)


# noinspection PyPep8Naming
def stay_outside_square(position, y_top, y_bottom, x_left, x_right):
    # Parameters assertions
    assert isinstance(position, Position)
    assert isinstance(y_top, (int, float))
    assert isinstance(y_bottom, (int, float))
    assert isinstance(x_left, (int, float))
    assert isinstance(x_right, (int, float))
    assert y_top > y_bottom
    assert x_right > x_left

    if is_outside_square(position, y_top, y_bottom, x_left, x_right):
        return Position(position.x, position.y)
    pos_y = y_top if position.y > y_top - (y_top - y_bottom) / 2 else y_bottom
    pos_x = x_right if position.x > x_right - (x_right - x_left) / 2 else x_left

    return Position(pos_x, pos_y)


# noinspection PyPep8Naming
def stay_outside_circle(position, center, radius):
    # Parameters assertions
    if is_outside_circle(position, center, radius):
        return Position(position.x, position.y)
    pos_angle = (position - center).angle
    pos_x = radius * m.cos(pos_angle) + center.x
    pos_y = radius * m.sin(pos_angle) + center.y
    return Position(pos_x, pos_y)
