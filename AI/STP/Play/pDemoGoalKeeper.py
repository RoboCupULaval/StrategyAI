#Under MIT License, see LICENSE.txt
from AI.STP.Play.PlayBase import PlayBase

__author__ = 'RoboCupULaval'

SEQUENCE_DEMO_GOAL_KEEPER = ['tGoalKeeper', 'tGoalKeeper', 'tGoalKeeper',
                             'tGoalKeeper', 'tGoalKeeper', 'tGoalKeeper']


class pDemoGoalKeeper(PlayBase):
    """
    Demonstration mode:
     + GoalKeeper behaviour for all bots.
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)
        self._sequence = [SEQUENCE_DEMO_GOAL_KEEPER]

    def getTactics(self, index=None):
        if index is None:
            return self._sequence[0]
        else:
            return self._sequence[index]
