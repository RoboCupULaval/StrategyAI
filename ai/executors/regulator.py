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

INTEGRAL_DECAY = 0.5 # reduit de moitié aux 1/8 de secondes
ZERO_ACCUMULATOR_TRHESHOLD = 0.5
FILTER_LENGTH = 1
REGULATOR_DEADZONE = 120

SIMULATION_MAX_NAIVE_CMD = math.sqrt(2) / 3
SIMULATION_MIN_NAIVE_CMD = 0
SIMULATION_MAX_THETA_CMD = math.pi / 8
SIMULATION_MIN_THETA_CMD = 0
SIMULATION_DEFAULT_STATIC_GAIN = 0.0009
SIMULATION_DEFAULT_INTEGRAL_GAIN = 0
SIMULATION_DEFAULT_THETA_GAIN = 1

REAL_MAX_NAIVE_CMD = 1200
REAL_DEADZONE_CMD = 110
REAL_MIN_NAIVE_CMD = REAL_DEADZONE_CMD
REAL_MAX_THETA_CMD = 300
REAL_MIN_THETA_CMD = 30
REAL_DEFAULT_STATIC_GAIN = 0.300
REAL_DEFAULT_INTEGRAL_GAIN = 0.600
REAL_DEFAULT_THETA_GAIN = 350
REAL_DEFAUT_INTEGRAL_THETA_GAIN = 0
#REAL_DEFAULT_THETA_GAIN = 0

ROBOT_NEAR_FORCE = 100
ROBOT_VELOCITY_MAX = 4
ROBOT_ACC_MAX = 2


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
                cmd.speed = self.regulators[robot_idx].\
                    update_pid_and_return_speed_command(cmd,
                                                        active_player,
                                                        delta_t,
                                                        idx=robot_idx)
        self._potential_field()

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
                        try:
                            force[0] += 1 / dist * math.cos(angle)
                        except:
                            pass
                        try:
                            force[1] += 1 / dist * math.sin(angle)
                        except:
                            pass

                for robot in self.ws.game_state.game.enemies.players.values():
                    dist = get_distance(current_robot_pos, robot.pose.position)
                    angle = math.atan2(current_robot_pos.y - robot.pose.position.y,
                                       current_robot_pos.x - robot.pose.position.x)
                    try:
                        force[0] += 1 / dist * math.cos(angle)
                    except:
                        pass
                    try:
                        force[1] += 1 / dist * math.sin(angle)
                    except:
                        pass

                # dist_goal = get_distance(current_robot_pos, ai_c.pose_goal.position)
                angle_goal = math.atan2(current_robot_pos.y - ai_c.pose_goal.position.y,
                                        current_robot_pos.x - ai_c.pose_goal.position.x)

                dt = self.ws.game_state.game.delta_t

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


