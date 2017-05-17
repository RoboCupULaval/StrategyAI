# Under MIT License, see LICENSE.txt

import math
import time

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.geometry import get_distance
from ai.Util.ai_command import AICommandType, AIControlLoopType, AICommand
from ai.executors.executor import Executor
from ai.states.game_state import GameState
from ai.states.world_state import WorldState
from config.config_service import ConfigService

import numpy as np


ROBOT_NEAR_FORCE = 2000
THRESHOLD_LAST_TARGET = 100


def sign(x):
    if x > 0:
        return 1
    if x == 0:
        return 0
    return -1


class PositionRegulator(Executor):
    def __init__(self, p_world_state: WorldState):
        super().__init__(p_world_state)
        self.is_simulation = ConfigService().config_dict["GAME"]["type"] == "sim"
        self.regulators = [PI(simulation_setting=self.is_simulation) for _ in range(6)]

        self.constants = _set_constants(simulation_setting=self.is_simulation)
        self.regulators = [PI(simulation_setting=self.is_simulation) for _ in range(12)]
        self.mnrc_speed = [MNRCFixedSpeed(simulation_setting=self.is_simulation) for _ in range(12)]
        self.last_timestamp = 0

        self.accel_max = self.constants["accel_max"]
        self.vit_max = self.constants["vit_max"]

    def exec(self):
        commands = self.ws.play_state.current_ai_commands
        delta_t = self.ws.game_state.game.delta_t
        # self._potential_field() # TODO finish <
        for cmd in commands.values():
            robot_idx = cmd.robot_id
            active_player = self.ws.game_state.game.friends.players[robot_idx]
            if cmd.command is AICommandType.MOVE:
                if cmd.control_loop_type is AIControlLoopType.POSITION:
                    speed = self.regulators[robot_idx].\
                        update_pid_and_return_speed_command(cmd,
                                                            active_player,
                                                            delta_t,
                                                            idx=robot_idx,
                                                            cruise_speed=cmd.cruise_speed)
                    cmd.speed = self.mnrc_speed[robot_idx].\
                        update(speed, active_player, delta_t)

                elif cmd.control_loop_type is AIControlLoopType.SPEED:
                    cmd.speed = self.mnrc_speed[robot_idx]. \
                        update(cmd.pose_goal, active_player, delta_t)

                elif cmd.control_loop_type is AIControlLoopType.OPEN:
                    cmd.speed = cmd.pose_goal

            elif cmd.command is AICommandType.STOP:
                self.mnrc_speed[robot_idx].reset()

class MNRCFixedSpeed(object):
    def __init__(self, simulation_setting=True):
        self.constants = _set_constants(simulation_setting)

        self.kp = self.constants['MNRC_KP']
        self.ki = self.constants['MNRC_KI']
        self.mnrc_dynamic = self.constants['MNRC_SPEED_DYNAMIC']
        self.robot_dynamic = self.constants['ROBOT_DYNAMIC']
        self.coupling_matrix = self.constants['ROBOT_COUPLING']
        self.robot_radius = self.constants['ROBOT_RADIUS']

        self.filtered_reference = np.array([0, 0, 0])
        self.err_sum = np.array([0, 0, 0])

    @staticmethod
    def _robot2fixed(robot_angle):
        return np.array(
            [[np.cos(robot_angle), -np.sin(robot_angle), 0], [np.sin(robot_angle), np.cos(robot_angle), 0], [0, 0, 1]])

    def update(self, reference: Pose, active_player, delta_t):
        """
        Update the MNRC of the active player
        """
        cruise_speed = np.array(active_player.velocity) / np.array([1000, 1000, 1])
        orientation = active_player.pose.orientation

        ref = reference.conv_2_np()

        k1 = 1 + delta_t * self.mnrc_dynamic
        k2 = delta_t * self.mnrc_dynamic
        self.filtered_reference = k1 * self.filtered_reference - k2 * ref

        err = self.filtered_reference - cruise_speed

        self.err_sum = self.err_sum + err * delta_t
        self.err_sum[self.err_sum > 1] = 1
        correction = self.kp * err + self.ki * self.err_sum

        # Compute model prediction
        rotation_matrix = self._robot2fixed(orientation)
        inverse_dynamic = -np.linalg.pinv(np.matmul(np.diag(self.robot_dynamic), rotation_matrix))
        model_prediction = self.mnrc_dynamic * (self.filtered_reference - ref) - self.robot_dynamic * cruise_speed

        # Return robot speed command
        speed_command = np.matmul(inverse_dynamic, model_prediction + correction)

        if active_player.id == 3:
            print(ref[2], self.filtered_reference[2], cruise_speed[2], err[2], self.err_sum[2], speed_command[2])

        speed_command[abs(speed_command) < 0.2] = 0
        return Pose(Position(speed_command[0], speed_command[1]), speed_command[2])

    def reset(self):
        self.filtered_reference = np.array([0, 0, 0])
        self.err_sum = np.array([0, 0, 0])

