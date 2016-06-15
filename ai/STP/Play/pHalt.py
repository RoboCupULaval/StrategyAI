# Under MIT License, see LICENSE.txt
""" Module contenant la stratégie pHalt. """
from ai.STP.Play.PlayBase import PlayBase

__author__ = 'RoboCupULaval'

SEQUENCE_HALT = ['tNull', 'tNull', 'tNull',
                 'tNull', 'tNull', 'tNull']


class pHalt(PlayBase):
    """ Cette stratégie applique la Tactic tHalt à tous les robots.
        Ils s'arrêtent complètement.
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)
        self._sequence = SEQUENCE_HALT

    def getTactics(self, index=None):
        if index is None:
            return self._sequence
        else:
            return self._sequence[index]
