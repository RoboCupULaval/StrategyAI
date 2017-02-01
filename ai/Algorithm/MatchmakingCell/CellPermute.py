#pylint: skip-file

from ai.Algorithm.Astar.AsPosition import AsPosition

class CellPermute():

    def __init__(self, p_robotId, p_robotPos):

        self.robotId = p_robotId
        self.robotPos = p_robotPos
        self.endPos = None
