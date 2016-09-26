# Under MIT licence, see LICENCE.txt

from abc import abstractmethod

__author__ = 'Robocup ULaval'


class Action:
    """
    Classe mère de toutes les actions
    """
    def __init__(self, p_gamestatemanager, p_playmanager):
        """
            :param p_info_manager: référence vers l'InfoManager
        """
        self.GameStateManager = p_gamestatemanager
        self.PlayManager = p_playmanager

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

    def get_name(self):
        return self.__class__.__name__
