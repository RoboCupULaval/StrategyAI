# Under MIT licence, see LICENCE.txt

from abc import abstractmethod

from functools import wraps,partial
from ai import InfoManager
from ai.STA.Tactic import tactic_constants
from ai.STA.Action.Idle import Idle

from RULEngine.Util.Pose import Pose

__author__ = 'RobocupULaval'


class Tactic:
    """
        Classe mère de toutes les tactiques
    """

    def __init__(self, p_info_manager, target=Pose(), time_to_live=tactic_constants.DEFAULT_TIME_TO_LIVE):
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
        self.target = target
        self.time_to_live = time_to_live
        self.last_state_time = self.info_manager.timestamp

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
        tactic_time = self.info_manager.timestamp
        next_action = self.current_state()
        if tactic_time - self.last_state_time > self.time_to_live and self.time_to_live > 0:
            self._reset_ttl()

        self.current_state = self.next_state
        next_ai_command = next_action.exec()
        return next_ai_command

    def _reset_ttl(self):
        """
            Quand le TTL expire, on réévalue le prochain état.
            Par défaut on ne fait rien.
        """
        self.last_state_time = self.info_manager.timestamp
