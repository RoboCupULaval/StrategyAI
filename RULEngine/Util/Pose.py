#Under MIT License, see LICENSE.txt

from RULEngine.Util.Position import Position
import numpy as np


ORIENTATION_ABSOLUTE_TOLERANCE = 0.004  # Half a degree to tolerance


class Pose(np.ndarray):

    def __new__(cls, position=Position(), orientation=0):
        obj = np.asarray(np.append(position, orientation)).view(cls)
        obj.position = position
        obj.orientation = orientation
        return obj

    @property
    def position(self):
        return self[0:2].view(Position)

    @position.setter
    def position(self, position: Position):
        self[0:2] = position[0:2]  # The height og the ball (z component) is discard in a pose

    @property
    def orientation(self):
        return float(self[2])

    @orientation.setter
    def orientation(self, orientation):
        self[2] = orientation

    def to_tuple(self):
        return self.position.x, self.position.y

    def conv_2_np(self) -> np.ndarray:
        return self

    def __str__(self):
        return '[pos={}, theta={}]'.format(self.position, self.orientation)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.position == other.position and np.isclose(self.orientation, other.orientation,
                                                              atol=ORIENTATION_ABSOLUTE_TOLERANCE)

    def __ne__(self, other):
        return not self.__eq__(other)

