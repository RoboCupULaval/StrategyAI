from ai.executors.Executor import Executor

from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Strategy.DoNothing import DoNothing


class PlayExecutor(Executor):

    def __init__(self, p_world_state):
        super().__init__(p_world_state)

    def exec(self):
        self._send_books()

        self._execute_strategy()
        self._execute_tactics()
        self._send_robots_status()

    def _execute_strategy(self):
        strategy = self.ws.play_state.current_strategy.object
        if strategy is not None:
            tactic_sequence = strategy.get_next_tactics_sequence()
        else:
            self.ws.play_state.set_strategy(self.ws.play_state.get_new_strategy("DoNothing")(self.ws.game_state))
            tactic_sequence = self.ws.play_state.current_strategy.object.get_next_tactics_sequence()

        for player_id in range(0, 6):
            if self.ws.play_state.current_tactics[player_id].status:  # TODO See if that enum works as intended
                self.ws.play_state.set_tactic(player_id, tactic_sequence[player_id])

    def _execute_tactics(self):
        for player_id in range(0, 6):
            self.ws.play_state.current_ai_commands.append(self.ws.play_state.current_tactics[player_id].object.exec())

    # FIXME revise this function please
    def _send_robots_status(self):
        for player_id in range(0, 6):
            self.ws.debug_interface.send_robot_status(player_id,
                                                      self.ws.play_state.current_tactics[player_id][0].get_name(),
                                                      "None",
                                                      self.ws.play_state.current_tactics[player_id][0].target)

    def _send_books(self):
        cmd_tactics = {'strategy': self.ws.play_state.strategy_book.get_strategies_name_list(),
                       'tactic': self.ws.play_state.tactic_book.get_tactics_name_list(),
                       'action': ['None']}
        self.ws.debug_interface.send_books(cmd_tactics)
