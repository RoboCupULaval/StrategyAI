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
    def norm(self):
        return np.sqrt(self.x ** 2 + self.y ** 2)

    @property
    def angle(self):
        return float(np.arctan2(self.y, self.x))

    def rotate(self, angle):
        return rotate(self, angle)

    def normalized(self):
        return normalized(self)

    def perpendicular(self):
        return perpendicular(self)

    def is_close(self, other, abs_tol=POSITION_ABS_TOL):
        return is_close(self, other, abs_tol)

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
    def from_array(cls, array):
        return cls(array[0], array[1])

    @classmethod
    def from_list(cls, new_list):
        return cls(new_list[0], new_list[1])

    @classmethod
    def from_dict(cls, new_dict):
        return cls(new_dict['x'], new_dict['y'])

    def to_dict(self):
        return {'x': self.x, 'y': self.y}


def rotate(vec: Position, angle):
    rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]).view(Position)
    return rotation @ vec


def normalized(vec: Position):
    return vec.copy() / vec.norm


def perpendicular(vec: Position):
    """Return the orthonormal vector to the np.array([0,0,1]) with right hand rule."""
    return normalized(Position(-vec.y, vec.x))


def is_close(vec1: Position, vec2: Position, abs_tol=0.001):
    return (vec1 - vec2).view(Position).norm < abs_tol
