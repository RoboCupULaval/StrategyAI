#pylint: skip-file

from ai.Algorithm.Astar.AsPosition import AsPosition
from ai.Algorithm.MatchmakingCell.Cell import Cell
from ai.Algorithm.MatchmakingCell.CellPermute import CellPermute

def matchmakingBestSolution(startPosList, endPosList):

    if (not (len(startPosList) == len(endPosList))):
        raise NameError("startPosList and endPosList length are not equals")

    cellList = []

    length = len(startPosList)
    for i in range(0, length, 1):
        fakeId = str(i)
        cellList.append(CellPermute(fakeId, startPosList[i]))
    
    allPermutations = permutation(cellList)

    currentBestPermutation = allPermutations[0]
    currentMinDist = getTotalDist(allPermutations[0], endPosList)

    for permute in allPermutations:
        tempDist = getTotalDist(permute, endPosList)
        if (tempDist < currentMinDist):
            currentMinDist = tempDist
            currentBestPermutation = permute

    for i in range(0, length, 1):
        currentBestPermutation[i].endPos = endPosList[i]

    return currentBestPermutation

def getTotalDist(cellList, endPosList):

    totalDist = 0
    length = len(cellList)
    for i in range(0, length, 1):
        totalDist += cellList[i].robotPos.getQuickDist(endPosList[i])

    return totalDist

def permutation(paths):

    result = []

    if (len(paths) > 1):
        for i in range(0, len(paths), 1):
            liste = list(paths)
            liste.remove(paths[i])
            permute = permutation(liste)
            temp = []

            length = len(permute)
            for j in range(0, length, 1):
                if (isinstance(permute[j], list)):
                    temp.append([paths[i]] + list(permute[j]))
                else:
                    temp.append([paths[i]] + list([permute[j]]))

            result.extend(temp)

    else:
        result = list(paths)

    return result



#------------------------------------------------------------------------------------------


def matchmakingOptimalSolution(startPosList, endPosList):
    if (not (len(startPosList) == len(endPosList))):
        raise NameError("startPosList and endPosList length are not equals")

    distList = []

    length = len(startPosList)
    for i in range(0, length, 1):
        for j in range(0, length, 1):
            fakeId = str(i)
            distList.append(Cell(fakeId, startPosList[i], endPosList[j]))

    distList.sort(key=lambda x : x.metric)

    count = 0
    optimalAssoc = []
    foundRobotId = set()
    foundEndId = set()

    while (len(optimalAssoc) < length):

        if (not (distList[count].robotId in foundRobotId or distList[count].endPos in foundEndId)):
            optimalAssoc.append(distList[count])
            foundRobotId.add(distList[count].robotId)
            foundEndId.add(distList[count].endPos)

        count += 1

    return optimalAssoc