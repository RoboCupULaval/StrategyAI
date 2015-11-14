from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from RULEngine.Util.geometry import *

__author__ = 'jbecirovski'

DEAD_ZONE = 300

class tPath(TacticBase):
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        ball_pst = info_manager.getBallPosition()
        bot_pst = info_manager.getPlayerPosition(id_player)
        dst = get_distance(ball_pst, bot_pst)
        
        if dst > DEAD_ZONE:
            return {'skill': 'sPath', 'target': ball_pst, 'goal': ball_pst}
        else:
            return {'skill': 'sNull', 'target': ball_pst, 'goal': ball_pst}