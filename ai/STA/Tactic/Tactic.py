# Under MIT licence, see LICENCE.txt

from abc import abstractmethod
from functools import wraps
from ai import InfoManager
from ai.STA.Tactic import tactic_constants
from ai.STA.Action.Idle import Idle

__author__ = 'RobocupULaval'


class Tactic:
    """
        Classe mère de toutes les tactiques
    """

    def __init__(self, p_info_manager):
        """
            Initialise la tactique

            :param p_info_manager: référence à la façade InfoManager
        """
        #assert isinstance(p_info_manager, InfoManager)
        self.info_manager = p_info_manager
        self.player_id = None
        self.current_state = self.halt
        self.next_state = self.halt
        self.status_flag = tactic_constants.INIT

    def halt(self):
        """
            S'exécute lorsque l'état courant est *Halt*
            :return: l'action Stop crée
        """
        stop = Idle(self.info_manager, self.player_id)
        self.next_state = self.halt
        return stop

    def exec(self):
        """
            Exécute une *Action* selon l'état courant
        """
        next_action = self.current_state()
        next_ai_command = next_action.exec()
        self.info_manager.set_player_next_action(self.player_id, next_ai_command)
        self.current_state = self.next_state

    def __str__(self):
        return self.__class__.__name__
