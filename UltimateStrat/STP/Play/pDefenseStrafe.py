from UltimateStrat.STP.Play.PlayBase import PlayBase

__author__ = 'gados'


class pDefenseStrafe(PlayBase):
    """
    pDefense represents the play in which robots intercept the ball coming towards the goalie and kick it in opponent side
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)

    def getTactics(self, index=None):
        sequence = [['tStop', 'tStop', 'tStop', 'tStop', 'tIntercept', 'tStop']]
        if index is None:
            return sequence[0]
        else:
            return sequence[index]