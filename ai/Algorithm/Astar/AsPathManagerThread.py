#pylint: skip-file

from AsPosition import AsPosition
from AsGraph import AsGraph
import threading

class AsPathManager():

    def __init__(self, topLeftCorner, downRigthCorner, robotRadius, interval, nbGraph):

        self.graphList = []

        for i in range(0, nbGraph, 1):
            self.graphList.append(AsGraph(topLeftCorner, downRigthCorner, robotRadius, interval))

    def getAllAsPath(self, startPosList, endPosList, obstacleList):

        nbPath = len(startPosList)
        if (len(self.graphList) < nbPath and len(endPosList) == nbPath):
            raise NameError("Not enough graph for the number of path wanted")

        threadList = []
        allAsPathList = []

        for i in range(0, nbPath, 1):

            updatedObstacleList = list(obstacleList)
            for j in range(0, nbPath, 1):
                if (j != i):
                    updatedObstacleList.append(startPosList[j])

            thread = threading.Thread(target=threadAs, args=(startPosList[i], endPosList[i], updatedObstacleList, self.graphList[i], allAsPathList))
            threadList.append(thread)

        for thread in threadList:
            thread.start()

        for thread in threadList:
            thread.join()

        return allAsPathList



def threadAs(robotStart, ball, obstacleList, graph, pathList):
    
    path = graph.aStarPath(robotStart, ball, obstacleList)
    pathList.append(path)



