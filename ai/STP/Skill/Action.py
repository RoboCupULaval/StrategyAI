# Under MIT licence, see LICENCE.txt

__author__ = 'Robocup ULaval'


from abc import abstractmethod
from functools import wraps
from ... import InfoManager
from ...Util import geometry

class Action:
    """
    Classe mère de toutes les actions
    """
    def __init__(self, pInfoManager):
        """
        Initialise l'action
        :param pInfoManager: référence vers l'InfoManager
        """
        self.InfoManager = pInfoManager

    def on_before(self):
        pass

    def on_after(self):
        pass

    @abstractmethod
    def exec(self):
        """
        Exécute la classe, doit être implémenté par les classes filles
        :return: Un tuple (Pose, kick)
            où Pose est la position où le robot doit aller
               kick est un booléen qui détermine si le robot doit frapper ou non
        """
        pass

