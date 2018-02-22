# Under MIT License, see LICENSE.txt
import math as m

from Util.position import Position

ORIENTATION_ABSOLUTE_TOLERANCE = 0.004


class Pose(object):

    def __init__(self, position: Position=Position(), orientation: float=0):

        self._orientation = wrap_to_2pi(orientation)
        self._position = position

    @property
    def x(self) -> float:
        return self._position.x

    @x.setter
    def x(self, new_x):
        self.position.x = new_x

    @property
    def y(self) -> float:
        return self._position.y

    @y.setter
    def y(self, new_y):
        self.position.y = new_y

    @property
    def position(self) -> Position:
        return self._position

    @position.setter
    def position(self, position: Position):
            self._position = position.copy()

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation):
        self._orientation = wrap_to_2pi(orientation)

    def __add__(self, other: Position):
        res = Pose(self.position + other, self.orientation)
        return res

    def __sub__(self, other: Position):
        res = Pose(self.position - other, self.orientation)
        return res

    def __eq__(self, other):
        orientation_equal = compare_angle(self.orientation, other.orientation, ORIENTATION_ABSOLUTE_TOLERANCE)
        position_equal = self.position == other.position
        return position_equal and orientation_equal

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '{}, orientation = {:5.3f}'.format(self.position, self.orientation)

    def __repr__(self):
        return 'Pose' + str(self)

    @classmethod
    def from_dict(cls, my_dict):
        return Pose(Position(my_dict['x'], my_dict['y']), my_dict['orientation'])

    @classmethod
    def from_values(cls, x, y, orientation):
        return cls(Position(x, y), orientation)

    def to_dict(self):
        return {'x': self.x, 'y': self.y, 'orientation': self.orientation}


def wrap_to_pi(angle):
    return (angle + m.pi) % (2 * m.pi) - m.pi


def wrap_to_2pi(angle):
    return angle % (2 * m.pi)


def compare_angle(angle1, angle2, abs_tol=0.004):
    return m.isclose(wrap_to_pi(angle1 - angle2), 0, abs_tol=abs_tol, rel_tol=0)
