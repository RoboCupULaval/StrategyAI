# Under MIT licence, see LICENCE.txt



import sys
import logging
from multiprocessing import Queue
from queue import Empty
from time import time
from typing import Dict
from collections import namedtuple
from math import sin, cos, sqrt

from RULEngine.robot import Robot, MAX_LINEAR_SPEED, MIN_LINEAR_SPEED, MAX_LINEAR_ACCELERATION

from RULEngine.robot import Robot, MAX_LINEAR_SPEED, MIN_LINEAR_SPEED
from Util.PID import PID
from Util.csv_plotter import CsvPlotter

from Util import Pose, Position
from Util.geometry import rotate, wrap_to_pi
from Util.constant import PLAYER_PER_TEAM
from Util.path import Path
from Util.path_smoother import path_smoother
from Util.scroll_plot import DynamicUpdate
from Util.trapezoidal_speed import get_next_velocity
from config.config_service import ConfigService
import numpy as np

RobotPacket = namedtuple('RobotPacket', 'robot_id command kick_type kick_force dribbler_active charge_kick')
RobotState = namedtuple('RobotState', 'timestamp is_team_yellow packet')


# TODO see if necessary, also same as RobotPacket
class EngineCommand(namedtuple('EngineCommand', 'robot_id cruise_speed path kick_type kick_force dribbler_active charge_kick target_orientation')):
    pass


def get_control_setting(game_type: str):

    if game_type == 'sim':
        translation = {'kp': 1, 'ki': .10, 'kd': 0}
        rotation = {'kp': .75, 'ki': 0.15, 'kd': 0}
    elif game_type == 'real':
        translation = {'kp': .01, 'ki': 0.0, 'kd': 0}
        rotation = {'kp': 0.5, 'ki': 0.02, 'kd': 0.0}
    else:
        raise TypeError('No matching game type found in control setting')

    return {'translation': translation, 'rotation': rotation}


class Observer:
    def __init__(self):
        pass

    def write(self, poses):
        pass


class Controller(list):
    def __init__(self, ai_queue: Queue, observer=Observer):
        self.ai_queue = ai_queue
        self.timestamp = None
        self.observer = observer

        logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger("Controller")

        self.cfg = ConfigService()
        self.team_color = self.cfg.config_dict['GAME']['our_color']

        control_setting = get_control_setting(self.cfg.config_dict['GAME']['type'])

        super().__init__(Robot(robot_id, PositionControl(control_setting), VelocityControl(control_setting))
                         for robot_id in range(PLAYER_PER_TEAM))

    def execute(self, track_frame: Dict) -> RobotState:

        self.timestamp = track_frame['timestamp']
        self.update_robots_states(track_frame[self.team_color])
        self.update_engine_commands()
        self.update_robot_path()

        commands = self.execute_controller()

        packet = self.generate_packet(commands)

        return packet

    def update_robots_states(self, robots_states):
        for robot in robots_states:
            self[robot['id']].pose = robot['pose']
            self[robot['id']].velocity = robot['velocity']

    def update_engine_commands(self):
        try:
            engine_cmds = self.ai_queue.get(block=False)
            for cmd in engine_cmds:
                robot_id = cmd.robot_id
                # TODO: engine command could be a field of Robot
                self[robot_id].kick_type = cmd.kick_type
                self[robot_id].kick_force = cmd.kick_force
                self[robot_id].dribbler_active = cmd.dribbler_active
                self[robot_id].raw_path = cmd.path
                self[robot_id].cruise_speed = cmd.cruise_speed
                self[robot_id].charge_kick = cmd.charge_kick
                self[robot_id].target_orientation = cmd.target_orientation
        except Empty:
            pass

    def update_robot_path(self):
        for robot in self:
            if robot.raw_path is not None and robot.pose is not None:
                robot.raw_path = robot.raw_path.quick_update_path(robot.pose.position)
                robot.path = path_smoother(robot, robot.raw_path)

    def execute_controller(self):
        commands = dict()
        for robot in self:
            if robot.pose is not None and robot.path is not None:  # active robots
                commands[robot.robot_id] = robot.speed_controller.execute(robot)

        return commands

    def generate_packet(self, commands):
        packet = RobotState(timestamp=self.timestamp,
                            is_team_yellow=True if self.team_color == 'yellow' else False,
                            packet=[])

        for robot_id, cmd in commands.items():
            robot = self[robot_id]
            packet.packet.append(
                RobotPacket(robot_id=robot_id,
                            command=cmd,
                            kick_type=robot.kick_type,
                            kick_force=robot.kick_force,
                            dribbler_active=robot.dribbler_active,
                            charge_kick=robot.charge_kick))
        return packet


class PositionControl:

    def __init__(self, control_setting: Dict):
        self.control_setting = control_setting
        self.controllers = {'x': PID(**self.control_setting['translation']),
                            'y': PID(**self.control_setting['translation']),
                            'orientation': PID(**self.control_setting['rotation'], wrap_error=True)}

    def execute(self, robot: Robot, target: Pose):
        robot = robot.pose

        pos_error = target.position - robot.position
        orientation_error = wrap_to_pi(target.orientation - robot.position)

        command = Pose()
        command.position = Position(self.controllers['x'].execute(pos_error.x),
                                    self.controllers['y'].execute(pos_error.y))
        command.orientation = self.controllers['orientation'].execute(orientation_error)

        command.position = rotate(command.position, -robot.orientation)

        overspeed_factor = command.norm / MAX_LINEAR_SPEED
        if overspeed_factor > 1:
            command.position /= overspeed_factor
        return command

    def reset(self):
        for controller in self.controllers.values():
            controller.reset()


class VelocityControl:

    def __init__(self, control_setting: Dict):
        self.orientation_controller = PID(**control_setting['rotation'], wrap_error=True)
        self.control_setting = control_setting
        self.controllers = {'x': PID(**self.control_setting['translation']),
                            'y': PID(**self.control_setting['translation']),
                            'orientation': PID(**self.control_setting['rotation'], wrap_error=True)}

    # TODO: Adapte those argument to the other controler
    def execute(self, robot: Robot):
        pose = robot.pose

        target = Pose(robot.path.points[1], robot.target_orientation)

        error = Pose()
        error.position = target.position - robot.pose.position
        error.orientation = wrap_to_pi(target.orientation - robot.pose.orientation)

        speed_norm = robot.cruise_speed
        if is_time_to_break(robot.pose, robot.path.points[-1], robot.cruise_speed):
            speed_norm = MIN_LINEAR_SPEED  # Near zero, but not quite

        #speed_norm = optimal_speed(robot.pose, path.points[-1], robot.cruise_speed) # TODO: test this IRL

        vel = speed_norm * error.position / error.norm

        command = Pose()
        command.position = rotate(vel, -pose.orientation)
        command.orientation = self.orientation_controller.execute(error.orientation)

        return command


def is_time_to_break(robots_pose, destination, cruise_speed):
    # TODO: we assume that the end speed is zero, which is not always the case
    dist_to_target = (destination - robots_pose.position).norm
    return dist_to_target < cruise_speed ** 2 / MAX_LINEAR_ACCELERATION


def optimal_speed(robots_pose, destination, cruise_speed):
    # TODO: we assume that the end speed is zero, which is not always the case
    dist_to_target = (destination - robots_pose.position).norm
    return max(cruise_speed, sqrt(MAX_LINEAR_ACCELERATION * dist_to_target))