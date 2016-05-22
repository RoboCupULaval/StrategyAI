Under MIT License, see LICENSE.txt
from ..Util.Pose import Pose


class Player():
    def __init__(self, id):
        self.id = id
        self.pose = Pose()

    def has_id(self, id):
        return self.id == id