class PID(object):
    def __init__(self, kp, ki, kd):
        self.gs = GameState()
        self.paths = {}
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.ki_sum = 0
        self.last_err = 0

    def update(self, target, value, delta_t):
        error = target - value
        cmd = self.kp * error
        self.ki_sum += error * self.ki * delta_t
        cmd += self.ki_sum
        cmd += self.kd * ((error - self.last_err) / delta_t)
        self.last_err = error
        return cmd


class PI(object):
    """
        Asservissement PI en position

        u = Kp * err + Sum(err) * Ki * dt
    """

    def __init__(self, simulation_setting=True):
        self.gs = GameState()
        self.paths = {}

        self.simulation_setting = simulation_setting
        self.constants = _set_constants(simulation_setting)
        self.accel_max = self.constants["accel_max"]
        self.vit_max = self.constants["vit_max"]
        self.xyKp = self.constants["xyKp"]
        self.ki = self.constants["ki"]
        self.kd = self.constants["kd"]
        self.thetaKp = self.constants["thetaKp"]
        self.thetaKd = self.constants["thetaKd"]
        self.thetaKi = self.constants["thetaKi"]
        # non-constant
        self.lastErr = 0
        self.lastErr_theta = 0
        self.kiSum = 0
        self.vit_min = 0.05
        self.thetaKiSum = 0
        self.last_target = 0
        self.position_dead_zone = self.constants["position_dead_zone"]  # 0.03
        self.rotation_dead_zone = 0.005 * math.pi
        self.last_theta_target = 0

    def update_pid_and_return_speed_command(self, game_state, cmd, active_player, delta_t=0.030, idx=4, cruise_speed=1.0):
        """ Met à jour les composants du pid et retourne une commande en vitesse. """
        assert isinstance(cmd, AICommand), "La consigne doit etre une Pose dans le PI"
        if cruise_speed:
            self.vit_max = cruise_speed
        else:
            self.vit_max = self.constants["vit_max"]
        self.paths[idx] = cmd.path
        delta_t = 0.05

        xmax = game_state.field.constant["FIELD_X_RIGHT"]
        ymax = game_state.field.constant["FIELD_Y_TOP"]
        # Position de la target (en m)
        r_x, r_y, r_theta = cmd.pose_goal.position.x / 1000, cmd.pose_goal.position.y / 1000, cmd.pose_goal.orientation
        r_x = min(r_x, xmax / 1000)
        r_x = max(r_x, -xmax / 1000)
        r_y = min(r_y, ymax / 1000)
        r_y = max(r_y, -ymax / 1000)
        # Position du robot (en m)
        t_x, t_y, t_theta = active_player.pose.position.x / 1000, active_player.pose.position.y / 1000, active_player.pose.orientation
        # Vitesse actuelle du robot (en m/s)
        v_x, v_y, v_theta = active_player.velocity[0] / 1000, active_player.velocity[1] / 1000, active_player.velocity[
            2]
        v_x, v_y = _correct_for_referential_frame(v_x, v_y, -active_player.pose.orientation)
        v_current = math.sqrt(v_x ** 2 + v_y ** 2)

        # Reinitialisation de l'integrateur lorsque la target change de position
        target = math.sqrt(r_x ** 2 + r_y ** 2)
        if abs(target - self.last_target) > THRESHOLD_LAST_TARGET:
            self.kiSum = 0
        self.last_target = target
        if abs(r_theta - self.last_theta_target) > THRESHOLD_LAST_TARGET / 100:
            self.thetaKiSum = 0
        self.last_theta_target = r_theta

        # CALCUL DE L'ERREUR
        delta_x = (r_x - t_x)
        delta_y = (r_y - t_y)
        delta_theta = (r_theta - t_theta)
        if abs(delta_theta) > math.pi:
            delta_theta = (2 * math.pi - abs(delta_theta)) * -sign(delta_theta)
        delta_x, delta_y = _correct_for_referential_frame(delta_x, delta_y, -active_player.pose.orientation)
        delta = math.sqrt(delta_x ** 2 + delta_y ** 2)
        angle = math.atan2(delta_y, delta_x)

        # DEAD-ZONE
        if delta <= self.position_dead_zone:
            delta = 0
        if math.fabs(delta_theta) <= self.rotation_dead_zone:
            delta_theta = 0

        # PID TRANSLATION
        # Proportionnel
        v_target = self.xyKp * delta
        # Intergral
        self.kiSum += delta * self.ki * delta_t * sign(delta_x * v_x + delta_y * v_y)
        v_target += math.fabs(self.kiSum)
        # Derivatif
        v_target += self.kd * ((delta - self.lastErr) / delta_t)
        self.lastErr = delta

        # PID ROTATION
        # Proportionnel
        v_theta_target = self.thetaKp * delta_theta
        # Intergral
        self.thetaKiSum += delta_theta * self.thetaKi * delta_t
        v_theta_target += self.thetaKiSum
        # Derivatif
        v_theta_target += self.thetaKd * ((delta_theta - self.lastErr_theta) / delta_t)
        self.lastErr_theta = delta_theta

        # SATURATION DE LA VITESSE
        # Selon l'acceleration maximale ou la vitesse maximale

        # Translation
        v_max = math.fabs(v_current) + self.accel_max * delta_t  # Selon l'acceleration maximale
        v_max = min(self.vit_max, v_max)  # Selon la vitesse maximale du robot
        v_max = min(math.sqrt(2 * 0.5 * delta), v_max)   # Selon la distance restante a parcourir
        if delta > 0.3:
            v_target += 1
        v_target = max(self.vit_min, min(v_max, v_target))
        v_theta_target = sign(v_theta_target) * min(math.pi, abs(v_theta_target))
        # Rotation
        #v_max = math.fabs(v_theta) + self.constants["theta-max-acc"] * delta_t
        #v_max = min(self.constants["theta-max-acc"], v_max)
        #v_theta_target = sign(v_theta_target) * min(math.fabs(v_theta_target), v_max)

        # DECOUPLAGE ??
        decoupled_angle = angle  #- v_theta * delta_t
        v_target_x = v_target * math.cos(decoupled_angle)
        v_target_y = v_target * math.sin(decoupled_angle)

        # DEAD-ZONE
        if delta <= self.position_dead_zone:
            v_target_x = 0
            v_target_y = 0
        if math.fabs(delta_theta) <= 0.04:
            v_theta_target = 0
        return Pose(Position(v_target_x, v_target_y), v_theta_target)


