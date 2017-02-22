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
        # self._potential_field()
        self._sanity_check_of_speed_command()


    def _simple_advance_path(self):
        current_ai_c = self.ws.play_state.current_ai_commands

        for ai_c in current_ai_c.values():
            if len(ai_c.path) > 0:
                next_point = ai_c.path[0]
                # TODO ORIENTATION! PLEASES!
                # TODO ORIENTATION! PLEASES!
                # TODO ORIENTATION! PLEASES!
                # TODO ORIENTATION! PLEASES!
                # TODO ORIENTATION! PLEASES!
                # TODO ORIENTATION! PLEASES!
                # TODO ORIENTATION! PLEASES!

                ai_c.pose_goal = Pose(next_point, ai_c.pose_goal.orientation)
                ai_c.speed = Pose(next_point, ai_c.pose_goal.orientation)
            else:
                ai_c.speed = ai_c.pose_goal
                #print(ai_c.speed)

    def _sanity_check_of_speed_command(self):
        for ai_c in self.ws.play_state.current_ai_commands.values():
            if ai_c.speed is None:
                ai_c.speed = ai_c.pose_goal

    def _potential_field(self):
        current_ai_c = self.ws.play_state.current_ai_commands

        for ai_c in current_ai_c.values():
            if len(ai_c.path) > 0:
                goal = ai_c.pose_goal
                force = [0, 0]
                current_robot_pos = self.ws.game_state.get_player_position(ai_c.robot_id)
                current_robot_velocity = self.ws.game_state.game.friends.players[ai_c.robot_id].velocity

                for robot in self.ws.game_state.game.friends.players.values():
                    if robot.id != ai_c.robot_id:
                        dist = get_distance(current_robot_pos, robot.pose.position)
                        angle = math.atan2(current_robot_pos.y - robot.pose.position.y,
                                           current_robot_pos.x - robot.pose.position.x)
                        force[0] += 1 / dist * math.cos(angle)
                        force[1] += 1 / dist * math.sin(angle)

                for robot in self.ws.game_state.game.enemies.players.values():
                    dist = get_distance(current_robot_pos, robot.pose.position)
                    angle = math.atan2(current_robot_pos.y - robot.pose.position.y,
                                       current_robot_pos.x - robot.pose.position.x)
                    force[0] += 1 / dist * math.cos(angle)
                    force[1] += 1 / dist * math.sin(angle)

                # dist_goal = get_distance(current_robot_pos, ai_c.pose_goal.position)
                angle_goal = math.atan2(current_robot_pos.y - ai_c.pose_goal.position.y,
                                        current_robot_pos.x - ai_c.pose_goal.position.x)

                dt = self.ws.game_state.game.delta_t

                a = (((current_robot_velocity[0] + 0.1) * math.cos(angle_goal) - current_robot_velocity[0]) / dt)
                b = (((current_robot_velocity[1] + 0.1) * math.cos(angle_goal) - current_robot_velocity[1]) / dt)
                acc_goal = math.sqrt(a**2 + b**2)

                angle_acc_goal = math.atan2(b, a)

                c = force[0] * ROBOT_NEAR_FORCE + (acc_goal*math.cos(angle_acc_goal))
                d = force[1] * ROBOT_NEAR_FORCE + (acc_goal*math.cos(angle_acc_goal))

                acc_robot_x = min(max(c, -ROBOT_ACC_MAX), ROBOT_ACC_MAX)
                acc_robot_y = min(max(d, -ROBOT_ACC_MAX), ROBOT_ACC_MAX)

                vit_robot_x = min(max(current_robot_velocity[0] + acc_robot_x * dt, -ROBOT_VELOCITY_MAX),
                                  ROBOT_VELOCITY_MAX)
                vit_robot_y = min(max(current_robot_velocity[1] + acc_robot_y * dt, -ROBOT_VELOCITY_MAX),
                                  ROBOT_VELOCITY_MAX)

