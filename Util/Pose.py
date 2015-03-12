from Util.Position import Position


class Pose():
    def __init__(self, position=Position(), orientation=0.0):
        self.position = position
        self.orientation = orientation

    def __str__(self):
        return str(self.position) + ", theta =" + str(self.orientation)
