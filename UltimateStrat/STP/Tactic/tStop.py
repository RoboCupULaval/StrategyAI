from UltimateStrat.STP.Tactic.TacticBase import TacticBase

__author__ = 'jbecirovski'


class tStop(TacticBase):
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        bot_position = info_manager.getPlayerPosition(id_player)
        return {'skill': 'sStop', 'target': bot_position, 'goal': bot_position}