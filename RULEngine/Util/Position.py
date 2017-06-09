# Under MIT License, see LICENSE.txt

import numpy as np


POSITION_ABSOLUTE_TOLERANCE = 0.01


class Position(np.ndarray):
    def __new__(cls, *args):

        if args is ():
            obj = np.zeros(3).view(cls)
        elif isinstance(args[0], np.ndarray):
            obj = np.asarray(args[0]).view(cls)
        elif len(args) == 2 or len(args) == 3:
            obj = np.asarray(args[:]).view(cls)
        else:
            raise TypeError

        if obj.size == 2:
            obj = np.append(obj, 0).view(cls)  # if no z-component provided, assume 0

        obj.x = obj[0]
        obj.y = obj[1]
        obj.z = obj[2]

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
    def z(self):
        return float(self[2])

    @z.setter
    def z(self, z):
        self[2] = z

    def distance(self):
        return np.linalg.norm(self)

    def angle(self):
        angle = np.arctan2(self[1], self[0])
        return angle if angle < np.pi else angle - 2 * np.pi

    def rotate(self, angle):
        rotation = np.array([[np.cos(angle), -np.sin(angle), 0],
                             [np.sin(angle), np.cos(angle), 0],
                             [0, 0, 1]]).view(Position)
        return np.dot(rotation, self)

    def normalized(self):
        if self.distance() == 0:
            raise ValueError
        return self / self.distance()

    def __eq__(self, other):
        return bool(np.all(np.isclose(self, other, atol=POSITION_ABSOLUTE_TOLERANCE)))

    def __ne__(self, other):
        return not self.__eq__(other)

    def conv_2_np(self):
        """Legacy. Do not use."""
        return self

    @staticmethod
    def from_np(array):
        """Legacy. Do not use."""
        return Position(array)
