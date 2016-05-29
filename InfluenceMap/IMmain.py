#Under MIT License, see LICENSE.txt
from InfluenceMap.InfluenceMap import InfluenceMap
import time
from RULEngine.Util.Position import Position

__author__ = 'RoboCupULaval'

if __name__ == "__main__":

    current_time = time.time()

    IM = InfluenceMap(30.0, strengthdecay=0.9, effectradius=32)

    print("Class creation --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    IM.setStarterBoard()

    print("Initial Setup  --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    print("Points Adding      --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    print(IM.findClosestPoint(20, 20, 0))

    print("Find closest       --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    print("Diverse functions  --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    # IM.printNumberOfCases()
    IM.clearBoard()
    IM.printNumberOfCases()
    print("Clear & Print      --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()
