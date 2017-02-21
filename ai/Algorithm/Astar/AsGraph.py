#pylint: skip-file

from ai.Algorithm.Astar.AsPosition import AsPosition
from ai.Algorithm.Astar.AsObstacle import AsObstacle
from ai.Algorithm.Astar.AsNode import AsNode
from math import sqrt, acos

class AsGraph():

    def __init__(self, topLeftCorner, downRigthCorner, robotRadius, interval):

        self.robotRadius = robotRadius
        self.interval = interval
        # topLeftCorner should be like (-100, 100)
        self.topLeftLimit = AsPosition(topLeftCorner.x, topLeftCorner.y)
        # downRigthCorner should be like (100, -100)
        self.downRigthLimit = AsPosition(downRigthCorner.x, downRigthCorner.y)
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

    def toggleObstacle(self, obstacle, free):

        topLeftKey = self.findNearNodeKey(AsPosition(obstacle.position.x - (self.robotRadius * 2), obstacle.position.y + (self.robotRadius * 2)))
        topLeftNode = self.graphHash[topLeftKey]

        for x in range(0, (self.robotRadius * 4), self.interval):
            for y in range(0, (self.robotRadius * 4), self.interval):
                currentKey = self.buildKey(AsPosition(topLeftNode.pos.x + x, topLeftNode.pos.y - y))
                if (currentKey in self.graphHash):
                    currentNode = self.graphHash[currentKey]
                    if (self.inShape(obstacle.position, currentNode.pos)):
                        currentNode.free = free

    def inShape(self, center, position):

        # radius * 2 to compensate for the radius of the moving robot
        return (((position.x - center.x)**2) + ((position.y - center.y)**2)) <= ((self.robotRadius*2)**2)


    def setAllObstacle(self, obstacleList, free):

        for obstacle in obstacleList:
            self.toggleObstacle(obstacle, free)

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
        tempPath = self.getPath(goalNode, startNode, endPos, goalFree)
        finalPath = self.mergePointToLine(tempPath)

        return finalPath



    def findNodeWithLowestFCost(self, nodeList):
        
        if (len(nodeList) <= 0):
            raise NameError("No more node in openList")

        currentNode = nodeList[0]
        for node in nodeList:
            if (node.fCost < currentNode.fCost):
                currentNode = node

        return currentNode

    def getPath(self, goalNode, startNode, endPos, goalFree):

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
            if (not nearNode.pos.getDist(startPos) < (self.interval * 0.75) or oldNode == nearNode):
                found = True
            
            nodeList = nearNode.neighbors
            

        return nearNode

    def findFourNearNode(self, startPos):

        pos = AsPosition(startPos.x, startPos.y)
        if (pos.x < (self.topLeftLimit.x + self.interval)) :
            pos.x = (self.topLeftLimit.x + self.interval)

        if (pos.x > (self.downRigthLimit.x - self.interval)) :
            pos.x = (self.downRigthLimit.x - self.interval)

        if (pos.y < (self.downRigthLimit.y + self.interval)) :
            pos.y = (self.downRigthLimit.y + self.interval)

        if (pos.y > (self.topLeftLimit.y - self.interval)) :
            pos.y = (self.topLeftLimit.y - self.interval)

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

    def mergePointToLine(self, path):

        newPath = []

        if (len(path) < 3):
            newPath = path
        else:
            start = 0
            forward = 2
            isLine = False
            while (forward < len(path)):
                stepX = path[start + 1].x - path[start].x
                stepY = path[start + 1].y - path[start].y
                stepVector = (stepX, stepY)

                forwardStepX = path[forward].x - path[start].x
                forwardStepY = path[forward].y - path[start].y
                forwardVector = (forwardStepX, forwardStepY)


                if (self.vectorAngleAreSame(stepVector, forwardVector)):
                    forward += 1
                    isLine = True
                else:
                    if (isLine):
                        newPath += [path[forward - 1]]
                        isLine = False
                        start = forward - 1
                        forward += 1
                    else:
                        newPath += [path[start + 1]]
                        start += 1
                        forward += 1

            if (isLine):
                newPath += [path[forward - 1]]
            else:
                newPath += [path[start + 1]]

        return newPath

    def vectorAngleAreSame(self, vector1, vector2):

        numerator = (vector1[0] * vector2[0]) + (vector1[1] * vector2[1])
        denominator1 = sqrt(vector1[0]**2 + vector1[1]**2)
        denominator2 = sqrt(vector2[0]**2 + vector2[1]**2)
        denominator = denominator1 * denominator2

        result = numerator / denominator

        angle = acos(result)

        return (angle < 0.01 and angle > -0.01)








