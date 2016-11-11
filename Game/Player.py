# Under MIT License, see LICENSE.txt
from ..Util.Pose import Pose
from ..Util.Vector import Vector
from ..Util.constant import DELTA_T


class Player():
    def __init__(self, team, id):
        self.id = id
        self.team = team
        self.pose = Pose()
        self.velocity = Vector(0, 0)

    def has_id(self, id):
        return self.id == id

    def update(self, pose, delta=DELTA_T):
        self.pose = pose
