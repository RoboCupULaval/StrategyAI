__author__ = 'MGagnon-Legault'

from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.area import isInsideSquare


from Util.geometry import *


class tSimplePathfinder(TacticBase):
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)
        self.Y_MAX_FIELD = 3000
        self.Y_MIN_FIELD = -3000
        self.X_MAX_FIELD = 4500
        self.X_MIN_FIELD = -4500
        self.Y_FIELD = 6000
        self.X_FIELD = 9000

    def apply(self, info_manager, id_player):
        action = info_manager.getPlayerNextPose(id_player)
        bot_pst = info_manager.getPlayerPosition(id_player)

        if distance(bot_pst, Position(3000, 0)) <= 100:
            return {'skill': 'sStop', 'target': bot_pst, 'goal': bot_pst}
        elif isinstance(action, list):
            return {'skill': 'sGoThroughPath', 'target': action, 'goal': bot_pst}
        else:
            action = self.createPath(info_manager, id_player)
            return {'skill': 'sGoThroughPath', 'target': action, 'goal': bot_pst}





    def createPath(self, info_manager, id_player):
        sequence = []
        player_position = info_manager.getPlayerPosition(id_player)
        endPosition = Pose(Position(-2000, 0), 0)
        startPosition = Pose(Position(-2000, 0), 0)
        sequence.append(startPosition)

        #Trouve les robots qui sont des obstacles dans le terrain dont il doit s'occuper
        possibleObstacle = []
        for bot_number in range(info_manager.getCountPlayer()):
            if bot_number != id_player:
                if isInsideSquare(info_manager.getPlayerPosition(bot_number), 2950, -2950, -4400, 4400):
                    possibleObstacle.append(info_manager.getPlayerPosition(bot_number))

        #arrange la liste d'obstacle potentiel par leur position en x  credit goes to Stackoverflow.com
        possibleObstacle.sort(key=lambda Position: Position.x)

        iii = 1
        positionFromLastPoint = player_position
        for position in possibleObstacle:
            if position.x <= player_position.x:
                if iii <= len(possibleObstacle):
                    possibleObstacle = possibleObstacle[iii:]
            else:
                tempPositionPoint = (self.Y_MAX_FIELD - abs(position.y))/2

                tempUpperPassingPoint = tempPositionPoint + position.y
                tempLowerPassingPoint = - tempPositionPoint - position.y
                    #(((-3000) - position.y)/2) - position.y


                tempDistanceUpperPoint = distance(positionFromLastPoint, Position(position.x, tempUpperPassingPoint))
                tempDistanceLowerPoint = distance(positionFromLastPoint, Position(position.x, tempLowerPassingPoint))

                if tempDistanceUpperPoint <= tempDistanceLowerPoint:
                    sequence.append(Pose(Position(position.x, tempUpperPassingPoint), 0))
                    positionFromLastPoint = Position(position.x, tempUpperPassingPoint)
                else:
                    sequence.append(Pose(Position(position.x, tempLowerPassingPoint), 0))
                    positionFromLastPoint = Position(position.x, tempLowerPassingPoint)
            iii += iii

        sequence.append(endPosition)
        return sequence


