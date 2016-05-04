from UltimateStrat.STP.Play.PlayBase import PlayBase

__author__ = 'yassinez'


class projet(PlayBase):
    """
    Notre projet est de demander au Robot d'avancer d'une certaine distance en esquivant les 3 obstacles.
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)

    def getTactics(self, index=None):
        sequence = [['tStop', 'tStop', 'tStop', 'tStop', 'tInfluence', 'tStop']]
        if index is None:
            return sequence[0]
        else:
            return sequence[index]