from math import *

from RULEngine.Util import Position
from RULEngine.Util.Position import Position

__author__ = 'RoboCupULaval'


def distance(position, other):
    if position.x == other.x and position.y == other.y:
        return 0
    else:
        return sqrt((position.x - other.x) ** 2 + (position.y - other.y) ** 2)


def get_milliseconds(time_mil):
    # Convert time.time() to milliseconds int
    assert isinstance(time_mil, float)
    return int(round(time_mil * 1000))


def get_intersection(line1, line2):
    """
        Args:
            line1: first line (a tuple of 2 Position objects)
            line2: second line (a tuple of 2 Position objects)

        Returns: The position where the two lines will intersect.  Infinity if the lines are parallels.
    """
    return get_determinant(line1[0], line1[1], line2[0], line2[1])
    # return line_intersection(line1, line2)


def get_determinant(point_a1, point_a2, point_b1, point_b2):
    """
    Args:
        point_a1: Point 1 on line A
        point_a2: Point 2 on line A
        point_b1: Point 1 on line B
        point_b2: Point 2 on line B

    Returns: The intersection point using determinants.
    """
    x1 = point_a1.x
    y1 = point_a1.y
    x2 = point_a2.x
    y2 = point_a2.y

    x3 = point_b1.x
    y3 = point_b1.y
    x4 = point_b2.x
    y4 = point_b2.y

    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denominator == 0:
        # The lines are parallels
        return Position(9999999, 9999999)

    # The purpose of the determinant det1 and det2 is to reduce the number of multiplications
    det1 = x1 * y2 - y1 * x2
    det2 = x3 * y4 - y3 * x4
    p_x = (det1 * (x3 - x4) - det2 * (x1 - x2)) / denominator
    p_y = (det1 * (y3 - y4) - det2 * (y1 - y2)) / denominator

    return Position(p_x, p_y)


def det(a, b):
    return a.x * b.y - a.y * b.x


def line_intersection(line1, line2):
    xdiff = Position(line1[0].x - line1[1].x, line2[0].x - line2[1].x)
    ydiff = Position(line1[0].y - line1[1].y, line2[0].y - line2[1].y)

    div = det(xdiff, ydiff)
    if div == 0:
        return Position(9999999, 9999999)

    d = Position(det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return Position(x, y)

    # print line_intersection((A, B), (C, D))


def get_modulus(vector):
    """
    Args:
        vector: vector with the form of (Position, Position)

    Returns: the modulus of the vector
    """
    assert isinstance(vector, (Position, Position))
    return sqrt(vector[0] ** 2 + vector[1] ** 2)


def get_orthogonal(vector, initial_position):
    """
    Args:
        vector: a vector with the form (Position, Position)
        initial_position: the start of the orthogonal vector

    Returns: an orthogonal vector
    """
    assert isinstance(vector, (Position, Position))
    # assert vector != Position(0, 0), 'vector should not be null'
    return initial_position, Position(-vector.y, vector.x) + initial_position


def get_first_to_arrive(distance1, speed1, acceleration1, distance2, speed2, acceleration2):
    """
    Args:
        distance1: The distance to be completed by the object 1
        speed1: object's 1 speed
        acceleration1: object's 1 acceleration
        distance2: The distance to be completed by the object 2
        speed2: object's 2 speed
        acceleration2: object's 2 acceleration

    Returns: 1 if the object 1 will arrive first to it's destination. 2 otherwise
    """

    if speed1 == 0 or speed2 == 0:
        return 0
    else:
        time1 = get_time_to_travel(distance1, speed1, acceleration1)
        time2 = get_time_to_travel(distance2, speed2, acceleration2)

        return 2 if time1 < time2 else 1


def get_time_to_travel(dist, speed, accel):
    """
    Args:
        dist: distance
        speed: speed
        accel: acceleration

    Returns: The time to complete the distance
    """

    if accel == 0:
        if speed == 0:
            return 9999999
        else:
            return dist / speed
    else:
        time1 = (-speed + sqrt(speed ** 2 - 2 * accel * dist)) / accel
        time2 = (-speed - sqrt(speed ** 2 - 2 * accel * dist)) / accel

        return time2 if time1 < time2 else time1