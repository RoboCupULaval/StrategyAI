#pylint: skip-file

class AsNode():

    def __init__(self, position):

        self.pos = position
        self.parent = None
        self.free = True
        self.neighbors = []
        self.key = str(position.x) + str(position.y)

        self.gCost = 0
        self.hCost = 0
        self.fCost = 0

    def addneighbor(self, neighborNode):
        self.neighbors += [neighborNode]

    def setCost(self, parentNode, endPos):
        
        self.gCost = self.pos.getDist(parentNode.pos) + parentNode.gCost
        self.hCost = self.pos.getDist(endPos)
        self.fCost = self.hCost + self.gCost

    def getNewfCost(self, parentNode, endPos):
        
        return self.pos.getDist(endPos) + self.pos.getDist(parentNode.pos) + parentNode.gCost
