#pylint: skip-file

from ai.Algorithm.Astar.AsPosition import AsPosition
from ai.Algorithm.Matchmaking import matchmakingBestSolution
from ai.Algorithm.Matchmaking import matchmakingOptimalSolution
import timeit



endPosList = [AsPosition(10.563, 22.003),AsPosition(34.564, 18.003),AsPosition(25.563, 67.003),AsPosition(26.643, 27.003),AsPosition(50.543, 15.003)]#,AsPosition(90.564, 51.003)]
robotStartList = [AsPosition(51.643, 51.003),AsPosition(61.543, 61.003),AsPosition(71.563, 71.003),AsPosition(81.543, 81.003),AsPosition(91.564, 91.003)]#,AsPosition(10.563, 34.003)]

start = timeit.default_timer()
result1 = matchmakingBestSolution(robotStartList, endPosList)
stop = timeit.default_timer()
print("--- Permutation : %s milliseconds ---" % ((stop - start) * 1000))



start = timeit.default_timer()
result2 = matchmakingOptimalSolution(robotStartList, endPosList)
stop = timeit.default_timer()
print("--- Matrice : %s milliseconds ---" % ((stop - start) * 1000))



print("Permutation Start All")

startPosStr = ""
for i in range(0, len(result1), 1):
    startPosStr += "(" + str(result1[i].robotPos.x) + "," + str(result1[i].robotPos.y) + ")  "

endPosStr = ""
for i in range(0, len(result1), 1):
    endPosStr += "(" + str(result1[i].endPos.x) + "," + str(result1[i].endPos.y) + ")  "

totalDist = 0
for i in range(0, len(result1), 1):
    totalDist += result1[i].robotPos.getDist(result1[i].endPos)

print("Start ->  " + startPosStr)
print("End   ->  " + endPosStr)
print("TotalDist   ->  " + str(totalDist))

print("Permutation End All")

print("-----------------------------------------------------------------------------------------------------------")

print("Matrice Start All")

startPosStr = ""
for i in range(0, len(result2), 1):
    startPosStr += "(" + str(result2[i].robotPos.x) + "," + str(result2[i].robotPos.y) + ")  "

endPosStr = ""
for i in range(0, len(result2), 1):
    endPosStr += "(" + str(result2[i].endPos.x) + "," + str(result2[i].endPos.y) + ")  "

totalDist = 0
for i in range(0, len(result2), 1):
    totalDist += result2[i].robotPos.getDist(result2[i].endPos)

print("Start ->  " + startPosStr)
print("End   ->  " + endPosStr)
print("TotalDist   ->  " + str(totalDist))

print("Matrice End All")




