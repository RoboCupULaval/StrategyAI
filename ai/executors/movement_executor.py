
from RULEngine.Util.constant import POSITION_DEADZONE
from RULEngine.Util.geometry import get_distance
from ai.executors.executor import Executor
from ai.Debug.debug_interface import DebugInterface


class MovementExecutor(Executor):

    def __init__(self, p_world_state):
        super().__init__(p_world_state)
        self.debug_interface = DebugInterface()

    def exec(self):
        self._simple_advance_path()

    def _simple_advance_path(self):
        current_ai_c = self.ws.play_state.current_ai_commands

        for ai_c in current_ai_c.values():
            if len(ai_c.path) > 1:
                next_point = ai_c.path[0]
                r_id = ai_c.robot_id
                current_position = self.ws.game_state.get_player_position(r_id)
                distance = get_distance(next_point.position, current_position)
                if distance < POSITION_DEADZONE:
                    current_ai_c.pop(0)
                    next_point = ai_c.path[0]

                ai_c.pose_goal = next_point
