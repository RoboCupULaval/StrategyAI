from PythonFramework.Util.constant import *
from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from PythonFramework.Util.geometry import *
__author__ = 'jbecirovski'


class tGoalKeeper(TacticBase):
    """
    Basic behaviour for Goal Keeper.
    """
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        p_ball = info_manager.getBallPosition()
        return {'skill': 'sGoBehindTargetGoal_GK', 'target': p_ball, 'goal': Position(-4500, 0)}
