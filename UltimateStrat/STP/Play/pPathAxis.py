#Under MIT License, see LICENSE.txt
from UltimateStrat.STP.Play.PlayBase import PlayBase

__author__ = 'RoboCupULaval'

SEQUENCE_PATH_AXIS = ['tNull', 'tNull', 'tNull',
                      'tNull', 'tPathAxis', 'tNull']

class pPathAxis(PlayBase):
    """
    Strategie de base qui permet au premier robot de se positionner sur la balle avec son dribbler.
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)
        self._sequence = [SEQUENCE_PATH_AXIS]

    def getTactics(self, index=None):
        if index is None:
            return self._sequence[0]
        else:
            return self._sequence[index]
