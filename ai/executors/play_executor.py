# Under MIT License, see LICENSE.txt

__author__ = "Maxime Gagnon-Legault"

from RULEngine.Util.singleton import Singleton

from ai.Util.sta_change_command import STAChangeCommand
from ai.Algorithm.auto_play import SimpleAutoPlay
from ai.Util.role import Role
from ai.states.game_state import GameState
from ai.states.play_state import PlayState
from config.config_service import ConfigService


class PlayExecutor(metaclass=Singleton):

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
        return
        if PlayState().autonomous_flag:
            if GameState().game.referee.team_info['ours']['goalie'] != self.goalie_id:
                self.goalie_id = GameState().game.referee.team_info['ours']['goalie']
                GameState().update_player_for_locked_role(self.goalie_id, Role.GOALKEEPER)
            self.auto_play.update(self._has_available_players_changed())

        self._execute_strategy()

        # self._send_auto_state()

    def order_change_of_sta(self, cmd: STAChangeCommand):
        pass

    def _execute_strategy(self) -> None:
        # Applique un stratégie par défault s'il n'en a pas (lors du démarage par exemple)
        # TODO change this so we don't send humancontrol when nothing is set/ Donothing would be better
        if PlayState().current_strategy is None:
            PlayState().set_strategy(PlayState().get_new_strategy("HumanControl")(GameState()))
        # L'éxécution en tant que telle
        PlayState().current_strategy.exec()
        # self.ws.play_state.current_ai_commands = self.ws.play_state.current_strategy.exec()

    # def _send_auto_state(self) -> None:
    #     self.ws.debug_interface.send_play_info(self.ws.game_state.game.referee.info,
    #                                             self.ws.game_state.game.referee.team_info,
    #                                             self.auto_play.info,
    #                                             self.ws.play_state.autonomous_flag)

    # def _send_books(self) -> None:
    #     """
    #     Envoie les livres de stratégies et de tactiques
    #
    #     :return: None
    #     """
    #     cmd_tactics = {'strategy': self.ws.play_state.
    #                    strategy_book.get_strategies_name_list(),
    #                    'tactic': self.ws.play_state.tactic_book.
    #                    get_tactics_name_list(),
    #                    'action': ['None']}
    #     self.ws.debug_interface.send_books(cmd_tactics)

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
