#pylint: skip-file

from ai.Algorithm.Astar.AsPosition import AsPosition

class Cell():

    def __init__(self, p_robotId, p_robotPos, p_endPos):

        self.robotId = p_robotId
        self.robotPos = p_robotPos
        self.endPos = p_endPos
        self.metric = p_robotPos.getQuickDist(p_endPos)
