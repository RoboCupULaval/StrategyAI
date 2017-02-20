# Under MIT License, see LICENSE.txt

from RULEngine.Debug.ui_debug_command import UIDebugCommand
from RULEngine.Util.Pose import Pose, Position
from ai.STA.Strategy.HumanControl import HumanControl
from ai.executors.executor import Executor
from ai.states.world_state import WorldState


class DebugExecutor(Executor):

    def __init__(self, p_world_state: WorldState):
        super().__init__(p_world_state)
        self.debug_in = []

    def exec(self):
        self._execute_incoming_debug_commands()

    def _execute_incoming_debug_commands(self):
        for command in self.debug_in:
            self._parse_command(UIDebugCommand(command))

    def set_reference(self, debug_ref)->None:
        self.debug_in = debug_ref

    def _parse_command(self, cmd: UIDebugCommand)->None:
        if cmd.is_strategy_cmd():
            self._parse_strategy(cmd)

        elif cmd.is_tactic_cmd():
            self._parse_tactic(cmd)

        else:
            pass

    def _parse_strategy(self, cmd: UIDebugCommand)->None:
        # TODO revise this function please, thank you!
        # TODO change this once UI-Debug send correct strategy names!

        strategy_key = cmd.data['strategy']

        if strategy_key == 'pStop':
            self.ws.play_state.set_strategy(self.ws.play_state.
                                            get_new_strategy("DoNothing")
                                            (self.ws.game_state))

        else:
            self.ws.play_state.set_strategy(self.ws.play_state.
                                            get_new_strategy(strategy_key)
                                            (self.ws.game_state))

    def _parse_tactic(self, cmd: UIDebugCommand)->None:
        # TODO make implementation for other tactic packets!
        # FIXME this pid thingy is getting out of control
        player_id = self._sanitize_pid(cmd.data['id'])
        tactic_name = cmd.data['tactic']

        # TODO ui must send better packets back with the args.
        target = cmd.data['target']
        target = Pose(Position(target[0], target[1]))
        tactic = self.ws.play_state.get_new_tactic('Idle')(self.ws.game_state,
                                                           player_id,
                                                           target)
        try:
            tactic = self.ws.play_state.get_new_tactic(tactic_name)\
                (self.ws.game_state, player_id, target)
        except Exception as e:
            print(e)
            print("La tactique n'a pas été appliquée par "
                  "cause de mauvais arguments.")

        if isinstance(self.ws.play_state.current_strategy, HumanControl):
            hc = self.ws.play_state.current_strategy
            hc.assign_tactic(tactic, player_id)
        else:
            hc = HumanControl(self.ws.game_state)
            hc.assign_tactic(tactic, player_id)
            self.ws.play_state.set_strategy(hc)

    @staticmethod
    def _sanitize_pid(pid: int)->int:
        # TODO find something better for this whole scheme
        if 0 <= pid < 6:
            return pid
        elif 6 <= pid < 12:
            return pid - 6
        else:
            return 0
