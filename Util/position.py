# Under MIT License, see LICENSE.txt
from typing import Dict, List

import numpy as np

POSITION_ABS_TOL = 0.01


class Position:

    def __init__(self, x=0, y=0):
        self._array = np.array([x, y])

    @classmethod
    def from_array(cls, array: np.ndarray):
        if array.size != 2:
            raise ValueError('Position can only be create with a size 2 array.')
        return cls(array[0], array[1])

    @classmethod
    def from_list(cls, new_list: List):
        return cls(new_list[0], new_list[1])

    @classmethod
    def from_dict(cls, new_dict: Dict):
        return cls(new_dict['x'], new_dict['y'])

    @property
    def x(self):
        return float(self.array[0])

    @x.setter
    def x(self, x):
        self._array[0] = x

    @property
    def y(self):
        return float(self.array[1])

    @y.setter
    def y(self, y):
        self._array[1] = y

    @property
    def norm(self):
        return float(np.sqrt(self.x ** 2 + self.y ** 2))

    @property
    def angle(self):
        return float(np.arctan2(self.y, self.x))

    @property
    def array(self):
        return self._array

    def to_dict(self):
        return {'x': self.x, 'y': self.y}

    def to_tuple(self):
        return self.x, self.y

    def copy(self):
        return Position.from_array(self.array.copy())

    def __add__(self, other):
        return Position.from_array(self.array + other.array)

    def __sub__(self, other):
        return Position.from_array(self.array - other.array)

    def __mul__(self, other):
        return Position.from_array(self.array * other)

    def __matmul__(self, other):
        return Position.from_array(self.array @ other)

    def __truediv__(self, other):
        return Position.from_array(self.array / other)

    def __neg__(self):
        return Position.from_array(-self.array)

    def __eq__(self, other):
        return (self - other).norm < POSITION_ABS_TOL

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, key):
        return self.array[key]

    def __setitem__(self, key, item):
        self.array[key] = item

    def __repr__(self):
        return 'Position' + str(self)

    def __str__(self):
        return '({:8.3f}, {:8.3f})'.format(self.x, self.y)

    def __hash__(self):
        return hash(str(self))

