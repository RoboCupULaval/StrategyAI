#pylint: skip-file

from ai.Algorithm.Astar.AsPosition import AsPosition
from ai.Algorithm.Astar.AsGraph import AsGraph
from ai.Algorithm.AsPathManager import AsPathManager
import timeit

"""
myGraphManager = AsPathManager(None)

endPosList = [AsPosition(50.5643, 51.003),AsPosition(50.5643, 51.003),AsPosition(50.5643, 51.003),AsPosition(50.5643, 51.003),AsPosition(50.5643, 51.003),AsPosition(50.5643, 51.003)]
robotStartList = [AsPosition(-4351.5643, -2551.003),AsPosition(-1261.5643, -1261.003),AsPosition(-2571.5643, -271.003),AsPosition(-11.5643, -881.003),AsPosition(-891.5643, -1191.003),AsPosition(1550.5643, 2034.003)]
obstacleList = [AsPosition(-134.5643, -441.00006),AsPosition(-915.543, -1510.006),AsPosition(-240.9743, 90.12006),AsPosition(-2436.7643, 2340.043),AsPosition(4000.5643, -1231.216),AsPosition(3230.5643, 741.003)]

start = timeit.default_timer()
paths = myGraphManager.getAllAsPath(robotStartList, endPosList, obstacleList)
stop = timeit.default_timer()


print("--- %s seconds ---" % (stop - start))

print("Start All")
print("------------------------------------------------------------------------------------------------------------------------------------------------------------------")

for path in paths:
    strPath = "Start  ->  "
    for pos in path:
        strPath += str(pos.x) + "," + str(pos.y) + "  "
    print(strPath + "->  End")
    print("------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        
print("End All")

"""

TopLeftCorner = AsPosition(-4500,3000)
DownRigthCorner = AsPosition(4500,-3000)
RobotRadius = 100  # real radius is 90, 100 help avoid collision and make it easier to find interval
PreciseInterval = 100

preciseGraph = AsGraph(TopLeftCorner, DownRigthCorner, RobotRadius, PreciseInterval)

myPath = [AsPosition(0, 0),AsPosition(100, 100),AsPosition(200, 200),AsPosition(300, 300),AsPosition(300, 400),AsPosition(300, 500)]

newPath = preciseGraph.mergePointToLine(myPath)

strPath = "Start  ->  "
for pos in newPath:
    strPath += str(pos.x) + "," + str(pos.y) + "  "
print(strPath + "->  End")





