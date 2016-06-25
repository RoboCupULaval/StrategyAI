# Under MIT licence, see LICENCE.txt

__author__ = 'Robocup ULaval'

from abc import abstractmethod
from functools import wraps
from ... import InfoManager
from ..Action.Stop import Stop


class Tactic:
    """
        Classe mère de toutes les tactiques
    """

    def __init__(self, p_info_manager):
        """
            Initialise la tactique

            Lors de la création d'une nouvelle tactique, il faut ajouter
            Sinon, on risque de perdre l'état halt

            :param p_info_manager: référence à la façade InfoManager
        """
        self.info_manager = p_info_manager
        self.player_id = None
        self.current_state = 'halt'
        self.next_state = 'halt'
        self.dispatch = {'halt': self.halt}

    def halt(self):
        """
            S'exécute lorsque l'état courant est *Halt*
            :return: l'action Stop crée
        """
        stop = Stop(self.info_manager, self.player_id)
        self.next_state = 'halt'
        return stop

    def exec(self):
        """
            Exécute une *Action* selon l'état courant
        """
        next_action = self.dispatch[self.current_state]()
        next_ai_command = next_action.exec()
        self.info_manager.set_player_next_action(self.player_id, next_ai_command)
        self.current_state = self.next_state
