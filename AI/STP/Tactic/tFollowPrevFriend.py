# Under MIT License, see LICENSE.txt
""" Tactic pour suivre le précédent robot """
from AI.STP.Tactic.TacticBase import TacticBase
from RULEngine.Util.geometry import *

__author__ = 'RoboCupULaval'


class tFollowPrevFriend(TacticBase):
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        player_position = info_manager.get_prev_player_position(id_player)
        bot_position = info_manager.get_player_position(id_player)
        dst_ball_bot = get_distance(player_position, bot_position)
        if dst_ball_bot > 500:
            return {'skill': 'sGoToTarget', 'target': player_position, 'goal': bot_position}
        else:
            return {'skill': 'sGoToTarget', 'target': bot_position, 'goal': bot_position}
