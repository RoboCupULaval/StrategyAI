from typing import Union

from Util.pose import Pose

from Util.position import Position


class Velocity(Pose):

    def __init__(self, *args):
        position, orientation = self._pose_builder(args)
        self._orientation = orientation
        self._position = position
        self.speed = self._position.norm()

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, angular_speed):
        self._orientation = float(angular_speed)

    def __add__(self, other):
        if isinstance(other, Velocity):
            res = Velocity(self.position + other.position, self.orientation + other.orientation)
        elif isinstance(other, Position):
            res = Velocity(self.position + other, self.orientation)
        else:
            raise TypeError
        return res

    def __sub__(self, other):
        if isinstance(other, Velocity):
            res = Velocity(self.position - other.position, self.orientation - other.orientation)
        elif isinstance(other, Position):
            res = Velocity(self.position - other, self.orientation)
        else:
            raise TypeError
        return res

    def __eq__(self, other: Union['Velocity', Position]):
        if isinstance(other, Position):
            return self.position == other
        elif isinstance(other, Velocity):
            orientation_equal = self.orientation == other.orientation
            position_equal = self.position == other.position
            return position_equal and orientation_equal
        else:
            raise TypeError

    def __ne__(self, other):
        return not self.__eq__(other)

    def scale(self, value):
        return Velocity(self.position * value, self.orientation)

