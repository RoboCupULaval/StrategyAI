Under MIT License, see LICENSE.txt
from UltimateStrat.STP.Play.PlayBase import PlayBase

__author__ = 'RoboCupULaval'


class pDemoGoalKeeper(PlayBase):
    """
    Demonstration mode:
     + GoalKeeper behaviour for all bots.
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)

    def getTactics(self, index=None):
        sequence = [['tGoalKeeper' for x in range(6)]]
        if index is None:
            return sequence[0]
        else:
            return sequence[index]
