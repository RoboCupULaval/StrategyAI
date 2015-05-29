from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from Util.geometry import *
__author__ = 'jbecirovski'


class tFollowBall(TacticBase):
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, bot_id):
        ball_position = info_manager.getBallPosition()
        bot_position = info_manager.getPlayerPosition(bot_id)
        dst_ball_bot = distance(ball_position, bot_position)

        if dst_ball_bot > 200:
            return ['sFollowTarget', ball_position, bot_position]
        else:
            return ['sFollowTarget', bot_position, bot_position]