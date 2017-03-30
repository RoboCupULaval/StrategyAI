#pylint: skip-file

from ai.Algorithm.Astar.AsPosition import AsPosition
from RULEngine.Util.Vector import Vector

class AsObstacle():

    def __init__(self, position, vector=Vector(1,0)):

        self.position = position
        self.vector = vector


    def getPos(self):

        return self.position

