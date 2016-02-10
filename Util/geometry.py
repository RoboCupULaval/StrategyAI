from math import sqrt

__author__ = 'jbecirovski'


def distance(position, other):
    if position.x == other.x and position.y == other.y:
        return 0
    else:
        return sqrt((position.x - other.x) ** 2 + (position.y - other.y) ** 2)


def get_milliseconds(time_mil):
    # Convert time.time() to milliseconds int
    assert isinstance(time_mil, float)
    return int(round(time_mil * 1000))