# Under MIT License, see LICENSE.txt

import numpy as np
import math as m

from RULEngine.Debug import debug_interface
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.SpeedPose import SpeedPose
from RULEngine.Util.PID import PID
from ai.Algorithm.path_partitionner import CollisionBody
from ai.Util.ai_command import AICommandType, AIControlLoopType, AICommand
from ai.Util.role import Role
from ai.executors.executor import Executor
from ai.states.world_state import WorldState
from config.config_service import ConfigService

MIN_DISTANCE_TO_REACH_TARGET_SPEED = 0.5


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class MotionExecutor(Executor):
    def __init__(self, p_world_state: WorldState):
        super().__init__(p_world_state)
        is_simulation = ConfigService().config_dict["GAME"]["type"] == "sim"
        self.robot_motion = [RobotMotion(p_world_state, player_id, is_sim=is_simulation) for player_id in range(12)]


    def exec(self):
        for player in self.ws.game_state.my_team.available_players.values():
            if player.ai_command is None:
                continue

            cmd = player.ai_command
            r_id = player.id

            player.collision_body_mask[0] = CollisionBody.COLLIDABLE
            if player is not self.ws.game_state.get_player_by_role(Role.GOALKEEPER):
                player.collision_body_mask[1] = CollisionBody.COLLIDABLE
            else:
                player.collision_body_mask[1] = CollisionBody.UNCOLLIDABLE

            if cmd.command is AICommandType.MOVE:

                if cmd.control_loop_type is AIControlLoopType.POSITION:
                    cmd.speed = self.robot_motion[r_id].update(cmd)

                elif cmd.control_loop_type is AIControlLoopType.SPEED:
                    speed = cmd.pose_goal.position.rotate(-player.pose.orientation)
                    cmd.speed = SpeedPose(speed, cmd.pose_goal.orientation)

                elif cmd.control_loop_type is AIControlLoopType.OPEN:
                    cmd.speed = SpeedPose(cmd.pose_goal)

            elif cmd.command is AICommandType.STOP:
                cmd.speed = SpeedPose()
                self.robot_motion[r_id].reset()


