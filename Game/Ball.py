# Under MIT License, see LICENSE.txt
from RULEngine.Util.tracking import Kalman
from ..Util.Position import Position
import math


class Ball():
    def __init__(self, type="ball", ncameras=4):
        self._position = Position()
        self.velocity = Position()
        self.kf = Kalman(type, ncameras)

    def kalman_update(self, poses, delta):
        ret = self.kf.filter(poses, None, delta)
        self._position = Position(ret[0], ret[1])
        self.velocity = Position(ret[2], ret[3])

    @property
    def position(self):
        return self._position

    def set_position(self, pos, delta):
        self.kalman_update(pos, delta)

