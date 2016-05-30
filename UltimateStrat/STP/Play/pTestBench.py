#Under MIT License, see LICENSE.txt
from UltimateStrat.STP.Play.PlayBase import PlayBase

__author__ = 'RoboCupULaval'

SEQUENCE_TEST_BENCH = ['tTestBench', 'tStop', 'tStop', 'tStop', 'tStop', 'tStop']

class pTestBench(PlayBase):
    """
    pTestBench is a test bench play for testing some tactics
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)
        self._sequence = SEQUENCE_TEST_BENCH

    def getTactics(self, index=None):
        if index is None:
            return self._sequence
        else:
            return self._sequence[index]
