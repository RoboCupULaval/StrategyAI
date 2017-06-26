# Under MIT License, see LICENSE.txt
import time

from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Game.Referee import RefereeCommand
from ai.Algorithm.auto_play import SimpleAutoPlay
from ai.executors.executor import Executor
from ai.states.world_state import WorldState
from config.config_service import ConfigService


class PlayExecutor(Executor):

    def __init__(self, p_world_state: WorldState):
        """
        initialise le PlayExecutor

        :param p_world_state: (WorldState) instance du worldstate
        """
        super().__init__(p_world_state)
        cfg = ConfigService()
        self.auto_play = SimpleAutoPlay(self.ws)
        self.ws.play_state.autonomous_flag = cfg.config_dict["GAME"]["autonomous_play"] == "true"
        self.last_time = 0

    def exec(self) -> None:
        """
        Execute la stratégie courante et envoie le status des robots et les livres de tactiques et stratégies

        :return: None
        """

        if self.ws.play_state.autonomous_flag:
            self.auto_play.update()

        self._execute_strategy()

        #if time.time() - self.last_time > 0.25:
            # TODO use handshake with the UI-DEBUG to stop sending it every frame! MGL 2017/03/16
        self._send_books()
        self.ws.debug_interface.send_team_color()

        self._send_robots_status()
        self._send_auto_state()
        self.last_time = time.time()


    def _execute_strategy(self) -> None:
        """
        Éxecute la stratégie courante.

        :return: None
        """
        # Applique un stratégie par défault s'il n'en a pas (lors du démarage par exemple)
        # TODO change this so we don't send humancontrol when nothing is set/ Donothing would be better
        if self.ws.play_state.current_strategy is None:
            self.ws.play_state.set_strategy(self.ws.play_state.get_new_strategy("HumanControl")(self.ws.game_state))
        # L'éxécution en tant que telle
        self.ws.play_state.current_strategy.exec()
        # self.ws.play_state.current_ai_commands = self.ws.play_state.current_strategy.exec()

    def _send_robots_status(self) -> None:
        """
        Envoie le status des robots (id, nom tactic + flag de status,
         nom action (phase tactic), target) par le debug interface.

        :return: None
        """
        states = self.ws.play_state.get_current_tactical_state()
        for state in states:
            player_id = state[0]
            tactic_name = state[1]
            action_name = state[2]
            target = (int(state[3].position.x), int(state[3].position.y))
            self.ws.debug_interface.send_robot_strategic_state(player_id,
                                                               tactic_name,
                                                               action_name,
                                                               target)

    def _send_auto_state(self) -> None:
        self.ws.debug_interface.send_play_info(self.ws.game_state.game.referee.info,
                                                self.ws.game_state.game.referee.team_info,
                                                self.auto_play.info,
                                                self.ws.play_state.autonomous_flag)

    def _send_books(self) -> None:
        """
        Envoie les livres de stratégies et de tactiques

        :return: None
        """
        cmd_tactics = {'strategy': self.ws.play_state.
                       strategy_book.get_strategies_name_list(),
                       'tactic': self.ws.play_state.tactic_book.
                       get_tactics_name_list(),
                       'action': ['None']}
        self.ws.debug_interface.send_books(cmd_tactics)
