from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from RULEngine.Util.geometry import *

__author__ = 'RoboCupULaval'


class tFollowBall(TacticBase):
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        ball_position = info_manager.getBallPosition()
        bot_position = info_manager.getPlayerPosition(id_player)
        #print("follow:" + str(bot_position))
        #print(info_manager.black_board['friend'][str(id_player)].keys())
        dst_ball_bot = get_distance(ball_position, bot_position)
        if dst_ball_bot > 500:
            return {'skill': 'sGoToTarget', 'target': ball_position, 'goal': bot_position}
        else:
            return {'skill': 'sGoToTarget', 'target': bot_position, 'goal': bot_position}