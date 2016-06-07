##Under MIT License, see LICENSE.txt
from AI.STP.Play.PlayBase import PlayBase

__author__ = 'RoboCupULaval'

SEQUENCE_DEFENSE = ['tGoalKeeper', 'tGoalKeeper', 'tGoalKeeper',
                    'tGoalKeeper', 'tGoalKeeper', 'tGoalKeeper']


class pDefense(PlayBase):
    """
    Competition mode:
     x GoalKeeper behaviour versus three forwards.
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)
        self._sequence = [SEQUENCE_DEFENSE]

    def getTactics(self, index=None):
        if index is None:
            return self._sequence[0]
        else:
            return self._sequence[index]
