#pylint: skip-file

from AsPosition import AsPosition
from AsGraph import AsGraph
import math

class AsPathManager():

    def __init__(self):

        self.TopLeftCorner = AsPosition(-4500,3000)
        self.DownRigthCorner = AsPosition(4500,-3000)
        self.RobotRadius = 100 # real radius is 90, 100 help avoid collision and make it easier to find interval
        self.PreciseInterval = 100
        self.ImpreciseInterval = 200
        self.MaxDist = math.sqrt((self.DownRigthCorner.x - self.TopLeftCorner.x)**2 + (self.TopLeftCorner.y - self.DownRigthCorner.y)**2)

        self.preciseGraph = AsGraph(self.TopLeftCorner, self.DownRigthCorner, self.RobotRadius, self.PreciseInterval)
        self.impreciseGraph = AsGraph(self.TopLeftCorner, self.DownRigthCorner, self.RobotRadius, self.ImpreciseInterval)

    def getAllAsPath(self, startPosList, endPosList, obstacleList):

        allAsPathList = []
        nbPath = len(startPosList)

        for i in range(0, nbPath, 1):

            graph = self.impreciseGraph
            endPos = endPosList[i]
            startPos = startPosList[i]
            totalDist = startPos.getDist(endPos)

            if (totalDist < self.MaxDist / 3):
                graph = self.preciseGraph

            if (totalDist > self.PreciseInterval * 10):
                ratio = math.fabs((self.PreciseInterval * 10) / totalDist)
                xPos = startPos.x + ((endPos.x - startPos.x) * ratio)
                yPos = startPos.y + ((endPos.y - startPos.y) * ratio)
                endPos = AsPosition(xPos, yPos)

            updatedObstacleList = list(obstacleList)
            for j in range(0, nbPath, 1):
                if (j != i):
                    updatedObstacleList.append(startPosList[j])

            allAsPathList += [graph.aStarPath(startPos, endPos, updatedObstacleList)]


        return allAsPathList




