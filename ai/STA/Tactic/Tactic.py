# Under MIT licence, see LICENCE.txt
from typing import List

from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic.tactic_constants import DEFAULT_TIME_TO_LIVE, Flags
from ai.Util.ai_command import AICommand
from ai.states.game_state import GameState

__author__ = 'RobocupULaval'


class Tactic:
    """
        Classe mère de toutes les tactiques
    """

    def __init__(self, p_game_state: GameState, player: Player, target: Pose=Pose(), args: List[str]=None,
                 time_to_live: float=DEFAULT_TIME_TO_LIVE):
        """
        Initialise la tactic avecc des valeurs par défault

        :param p_game_state: L'état du monde pour le jeu en cours
        :param player_id: L'identifiant du robot
        :param target: Pose général pouvant être utilisé par les classes enfants comme elles veulent
        :param time_to_live: Temps de vie de la tactique avant qu'elle ne se réinitialise (pas implémenter?)
        """
        assert isinstance(p_game_state, GameState)
        assert isinstance(player, Player)
        assert isinstance(target, Pose), "La target devrait être une Pose"

        self.game_state = p_game_state
        self.player = player
        self.player_id = player.id

        self.args = args
        if self.args is None:
            self.args = []

        self.current_state = self.halt
        self.next_state = self.halt
        self.status_flag = Flags.INIT
        self.target = target
        self.time_to_live = time_to_live
        self.last_state_time = self.game_state.get_timestamp()

    def halt(self) -> Idle:
        """
            S'exécute lorsque l'état courant est *Halt*. Générique pour arrêter n
            'importe quelles tactiques enfants

            :return: un nouvelle instance de l'action Idle pour le robot
        """
        stop = Idle(self.game_state, self.player_id)
        self.next_state = self.halt
        return stop

    def exec(self) -> AICommand:
        """
            Exécute une *Action* selon l'état courant

            :return: un AICommand
        """
        tactic_time = self.game_state.get_timestamp()
        next_action = self.current_state()
        if tactic_time - self.last_state_time > self.time_to_live > 0:
            self._reset_ttl()

        self.current_state = self.next_state
        next_ai_command = next_action.exec()
        self.player.ai_command = next_ai_command
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
        # TODO revise please MGL 2017/03/16
        self.last_state_time = self.game_state.timestamp
