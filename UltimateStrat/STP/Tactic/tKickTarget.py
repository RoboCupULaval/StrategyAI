from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from RULEngine.Util.geometry import get_angle
from Util.geometry import *
from RULEngine.Util.constant import *


__author__ = 'jama'


class tKickTarget(TacticBase):
    """
    tKickTarget kick the ball to the center of the field
    """
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        goal_position = Position(0, 0)
        bot_position = info_manager.getPlayerPosition(id_player)
        dst_bot_center = distance(goal_position, bot_position)
        if info_manager.getPlayerOrientation(id_player) != get_angle(bot_position, goal_position):
            return {'skill': 'sFaceTarget', 'target': goal_position, 'goal': bot_position}
        else:
            if dst_bot_center < 2 * FIELD_X_RIGHT / 3:
                return {'skill': 'sKickLow', 'target': bot_position, 'goal': bot_position}
            elif dst_bot_center > 2 * 2 * FIELD_X_RIGHT / 3:
                return {'skill': 'sKickHigh', 'target': bot_position, 'goal': bot_position}
            else:
                return {'skill': 'sKickMedium', 'target': bot_position, 'goal': bot_position}
