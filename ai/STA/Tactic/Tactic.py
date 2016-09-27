# Under MIT licence, see LICENCE.txt

from functools import partial

from RULEngine.Util.Pose import Pose
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic import tactic_constants

__author__ = 'RobocupULaval'


class Tactic:
    """
        Classe mère de toutes les tactiques
    """

    def __init__(self, p_gamestatemanager, player_id, target=Pose(),
                 time_to_live=tactic_constants.DEFAULT_TIME_TO_LIVE):
        """
            Initialise la tactique

            :param p_info_manager: référence à la façade InfoManager
        """
        self.GameStateManager = p_gamestatemanager
        self.player_id = player_id
        self.current_state = self.halt
        self.next_state = self.halt
        self.status_flag = tactic_constants.INIT
        self.target = target
        self.time_to_live = time_to_live
        self.last_state_time = self.GameStateManager.get_timestamp()

    def halt(self, reset=False):
        """
            S'exécute lorsque l'état courant est *Halt*
            :return: l'action Stop crée
        """
        stop = Idle(self.GameStateManager, self.player_id)
        self.next_state = self.halt
        return stop

    def exec(self):
        """
            Exécute une *Action* selon l'état courant
        """
        tactic_time = self.GameStateManager.get_timestamp()
        next_action = self.current_state()
        if tactic_time - self.last_state_time > self.time_to_live and self.time_to_live != 0:
            self.last_state_time = tactic_time
            self.next_state = partial(self.halt, reset=True)

        self.current_state = self.next_state
        next_ai_command = next_action.exec()
        return next_ai_command

    def get_name(self):
        return self.__class__.__name__
