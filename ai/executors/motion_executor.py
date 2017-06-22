# Under MIT License, see LICENSE.txt

import numpy as np
import math as m

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.PID import PID
from ai.Util.ai_command import AICommandType, AIControlLoopType, AICommand
from ai.executors.executor import Executor
from ai.states.world_state import WorldState
from config.config_service import ConfigService


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

            if cmd.command is AICommandType.MOVE:
                if cmd.control_loop_type is AIControlLoopType.POSITION:
                    cmd.speed = self.robot_motion[r_id].update(cmd)

                elif cmd.control_loop_type is AIControlLoopType.SPEED:
                    speed = cmd.pose_goal.rotate(-player.pose.orientation)
                    cmd.speed = Pose(Position(speed.position.x, speed.position.y), speed.orientation)

                elif cmd.control_loop_type is AIControlLoopType.OPEN:
                    cmd.speed = cmd.pose_goal

            elif cmd.command is AICommandType.STOP:
                cmd.speed = Pose(Position(0, 0), 0)
                self.robot_motion[r_id].stop()


class RobotMotion(object):
    def __init__(self, world_state: WorldState, robot_id, is_sim=True):
        self.ws = world_state
        self.id = robot_id

        self.dt = None

        self.setting = get_control_setting(is_sim)
        self.setting.translation.max_acc = None
        self.setting.translation.max_speed = None
        self.setting.rotation.max_speed = None

        self.current_pose = Pose()
        self.current_velocity = Pose()
        self.current_speed = Position()
        self.current_acceleration = Position()

        self.pose_error = Pose()
        self.position_error = Position()

        self.target_pose = Pose()
        self.target_speed = 0
        self.target_direction = Position()

        self.last_translation_cmd = Position()
        self.cruise_speed = 0

        self.next_speed = 0

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

    def update(self, cmd: AICommand) -> Pose():

        self.update_states(cmd)

        # Rotation control
        rotation_cmd = self.angle_controller.update(self.pose_error.orientation)
        rotation_cmd = self.apply_rotation_constraints(rotation_cmd)

        # Translation control
        if self.target_reached() and self.target_speed < self.setting.translation.deadzone:
            translation_cmd = Position(self.x_controller.update(self.pose_error.position.x),
                                       self.y_controller.update(self.pose_error.position.y))
            self.next_speed = 0
            print('target reached:', self.pose_error.position)
        else:
            translation_cmd = self.get_next_velocity()

        translation_cmd = self.apply_translation_constraints(translation_cmd)

        # Adjust command to robot's orientation
        translation_cmd = translation_cmd.rotate(-self.current_pose.orientation)

        print('{:5.3f}, {:5.3f}, {:5.3f}'.format(self.current_speed, translation_cmd.norm(), rotation_cmd))

        return Pose(translation_cmd, rotation_cmd)

    def get_next_velocity(self) -> Position:
        """Return the next velocity according to a constant acceleration model of a point mass.
           It try to produce a trapezoidal velocity path with the required cruising and target speed.
           The target speed is the speed that the robot need to reach at the target point."""

        deceleration_factor = 2

        if not np.isclose(self.current_speed, self.next_speed, atol=0.25):
            self.next_speed = self.current_speed

        if self.target_reached():  # We need to go to target speed
            if self.next_speed < self.target_speed:  # Target speed is faster than current speed
                self.next_speed += self.setting.translation.max_acc * self.dt
                if self.next_speed > self.target_speed:  # Next_speed is too fast
                    self.next_speed = self.target_speed
            else:  # Target speed is slower than current speed
                self.next_speed -= deceleration_factor * self.setting.translation.max_acc * self.dt
        else:  # We need to go to the cruising speed
            if self.next_speed < self.cruise_speed:  # Going faster
                self.next_speed += self.setting.translation.max_acc * self.dt

        self.next_speed = np.clip(self.next_speed, 0, self.cruise_speed)  # We don't want to go faster than cruise speed
        next_velocity = self.target_direction * self.next_speed

        return next_velocity

    def apply_rotation_constraints(self, r_cmd: float) -> float:
        deadzone = self.setting.rotation.deadzone
        sensibility = self.setting.rotation.sensibility
        max_speed = self.setting.rotation.max_speed

        if abs(r_cmd) < sensibility:
            r_cmd = 0
        elif abs(r_cmd) < deadzone:
            r_cmd = m.copysign(deadzone, r_cmd)
        else:
            r_cmd = clamp(r_cmd, -max_speed, max_speed)
        return r_cmd

    def apply_translation_constraints(self, t_cmd: Position) -> Position:
        deadzone = self.setting.translation.deadzone
        sensibility = self.setting.translation.sensibility
        signs = np.copysign(1, t_cmd.view(np.ndarray))

        t_cmd = self.limit_acceleration(t_cmd)
        t_cmd = self.limit_speed(t_cmd)

        t_cmd[np.abs(t_cmd) < sensibility] = 0
        t_cmd[np.abs(t_cmd) < deadzone] = deadzone
        t_cmd = np.copysign(t_cmd, signs)

        return t_cmd

    def limit_acceleration(self, translation_cmd: Position) -> Position:
        delta_speed = translation_cmd - self.last_translation_cmd
        if np.any([np.abs(delta_speed) > 0]):
            self.current_acceleration = float(np.sqrt(np.sum(np.square(delta_speed))) / self.dt)
            self.current_acceleration = clamp(self.current_acceleration, 0, self.setting.translation.max_acc)
            translation_cmd = self.last_translation_cmd + delta_speed.normalized() * self.current_acceleration * self.dt
            self.last_translation_cmd = translation_cmd

        return translation_cmd

    def limit_speed(self, translation_cmd: Position) -> Position:
        if np.any([np.abs(translation_cmd) > 0]):
            translation_speed = float(np.sqrt(np.sum(np.square(translation_cmd))))
            translation_speed = clamp(translation_speed, 0, self.setting.translation.max_speed)
            new_speed = translation_cmd.normalized() * translation_speed
        else:
            new_speed = translation_cmd
        return new_speed

    def target_reached(self, boost_factor=1) -> bool:
        distance_to_reach_target_speed = 0.5 * (self.target_speed ** 2 - self.cruise_speed ** 2)
        distance_to_reach_target_speed /= self.setting.translation.max_acc
        distance_to_reach_target_speed = boost_factor * abs(distance_to_reach_target_speed)
        if np.sum(np.square(self.position_error)) <= distance_to_reach_target_speed ** 2:
            return True
        else:
            return False

    def update_states(self, cmd: AICommand):
        self.dt = self.ws.game_state.game.delta_t

        # Dynamics constraints
        self.setting.translation.max_acc = self.ws.game_state.get_player(self.id).max_acc
        self.setting.translation.max_speed = self.ws.game_state.get_player(self.id).max_speed
        self.setting.rotation.max_speed = self.ws.game_state.get_player(self.id).max_angular_speed

        # Current state of the robot
        self.current_pose = self.ws.game_state.game.friends.players[self.id].pose.scale(1 / 1000)
        self.current_velocity = self.ws.game_state.game.friends.players[self.id].velocity.scale(1 / 1000)
        self.current_speed = self.current_velocity.position.norm()

        # Desired parameters
        if cmd.path:
            self.target_pose = Pose(cmd.path[0], cmd.pose_goal.orientation).scale(1 / 1000)
            self.target_speed = cmd.path_speeds[1] / 1000
        else:  # No pathfinder case
            self.target_pose = cmd.pose_goal
            self.target_speed = 0

        self.pose_error = self.target_pose - self.current_pose  # Pose are always wrap to pi
        self.position_error = self.pose_error.position
        if np.any([self.position_error > 0]):
            self.target_direction = self.position_error.normalized()
        else:
            self.target_direction = Position()
        self.cruise_speed = cmd.cruise_speed

    def stop(self):
        self.angle_controller.reset()
        self.x_controller.reset()
        self.y_controller.reset()
        self.last_translation_cmd = Position()
        self.next_speed = 0


def get_control_setting(is_sim: bool):

    if is_sim:
        translation = {"kp": 0.8, "ki": 0.01, "kd": 0, "antiwindup": 20, "deadzone": 0, "sensibility": 0}
        rotation = {"kp": 1, "ki": 0, "kd": 0, "antiwindup": 0, "deadzone": 0, "sensibility": 0}
    else:
        translation = {"kp": 0.8, "ki": 0.01, "kd": 0, "antiwindup": 20, "deadzone": 0.2, "sensibility": 0.075}
        rotation = {"kp": 0.05, "ki": 0.02, "kd": 0, "antiwindup": 20, "deadzone": 0.3, "sensibility": 0.15}

    control_setting = DotDict()
    control_setting.translation = DotDict(translation)
    control_setting.rotation = DotDict(rotation)

    return control_setting


def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min(val, max_val), min_val)
