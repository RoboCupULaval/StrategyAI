from ai.executors.Executor import Executor

from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Strategy.DoNothing import DoNothing


class PlayExecutor(Executor):

    def __init__(self):
        super().__init__()

    def exec(self, p_world_state):
        self.ws = p_world_state

        self._execute_strategy()
        self._execute_tactics()

    def _execute_strategy(self):
        strategy = self.ws.play_state.current_strategy.object
        if strategy is not None:
            tactic_sequence = strategy.get_next_tactics_sequence()
        else:
            self.ws.play_state.set_strategy(DoNothing(self.ws.game_state))
            tactic_sequence = self.ws.play_state.current_strategy.object.get_next_tactics_sequence()

        for player_id in range(0, 6):
            if self.ws.play_state.current_tactics[player_id].status:  # TODO See if that enum works as intended
                self.ws.play_state.set_tactic(player_id, tactic_sequence[player_id])

    def _execute_tactics(self):
        for player_id in range(0, 6):
            self.ws.play_state.current_ai_commands.append(self.ws.play_state.current_tactics[player_id].object.exec())

