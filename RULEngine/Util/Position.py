# Under MIT License, see LICENSE.txt

import numpy as np


class Position(np.ndarray):
    def __new__(cls, *args, abs_tol=0.01, z=0):

        if args is ():
            obj = np.zeros(2).view(cls)
        elif isinstance(args[0], (list, tuple, np.ndarray, Position)) and len(args) == 1:
            obj = np.asarray(args[0].copy()).view(cls)
        elif len(args) == 2:
            obj = np.asarray(args[:]).view(cls)
        else:
            raise TypeError

        obj.x = obj[0]
        obj.y = obj[1]

        obj.z = z
        obj.abs_tol = abs_tol

        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.z = getattr(obj, 'z', 0)
        self.abs_tol = getattr(obj, 'abs_tol', 0.01)

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

    def distance(self):
        return np.linalg.norm(self)

    def angle(self):
        angle = np.arctan2(self[1], self[0])
        return angle if angle < np.pi else angle - 2 * np.pi

    def rotate(self, angle):
        rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]).view(Position)
        return np.dot(rotation, self)

    def normalized(self):
        if self.distance() == 0:
            raise ValueError
        return self / self.distance()

    def __eq__(self, other):
        min_abs_tol = min(self.abs_tol, other.abs_tol)
        return np.allclose(self.view(np.ndarray), other.view(np.ndarray), atol=min_abs_tol)

    def __ne__(self, other):
        return not self.__eq__(other)

    def conv_2_np(self):
        """Legacy. Do not use."""
        return self

    @staticmethod
    def from_np(array):
        """Legacy. Do not use."""
        return Position(array)

    def __hash__(self):
        return hash(str(self))