class RobotMotion(object):
    def __init__(self, world_state: WorldState, robot_id, is_sim=True):
        self.ws = world_state
        self.id = robot_id
        self.is_sim = is_sim
        self.setting = get_control_setting(is_sim)
        self.setting.translation.max_acc = None
        self.setting.translation.max_speed = None
        self.setting.rotation.max_angular_acc = None
        self.setting.rotation.max_speed = None

        self.current_pose = Pose()
        self.current_orientation = 0.0
        self.current_velocity = Pose()
        self.current_angular_speed = 0.0
        self.current_speed = 0.0
        self.current_acceleration = Position()

        self.pose_error = Pose()
        self.position_error = Position()

        self.target_pose = Pose()
        self.target_speed = 0.0
        self.target_direction = Position()
        self.target_angular_speed = 0.0
        self.target_angle = 0.0
        self.angle_error = 0.0

        self.last_translation_cmd = Position()
        self.cruise_speed = 0.0
        self.cruise_angular_speed = 0.0

        self.next_speed = 0.0
        self.next_angular_speed = 0.0

        self.x_controller = PID(self.setting.translation.kp,
                                self.setting.translation.ki,
                                self.setting.translation.kd,
                                self.setting.translation.antiwindup)

        self.y_controller = PID(self.setting.translation.kp,
                                self.setting.translation.ki,
                                self.setting.translation.kd,
                                self.setting.translation.antiwindup)

        self.angle_controller = PID(self.setting.rotation.kp,
                                    self.setting.rotation.ki,
                                    self.setting.rotation.kd,
                                    self.setting.rotation.antiwindup,
                                    wrap_err=True)
        self.position_flag = False
        self.rotation_flag = False
        self.last_position = Position()
        self.target_turn = self.target_pose.position

    def update(self, cmd: AICommand) -> Pose():
        #print(cmd.path_speeds)
        self.update_states(cmd)

        # Rotation control
        rotation_cmd = self.angle_controller.update(self.pose_error.orientation, dt=self.dt)
        rotation_cmd = self.apply_rotation_constraints(rotation_cmd)
        if abs(self.pose_error.orientation) < 0.2:
            self.rotation_flag = True
        # Translation control
        self.position_flag = False
        if self.position_error.norm() < MIN_DISTANCE_TO_REACH_TARGET_SPEED * max(1.0, self.cruise_speed):
            if self.target_speed < 0.01:
                self.position_flag = True

        if self.position_flag:
            translation_cmd = Position(self.x_controller.update(self.pose_error.position.x, dt=self.dt),
                                       self.y_controller.update(self.pose_error.position.y, dt=self.dt))
        else:
            translation_cmd = self.get_next_velocity()
        # Adjust command to robot's orientation
        # self.ws.debug_interface.add_line(start_point=(self.current_pose.position[0] * 1000, self.current_pose.position[1] * 1000),
        #                                  end_point=(self.current_pose.position[0] * 1000 + translation_cmd[0] * 600, self.current_pose.position[1] * 1000 + translation_cmd[1] * 600),
        #                                  timeout=0.01, color=debug_interface.CYAN.repr())

        compasation_ref_world = translation_cmd.rotate(self.dt * rotation_cmd)
        translation_cmd = translation_cmd.rotate(-(self.current_pose.orientation))
        if not self.rotation_flag and cmd.path[-1] is not cmd.path[0]:
            translation_cmd *= translation_cmd * 0.0
            self.next_speed = 0.0
            self.x_controller.reset()
            self.y_controller.reset()
        if self.position_error.norm() > 0.1 and self.rotation_flag:
            self.angle_controller.reset()
            rotation_cmd = 0



        # self.ws.debug_interface.add_line(
        #     start_point=(self.current_pose.position[0] * 1000, self.current_pose.position[1] * 1000),
        #     end_point=(self.current_pose.position[0] * 1000 + compasation_ref_world[0] * 600,
        #                self.current_pose.position[1] * 1000 + compasation_ref_world[1] * 600),
        #     timeout=0.01, color=debug_interface.ORANGE.repr())
        translation_cmd = self.apply_translation_constraints(translation_cmd)
        #if not translation_cmd.norm() < 0.01:
        #    print(translation_cmd, "self.target_reached()", self.target_reached(), "self.next_speed", self.next_speed,"self.target_speed", self.target_speed )
        # self.debug(translation_cmd, rotation_cmd)
        return SpeedPose(translation_cmd, rotation_cmd)

    def get_next_velocity(self) -> Position:
        """Return the next velocity according to a constant acceleration model of a point mass.
           It try to produce a trapezoidal velocity path with the required cruising and target speed.
           The target speed is the speed that the robot need to reach at the target point."""

        if self.current_speed < self.target_speed: # accelerate
            self.next_speed += self.setting.translation.max_acc * self.dt
        else:
            if self.distance_accelerate():
                self.next_speed += self.setting.translation.max_acc * self.dt
            elif self.distance_break():
                self.next_speed -= self.setting.translation.max_acc * self.dt
            else:
                self.next_speed = self.current_speed
        # if self.target_reached():  # We need to go to target speed
        #     if self.next_speed < self.target_speed:  # Target speed is faster than current speed
        #         self.next_speed += self.setting.translation.max_acc * self.dt
        #         if self.next_speed > self.target_speed:  # Next_speed is too fast
        #             self.next_speed = self.target_speed
        #     else:  # Target speed is slower than current speed
        #         self.next_speed -= self.setting.translation.max_acc * self.dt *2
        # else:  # We need to go to the cruising speed
        #     if self.next_speed < self.cruise_speed:  # Going faster
        #         self.next_speed += self.setting.translation.max_acc * self.dt
        #         # self.next_speed = min(self.cruise_speed, self.next_speed)
        #     else:
        #         self.next_speed -= self.setting.translation.max_acc * self.dt * 2

        self.next_speed = np.clip(self.next_speed, 0.0, self.cruise_speed)
        self.next_speed = np.clip(self.next_speed, 0.0, self.setting.translation.max_speed)
        next_velocity = Position(self.target_direction * self.next_speed)

        return next_velocity

    def apply_rotation_constraints(self, r_cmd: float) -> float:
        if self.current_speed < 0.1:
            deadzone = self.setting.rotation.deadzone
        else:
            deadzone = 0.0

        sensibility = self.setting.rotation.sensibility
        max_speed = self.setting.rotation.max_speed

        r_cmd = self.limit_angular_speed(r_cmd)
        r_cmd = RobotMotion.apply_deadzone(r_cmd, deadzone, sensibility)
        r_cmd = clamp(r_cmd, -max_speed, max_speed)

        return r_cmd

    def apply_translation_constraints(self, t_cmd: Position) -> Position:
        deadzone = self.setting.translation.deadzone
        sensibility = self.setting.translation.sensibility

        t_cmd = self.limit_speed(t_cmd)
        t_cmd[0] = RobotMotion.apply_deadzone(t_cmd[0], deadzone, sensibility)
        t_cmd[1] = RobotMotion.apply_deadzone(t_cmd[1], deadzone, sensibility)

        return t_cmd

    @staticmethod
    def apply_deadzone(value, deadzone, sensibility):
        if m.fabs(value) < sensibility:
            value = 0.0
        elif m.fabs(value) <= deadzone:
            value = m.copysign(deadzone, value)
        return value

    def limit_speed(self, translation_cmd: Position) -> Position:
        if translation_cmd.norm() != 0.0:
            translation_speed = float(np.sqrt(np.sum(np.square(translation_cmd))))
            translation_speed = clamp(translation_speed, 0, self.setting.translation.max_speed)
            new_speed = translation_cmd.normalized() * translation_speed
        else:
            new_speed = Position()
        return new_speed

    def limit_angular_speed(self, angular_speed: float) -> float:
        if m.fabs(angular_speed) != 0.0:
            rotation_sign = m.copysign(1, angular_speed)
            angular_speed = clamp(m.fabs(angular_speed), 0.0, self.setting.translation.max_speed)
            new_speed = m.copysign(angular_speed, rotation_sign) * angular_speed
        else:
            new_speed = 0.0
        return new_speed

    def target_reached(self, boost_factor=1) -> bool:  # distance_to_reach_target_speed
        distance = 0.5 * (self.target_speed ** 2 - self.current_speed ** 2) / self.setting.translation.max_acc
        distance = boost_factor * m.fabs(distance)
        distance = max(distance, MIN_DISTANCE_TO_REACH_TARGET_SPEED)
        return self.position_error.norm() <= distance

    def distance_accelerate(self, boost_factor=1) -> bool:  # distance_to_reach_target_speed
        distance = 0.5 * (self.target_speed ** 2 - self.current_speed ** 2) / self.setting.translation.max_acc
        distance = boost_factor * m.fabs(distance)
        distance = max(distance, MIN_DISTANCE_TO_REACH_TARGET_SPEED)
        return self.position_error.norm() >= distance * 2


    def distance_break(self, boost_factor=1) -> bool:  # distance_to_reach_target_speed
        distance = 0.5 * (self.target_speed ** 2 - self.current_speed ** 2) / self.setting.translation.max_acc
        distance = boost_factor * m.fabs(distance)
        distance = max(distance, MIN_DISTANCE_TO_REACH_TARGET_SPEED)
        return self.position_error.norm() <= distance

    def update_states(self, cmd: AICommand):
        self.dt = self.ws.game_state.game.delta_t

        # Dynamics constraints
        self.setting.translation.max_acc = self.ws.game_state.get_player(self.id).max_acc
        self.setting.translation.max_speed = self.ws.game_state.get_player(self.id).max_speed
        self.setting.translation.max_angular_acc = self.ws.game_state.get_player(self.id).max_angular_acc
        self.setting.rotation.max_speed = self.ws.game_state.get_player(self.id).max_angular_speed

        # Current state of the robot
        self.current_pose = self.ws.game_state.game.friends.players[self.id].pose.scale(1 / 1000)
        self.current_velocity = self.ws.game_state.game.friends.players[self.id].velocity.scale(1 / 1000)
        self.current_speed = self.current_velocity.position.norm()
        self.current_angular_speed = self.current_velocity.orientation
        self.current_orientation = self.current_pose.orientation

        # Desired parameters
        if cmd.path != []:
            current_path_position = Position(cmd.path[0] / 1000)
            if not self.last_position.is_close(current_path_position, 0.1) and self.target_speed < 0.2:
                self.reset()
                self.last_position = current_path_position

            self.target_pose = Pose(cmd.path[0], cmd.pose_goal.orientation).scale(1 / 1000)
            self.target_turn = cmd.path_turn[1] / 1000
            self.target_speed = cmd.path_speeds[1] / 1000

        else:  # No pathfinder case
            self.target_pose = cmd.pose_goal.scale(1 / 1000)
            self.target_turn = self.target_pose.position
            self.target_speed = 0.0

        self.target_angle = self.target_pose.orientation
        self.pose_error = self.target_pose - self.current_pose  # Pose are always wrap to pi
        self.position_error = self.pose_error.position
        self.angle_error = self.pose_error.orientation
        if self.position_error.norm() != 0.0:
            self.target_direction = (self.target_turn - self.current_pose.position).normalized()

        self.cruise_speed = cmd.cruise_speed

    def reset(self):
        self.angle_controller.reset()
        self.x_controller.reset()
        self.y_controller.reset()
        self.position_flag = False
        self.rotation_flag = False
        self.last_translation_cmd = Position()
        self.next_speed = 0.0
        self.next_angular_speed = 0.0
        self.last_position = Position()

    def debug(self, translation_cmd, rotation_cmd):
        print('Speed: {:5.3f}, Command: {}, {:5.3f}, next speed: {:5.3f}, target_speed: {:5.3f}, '
              '{:5.3f}, reached:{}, error: {}'.format(self.current_speed,
                                                      translation_cmd,
                                                      rotation_cmd,
                                                      self.next_speed,
                                                      self.target_speed,
                                                      self.target_direction.angle()/m.pi*180,
                                                      self.target_reached(),
                                                      self.pose_error))


def get_control_setting(is_sim: bool):

    if is_sim:
        translation = {"kp": 1, "ki": 0.1, "kd": 0.5, "antiwindup": 0, "deadzone": 0, "sensibility": 0}
        rotation = {"kp": 3, "ki": 3, "kd": 0.01, "antiwindup": 0, "deadzone": 0, "sensibility": 0}
    else:
        translation = {"kp": 1, "ki": 0.1, "kd": 0.5, "antiwindup": 0, "deadzone": 0, "sensibility": 0}
        rotation = {"kp": 3, "ki": 3, "kd": 0.01, "antiwindup": 0, "deadzone": 0, "sensibility": 0}

    control_setting = DotDict()
    control_setting.translation = DotDict(translation)
    control_setting.rotation = DotDict(rotation)

    return control_setting


def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min(val, max_val), min_val)
