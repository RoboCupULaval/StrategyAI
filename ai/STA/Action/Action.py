# Under MIT licence, see LICENCE.txt

from abc import abstractmethod
from ai.states.game_state import GameState

__author__ = 'Robocup ULaval'


class Action:
    """
    Classe mère de toutes les actions
    """
    def __init__(self, p_game_state):
        """
            :param p_game_state: L'état courant du jeu.
        """
        # assert(isinstance(p_game_state, GameState))
        self.game_state = p_game_state

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

    def __str__(self):
        return self.__class__.__name__
