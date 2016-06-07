#Under MIT License, see LICENSE.txt
from AI.STP.Play.PlayBase import PlayBase

__author__ = 'RoboCupULaval'

SEQUENCE_PATH = ['tNull', 'tNull', 'tNull',
                 'tNull', 'tPath', 'tNull']

class pPath(PlayBase):
    """
    Default mode:
     + All bots stop their current action.
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)
        self._sequence = [SEQUENCE_PATH]

    def getTactics(self, index=None):
        if index is None:
            return self._sequence[0]
        else:
            return self._sequence[index]
