# Under MIT licence, see LICENCE.txt

from abc import abstractmethod

__author__ = 'Robocup ULaval'


class Action:
    """
    Classe mère de toutes les actions
    """
    def __init__(self, p_info_manager):
        """
            :param p_info_manager: référence vers l'InfoManager
        """
        # FIXME: hack
        # assert(isinstance(p_info_manager, InfoManager))
        self.info_manager = p_info_manager

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

    def __str__(self):
        return self.__class__.__name__

