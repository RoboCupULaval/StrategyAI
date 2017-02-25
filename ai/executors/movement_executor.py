from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import get_distance
from ai.executors.executor import Executor
import math

ROBOT_NEAR_FORCE = 30
ROBOT_VELOCITY_MAX = 4
ROBOT_ACC_MAX = 2


class MovementExecutor(Executor):

    def __init__(self, p_world_state):
        super().__init__(p_world_state)
        self.debug_interface = DebugInterface()
        self._sanity_check_of_speed_command()

    def exec(self):
        self._simple_advance_path()
        self._sanity_check_of_speed_command()

    def _simple_advance_path(self):
        current_ai_c = self.ws.play_state.current_ai_commands

        for ai_c in current_ai_c.values():
            if len(ai_c.path) > 1:
                next_point = ai_c.path[1]
                ai_c.pose_goal = Pose(next_point, ai_c.pose_goal.orientation)
                ai_c.speed = Pose(next_point, ai_c.pose_goal.orientation)
            if len(ai_c.path) > 0:
                next_point = ai_c.path[0]
                ai_c.pose_goal = Pose(next_point, ai_c.pose_goal.orientation)
                ai_c.speed = Pose(next_point, ai_c.pose_goal.orientation)
            else:
                ai_c.speed = ai_c.pose_goal
                #print(ai_c.speed)

    def _sanity_check_of_speed_command(self):
        for ai_c in self.ws.play_state.current_ai_commands.values():
            if ai_c.speed is None:
                ai_c.speed = ai_c.pose_goal

