#Under MIT License, see LICENSE.txt
from UltimateStrat.STP.Tactic.TacticBase import TacticBase

__author__ = 'RoboCupULaval'


class tStop(TacticBase):
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        bot_position = info_manager.get_player_position(id_player)
        return {'skill': 'sStop', 'target': bot_position, 'goal': bot_position}
