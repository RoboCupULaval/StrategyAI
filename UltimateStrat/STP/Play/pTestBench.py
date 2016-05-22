#Under MIT License, see LICENSE.txt
from UltimateStrat.STP.Play.PlayBase import PlayBase

__author__ = 'RoboCupULaval'


class pTestBench(PlayBase):
    """
    pTestBench is a test bench play for testing some tactics
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)

    def getTactics(self, index=None):
        sequence = [['tTestBench', 'tStop', 'tStop',
                          'tStop', 'tStop', 'tStop']]
        if index is None:
            return sequence[0]
        else:
            return sequence[index]
