import math

from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import get_distance
from ai.executors.executor import Executor
from ai.Util.ai_command import AICommandType

ROBOT_NEAR_FORCE = 30
ROBOT_VELOCITY_MAX = 4
ROBOT_ACC_MAX = 2
PATHFINDER_DEADZONE = 100


class MovementExecutor(Executor):

    def __init__(self, p_world_state):
        super().__init__(p_world_state)
        self.debug_interface = DebugInterface()
        self._sanity_check_of_speed_command()

    def exec(self):
        # TODO revise and put in stone the way we do that! MGL 2017/03/16
        self._simple_advance_path()
        self._sanity_check_of_speed_command()

    def _simple_advance_path(self):
        current_ai_cmd = self.ws.play_state.current_ai_commands

        for ai_cmd in current_ai_cmd.values():
            if ai_cmd.path:
                current_pose = self.ws.game_state.get_player_pose(ai_cmd.robot_id)
                next_position = ai_cmd.path[0]
                distance = get_distance(current_pose.position, next_position)
                while distance < PATHFINDER_DEADZONE and len(ai_cmd.path) > 1:
                    self.ws.debug_interface.add_log(1, "Gestion path; retrait point trop rapproche.")
                    ai_cmd.path = ai_cmd.path[1:]
                    next_position = ai_cmd.path[0]
                    distance = get_distance(current_pose.position, next_position)
                ai_cmd.pose_goal = Pose(next_position, ai_cmd.pose_goal.orientation)

    def _sanity_check_of_speed_command(self):
        for ai_c in self.ws.play_state.current_ai_commands.values():
            if ai_c.speed is None:
                ai_c.speed = ai_c.pose_goal

