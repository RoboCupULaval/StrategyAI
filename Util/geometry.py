from cmath import sqrt

__author__ = 'jbecirovski'


def distance(position, other):
    return sqrt((position.x - other.x) ** 2 + (position.y - other.y) ** 2)