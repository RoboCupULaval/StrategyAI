# Under MIT License, see LICENSE.txt

from RULEngine.Util.Position import Position
import numpy as np
import math as m

ORIENTATION_ABSOLUTE_TOLERANCE = 0.004  # Half a degree of absolute tolerance


class Pose(object):

    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], Pose):
                position = args[0].position.copy()
                orientation = args[0].orientation
            elif isinstance(args[0], Position):  # Only a position object
                position = args[0].copy()
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
                raise TypeError
        elif len(args) == 2:  # Position and orientation or ndarray and orientation
            if isinstance(args[0], Position):
                position = args[0].copy()
                orientation = args[1]
            elif isinstance(args[0], np.ndarray):
                assert(args[0].size == 2),  'ndarray should be of length 2.'
                position = Position(args[0])
                orientation = args[1]
            else:
                raise TypeError
        else:  # Nothing is given, default case
            position = Position()
            orientation = 0

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

    def __add__(self, other: ('Pose', Position)):
        if isinstance(other, Pose):
            res = Pose(self.position + other.position, self.orientation + other.orientation)
        elif isinstance(other, Position):
            res = Pose(self.position + other, self.orientation)
        else:
            raise TypeError
        return res

    def __sub__(self, other: ('Pose', Position)):
        if isinstance(other, Pose):
            res = Pose(self.position - other.position, self.orientation - other.orientation)
        elif isinstance(other, Position):
            res = Pose(self.position - other, self.orientation)
        else:
            raise TypeError
        return res

    def __eq__(self, other: ('Pose', Position)):
        if isinstance(other, Position):
            return self.position == other
        elif isinstance(other, Pose):
            orientation_equal = Pose.compare_angle(self.orientation, other.orientation)
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

    @staticmethod
    def wrap_to_pi(angle):
        return (angle + np.pi) % (2 * np.pi) - np.pi

    @staticmethod
    def compare_angle(angle1, angle2, abs_tol=ORIENTATION_ABSOLUTE_TOLERANCE):
        return m.isclose(Pose.wrap_to_pi(angle1 - angle2), 0, abs_tol=abs_tol, rel_tol=0)

    def to_tuple(self):
        return self.position.x, self.position.y

    def conv_2_np(self) -> np.ndarray:
        return np.asarray(np.append(self.position, [self.orientation]))
