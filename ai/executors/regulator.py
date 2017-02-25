# Under MIT License, see LICENSE.txt
import math

import time

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.geometry import get_distance
from ai.Util.ai_command import AICommandType, AICommand
from ai.executors.executor import Executor
from ai.states.game_state import GameState
from ai.states.world_state import WorldState
import numpy as np


ROBOT_NEAR_FORCE = 100
ROBOT_VELOCITY_MAX = 20
ROBOT_ACC_MAX = 5


def sign(x):
    if x > 0:
        return 1
    if x == 0:
        return 0
    return -1


class PositionRegulator(Executor):
    def __init__(self, p_world_state: WorldState, is_simulation=False):
        super().__init__(p_world_state)
        self.regulators = [PI(simulation_setting=is_simulation) for _ in range(6)]
        self.last_timestamp = 0

    def exec(self):
        commands = self.ws.play_state.current_ai_commands
        delta_t = self.ws.game_state.game.delta_t
        for cmd in commands.values():
            if cmd.command is AICommandType.MOVE:
                robot_idx = cmd.robot_id
                active_player = self.ws.game_state.game.friends.players[robot_idx]
                if not cmd.rotate_around_flag:
                    cmd.speed = self.regulators[robot_idx].\
                        update_pid_and_return_speed_command(cmd,
                                                            active_player,
                                                            delta_t,
                                                            idx=robot_idx)
                else:
                    cmd.speed = self.regulators[robot_idx].\
                        rotate_around(cmd, active_player, delta_t)

        #self._potential_field()

    def _potential_field(self):
        current_ai_c = self.ws.play_state.current_ai_commands

        for ai_c in current_ai_c.values():
            if ai_c.command == AICommandType.MOVE and len(ai_c.path) > 0:
                goal = ai_c.pose_goal
                force = [0, 0]
                current_robot_pos = self.ws.game_state.get_player_position(ai_c.robot_id)
                current_robot_velocity = self.ws.game_state.game.friends.players[ai_c.robot_id].velocity

                for robot in self.ws.game_state.game.friends.players.values():
                    if robot.id != ai_c.robot_id:
                        dist = get_distance(current_robot_pos, robot.pose.position)
                        angle = math.atan2(current_robot_pos.y - robot.pose.position.y,
                                           current_robot_pos.x - robot.pose.position.x)
                        try:
                            force[0] += 1 / dist * math.cos(angle)
                        except:
                            print("div 0 - 1")
                            pass
                        try:
                            force[1] += 1 / dist * math.sin(angle)
                        except:
                            print("div 0 - 2")
                            pass

                for robot in self.ws.game_state.game.enemies.players.values():
                    dist = get_distance(current_robot_pos, robot.pose.position)
                    angle = math.atan2(current_robot_pos.y - robot.pose.position.y,
                                       current_robot_pos.x - robot.pose.position.x)
                    try:
                        force[0] += 1 / dist * math.cos(angle)
                    except:
                        print("div 0 - 3")
                        pass
                    try:
                        force[1] += 1 / dist * math.sin(angle)
                    except:
                        print("div 0 - 4")
                        pass

                # dist_goal = get_distance(current_robot_pos, ai_c.pose_goal.position)
                angle_goal = math.atan2(current_robot_pos.y - ai_c.pose_goal.position.y,
                                        current_robot_pos.x - ai_c.pose_goal.position.x)

                dt = 0.3  # self.ws.game_state.game.delta_t

                a = (((current_robot_velocity[0] + 0.1) * math.cos(angle_goal) - current_robot_velocity[0]) / dt)
                b = (((current_robot_velocity[1] + 0.1) * math.cos(angle_goal) - current_robot_velocity[1]) / dt)
                acc_goal = math.sqrt(a ** 2 + b ** 2)

                angle_acc_goal = math.atan2(b, a)

                c = force[0] * ROBOT_NEAR_FORCE + (acc_goal * math.cos(angle_acc_goal))
                d = force[1] * ROBOT_NEAR_FORCE + (acc_goal * math.cos(angle_acc_goal))

                acc_robot_x = min(max(c, -ROBOT_ACC_MAX), ROBOT_ACC_MAX)
                acc_robot_y = min(max(d, -ROBOT_ACC_MAX), ROBOT_ACC_MAX)

                vit_robot_x = min(max(current_robot_velocity[0] + acc_robot_x * dt, -ROBOT_VELOCITY_MAX),
                                  ROBOT_VELOCITY_MAX)
                vit_robot_y = min(max(current_robot_velocity[1] + acc_robot_y * dt, -ROBOT_VELOCITY_MAX),
                                  ROBOT_VELOCITY_MAX)
                ai_c.path[0] = Position(vit_robot_x, vit_robot_y)


