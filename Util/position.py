# Under MIT License, see LICENSE.txt

import numpy as np

POSITION_ABS_TOL = 0.01


class Position(np.ndarray):

    def __new__(cls, x: float=0, y: float=0):
        obj = np.asarray((x, y)).view(cls)
        obj.x, obj.y = obj
        return obj

    @classmethod
    def from_array(cls, array):
        return cls(array[0], array[1])

    @classmethod
    def from_list(cls, new_list):
        return cls(new_list[0], new_list[1])

    @classmethod
    def from_dict(cls, new_dict):
        return cls(new_dict['x'], new_dict['y'])

    @property
    def x(self):
        return float(self[0])

    @x.setter
    def x(self, x):
        self[0] = x

    @property
    def y(self):
        return float(self[1])

    @y.setter
    def y(self, y):
        self[1] = y

    @property
    def norm(self):
        return float(np.sqrt(self.x ** 2 + self.y ** 2))

    @property
    def angle(self):
        return float(np.arctan2(self.y, self.x))

    def to_dict(self):
        return {'x': self.x, 'y': self.y}

    def __add__(self, other):
        return super().__add__(other).view(Position)

    def __sub__(self, other):
        return super().__sub__(other).view(Position)

    def __eq__(self, other):
        return (self - other).view(Position).norm < POSITION_ABS_TOL

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Position' + str(self)

    def __str__(self):
        return '({:8.3f}, {:8.3f})'.format(self[0], self[1])

    def __hash__(self):
        return hash(str(self))

