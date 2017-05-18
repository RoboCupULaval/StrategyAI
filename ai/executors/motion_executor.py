# Under MIT License, see LICENSE.txt


from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Util.ai_command import AICommandType, AIControlLoopType, AICommand
from ai.executors.executor import Executor
from ai.states.world_state import WorldState

from enum import IntEnum
import numpy as np

from config.config_service import ConfigService


class Pos(IntEnum):
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
        self.robot_motion = [RobotMotion(p_world_state, player_id, is_sim=self.is_simulation) for player_id in
                             range(12)]

    def exec(self):
        commands = self.ws.play_state.current_ai_commands

        for cmd in commands.values():

            robot_id = cmd.robot_id
            active_player = self.ws.game_state.game.friends.players[robot_id]

            if cmd.command is AICommandType.MOVE:
                if cmd.control_loop_type is AIControlLoopType.POSITION:
                    cmd.speed = self.robot_motion[robot_id].update(cmd)

                elif cmd.control_loop_type is AIControlLoopType.SPEED:
                    speed = fixed2robot(cmd.pose_goal.conv_2_np(), active_player.pose.orientation)
                    cmd.speed = Pose(Position(speed[Pos.X], speed[Pos.Y]), speed[Pos.THETA])

                elif cmd.control_loop_type is AIControlLoopType.OPEN:
                    cmd.speed = cmd.pose_goal

            elif cmd.command is AICommandType.STOP:
                cmd.speed = Pose(Position(0, 0), 0)
                self.robot_motion[robot_id].stop()