class PID(object):
    def __init__(self, kp, ki, kd, simulation_setting=True):
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

        self.rotate_pid = [PID(0.0001, 0, 0), PID(1, 0, 0), PID(1.2, 0, 0)]

        self.simulation_setting = simulation_setting
        self.constants = _set_constants(simulation_setting)
        self.accel_max = self.constants["accel_max"]
        self.vit_max = self.constants["vit_max"]
        self.xyKp = self.constants["xyKp"]
        self.ki = self.constants["ki"]
        self.kd = self.constants["kd"]
        self.thetaKp = self.constants["thetaKp"]
        self.thetaKi = self.constants["thetaKi"]
        # non-constant
        self.lastErr = 0
        self.kiSum = 0
        self.vit_min = 0.05
        self.thetaKiSum = 0
        self.last_target = None
        self.position_dead_zone = self.constants["position_dead_zone"] #0.03
        self.rotation_dead_zone = 0.01 * math.pi
        self.last_theta_target = None

    def update_pid_and_return_speed_command(self, cmd, active_player, delta_t=0.030, idx=4, robot_speed=0.2):
        """ Met à jour les composants du pid et retourne une commande en vitesse. """
        assert isinstance(cmd, AICommand), "La consigne doit etre une Pose dans le PI"
        self.paths[idx] = cmd.path
        # print("delta t (regulator)   :   ", delta_t)
        delta_t = 0.03

        r_x, r_y, r_theta = cmd.pose_goal.position.x, cmd.pose_goal.position.y, cmd.pose_goal.orientation
        t_x, t_y, t_theta = active_player.pose.position.x, active_player.pose.position.y, active_player.pose.orientation

        target = math.sqrt(r_x**2 + r_y**2)

        # always true?
        if target != self.last_target:
            self.kiSum = 0

        v_x = active_player.velocity[0]
        v_y = active_player.velocity[1]
        v_theta = active_player.velocity[2]
        v_x, v_y = _correct_for_referential_frame(v_x, v_y, -active_player.pose.orientation)
        v_current = math.sqrt(v_x**2 + v_y**2)

        delta_x = (r_x - t_x)/1000
        delta_y = (r_y - t_y)/1000
        delta_theta = (r_theta - t_theta)

        delta_x, delta_y = _correct_for_referential_frame(delta_x, delta_y, -active_player.pose.orientation)

        delta = math.sqrt(delta_x**2 + delta_y**2)
        angle = math.atan2(delta_y, delta_x)

        self.vit_min = 0.06
        if delta <= self.position_dead_zone:
            self.vit_min = 0
            delta = 0

        v_target = self.xyKp * delta
        self.kiSum += delta * self.ki * delta_t * sign(delta_x * v_x + delta_y * v_y)
        v_target += math.fabs(self.kiSum)
        v_target += self.kd * ((delta - self.lastErr) / delta_t)
        self.lastErr = delta

        #print('kiSum', self.kiSum)

        v_max = math.fabs(v_current) + self.accel_max * delta_t
        v_max = min(self.vit_max, v_max)
        v_target = max(self.vit_min, min(v_max, v_target))

        minimal_dist = v_current / (2 * self.accel_max)
        if minimal_dist < math.fabs(delta):
            v_limited = delta * 2 * self.accel_max
            v_target = min(v_target, v_limited)

        decoupled_angle = angle - v_theta * delta_t

        v_target_x = v_target * math.cos(decoupled_angle)
        v_target_y = v_target * math.sin(decoupled_angle)


        if r_theta != self.last_theta_target:
            self.kiSum = 0

        v_theta_target = self.thetaKp * delta_theta
        self.thetaKiSum += delta_theta * self.thetaKi * delta_t
        v_theta_target += self.thetaKiSum

        # print('Error : ', delta)
        if delta <= self.position_dead_zone:
            v_target_x = 0
            v_target_y = 0
        #if math.fabs(delta_theta) <= self.rotation_dead_zone:
            #v_theta_target = 0

        return Pose(Position(v_target_x, v_target_y), v_theta_target)

    def rotate_around(self, command, active_player, delta_t):
        delta_t = 0.03
        r = command.rotate_around_goal.radius
        phi = command.rotate_around_goal.direction
        theta = command.rotate_around_goal.orientation

        #print(command.rotate_around_goal.center_position)
        r_p, phi_p = _xy_to_rphi_(active_player.pose.position, command.rotate_around_goal.center_position)
        theta_p = active_player.pose.orientation

        vr = self.rotate_pid[0].update(r, r_p, delta_t)
        vphi = self.rotate_pid[1].update(phi, phi_p, delta_t)
        vtheta = self.rotate_pid[2].update(theta, theta_p, delta_t)

        #print(vr, "  ", vphi, "  ", vtheta)
        print(theta - theta_p)

        vx, vy = _vit_rphi_to_xy(r, phi, vr, vphi)

        vx, vy = _correct_for_referential_frame(vx, vy, -active_player.pose.orientation)

        #print(vx, "       ", vy)
        return Pose(Position(vx/1000, vy/1000), vtheta)

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
                "position_dead_zone": 0.03
                }
    else:
        return {"ROBOT_NEAR_FORCE": 1000,
                "ROBOT_VELOCITY_MAX": 4,
                "ROBOT_ACC_MAX": 2,
                "accel_max": 0.5,
                "vit_max": 0.5,
                "vit_min": 0.05,
                "xyKp": 0.7,
                "ki": 0.005,
                "kd": 0.02,
                "thetaKp": 0.6,
                "thetaKi": 0.2,
                "position_dead_zone": 0.03
                }


def _xy_to_rphi_(robot_position, ball_position):
    r = math.sqrt((robot_position.x - ball_position.x) ** 2 + (robot_position.y - ball_position.y) ** 2)
    phi = math.atan2(-(robot_position.y - ball_position.y), -(robot_position.x - ball_position.x))
    return (r, phi)


# pas vraiment nécessaire
def _rphi_to_xy_(r,phi, ball_position):
    x = r * math.cos(phi) + ball_position.x
    y = r * math.sin(phi) + ball_position.y
    return (x,y)


def _vit_rphi_to_xy(r, phi, vr, vphi):
    vx = vr*math.cos(phi)-r*vphi*math.sin(phi)
    vy = vr*math.sin(phi)+r*vphi*math.cos(phi)
    return (vx, vy)
