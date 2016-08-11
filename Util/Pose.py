#Under MIT License, see LICENSE.txt
from .Position import Position
import math as m

ORIENTATION_DELTA_TOLERANCE_MAGNITUDE = 1e4

class Pose(object):
    """  Container of position and orientation """
    def __init__(self, position=Position(), orientation=0.0):
        assert(isinstance(position, Position)), 'position should be Position object.'
        assert(isinstance(orientation, (int, float))), 'orientation should be int or float value.'

        self.position = position
        self.orientation = orientation
        if self.orientation >= m.pi:
            self.orientation -= 2 * m.pi
        elif self.orientation <= -m.pi:
            self.orientation += 2*m.pi

    def __str__(self):
        return '[{}, theta={}]'.format(self.position, self.orientation)
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        orientation_left_side = int(self.orientation * ORIENTATION_DELTA_TOLERANCE_MAGNITUDE)
        orientation_right_side = int(other.orientation * ORIENTATION_DELTA_TOLERANCE_MAGNITUDE)
        orientation_test = orientation_left_side == orientation_right_side
        return self.position == other.position and orientation_test

    def __ne__(self, other):
        return not self.__eq__(other)