class RobotMotion(object):
    def __init__(self, p_world_state: WorldState, robot_id, is_sim=True):
        self.ws = p_world_state
        self.id = robot_id

        self.dt = None

        self.setting = get_control_setting(is_sim)
        self.setting.translation.max_acc = None
        self.setting.translation.max_speed = None
        self.setting.rotation.max_speed = None

        self.current_position = np.zeros(3)
        self.current_orientation = 0
        self.current_velocity = np.zeros(3)
        self.current_acceleration = np.zeros(2)

        self.pos_error = np.zeros(3)
        self.translation_error = np.zeros(2)

        self.target_position = np.zeros(3)
        self.target_speed = np.zeros(3)
        self.target_acceleration = np.zeros(3)

        self.last_translation_cmd = np.zeros(2)
        self.cruise_speed = np.zeros(2)

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

    def update(self, cmd: AICommand) -> Pose():
        self.update_states(cmd)

        rotation_cmd = np.array(self.angle_controller.update(self.pos_error[Pos.THETA]))
        rotation_cmd = np.clip(rotation_cmd,
                               -self.setting.rotation.max_speed,
                               self.setting.rotation.max_speed)
        rotation_cmd = self.apply_deadzone(rotation_cmd, self.setting.rotation.deadzone)

        translation_cmd = self.get_next_velocity()
        translation_cmd += np.array([self.x_controller.update(self.pos_error[Pos.X]),
                                     self.y_controller.update(self.pos_error[Pos.Y])])
        translation_cmd = self.limit_acceleration(translation_cmd)
        translation_cmd = np.clip(translation_cmd, -self.cruise_speed, self.cruise_speed)
        translation_cmd = fixed2robot(translation_cmd, self.current_orientation)
        translation_cmd = self.apply_deadzone(translation_cmd, self.setting.translation.deadzone)

        return Pose(Position(translation_cmd[Pos.X], translation_cmd[Pos.Y]), rotation_cmd)

    def get_next_velocity(self) -> np.ndarray:
        """Return the next velocity according to a constant acceleration model of a point mass.
           It try to produce a trapezoidal velocity path with the required cruising and target speed"""

        eps = 1 * self.target_acceleration * self.dt
        current_speed = np.abs(self.current_velocity[0:2])

        distance_to_reach_speed = np.square(self.target_speed) - np.square(current_speed)
        distance_to_reach_speed = 0.5 * np.abs(distance_to_reach_speed / self.target_acceleration)

        next_speed = np.array([0.0, 0.0])
        for coord in range(2):  # For X and Y velocity components
            if np.abs(self.pos_error[coord]) - distance_to_reach_speed[coord] <= eps[coord]:  # Slowing down until target speed
                next_speed[coord] = current_speed[coord] - self.target_acceleration[coord] * self.dt
                if next_speed[coord] < 0:
                    next_speed[coord] = 0
                if np.abs(self.pos_error[coord]) < eps[coord]:
                    next_speed[coord] = self.target_speed[coord]
            else:  # Acceleration until cruising speed
                next_speed[coord] = current_speed[coord] + self.target_acceleration[coord] * self.dt
                if next_speed[coord] >= self.cruise_speed[coord]:
                    next_speed[coord] = self.cruise_speed[coord]

        next_velocity = next_speed * np.sign(self.translation_error)

        return next_velocity

    def limit_acceleration(self, translation_cmd: np.ndarray) -> np.ndarray:
        self.current_acceleration = (translation_cmd - self.last_translation_cmd) / self.dt
        self.current_acceleration = np.clip(self.current_acceleration,
                                            -self.setting.translation.max_acc,
                                            self.setting.translation.max_acc)
        translation_cmd = self.last_translation_cmd + self.current_acceleration * self.dt
        self.last_translation_cmd = translation_cmd

        return translation_cmd

    @staticmethod
    def apply_deadzone(signal: np.ndarray, deadzone: float) -> np.ndarray:
        return signal - np.clip(signal, -deadzone, deadzone)

    def update_states(self, cmd: AICommand):
        self.dt = self.ws.game_state.game.delta_t

        # Dynamics constraints
        self.setting.translation.max_acc = self.ws.game_state.get_player(self.id).max_acc
        self.setting.translation.max_speed = self.ws.game_state.get_player(self.id).max_speed
        self.setting.rotation.max_speed = self.ws.game_state.get_player(self.id).max_angular_speed

        # Current state of the robot
        self.current_position = self.ws.game_state.game.friends.players[self.id].pose.conv_2_np()
        self.current_position = self.current_position / np.array([1000, 1000, 1])
        self.current_orientation = self.current_position[Pos.THETA]
        self.current_velocity = np.array(self.ws.game_state.game.friends.players[self.id].velocity)
        self.current_velocity = self.current_velocity / np.array([1000, 1000, 1])

        self.pos_error = self.target_position - self.current_position
        self.translation_error = self.pos_error[0:2]
        if self.pos_error[Pos.THETA] > np.pi:  # Try to minimize the rotation angle
            self.pos_error[Pos.THETA] = self.pos_error[Pos.THETA] - 2*np.pi

        # Desired parameters
        self.target_position = cmd.pose_goal.conv_2_np()
        self.target_position = self.target_position / np.array([1000, 1000, 1])
        self.target_speed = np.abs(cmd.path_speeds[1] * normalized(self.translation_error))
        self.target_acceleration = np.abs(self.setting.translation.max_acc * normalized(self.translation_error))
        self.target_acceleration[self.target_acceleration == 0] = 10 ** (-6)  # Avoid division by zero later
        self.cruise_speed = np.abs(cmd.cruise_speed * normalized(self.translation_error))

    def stop(self):
        self.angle_controller.reset()
        self.x_controller.reset()
        self.y_controller.reset()
        self.last_translation_cmd = np.zeros(2)
        self.current_position = np.zeros(3)
        self.current_orientation = 0
        self.current_velocity = np.zeros(3)
        self.current_acceleration = np.zeros(2)
        self.pos_error = np.zeros(3)
        self.target_position = np.zeros(3)
        self.target_speed = np.zeros(2)
        self.target_acceleration = np.zeros(3)
        self.last_translation_cmd = np.zeros(2)
        self.cruise_speed = np.zeros(2)
        self.translation_error = np.zeros(2)


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


def get_control_setting(is_sim: bool):

    if is_sim:
        translation = {"kp": 0.05, "ki": 0, "kd": 0.05, "antiwindup": 10, "deadzone": 0}
        rotation = {"kp": 1, "ki": 0, "kd": 0, "antiwindup": 0, "deadzone": 0}
    else:
        translation = {"kp": 0.7, "ki": 0.005, "kd": 0, "antiwindup": 0, "deadzone": 0.01}
        rotation = {"kp": 1, "ki": 0.05, "kd": 0, "antiwindup": 0, "deadzone": 0.05}

    control_setting = DotDict()
    control_setting.translation = DotDict(translation)
    control_setting.rotation = DotDict(rotation)

    return control_setting


def robot2fixed(vector: np.ndarray, angle: float) -> np.ndarray:
    tform = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return np.dot(tform, vector)


def fixed2robot(vector: np.ndarray, angle: float) -> np.ndarray:
    return robot2fixed(vector, -angle)


def normalized(vector: np.ndarray) -> np.ndarray:
    return vector / np.linalg.norm(vector)


if __name__ == "__main__":
    pass
