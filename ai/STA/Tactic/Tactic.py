# Under MIT licence, see LICENCE.txt

from functools import partial

from RULEngine.Util.Pose import Pose
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic.tactic_constants import DEFAULT_TIME_TO_LIVE, Flags

__author__ = 'RobocupULaval'


class Tactic:
    """
        Classe mère de toutes les tactiques
    """

    def __init__(self, p_game_state, player_id, target=Pose(),
                 time_to_live=DEFAULT_TIME_TO_LIVE):
        """
            Initialise la tactique

            :param p_info_manager: référence à la façade InfoManager
        """
        self.game_state = p_game_state
        self.player_id = player_id
        self.current_state = self.halt
        self.next_state = self.halt
        self.status_flag = Flags.INIT
        self.target = target
        self.time_to_live = time_to_live
        self.last_state_time = self.game_state.get_timestamp()

    def halt(self):
        """
            S'exécute lorsque l'état courant est *Halt*
            :return: l'action Stop crée
        """
        stop = Idle(self.game_state, self.player_id)
        self.next_state = self.halt
        return stop

    def exec(self):
        """
            Exécute une *Action* selon l'état courant
        """
        tactic_time = self.game_state.get_timestamp()
        next_action = self.current_state()
        if tactic_time - self.last_state_time > self.time_to_live and self.time_to_live > 0:
            self._reset_ttl()

        self.current_state = self.next_state
        next_ai_command = next_action.exec()
        return next_ai_command

    def get_name(self):
        return self.__class__.__name__

    def __str__(self):
        return self.__class__.__name__

    def _reset_ttl(self):
        """
            Quand le TTL expire, on réévalue le prochain état.
            Par défaut on ne fait rien.
        """
        self.last_state_time = self.game_state.timestamp
