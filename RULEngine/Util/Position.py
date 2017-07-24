# Under MIT License, see LICENSE.txt

import numpy as np
import warnings

POSITION_ABS_TOL = 0.01


class Position(np.ndarray):

    def __new__(cls, *args):
        if not args:
            obj = np.zeros(2).view(cls)
        elif not isinstance(args, (int, float, np.number)):
            obj = np.asarray(args).flatten().copy().view(cls)
        else:
            raise ValueError
        obj.x, obj.y = obj
        return obj

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
    def abs_tol(self):
        return POSITION_ABS_TOL

    @property
    def z(self):
        return 0

    @z.setter
    def z(self, z):
        pass

    def norm(self):
        """Return the distance of the point from the origin"""

        return float(np.sqrt(np.sum(np.square(self))))

    def angle(self):
        """Return the angle of the point from the x-axis between -pi and pi"""
        if not self.norm():
            warnings.warn('Angle is not defined for (0, 0). Result will be 0.')
        return float(np.arctan2(self[1], self[0]))

    def rotate(self, angle):
        rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]).view(Position)
        return np.dot(rotation, self)

    def normalized(self):
        if not self.norm():
            raise ZeroDivisionError
        return self / self.norm()

    def perpendicular(self):
        """Retourne la normale unitaire entre le vecteur et la normal au plan np.array([0,0,1]). Right hand rule."""
        return Position(self[1], -self[0]).normalized()

    def __eq__(self, other):
        return np.allclose(self, other, atol=POSITION_ABS_TOL)

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
        if len(self) == 2:
            return 'Position({:8.3f}, {:8.3f})'.format(self[0], self[1])
        else:
            return super().__repr__()

    def __str__(self):
        if len(self) == 2:
            return '[{:8.3f}, {:8.3f}]'.format(self[0], self[1])
        else:
            return super().__str__()

    def __hash__(self):
        return hash(str(self))


def position_builder(args):
    if not args:
        obj = np.zeros(2)
    elif not isinstance(args, (int, float)):
        obj = np.asarray(args).flatten().copy()
    else:
        raise ValueError
    return obj
