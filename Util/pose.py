# Under MIT License, see LICENSE.txt
import math as m
from typing import Union

import numpy as np

from .constant import ORIENTATION_ABSOLUTE_TOLERANCE
from .position import Position


class Pose(object):

    def __init__(self, *args):
        position, orientation = self._pose_builder(args)

        # wrap the orientation between -pi and pi
        self._orientation = float(Pose.wrap_to_pi(orientation))
        self._position = position

    @property
    def x(self) -> Position:
        return self._position.x

    @property
    def y(self) -> Position:
        return self._position.y

    @property
    def position(self) -> Position:
        return self._position

    @position.setter
    def position(self, position: (Position, np.ndarray)):
            self._position = Position(position)

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation):
        self._orientation = Pose.wrap_to_pi(orientation)

    def __add__(self, other):
        if isinstance(other, Pose):
            res = Pose(self.position + other.position, self.orientation + other.orientation)
        elif isinstance(other, Position):
            res = Pose(self.position + other, self.orientation)
        else:
            raise TypeError
        return res

    def __sub__(self, other):
        if isinstance(other, Pose):
            res = Pose(self.position - other.position, self.orientation - other.orientation)
        elif isinstance(other, Position):
            res = Pose(self.position - other, self.orientation)
        else:
            raise TypeError
        return res

    def __eq__(self, other):
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
        if isinstance(other, (int, float, np.number)):
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

    def _pose_builder(self, args):
        """ This pose builder method allows us to keep the __init__ method of
            pose clean, while doing the multiple if/else if outside of it.
            TODO : Find a more elegant way of doing this, either with @singleDispatch or
            by reducing the possible constructor arguments. -DC, 16/06/2017
        """
        builders = {
            1: self._build_from_single,
            2: self._build_from_double,
            3: self._build_from_triple
        }

        if not args:
            return Position(), 0
        elif len(args) in builders:
            return builders[len(args)](args)
        else:
            raise ValueError

    def _build_from_single(self, arg):
        # At some points, we pass a unary tuple instead of a useful object. This breaks the if conditions, so we
        # extract the desired object from the tuple before type-checking it.
        if isinstance(arg, tuple):
            arg = arg[0]

        if isinstance(arg, Pose):  # From another Pose object
            position = arg.position.copy()
            orientation = arg.orientation
        elif isinstance(arg, Position):  # Only a position object
            position = arg.copy()
            orientation = 0
        elif isinstance(arg, np.ndarray):  # Only a ndarray
            if arg.size == 3:
                position = Position(arg[0:2])
                orientation = arg[2]
            elif arg.size == 2:
                position = Position(arg)
                orientation = 0
            else:
                raise ValueError
        else:
            raise ValueError

        return position, orientation

    def _build_from_double(self, args):
        if isinstance(args[0], Position) or (isinstance(args[0], np.ndarray) and args[0].size == 2):
            # ndArray size must be 2
            position = args[0].copy()
            orientation = args[1]
        else:
            raise ValueError

        return position, orientation

    def _build_from_triple(self, args):
        position = Position(args[0:2])
        orientation = args[2]

        return position, orientation

    @classmethod
    def from_dict(cls, dict):
        return Pose(dict["x"], dict["y"], dict["orientation"])

    def to_dict(self):
        return {'x': self.x, 'y': self.y, 'orientation': self.orientation}
