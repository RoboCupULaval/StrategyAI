from UltimateStrat.STP.Play.PlayBase import PlayBase

__author__ = 'jbecirovski'


class pHalt(PlayBase):
    """
    Default mode:
     + All bots stop their current action.
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)

    def getTactics(self, index=None):
        sequence = [['tNull' for x in range(6)]]
        if index is None:
            return sequence[0]
        else:
            return sequence[index]
