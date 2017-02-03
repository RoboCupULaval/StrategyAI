# Under MIT License, see LICENSE.txt
import math

import time

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.game_world import GameWorld
from ai.executors.executor import Executor

INTEGRAL_DECAY = 0.981  # réduit de moitié à toutes les 10 itérations
ZERO_ACCUMULATOR_TRHESHOLD = 0.5
FILTER_LENGTH = 1

SIMULATION_MAX_NAIVE_CMD = math.sqrt(2) / 3
SIMULATION_MIN_NAIVE_CMD = 0
SIMULATION_MAX_THETA_CMD = math.pi / 8
SIMULATION_MIN_THETA_CMD = 0
SIMULATION_DEFAULT_STATIC_GAIN = 0.00095
SIMULATION_DEFAULT_INTEGRAL_GAIN = 0.0009
SIMULATION_DEFAULT_THETA_GAIN = 1

REAL_MAX_NAIVE_CMD = 1200
REAL_MIN_NAIVE_CMD = 80
REAL_MAX_THETA_CMD = 300
REAL_MIN_THETA_CMD = 45
REAL_DEFAULT_STATIC_GAIN = 0.325
REAL_DEFAULT_INTEGRAL_GAIN = 0.350
#REAL_DEFAULT_THETA_GAIN = 160
REAL_DEFAULT_THETA_GAIN = 0


class PositionRegulator(Executor):
    def __init__(self, p_world_state: GameWorld, is_simulation=False):
        super().__init__(p_world_state)
        self.regulators = [PI(simulation_setting=is_simulation) for _ in range(6)]
        self.last_cmd_time = time.time()

    def exec(self):
        commands = self.ws.play_state.current_ai_commands
        for cmd in commands.values():
            current_time = time.time()
            delta_t = current_time - self.last_cmd_time
            self.last_cmd_time = current_time
            robot_idx = cmd.robot_id
            retroaction_pose = self.ws.game_state.get_player_pose(robot_idx)
            cmd.pose_goal = self.regulators[robot_idx].\
                update_pid_and_return_speed_command(cmd.pose_goal, retroaction_pose, delta_t)
            #cmd.pose_goal.position.x = cmd.pose_goal.position.x / 2
            #cmd.pose_goal.position.y = cmd.pose_goal.position.y / 2


class PI(object):
    """
        Asservissement PI en position

        u = Kp * err + Sum(err) * Ki * dt
    """

    def __init__(self, simulation_setting=True):
        self.accumulator_x = 0
        self.accumulator_y = 0
        self.constants = _set_constants(simulation_setting)
        self.kp = self.constants['default-kp']
        self.ki = self.constants['default-ki']
        self.ktheta = self.constants['default-ktheta']
        self.last_command_x = 0
        self.last_command_y = 0
        self.previous_cmd = []

    def update_pid_and_return_speed_command(self, pose_goal, player_pose, delta_t=0.030):
        """ Met à jour les composants du pid et retourne une commande en vitesse. """
        assert isinstance(pose_goal, Pose), "La consigne doit etre une Pose dans le PI"
        r_x, r_y = pose_goal.position.x, pose_goal.position.y
        t_x, t_y = player_pose.position.x, player_pose.position.y
        e_x = r_x - t_x
        e_y = r_y - t_y

        # composante proportionnel
        up_x = self.kp * e_x
        up_y = self.kp * e_y

        # composante integrale, decay l'accumulator
        ui_x, ui_y = self._compute_integral(delta_t, e_x, e_y)
        self._zero_accumulator()

        u_x = up_x + ui_x
        u_y = up_y + ui_y

        # correction frame reference et saturation
        x, y = self._referential_correction_saturation(player_pose, u_x, u_y)

        # correction de theta
        e_theta = pose_goal.orientation - player_pose.orientation
        theta = self.ktheta * e_theta
        theta = self._saturate_orientation(theta)

        cmd = Pose(Position(x, y), theta)
        cmd = self._filter_cmd(cmd)
        cmd.orientation = theta
        return cmd

    def _saturate_orientation(self, theta):
        if abs(theta) > self.constants['max-theta-cmd']:
            if theta > 0:
                return self.constants['max-theta-cmd']
            else:
                return -self.constants['max-theta-cmd']
        elif abs(theta) < self.constants['min-theta-cmd']:
            return 0
        else:
            return theta

    def _referential_correction_saturation(self, player_pose, u_x, u_y):
        x, y = _correct_for_referential_frame(u_x, u_y, player_pose.orientation)

        if abs(x) > self.constants['max-naive-cmd']:
            if x > 0:
                x = self.constants['max-naive-cmd']
            else:
                x = -self.constants['max-naive-cmd']

        if abs(x) < self.constants['min-naive-cmd']:
            x = 0

        if abs(y) > self.constants['max-naive-cmd']:
            if y > 0:
                y = self.constants['max-naive-cmd']
            else:
                y = -self.constants['max-naive-cmd']

        if abs(y) < self.constants['min-naive-cmd']:
            y = 0

        return x, y

    def _compute_integral(self, delta_t, e_x, e_y):
        ui_x = self.ki * e_x * delta_t
        ui_y = self.ki * e_y * delta_t
        self.accumulator_x = (self.accumulator_x * INTEGRAL_DECAY * delta_t) + ui_x
        self.accumulator_y = (self.accumulator_y * INTEGRAL_DECAY * delta_t) + ui_y
        return ui_x, ui_y

    def _zero_accumulator(self):
        if self.accumulator_x < ZERO_ACCUMULATOR_TRHESHOLD:
            self.accumulator_x = 0

        if self.accumulator_y < ZERO_ACCUMULATOR_TRHESHOLD:
            self.accumulator_y = 0

    def _filter_cmd(self, cmd):
        self.previous_cmd.append(cmd)
        xsum = 0
        ysum = 0
        for cmd in self.previous_cmd:
            xsum += cmd.position.x
            ysum += cmd.position.y

        xsum /= len(self.previous_cmd)
        ysum /= len(self.previous_cmd)
        if len(self.previous_cmd) > FILTER_LENGTH:
            self.previous_cmd.pop(0)
        return Pose(Position(xsum, ysum))


def _set_constants(simulation_setting):
    if simulation_setting:
        return {'max-naive-cmd':SIMULATION_MAX_NAIVE_CMD,
                'min-naive-cmd':SIMULATION_MIN_NAIVE_CMD,
                'max-theta-cmd':SIMULATION_MAX_THETA_CMD,
                'min-theta-cmd':SIMULATION_MIN_THETA_CMD,
                'default-kp':SIMULATION_DEFAULT_STATIC_GAIN,
                'default-ki':SIMULATION_DEFAULT_INTEGRAL_GAIN,
                'default-ktheta':SIMULATION_DEFAULT_THETA_GAIN
                }
    else:
        return {'max-naive-cmd':REAL_MAX_NAIVE_CMD,
                'min-naive-cmd':REAL_MIN_NAIVE_CMD,
                'max-theta-cmd':REAL_MAX_THETA_CMD,
                'min-theta-cmd':REAL_MIN_THETA_CMD,
                'default-kp':REAL_DEFAULT_STATIC_GAIN,
                'default-ki':REAL_DEFAULT_INTEGRAL_GAIN,
                'default-ktheta':REAL_DEFAULT_THETA_GAIN
                }


def _correct_for_referential_frame(x, y, orientation):
    cos = math.cos(-orientation)
    sin = math.sin(-orientation)

    corrected_x = (x * cos - y * sin)
    corrected_y = (y * cos + x * sin)
    return corrected_x, corrected_y
