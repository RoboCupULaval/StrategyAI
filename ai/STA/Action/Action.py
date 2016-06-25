# Under MIT licence, see LICENCE.txt

from abc import abstractmethod
from functools import wraps

from ...Util import geometry
from ...Util.types import AICommand

__author__ = 'Robocup ULaval'

class Action:
    """
    Classe mère de toutes les actions
    """
    def __init__(self, p_info_manager):
        """
            :param pInfoManager: référence vers l'InfoManager
        """
        self.InfoManager = p_info_manager

    def on_before(self):
        pass

    def on_after(self):
        pass

    @abstractmethod
    def exec(self):
        """
        Calcul la prochaine action d'un joueur
        :return: AICommand
        """
        pass

