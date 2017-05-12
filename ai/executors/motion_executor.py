# Under MIT License, see LICENSE.txt


from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Util.ai_command import AICommandType, AIControlLoopType, AICommand
from ai.executors.executor import Executor
from ai.states.game_state import GameState
from ai.states.world_state import WorldState

from enum import Enum
import numpy as np
import time

from config.config_service import ConfigService


class Pos(Enum):
    X = 0
    Y = 1
    THETA = 2


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class MotionExecutor(Executor):
    def __init__(self, p_world_state: WorldState):
        super().__init__(p_world_state)
        self.is_simulation = ConfigService().config_dict["GAME"]["type"] == "sim"
        self.robot_motion = [RobotMotion(p_world_state, player_id, is_sim=self.is_simulation) for player_id in range(12)]

    def exec(self):
        commands = self.ws.play_state.current_ai_commands
        delta_t = self.ws.game_state.game.delta_t

        for cmd in commands.values():
            robot_idx = cmd.robot_id
            active_player = self.ws.game_state.game.friends.players[robot_idx]
            if cmd.command is AICommandType.MOVE:
                if cmd.control_loop_type is AIControlLoopType.POSITION:
                    cmd.speed = self.robot_motion[robot_idx].update(cmd)
                elif cmd.control_loop_type is AIControlLoopType.SPEED:
                    speed = robot2fixed(cmd.pose_goal.conv_2_np(), active_player.pose.orientation)
                    cmd.speed = Pose(Position(speed[0], speed[1]), speed[2])
                elif cmd.control_loop_type is AIControlLoopType.OPEN:
                    cmd.speed = cmd.pose_goal
            elif cmd.command is AICommandType.STOP:
                cmd.speed = np.zeros(3)
                self.robot_motion[robot_idx].stop()


class RobotMotion(object):
    def __init__(self,  p_world_state: WorldState, player_id, is_sim=True):

        self.ws = p_world_state

        self.setting = get_control_setting(is_sim)

        self.id = player_id

        self.current_position = np.zeros(3)
        self.current_velocity = np.zeros(3)

        self.target_position = np.zeros(3)
        self.target_velocity = np.zeros(3)

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
                                    self.setting.rotation.antiwindup)

        self.last_translation_cmd = np.zeros(2)

    def update(self, cmd : AICommand) -> Pose():
        self.update_state(cmd)

        pos_error = self.target_position - self.current_position

        # Rotation control

        rotation_cmd = self.angle_controller.update(pos_error[2])

        # Limit the angular speed
        if np.abs(rotation_cmd) > self.setting.rotation['max_speed']:
            if rotation_cmd > 0:
                rotation_cmd = self.setting.rotation['max_speed']
            else:
                rotation_cmd = -self.setting.rotation['max_speed']

        # Translation control

        next_target_velocity = np.array([0, 0])
        translation_cmd = np.array([self.target_velocity[0], self.target_velocity[1]])
        translation_cmd += np.array(next_target_velocity - self.target_velocity)
        translation_cmd += np.array([self.x_controller.update(pos_error[0]),
                                    self.y_controller.update(pos_error[1])])

        # Limit the acceleration
        dt = self.ws.game_state.game.delta_t
        if dt > 0:
            current_acc = (translation_cmd - self.last_translation_cmd) / dt
            np.clip(current_acc, -self.setting.translation.max_acc, self.setting.translation.max_acc, out=current_acc)
        else:
            current_acc = np.zeros(2)
        translation_cmd = self.last_translation_cmd + current_acc * dt

        self.last_translation_cmd = translation_cmd

        velocity_cmd = np.array([translation_cmd[0], translation_cmd[1], rotation_cmd])
        print(velocity_cmd)
        velocity_cmd = robot2fixed(velocity_cmd, self.current_position[2])
        print(velocity_cmd)

        return Pose(Position(velocity_cmd[0], velocity_cmd[1]), velocity_cmd[2])

    def update_state(self, cmd):
        self.current_position = self.ws.game_state.game.friends.players[self.id].pose.conv_2_np()
        self.current_velocity = np.array(self.ws.game_state.game.friends.players[self.id].velocity)
        self.target_position = cmd.pose_goal.conv_2_np()
        path_speeds = cmd.path_speeds #une liste de scalaires représentant la norme max de la vitesse que doit avoir le robot
        self.target_velocity = path_speeds[1] * (self.target_position[0:2] - self.current_position[0:2])\
                               / np.linalg.norm(self.target_position[0:2] - self.current_position[0:2])

    def stop(self):
        self.last_translation_cmd = np.zeros(2)
        self.angle_controller.reset()
        self.x_controller.reset()
        self.y_controller.reset()


class PID(object):
    def __init__(self, kp: float, ki: float, kd: float, antiwindup_size=0):
        """
        Simple PID parallel implementation
        Args:
            kp: proportional gain
            ki: integral gain
            kd: derivative gain
            antiwindup_size: max error accumulation of the error integration
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.err_sum = 0
        self.last_err = 0

        self.antiwindup_size = antiwindup_size
        if self.antiwindup_size > 0:
            self.antiwindup_active = True
            self.old_err = np.zeros(self.antiwindup_size)
            self.antiwindup_idx = 0
        else:
            self.antiwindup_active = False

    def update(self, err: float) -> float:
        d_err = err - self.last_err
        self.last_err = err
        self.err_sum += err

        if self.antiwindup_active:
            self.err_sum -= self.old_err[self.antiwindup_idx]
            self.old_err[self.antiwindup_idx] = err
            self.antiwindup_idx = (self.antiwindup_idx + 1) % self.antiwindup_size

        return (err * self.kp) + (self.err_sum * self.ki) + (d_err * self.kd)

    def reset(self):
        if self.antiwindup_active:
            self.old_err = np.zeros(self.antiwindup_size)
        self.err_sum = 0


def get_control_setting(is_sim):
    if is_sim:
        translation = {"kp": 0.7, "ki": 0.005, "kd": 0.02, "antiwindup": 0,
                       "max_speed": 50, "max_acc": 100, "deadzone": 0.03}
        rotation = {"kp": 0.6, "ki": 0.2, "kd": 0.3, "antiwindup": 0,
                    "max_speed": 6, "max_acc": 4, "deadzone": 0}
    else:
        translation = {"kp": 2, "ki": 0.05, "kd": 0.4, "antiwindup": 0,
                       "max_speed": 2, "max_acc": 1.5, "deadzone": 0.03}
        rotation = {"kp": 0.7, "ki": 0.07, "kd": 0, "antiwindup": 0,
                    "max_speed": 6, "max_acc": 4, "deadzone": 0}
    control_setting = DotDict()
    control_setting.translation = DotDict(translation)
    control_setting.rotation = DotDict(rotation)
    return control_setting


def robot2fixed(vector: np.ndarray, angle: float) -> np.ndarray:
    tform = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    vector_rot = np.array([[vector[0]], [vector[1]]])
    vec_rotated = np.dot(tform, vector_rot)
    return np.array([vec_rotated[0], vec_rotated[1], vector[2]])

if __name__ == "__main__":
    pass
