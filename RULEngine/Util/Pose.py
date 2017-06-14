# Under MIT License, see LICENSE.txt
import numpy as np
import math as m
from typing import Union

from RULEngine.Util.Position import Position
from RULEngine.Util.constant import ORIENTATION_ABSOLUTE_TOLERANCE


class Pose(object):

    def __init__(self, *args):

        if len(args) == 0:
            position = Position()
            orientation = 0
        elif len(args) == 1:
            if isinstance(args[0], Pose):  # From another Pose object
                position = Position(args[0].position)
                orientation = args[0].orientation
            elif isinstance(args[0], Position):  # Only a position object
                position = Position(args[0])
                orientation = 0
            elif isinstance(args[0], np.ndarray):  # Only a ndarray
                if args[0].size == 3:
                    position = Position(args[0][0:2])
                    orientation = args[0][2]
                elif args[0].size == 2:
                    position = Position(args[0])
                    orientation = 0
                else:
                    raise ValueError
            else:
                raise ValueError
        elif len(args) == 2:  # Position and orientation or ndarray and orientation
            if isinstance(args[0], (Position, np.ndarray)):
                if isinstance(args[0], np.ndarray):
                    assert(args[0].size == 2),  'ndarray should be of length 2.'
                position = Position(args[0])
                orientation = args[1]
            else:
                raise ValueError
        elif len(args) == 3:
            position = Position(args[0:2])
            orientation = args[2]
        else:
            raise ValueError

        # wrap the orientation between -pi and pi
        self._orientation = float(Pose.wrap_to_pi(orientation))
        self._position = position

    @property
    def position(self) -> Position:
        return self._position

    @position.setter
    def position(self, position: (Position, np.ndarray)):
        if isinstance(position, Position):
            self._position = position
        else:
            self._position = Position(position)

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation):
        self._orientation = Pose.wrap_to_pi(orientation)

    def __add__(self, other: Union['Pose', Position]):
        if isinstance(other, Pose):
            res = Pose(self.position + other.position, self.orientation + other.orientation)
        elif isinstance(other, Position):
            res = Pose(self.position + other, self.orientation)
        else:
            raise TypeError
        return res

    def __sub__(self, other: Union['Pose', Position]):
        if isinstance(other, Pose):
            res = Pose(self.position - other.position, self.orientation - other.orientation)
        elif isinstance(other, Position):
            res = Pose(self.position - other, self.orientation)
        else:
            raise TypeError
        return res

    def __eq__(self, other: Union['Pose', Position]):
        if isinstance(other, Position):
            return self.position == other
        elif isinstance(other, Pose):
            orientation_equal = self.compare_orientation(other.orientation)
            position_equal = self.position == other.position
            return position_equal and orientation_equal
        else:
            raise TypeError

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '{}, orientation = {:5.3f}'.format(self.position, self.orientation)

    def __repr__(self):
        return 'Pose({},{:7.3f})'.format(self.position, self.orientation)

    def __getitem__(self, item):
        assert(isinstance(item, int)), 'getitem only support integer indexing'
        if 0 <= item < 2:
            return self.position[item]
        elif item == 2:
            return self.orientation
        else:
            raise IndexError('Out of range')

    def scale(self, value):
        return Pose(self.position * value, self.orientation)

    @staticmethod
    def wrap_to_pi(angle):
        return (angle + np.pi) % (2 * np.pi) - np.pi

    def compare_orientation(self, other, abs_tol=ORIENTATION_ABSOLUTE_TOLERANCE):
        if isinstance(other, (int, float, np.generic)):
            angle = other
        elif isinstance(other, Pose):
            angle = other.orientation
        else:
            raise TypeError

        return m.isclose(Pose.wrap_to_pi(self.orientation - angle), 0, abs_tol=abs_tol, rel_tol=0)

    def to_array(self):
        return np.array([self.position.x, self.position.y, self.orientation])

    def to_tuple(self):
        return self.position.x, self.position.y

    def conv_2_np(self) -> np.ndarray:
        """Legacy. Do not use."""
        return self.to_array()
