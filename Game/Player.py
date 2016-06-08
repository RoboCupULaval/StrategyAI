#Under MIT License, see LICENSE.txt
from ..Util.Pose import Pose


class Player():
    def __init__(self, team, id):
        self.id = id
        self.team = team
        self.pose = Pose()

    def has_id(self, id):
        return self.id == id
