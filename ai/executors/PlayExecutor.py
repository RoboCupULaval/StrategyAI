from ai.executors.Executor import Executor


class PlayExecutor(Executor):

    def __init__(self, p_world_state):
        super().__init__(p_world_state)

    def exec(self):
        self._send_books()

        self._execute_strategy()
        self._send_robots_status()

    def _execute_strategy(self):
        if self.ws.play_state.current_strategy is None:
            self.ws.play_state.set_strategy(self.ws.play_state.get_new_strategy("DoNothing")(self.ws.game_state))
        self.ws.play_state.current_ai_commands = self.ws.play_state.current_strategy.exec()

            # FIXME revise this function please
    def _send_robots_status(self):
        states = self.ws.play_state.get_current_tactical_state()
        for state in states:
            player_id = state[0]
            tactic_name = state[1]
            action_name = state[2]
            target = (int(state[3].position.x), int(state[3].position.y))
            self.ws.debug_interface.send_robot_status(player_id,
                                                      tactic_name,
                                                      action_name,
                                                      target)

    def _send_books(self):
        cmd_tactics = {'strategy': self.ws.play_state.strategy_book.get_strategies_name_list(),
                       'tactic': self.ws.play_state.tactic_book.get_tactics_name_list(),
                       'action': ['None']}
        self.ws.debug_interface.send_books(cmd_tactics)
