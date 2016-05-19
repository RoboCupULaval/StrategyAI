from RULEngine.Util.Pose import Pose, Position
from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from Util.geometry import *

__author__ = 'jbecirovski'


class tKickerTest(TacticBase):
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        bot_pst = info_manager.getPlayerPosition(id_player)
        ball_pst = info_manager.getBallPosition()

        if distance(Position(), ball_pst) < 500:
            if distance(bot_pst, ball_pst) < 180:
                return {'skill': 'sKickMedium', 'target': bot_pst, 'goal': bot_pst}
            else:
                return {'skill': 'sFollowTarget', 'target': ball_pst, 'goal': bot_pst}
        else:
            return {'skill': 'sFollowTarget', 'target': Position(1000, 0), 'goal': bot_pst}
