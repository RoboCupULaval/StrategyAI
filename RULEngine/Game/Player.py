# Under MIT License, see LICENSE.txt
from RULEngine.Util.Position import Position
from ..Util.Pose import Pose
from ..Util.Vector import Vector
from ..Util.constant import DELTA_T
from RULEngine.Util.tracking import Kalman

import numpy as np


class Player:
    def __init__(self, team, id, kalman=False, type="friends", ncameras=1):

        self.cmd = [0, 0, 0]
        self.id = id

        self.team = team
        self.kf = Kalman(type, ncameras=4)
        self.pose = Pose()

        self.velocity = [0, 0, 0]

    def has_id(self, pid):
        return self.id == pid

    def update(self, pose, delta=DELTA_T):
        old_pose = self.pose
        self.pose = pose

    def kalman_update(self, poses, delta):
        ret = self.kf.filter(poses, self.cmd, delta)
        self.pose = Pose(Position(ret[0], ret[1]), ret[4])
        self.velocity = [ret[2], ret[3], ret[5]]
        print(self.velocity)


    def set_command(self, cmd):
        self.cmd = [cmd.pose.position.x, cmd.pose.position.y, cmd.pose.orientation]

