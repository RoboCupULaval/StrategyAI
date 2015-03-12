from Util.Pose import Pose


class Player():
    def __init__(self, id):
        self.id = id
        self.pose = Pose()

    #def __eq__(self, other):
    #    return self.id == other.id

    def has_id(self, id):
        return self.id == id