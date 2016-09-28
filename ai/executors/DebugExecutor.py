from RULEngine.Util.Pose import Pose, Position
from ai.Debug.UIDebugCommand import UIDebugCommand
from ai.executors.Executor import Executor
from ai.states.PlayState import STAStatus
import copy

class DebugExecutor(Executor):

    def __init__(self, p_world_state):
        super().__init__(p_world_state)

    def exec(self):

        self._execute_incoming_debug_commands()
        self._execute_outgoing_debug_commands()

    def _execute_incoming_debug_commands(self):
        for command in self.ws.debug_state.from_ui_debug_commands:
            self.ws.debug_state.transformed_ui_debug_commands.append(UIDebugCommand(command))

        self._apply_incoming_debug_command()

    def _apply_incoming_debug_command(self):
        for command in self.ws.debug_state.transformed_ui_debug_commands:
            self._parse_command(command)

    def _execute_outgoing_debug_commands(self):
        # todo make this work!
        packet_represented_commands = [c.get_packet_repr() for c in self.ws.debug_state.from_ai_raw_debug_cmds]
        #print(self.ws.debug_state.to_ui_packet_debug_cmds)
        self.ws.debug_state.to_ui_packet_debug_cmds = copy.deepcopy(packet_represented_commands)
        try:
            print(type(self.ws.debug_state.to_ui_packet_debug_cmds[0]))
        except:
            pass
        self.ws.debug_state.from_ai_raw_debug_cmds.clear()

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
            self.ws.play_state.set_strategy(self.ws.play_state.get_new_strategy("DoNothing")(self.ws.game_state))
            self._lock_in_strategy()

        else:
            self.ws.play_state.set_strategy(strategy_key)
            self._lock_in_strategy()

    def _lock_in_strategy(self):
        self.ws.play_state.set_strategy_status(STAStatus.LOCKED)
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

        self.ws.play_state.set_tactic(player_id, self.ws.play_state.get_new_tactic(tactic_name)(self.ws.game_state,
                                                                                                player_id),
                                      STAStatus.LOCKED)

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
