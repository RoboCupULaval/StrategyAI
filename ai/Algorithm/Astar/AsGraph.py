#pylint: skip-file

from AsPosition import AsPosition
from AsNode import AsNode

class AsGraph():

    def __init__(self, topLeftCorner, downRigthCorner, robotRadius, interval):

        self.robotRadius = robotRadius
        self.interval = interval
        # topLeftCorner should be like (-100, 100)
        self.topLeftLimit = AsPosition(topLeftCorner.x + robotRadius, topLeftCorner.y - robotRadius)
        # downRigthCorner should be like (100, -100)
        self.downRigthLimit = AsPosition(downRigthCorner.x - robotRadius, downRigthCorner.y + robotRadius)
        self.graphList = []
        self.graphHash = {}

        self.buildGraph()
        self.addneighbors()

        if (not ((self.downRigthLimit.x - self.topLeftLimit.x) % self.interval == 0) or not ((self.topLeftLimit.y - self.downRigthLimit.y) % self.interval == 0)):
            raise NameError("width or height doesnt fit with the interval")

        if ((self.interval**2)*2 < 4 * self.robotRadius):
            raise NameError("Interval too big for robot radius (collision may not be avoid)")


    def buildGraph(self):

        width = self.downRigthLimit.x - self.topLeftLimit.x + self.interval
        height = self.topLeftLimit.y - self.downRigthLimit.y + self.interval

        startPoint = AsPosition(self.topLeftLimit.x, self.downRigthLimit.y)

        for x in range(0, width, self.interval):
            for y in range(0, height, self.interval):
                currentPos = AsPosition(startPoint.x + x, startPoint.y + y)
                strPos = self.buildKey(currentPos)
                currentNode = AsNode(currentPos)
                self.graphList.append(currentNode)
                self.graphHash[strPos] = currentNode

    def buildKey(self, position):
        return str(position.x) + str(position.y)

    def addneighbors(self):

        posList = [AsPosition(self.interval, 0),AsPosition(-self.interval, 0),AsPosition(0, self.interval),AsPosition(0, -self.interval),AsPosition(self.interval, self.interval),AsPosition(-self.interval, -self.interval),AsPosition(self.interval, -self.interval),AsPosition(-self.interval, self.interval)]
        for node in self.graphList :
            for pos in posList:
                neighborPos = node.pos.getAddPos(pos)
                key = self.buildKey(neighborPos)
                if (key in self.graphHash):
                    node.addneighbor(self.graphHash[key])

    def findNearNodeKey(self, position):

        pos = AsPosition(position.x, position.y)
        if (pos.x < self.topLeftLimit.x) :
            pos.x = self.topLeftLimit.x

        if (pos.x > self.downRigthLimit.x) :
            pos.x = self.downRigthLimit.x

        if (pos.y < self.downRigthLimit.y) :
            pos.y = self.downRigthLimit.y

        if (pos.y > self.topLeftLimit.y) :
            pos.y = self.topLeftLimit.y

        x = ((self.downRigthLimit.x + pos.x) % self.interval)
        difX = x * -1
        y = ((self.topLeftLimit.y + pos.y) % self.interval)
        difY = y * -1

        if (x > self.interval - x):
            difX = self.interval - x

        if (y > self.interval - y):
            difY = self.interval - y
    
        nearPosition = AsPosition(round(pos.x + difX), round(pos.y + difY))
        key = self.buildKey(nearPosition)

        if (not (key in self.graphHash)):
            raise NameError('Near point outside graph')

        return key

    def toggleObstacle(self, position, free):

        topLeftKey = self.findNearNodeKey(AsPosition(position.x - (self.robotRadius * 2), position.y + (self.robotRadius * 2)))
        topLeftNode = self.graphHash[topLeftKey]

        for x in range(0, (self.robotRadius * 4), self.interval):
            for y in range(0, (self.robotRadius * 4), self.interval):
                currentKey = self.buildKey(AsPosition(topLeftNode.pos.x + x, topLeftNode.pos.y - y))
                if (currentKey in self.graphHash):
                    currentNode = self.graphHash[currentKey]
                    if (self.inShape(position, currentNode.pos)):
                        currentNode.free = free

    def inShape(self, center, position):

        # radius * 2 to compensate for the radius of the moving robot
        return (((position.x - center.x)**2) + ((position.y - center.y)**2)) <= ((self.robotRadius*2)**2)


    def setAllObstacle(self, obstacleList, free):

        for pos in obstacleList:
            self.toggleObstacle(pos, free)

    def aStarPath(self, startPos, endPos, obstacleList):

        self.setAllObstacle(obstacleList, False)

        startNode = self.findNearNodeTowardGoalForStart(startPos, endPos)
        goalNode = self.findNearNodeTowardGoalForEnd(endPos, startPos)
        goalKey = goalNode.key
        startNode.setCost(startNode, goalNode.pos)

        startFree = self.startPosIsFree(startPos)
        goalFree = self.endPosIsFree(endPos)

        if (startPos.getDist(endPos) < self.interval):
            self.setAllObstacle(obstacleList, True)
            if (goalFree):
                return [endPos]
            else:
                return [goalNode.pos]

        if (not startFree):
            self.setAllObstacle(obstacleList, True)
            return [startPos]

        openNode = [startNode]
        openSet = set()
        openSet.add(startNode.key)
        closeNode = set()
        found = False

        while (not found):
            currentNode = self.findNodeWithLowestFCost(openNode)
            openNode.remove(currentNode)
            openSet.remove(currentNode.key)
            closeNode.add(currentNode.key)

            if (currentNode.key == goalKey):
                found = True

            for node in currentNode.neighbors:
                if (node.free and not (node.key in closeNode)):
                    newFCost = node.getNewfCost(currentNode, goalNode.pos)
                    if (not (node.key in openSet) or (newFCost < node.fCost)):
                        node.setCost(currentNode, goalNode.pos)
                        node.parent = currentNode
                        if (not (node.key in openSet)):
                            openNode.append(node)
                            openSet.add(node.key)

        self.setAllObstacle(obstacleList, True)
        return self.getPath(goalNode, startNode, startPos, endPos, goalFree)



    def findNodeWithLowestFCost(self, nodeList):
        
        if (len(nodeList) <= 0):
            raise NameError("No more node in openList")

        currentNode = nodeList[0]
        for node in nodeList:
            if (node.fCost < currentNode.fCost):
                currentNode = node

        return currentNode

    def getPath(self, goalNode, startNode, startPos, endPos, goalFree):

        path = []
        if (goalFree):
            path.append(endPos)

        startKey = startNode.key
        found = False
        currentNode = goalNode

        while (not found):
            path.append(currentNode.pos)

            if (currentNode.key == startKey):
                found = True

            currentNode = currentNode.parent

        path.reverse()
        return path


    def findNearNodeTowardGoalForEnd(self, startPos, endPos):

        nodeList = self.findFourNearNode(startPos)

        nearNode = nodeList[0]
        found = False

        while (not found):

            for node in nodeList:
                if (node.pos.getDist(endPos) < nearNode.pos.getDist(endPos)):
                    nearNode = node

            if (nearNode.free):
                found = True
            
            nodeList = nearNode.neighbors
            

        return nearNode

    def findNearNodeTowardGoalForStart(self, startPos, endPos):

        nodeList = self.findFourNearNode(startPos)

        nearNode = nodeList[0]
        for node in nodeList:
            if (node.pos.getDist(endPos) > nearNode.pos.getDist(endPos)):
                    nearNode = node

        found = False

        while (not found):

            oldNode = nearNode

            for node in nodeList:
                if (node.pos.getDist(endPos) < nearNode.pos.getDist(endPos) and node.free):
                    nearNode = node

            # not nearNode.pos.getDist(startPos) < (self.interval / 2) -> eviter de rester sur place,
            # oldNode == nearNode -> eviter de tourner en rond (ca marchera pas, on retourne le dernier noeud libre et on attend que les joueurs bougent)
            if (not nearNode.pos.getDist(startPos) < (self.interval / 2) or oldNode == nearNode):
                found = True
            
            nodeList = nearNode.neighbors
            

        return nearNode

    def findFourNearNode(self, startPos):

        pos = AsPosition(startPos.x, startPos.y)
        if (pos.x < self.topLeftLimit.x) :
            pos.x = self.topLeftLimit.x

        if (pos.x > self.downRigthLimit.x) :
            pos.x = self.downRigthLimit.x

        if (pos.y < self.downRigthLimit.y) :
            pos.y = self.downRigthLimit.y

        if (pos.y > self.topLeftLimit.y) :
            pos.y = self.topLeftLimit.y

        diffX1 = ((self.downRigthLimit.x + pos.x) % self.interval)
        diffX2 = self.interval - diffX1
        diffY1 = ((self.topLeftLimit.y + pos.y) % self.interval)
        diffY2 = self.interval - diffY1

        nearPosList = [AsPosition(round(pos.x - diffX1), round(pos.y - diffY1))]
        nearPosList.append(AsPosition(round(pos.x - diffX1), round(pos.y + diffY2)))
        nearPosList.append(AsPosition(round(pos.x + diffX2), round(pos.y - diffY1)))
        nearPosList.append(AsPosition(round(pos.x + diffX2), round(pos.y + diffY2)))

        nodeList = []
        for position in nearPosList:
            nodeList.append(self.graphHash[self.buildKey(position)])

        return nodeList

    def endPosIsFree(self, pos):

        nearList = self.findFourNearNode(pos)

        free = True
        for node in nearList:
            free = free and node.free

        return free

    def startPosIsFree(self, pos):

        nearList = self.findFourNearNode(pos)

        free = False
        for node in nearList:
            free = free or node.free

        return free