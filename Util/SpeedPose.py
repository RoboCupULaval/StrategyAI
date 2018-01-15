from typing import Union

from RULEngine.Util.Pose import Pose

from Util import Position


class SpeedPose(Pose):

    def __init__(self, *args):
        position, orientation = self._pose_builder(args)
        self._orientation = orientation
        self._position = position

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, angular_speed):
        self._orientation = float(angular_speed)

    def __add__(self, other: Union['SpeedPose', Position]):
        if isinstance(other, SpeedPose):
            res = SpeedPose(self.position + other.position, self.orientation + other.orientation)
        elif isinstance(other, Position):
            res = SpeedPose(self.position + other, self.orientation)
        else:
            raise TypeError
        return res

    def __sub__(self, other: Union['SpeedPose', Position]):
        if isinstance(other, SpeedPose):
            res = SpeedPose(self.position - other.position, self.orientation - other.orientation)
        elif isinstance(other, Position):
            res = SpeedPose(self.position - other, self.orientation)
        else:
            raise TypeError
        return res

    def __eq__(self, other: Union['SpeedPose', Position]):
        if isinstance(other, Position):
            return self.position == other
        elif isinstance(other, SpeedPose):
            orientation_equal = self.orientation == other.orientation
            position_equal = self.position == other.position
            return position_equal and orientation_equal
        else:
            raise TypeError

    def __ne__(self, other):
        return not self.__eq__(other)

    def scale(self, value):
        return SpeedPose(self.position * value, self.orientation)

