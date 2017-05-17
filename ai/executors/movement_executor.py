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

    def exec(self):
        # TODO revise and put in stone the way we do that! MGL 2017/03/16
        # self._simple_advance_path()
        # self._sanity_check_of_speed_command()
        pass

    def _simple_advance_path(self):

        for player in self.ws.game_state.my_team.available_players.values():
            if player.ai_command.path:
                current_pose = player.pose
                next_position = player.ai_command.path[0]
                distance = get_distance(current_pose.position, next_position)
                while distance < PATHFINDER_DEADZONE and len(player.ai_command.path) > 1:
                    self.ws.debug_interface.add_log(1, "Gestion path; retrait point trop rapproche.")
                    player.ai_command.path = player.ai_command.path[1:]
                    next_position = player.ai_command.path[0]
                    distance = get_distance(current_pose.position, next_position)
                    player.ai_command.pose_goal = Pose(next_position, player.ai_command.pose_goal.orientation)

    def _sanity_check_of_speed_command(self):
        for player in self.ws.game_state.my_team.available_players.values():
            if player.ai_command.speed is None:
                player.ai_command.speed = player.ai_command.pose_goal

