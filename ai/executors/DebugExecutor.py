from RULEngine.Util.Pose import Pose, Position
from ai.Debug.UIDebugCommand import UIDebugCommand
from ai.executors.Executor import Executor
from ai.states.PlayState import STAStatus


class DebugExecutor(Executor):

    def __init__(self):
        super().__init__()

    def exec(self, p_world_state):
        self.ws = p_world_state
        self._execute_incoming_debug_commands()
        self._execute_outgoing_debug_commands()

    def _execute_incoming_debug_commands(self):
        for command in self.ws.debug_state.raw_ui_debug_commands:
            self.ws.debug_state.transformed_ui_debug_commands.append(UIDebugCommand(command))

        self._apply_incoming_debug_command()

    def _apply_incoming_debug_command(self):
        for command in self.ws.debug_state.transformed_ui_debug_commands:
            self._parse_command(command)

    def _execute_outgoing_debug_commands(self):
        # todo make this work!
        for command in self.ws.debug_state.to_ui_debug_commands:
            pass
        pass

    def _parse_command(self, cmd):
        if cmd.is_strategy_cmd():
            self._parse_strategy(cmd)

        elif cmd.is_tactic_cmd():
            self._parse_tactic(cmd)

        else:
            pass

    def _parse_strategy(self, cmd):
        # TODO revise this function please, thank you!
        # TODO change this once UI-Debug send correct strategy names!

        strategy_key = cmd.data['strategy']

        if strategy_key == 'pStop':
            self.ws.play_state.set_strategy("DoNothing")
            self._lock_in_strategy()

        else:
            self.ws.play_state.set_strategy(strategy_key)
            self._lock_in_strategy()

    def _lock_in_strategy(self):
        self.ws.play_state.current_strategy[0](STAStatus.LOCKED)
        self.ws.play_state.set_tactic_status([0, 1, 2, 3, 4, 5], STAStatus.FREE)

    def _parse_tactic(self, cmd):
        # TODO make implementation for other tactic packets! And finish this please
        # FIXME this pid thingy is getting out of control
        player_id = self._sanitize_pid(cmd.data['id'])

        self._lock_in_strategy()

        tactic_name = cmd.data['tactic']
        # TODO ui must send better packets back with the args.
        target = cmd.data['target']

        target = Pose(Position(target[0], target[1]))

        self.ws.play_state.set_tactic(tactic_name, STAStatus.LOCKED)

    def _lock_in_tactic(self, pid):
        self.ws.play_state.set_tactic_status(pid, STAStatus.LOCKED)

    @staticmethod
    def _sanitize_pid(pid):
        # TODO find something better for this whole scheme
        if 0 <= pid < 6:
            return pid
        elif 6 <= pid < 12:
            return pid - 6
        else:
            return 0