class PI(object):
    """
        Asservissement PI en position

        u = Kp * err + Sum(err) * Ki * dt
    """

    def __init__(self, simulation_setting=True):
        self.gs = GameState()
        self.paths = {}
        # are we in a simulation?
        self.simulation_setting = simulation_setting
        self.constants = _set_constants(simulation_setting)
        self.accel_max = self.constants["accel_max"]
        self.vit_max = self.constants["vit_max"]
        self.kp = self.constants["kp"]
        self.last_err_x = self.constants["last_err_x"]
        self.last_err_y = self.constants["last_err_y"]



        # self.accumulator_x = 0
        # self.accumulator_y = 0
        # self.accumulator_t = 0
        # self.constants = _set_constants(simulation_setting)
        # self.kp = self.constants['default-kp']
        # self.ki = self.constants['default-ki']
        # self.ktheta = self.constants['default-ktheta']
        # self.itheta = self.constants['default-itheta']
        # self.last_command_x = 0
        # self.last_command_y = 0
        # self.previous_cmd = []
        #self.val_filtered = open('filtered.txt', 'w')

    def update_pid_and_return_speed_command(self, cmd, active_player, delta_t=0.030, idx=4, robot_speed=0.2):
        """ Met à jour les composants du pid et retourne une commande en vitesse. """
        assert isinstance(cmd, AICommand), "La consigne doit etre une Pose dans le PI"
        player_pose = active_player.pose
        #print("regulator_pose", [player_pose.position.x, player_pose.position.y, player_pose.orientation])
        vit = [0, 0, 0]

        Kp = 0.5
        Kd = 0.2
        self.paths[idx] = cmd.path

        # if len(self.paths[idx]) > 0 and\
        #    (cmd.pose_goal is not self.paths[idx][-1]):
        r_x, r_y = cmd.pose_goal.position.x, cmd.pose_goal.position.y
        t_x, t_y = active_player.pose.position.x, active_player.pose.position.y

        v_x = active_player.velocity[0]
        v_y = active_player.velocity[1]
        v_x, v_y = _correct_for_referential_frame(v_x, v_y, -active_player.pose.orientation)
        v_current = math.sqrt(v_x**2 + v_y**2)

        # player_local_velocity = [active_player.velocity[0], active_player.velocity[1]]
        # player_local_velocity[0], player_local_velocity[1] = _correct_for_referential_frame(player_local_velocity[0], player_local_velocity[1], -active_player.pose.orientation)

        delta_x = (r_x - t_x)/1000
        delta_y = (r_y - t_y)/1000

        #quick fix pour real life
        #delta_x = delta_x - sign(delta_x) * 0.2
        #delta_y = delta_y - sign(delta_y) * 0.2
        # print("pos before",delta_x, delta_y)
        delta_x, delta_y = _correct_for_referential_frame(delta_x, delta_y, -active_player.pose.orientation)

        delta = math.sqrt(delta_x**2 + delta_y**2)
        angle = math.atan2(delta_y, delta_x)

        if delta <= 0.05:
            delta = 0

        v_target = self.kp * delta
        v_max = math.fabs(v_current) + self.accel_max * delta_t
        v_max = min(self.vit_max, v_max)
        v_target = min(v_max, v_target)

        v_target_x = v_target * math.cos(angle)
        v_target_y = v_target * math.sin(angle)

        # print("pos transform",delta_x, delta_y)
        # try:
        #     if abs(delta_x) > abs(delta_y):
        #         ratio_vit_x = 1
        #         ratio_vit_y = abs(delta_y / delta_x)
        #         if ratio_vit_y > 1:
        #             ratio_vit_y = 1
        #     else:
        #         ratio_vit_x = abs(delta_x / delta_y)
        #         if ratio_vit_x > 1:
        #             ratio_vit_x = 1
        #         ratio_vit_y = 1
        # except ZeroDivisionError:
        #     ratio_vit_x = 0
        #     ratio_vit_y = 0
        #
        # accel_x = self.accel_max * ratio_vit_x
        # accel_y = self.accel_max * ratio_vit_y


        # try:
        #     robot_speed_x = ratio_vit_x * robot_speed * delta_x / (delta_x ** 2 + delta_y ** 2) ** 0.5
        # except ZeroDivisionError:
        #     robot_speed_x = 0
        # try:
        #     robot_speed_y = ratio_vit_y * robot_speed * delta_y / (delta_x ** 2 + delta_y ** 2) ** 0.5
        # except ZeroDivisionError:
        #     robot_speed_y = 0
        #
        # # accel ou decel en x ?
        # if abs(delta_x) < player_local_velocity[0]**2/(accel_x / 4) and \
        #                 sign(delta_x) == sign(player_local_velocity[0]):
        #     # on doit ralentir
        #     vit[0] = player_local_velocity[0] - sign(delta_x) * accel_x *delta_t
        # elif abs(delta_x) < 0.3:
        #     # on est arrive!
        #     vit[0] = 0
        # else:
        #     # on peut encore accelerer!
        #     if abs(player_local_velocity[0]) < abs(robot_speed_x):
        #         vit[0] = player_local_velocity[0] + sign(delta_x) * accel_x * delta_t
        #     else:
        #         vit[0] = robot_speed_x
        # # accel ou decel en y ?
        # if abs(delta_y) < player_local_velocity[1] ** 2 / (accel_y / 4) and \
        #                 sign(delta_y) == sign(player_local_velocity[1]):
        #     # on doit ralentir
        #     vit[1] = player_local_velocity[1] - sign(delta_y) * accel_y * delta_t
        # elif abs(delta_y) < 0.3:
        #     # on est arrive!
        #     vit[1] = 0
        # else:
        #     # on peut encore accelerer!
        #     if abs(player_local_velocity[1]) < abs(robot_speed_y):
        #         vit[1] = player_local_velocity[1] + sign(delta_y) * accel_y * delta_t
        #     else:
        #         vit[1] = robot_speed_y
        # print(active_player.pose.orientation)

        # vit[0], vit[1] = _correct_for_referential_frame(vit[0], vit[1], -active_player.pose.orientation)
        # self.val_filtered.write("{}, {}\n".format(vit[0], vit[1]))
        # print("computed_velocity", vit)
        # if self.last_err_x != 0 and delta_t != 0:
        #     d_e_x = (e_x - self.last_err_x) / delta_t
        #     d_e_y = (e_y - self.last_err_y) / delta_t
        # else:
        #     d_e_x = 0
        #     d_e_y = 0
        # self.last_err_x = e_x
        # self.last_err_y = e_y
        # vit = np.array([Kp*e_x+Kd*d_e_x, Kp*e_y+Kd*d_e_y])
        # norm = np.linalg.norm(vit)
        # if norm > 1:
        #     vit /= norm
        # #elif norm < 0.5:
        # #    return Pose(Position(0, 0))
        #
        # vit *= robot_speed
        #print('FUUUUUUUUUUUUUUUUUUUUUUU', vit)
        #return Pose(Position(vit[0], vit[1]), cmd.speed.orientation)
        # print('FUUUUUUUUUUUUUUUUUUUUUUU', vit)
        # if abs(vit[0]) > robot_speed:
        #     vit[0] = sign(vit[0]) * robot_speed
        # if abs(vit[1]) > robot_speed:
        #     vit[1] = sign(vit[1]) * robot_speed
        #print(v_target_x, "    ", v_target_y)
        return Pose(Position(v_target_x, v_target_y), 0)


def _correct_for_referential_frame(x, y, orientation):

    cos = math.cos(orientation)
    sin = math.sin(orientation)

    corrected_x = (x * cos - y * sin)
    corrected_y = (y * cos + x * sin)
    return corrected_x, corrected_y


def _set_constants(simulation_setting):
    if simulation_setting:
        return {"ROBOT_NEAR_FORCE": 100,
                "ROBOT_VELOCITY_MAX": 4,
                "ROBOT_ACC_MAX": 2,
                "accel_max": 1,
                "vit_max": 0.5,
                "kp": 0.25,
                "last_err_x": 0,
                "last_err_y": 0
                }
    else:
        return {"ROBOT_NEAR_FORCE": 100,
                "ROBOT_VELOCITY_MAX": 4,
                "ROBOT_ACC_MAX": 2,
                "accel_max": 1,
                "vit_max": 0.5,
                "kp": 0.25,
                "last_err_x": 0,
                "last_err_y": 0
                }



