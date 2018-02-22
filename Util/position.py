# Under MIT License, see LICENSE.txt

import numpy as np

POSITION_ABS_TOL = 0.01


class Position(np.ndarray):

    def __new__(cls, x: float=0, y: float=0):
        obj = np.asarray((x, y)).view(cls)
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

    def norm(self):
        """Return the distance of the point from the origin"""
        return np.sqrt(self[0] ** 2 + self[1] ** 2)  # Faster than np.linalg.norm()

    def angle(self):
        """Return the angle of the point from the x-axis between -pi and pi"""
        return float(np.arctan2(self[1], self[0]))

    def rotate(self, angle):
        rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]).view(Position)
        return np.dot(rotation, self)

    def normalized(self):
        return self / self.norm()

    def perpendicular(self):
        """Return the orthonormal vector to the np.array([0,0,1]) with right hand rule."""
        return Position(self[1], -self[0]).normalized()

    def is_close(self, other, abs_tol=POSITION_ABS_TOL):
        return (self - other).view(Position).norm() < abs_tol

    def __eq__(self, other):
        return self.is_close(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Position' + str(self)

    def __str__(self):
        return '({:8.3f}, {:8.3f})'.format(self[0], self[1])

    def __hash__(self):
        return hash(id(self))

    @classmethod
    def from_np(cls, array):
        return cls(array)

    @classmethod
    def from_dict(cls, new_dict):
        return cls(new_dict['x'], new_dict['y'])

    def to_dict(self):
        return {'x': self.x, 'y': self.y}