def _correct_for_referential_frame(x, y, orientation):

    cos = math.cos(orientation)
    sin = math.sin(orientation)

    corrected_x = (x * cos - y * sin)
    corrected_y = (y * cos + x * sin)
    return corrected_x, corrected_y


def _set_constants(simulation_setting):
    if simulation_setting:
        return {"ROBOT_NEAR_FORCE": 1000,
                "ROBOT_VELOCITY_MAX": 4,
                "ROBOT_ACC_MAX": 2,
                "accel_max": 100,
                "vit_max": 50,
                "vit_min": 25,
                "xyKp": 0.7,
                "ki": 0.005,
                "kd": 0.02,
                "thetaKp": 0.6,
                "thetaKi": 0.2,
                "thetaKd": 0.3,
                "theta-max-acc": 6*math.pi,
                "position_dead_zone": 0.03,
                "MNRC_KP": np.array([14, 14, 14]),
                "MNRC_KI": np.array([50, 50, 50]),
                "MNRC_SPEED_DYNAMIC": np.array([-5, -5, -5]),
                "ROBOT_DYNAMIC": np.array([-4, -4, -4]),
                "ROBOT_COUPLING": np.array([[-0.7071, 0.7071, 0.0850],
                                            [-0.7071, -0.7071, 0.0850],
                                            [0.7071, -0.7071, 0.0850],
                                            [0.7071, 0.7071, 0.0850]]),
                "ROBOT_RADIUS": 0.025
                }
    else:
        return {"ROBOT_NEAR_FORCE": 1000,
                "ROBOT_VELOCITY_MAX": 4,
                "ROBOT_ACC_MAX": 2,
                "accel_max": 4.0,
                "vit_max": 4.0,
                "vit_min": 0.05,
                "xyKp": 2,
                "ki": 0.02,
                "kd": 0.4,
                "thetaKp": 0.7,
                "thetaKd": 0,
                "thetaKi": 0.01,
                "theta-max-acc": 0.05 * math.pi,
                "position_dead_zone": 0.04,
                "MNRC_KP": np.array([0.1, 0.1, 0.1]),
                "MNRC_KI": np.array([0.1, 0.1, 0.1]),
                "MNRC_SPEED_DYNAMIC": np.array([-5, -5, -5]),
                "ROBOT_DYNAMIC": np.array([-5, -5, -5]),
                "ROBOT_COUPLING": np.array([[-0.7071, 0.7071, 0.0850],
                                            [-0.7071, -0.7071, 0.0850],
                                            [0.7071, -0.7071, 0.0850],
                                            [0.7071, 0.7071, 0.0850]]),
                "ROBOT_RADIUS": 0.025
                }


def _xy_to_rphi_(robot_position, ball_position):
    r = math.sqrt((robot_position.x - ball_position.x) ** 2 + (robot_position.y - ball_position.y) ** 2)
    phi = math.atan2((robot_position.y - ball_position.y), (robot_position.x - ball_position.x))
    return r, phi


# pas vraiment nécessaire
# TODO remove
def _rphi_to_xy_(r, phi, ball_position):
    x = r * math.cos(phi) + ball_position.x
    y = r * math.sin(phi) + ball_position.y
    return x, y


def _vit_rphi_to_xy(r, phi, vr, vphi):
    vx = vr*math.cos(phi)-r*vphi*math.sin(phi)
    vy = vr*math.sin(phi)+r*vphi*math.cos(phi)
    return vx, vy