#pylint: skip-file

from math import sqrt, fabs

class AsPosition():

    def __init__(self, x, y):

        self.x = x
        self.y = y

    def getAddPos(self, position):
        x = self.x + position.x
        y = self.y + position.y
        return AsPosition(x, y)

    def getDist(self, goalPos):

        return sqrt(((self.x - goalPos.x)**2) + ((self.y - goalPos.y)**2))

    def getQuickDist(self, goalPos):

        x = self.x - goalPos.x
        y = self.y - goalPos.y
        return x*x + y*y
