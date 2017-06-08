# Under MIT License, see LICENSE.txt

import numpy as np


class Position(np.ndarray):
    def __new__(cls, x=0, y=0, z=0):
        obj = np.asarray(np.array([x, y])).view(cls)
        obj.x = x
        obj.y = y
        obj.z = z
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.z = getattr(obj, 'z', 0)

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

    def __eq__(self, other):
        return bool(np.all(np.isclose(self, other, atol=0.01)))

    def __ne__(self, other):
        return not self.__eq__(other)

    def conv_2_np(self):
        return self

    @staticmethod
    def from_np(array):
        return Position(array[0], array[1])


