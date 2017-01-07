# Under MIT License, see LICENSE.txt
from ..Util.Pose import Pose
from ..Util.Vector import Vector
from ..Util.constant import DELTA_T


class Player:
    def __init__(self, team, id):
        self.id = id
        self.team = team
        self.pose = Pose()
        self.velocity = Vector(0, 0)

    def has_id(self, pid):
        return self.id == pid

    def update(self, pose, delta=DELTA_T):
        old_pose = self.pose
        delta_position = pose.position - old_pose.position

        try:
            self.velocity.x = delta_position.x / delta
            self.velocity.y = delta_position.y / delta
        except ZeroDivisionError:
            self.velocity = Vector(0, 0)

        self.pose = pose
