# Under MIT License, see LICENSE.txt

from typing import Dict

import numpy as np

import Util.position
Position = Util.position.Position

import Util.geometry as geometry


ORIENTATION_ABSOLUTE_TOLERANCE = 0.004

# pylint: disable=invalid-name
class Pose:

    def __init__(self, position: Position=Position(), orientation: float=0):
        if isinstance(position, np.ndarray):
            raise TypeError("You need to pass a Position to Pose, use Position.from_array() to convert it.")
        self._orientation = orientation
        self._position = position.copy()

    @classmethod
    def from_dict(cls, my_dict: Dict[str, float]) -> 'Pose':
        return cls(Position(my_dict['x'], my_dict['y']), my_dict['orientation'])

    @classmethod
    def from_values(cls, x: float, y: float, orientation: float=0) -> 'Pose':
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
    def norm(self) -> float:
        return self.position.norm

    @property
    def orientation(self) -> float:
        return self._orientation

    @orientation.setter
    def orientation(self, orientation: float):
        self._orientation = orientation

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.orientation])

    def to_dict(self) -> Dict[str, float]:
        return {'x': self.x, 'y': self.y, 'orientation': self.orientation}

    def flip_x(self):
        return Pose.from_values(-self.x, self.y, geometry.wrap_to_pi(self.orientation + np.pi))

    def __add__(self, other: Position) -> 'Pose':
        assert(isinstance(other, Position))
        return Pose(self.position + other, self.orientation)

    def __sub__(self, other: Position) -> 'Pose':
        return self + (-other)

    def __eq__(self, other: 'Pose') -> bool:
        orientation_equal = geometry.compare_angle(self.orientation,
                                                   other.orientation,
                                                   abs_tol=ORIENTATION_ABSOLUTE_TOLERANCE)
        position_equal = self.position == other.position
        return position_equal and orientation_equal

    def __ne__(self, other: 'Pose') -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return '{}, orientation = {:5.3f}'.format(self.position, self.orientation)

    def __repr__(self) -> str:
        return 'Pose' + str(self)
