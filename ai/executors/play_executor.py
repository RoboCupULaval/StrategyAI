# Under MIT License, see LICENSE.txt
import time

from multiprocessing import Queue

from Debug.uidebug_command_factory import UIDebugCommandFactory
from Util.role import Role
from ai.Algorithm.auto_play import SimpleAutoPlay
from ai.executors.executor import Executor
from ai.states.game_state import GameState
from ai.states.play_state import PlayState
from config.config_service import ConfigService


class PlayExecutor(Executor):

    def __init__(self, ui_recv_queue: Queue):
        """
        initialise le PlayExecutor

        :param p_world_state: (WorldState) instance du worldstate
        """
        super().__init__()
        cfg = ConfigService()
        self.auto_play = SimpleAutoPlay()
        PlayState().autonomous_flag = cfg.config_dict["GAME"]["autonomous_play"] == "true"
        self.last_time = 0
        self.last_available_players = {}
        self.goalie_id = -1
        self.ui_recv_queue = ui_recv_queue

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

        if time.time() - self.last_time > 0.25:
            # TODO use handshake with the UI-DEBUG to stop sending it every frame! MGL 2017/03/16
            self._send_books()
            self.last_time = time.time()


    def _send_books(self) -> None:
        """
        Envoie les livres de stratégies et de tactiques

        :return: None
        """
        cmd_tactics = {'strategy': PlayState().strategy_book.get_strategies_name_list(),
                       'tactic': PlayState().tactic_book.get_tactics_name_list(),
                       'action': ['None']}

        msg = UIDebugCommandFactory().send_books(cmd_tactics)
        self.ui_recv_queue.put(msg)


    def _has_available_players_changed(self) -> bool:
        available_players = GameState().my_team.available_players
        player_change = False
        for i in available_players:
            if i not in self.last_available_players:
                player_change = True
                break
        if not player_change:
            for i in self.last_available_players:
                if i not in available_players:
                    player_change = True
                    break
        self.last_available_players = available_players.copy()
        return player_change
