# Under MIT License, see LICENSE.txt
import time

from multiprocessing import Queue

from RULEngine.Debug.uidebug_command_factory import UIDebugCommandFactory
from Util.role import Role
from ai.Algorithm.auto_play import SimpleAutoPlay
from ai.executors.executor import Executor
from ai.states.game_state import GameState
from ai.states.play_state import PlayState
from config.config_service import ConfigService


class PlayExecutor(Executor):

    def __init__(self):
        """
        initialise le PlayExecutor

        :param p_world_state: (WorldState) instance du worldstate
        """
        super().__init__()
        cfg = ConfigService()
        self.auto_play = SimpleAutoPlay()
        PlayState().autonomous_flag = cfg.config_dict["GAME"]["autonomous_play"] == "true"
        self.last_available_players = {}
        self.goalie_id = -1

    def exec(self) -> None:
        """
        Execute la stratégie courante et envoie le status des robots et les livres de tactiques et stratégies

        :return: None
        """
        if PlayState().autonomous_flag:
            if GameState().game.referee.team_info['ours']['goalie'] != self.goalie_id:
                self.goalie_id = GameState().game.referee.team_info['ours']['goalie']
                GameState().update_player_for_locked_role(self.goalie_id, Role.GOALKEEPER)
            self.auto_play.update(self._has_available_players_changed())

        self._execute_strategy()

        # self._send_auto_state()

    def _execute_strategy(self) -> None:
        """
        Éxecute la stratégie courante.

        :return: None
        """
        # Applique un stratégie par défault s'il n'en a pas (lors du démarage par exemple)
        # TODO change this so we don't send humancontrol when nothing is set/ Donothing would be better
        if PlayState().current_strategy is None:
            PlayState().set_strategy(PlayState().get_new_strategy("HumanControl")(GameState()))
        # L'éxécution en tant que telle
        PlayState().current_strategy.exec()