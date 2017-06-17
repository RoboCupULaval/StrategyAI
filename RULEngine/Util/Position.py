# Under MIT License, see LICENSE.txt

import numpy as np
import warnings


class Position(np.ndarray):

    def __new__(cls, *args, z=0, abs_tol=0.01):
        obj = position_builder(args, cls)

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

    def norm(self):
        """Return the distance of the point from the origin"""
        return float(np.linalg.norm(self.view(np.ndarray)))

    def angle(self):
        """Return the angle of the point from the x-axis between -pi and pi"""
        if self == Position(0, 0):
            warnings.warn('Angle is not defined for (0, 0). Result will be 0.')
        return float(np.arctan2(self[1], self[0]))

    def rotate(self, angle):
        rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]).view(Position)
        return np.dot(rotation, self)

    def normalized(self):
        if self.norm() == 0:
            raise ZeroDivisionError
        return self / self.norm()

    def __eq__(self, other):
        if isinstance(other, Position):
            min_abs_tol = min(self.abs_tol, other.abs_tol)
            return np.allclose(self, other, atol=min_abs_tol)
        # elif isinstance(other, np.ndarray):
        #     min_abs_tol = min(self.abs_tol, other.position.abs_tol)
        #     return np.allclose(self, other.position, atol=min_abs_tol)
        else:
            raise TypeError

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_array(self):
        return self

    def conv_2_np(self):
        """Legacy. Do not use."""
        return self.to_array()

    @staticmethod
    def from_np(array):
        """Legacy. Do not use."""
        return Position(array)

    def __repr__(self):
        return 'Position({:8.3f}, {:8.3f})'.format(self[0], self[1])

    def __str__(self):
        return '[{:8.3f}, {:8.3f}]'.format(self[0], self[1])

    def __hash__(self):
        return hash(str(self))

def position_builder(args, cls):
    if len(args) == 0:
        obj = Position(0, 0)
    elif len(args) == 1:
        if isinstance(args[0], (list, Position, np.ndarray)) and len(args[0]) == 2:
            obj = np.asarray(args[0].copy()).view(cls)
        elif isinstance(args[0], tuple) and len(args[0]) == 2:
            obj = np.asarray(args[0]).view(cls)
        else:
            raise ValueError
    elif len(args) == 2:
        obj = np.asarray(args).copy().view(cls)
    else:
        raise ValueError

    return obj
