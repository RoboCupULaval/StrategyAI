from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from PythonFramework.Util.geometry import *

__author__ = 'jbecirovski'


class tFollowPrevFriend(TacticBase):
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        player_position = info_manager.getPrevPlayerPosition(id_player)
        bot_position = info_manager.getPlayerPosition(id_player)
        dst_ball_bot = get_distance(player_position, bot_position)
        if dst_ball_bot > 500:
            return {'skill': 'sGoToTarget', 'target': player_position, 'goal': bot_position}
        else:
            return {'skill': 'sGoToTarget', 'target': bot_position, 'goal': bot_position}