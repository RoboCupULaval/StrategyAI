from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from RULEngine.Util.geometry import get_angle
from Util.geometry import *
from RULEngine.Util.constant import *


__author__ = 'jama'


class tFaceBall(TacticBase):
    """
    tFaceBall always face the ball
    """
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        ball_position = info_manager.getBallPosition()
        bot_position = info_manager.getPlayerPosition(id_player)
        if info_manager.getPlayerOrientation(id_player) != get_angle(bot_position, ball_position):
            return {'skill': 'sFaceTarget', 'target': ball_position, 'goal': bot_position}
        else:
            return {'skill': 'sWait', 'target': bot_position, 'goal': bot_position}
