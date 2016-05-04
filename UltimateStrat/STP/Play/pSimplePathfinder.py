__author__ = 'MGagnon-Legault'

from UltimateStrat.STP.Play.PlayBase import PlayBase

class pSimplePathfinder(PlayBase):
    """

    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)

    def getTactics(self, index=None):
        sequence = [['tStop', 'tStop', 'tStop',
                          'tStop', 'tSimplePathfinder', 'tStop']]

        if index is None:
            return sequence[0]
        else:
            return sequence[index]

