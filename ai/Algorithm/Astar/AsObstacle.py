#pylint: skip-file

from ai.Algorithm.Astar.AsPosition import AsPosition

class AsObstacle():

    def __init__(self, position, direction=0, speed=1):

        self.position = position
        self.direction = direction
        self.speed = speed


    def getPos(self, position):

        return self.position

