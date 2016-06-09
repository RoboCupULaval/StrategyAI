# Under MIT licence, see LICENCE.txt

__author__ = 'Robocup ULaval'


from abc import abstractmethod
from functools import wraps
from ... import InfoManager
from ...Util import geometry

class Action:
    """
    Classe mère de toutes les actions
    méthodes:
        exec(self) : Retourne un tuple (Pose, kick)
            où Pose est la position où le robot doit aller
               kick est un booléen qui détermine si le robot doit frapper ou non
    attributs:
        info_manager: référence à la façade InfoManager
    """
    def __init__(self, info_manager):
        self.info_manager = info_manager

    @abstractmethod
    def exec(self):
        pass