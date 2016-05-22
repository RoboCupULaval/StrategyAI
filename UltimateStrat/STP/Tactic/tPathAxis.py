#Under MIT License, see LICENSE.txt
from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from RULEngine.Util.Position import Position

class tPathAxis(TacticBase):
    """
    Comportement pour un robot qui a le pathfinder Axis
    """
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        p_ball = info_manager.getBallPosition()
        return {'skill': 'sPathAxis', 'target': p_ball, 'goal': p_ball}
