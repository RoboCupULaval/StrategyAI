# Under MIT License, see LICENSE.txt
import math as m
import numpy as np

from Util.position import Position

ORIENTATION_ABSOLUTE_TOLERANCE = 0.004


class Pose:

    def __init__(self, position: Position=Position(), orientation: float=0):

        self._orientation = orientation
        self._position = position.copy()

    @classmethod
    def from_dict(cls, my_dict):
        return cls(Position(my_dict['x'], my_dict['y']), my_dict['orientation'])

    @classmethod
    def from_values(cls, x, y, orientation=0):
        return cls(Position(x, y), orientation)

    @property
    def x(self) -> float:
        return self._position.x

    @x.setter
    def x(self, new_x: float):
        self.position.x = new_x

    @property
    def y(self) -> float:
        return self._position.y

    @y.setter
    def y(self, new_y: float):
        self.position.y = new_y

    @property
    def position(self) -> Position:
        return self._position

    @position.setter
    def position(self, position: Position):
        self._position = position.copy()

    @property
    def norm(self):
        return self.position.norm

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation):
        self._orientation = orientation

    def to_array(self):
        return np.array([self.x, self.y, self.orientation])

    def to_dict(self):
        return {'x': self.x, 'y': self.y, 'orientation': self.orientation}

    def __add__(self, other: Position):
        assert(isinstance(other, Position))
        return Pose(self.position + other, self.orientation)

    def __sub__(self, other: Position):
        return self + (-other)

    def __eq__(self, other):
        orientation_equal = m.isclose(self.orientation, other.orientation,
                                      abs_tol=ORIENTATION_ABSOLUTE_TOLERANCE, rel_tol=0)
        position_equal = self.position == other.position
        return position_equal and orientation_equal

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '{}, orientation = {:5.3f}'.format(self.position, self.orientation)

    def __repr__(self):
        return 'Pose' + str(self)
