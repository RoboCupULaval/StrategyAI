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
from Util.PID import PID
from Util.csv_plotter import CsvPlotter

from Util import Pose
from Util.constant import PLAYER_PER_TEAM
from Util.path import Path
from Util.path_smoother import path_smoother
from Util.scroll_plot import DynamicUpdate
from Util.trapezoidal_speed import get_next_velocity
from config.config_service import ConfigService
import numpy as np

RobotPacket = namedtuple('RobotPacket', 'robot_id command kick_type kick_force dribbler_active')
RobotPacketFrame = namedtuple('RobotPacketFrame', 'timestamp is_team_yellow packet')


# TODO see if necessary, also same as RobotPacket
class EngineCommand(namedtuple('EngineCommand', 'robot_id cruise_speed path kick_type kick_force dribbler_active target_orientation')):
    pass


def get_control_setting(game_type: str):

    if game_type == 'sim':
        translation = {'kp': 1, 'ki': .10, 'kd': 0}
        rotation = {'kp': .75, 'ki': 0.15, 'kd': 0}
    elif game_type == 'real':
        translation = {'kp': .01, 'ki': 0.0, 'kd': 0}
        rotation = {'kp': .01, 'ki': 0.0035, 'kd': 0.0001}
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
        self.dt = 0
        self.last_time = 0
        self.timestamp = None
        self.observer = observer

        logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger("Controller")

        self.cfg = ConfigService()
        self.team_color = self.cfg.config_dict['GAME']['our_color']

        control_setting = get_control_setting(self.cfg.config_dict['GAME']['type'])

        super().__init__(Robot(robot_id, PositionControl(control_setting), VelocityControl(control_setting)) for robot_id in range(PLAYER_PER_TEAM))

    def execute(self, track_frame: Dict) -> RobotPacketFrame:
        self.dt, self.last_time = time() - self.last_time, time()
        self.timestamp = track_frame['timestamp']
        self.update_robots_states(track_frame[self.team_color])
        self.update_ai_commands()

        packet = RobotPacketFrame(timestamp=self.timestamp,
                                  is_team_yellow=True if self.team_color == 'yellow' else False,
                                  packet=[])

        for robot in self:
            if robot.pose is not None and robot.path is not None: # active robots
                self.update_robot_path(robot)
                target = Pose(robot.path.points[1], robot.target_orientation).to_dict()

                if sqrt((target["x"]-robot.pose['x'])**2 + (target["y"]-robot.pose['y'])**2) > 50:
                    command = robot.speed_controller.execute(robot, robot.path, robot.target_orientation)
                else:
                    command = robot.position_controller.execute(robot, target)
            else:
                command = {"x": 0, "y": 0, "orientation": 0}
            packet.packet.append(RobotPacket(robot_id=robot.robot_id,
                                             command=command,
                                             kick_type=robot.kick_type,
                                             kick_force=robot.kick_force,
                                             dribbler_active=robot.dribbler_active))
            #self.observer.write([Pose.from_dict(robot.velocity).position.norm(), np.linalg.norm([command['x'], command['y']])])
        return packet

    def update_robots_states(self, robots_states):
        for robot in robots_states:
            robot_id = robot['id']
            self[robot_id].pose = {'x': robot['pose']['x'],
                                   'y': robot['pose']['y'],
                                   'orientation': robot['pose']['orientation']}
            self[robot_id].velocity = {'x': robot['velocity']['x'],
                                       'y': robot['velocity']['y'],
                                       'orientation': robot['velocity']['orientation']}

    def update_ai_commands(self):
        try:
            ai_commands = self.ai_queue.get(block=False)
            for cmd in ai_commands:
                robot_id = cmd.robot_id
                self[robot_id].kick_type = cmd.kick_type
                self[robot_id].kick_force = cmd.kick_force
                self[robot_id].dribbler_active = cmd.dribbler_active
                self[robot_id].raw_path = cmd.path
                self[robot_id].path = cmd.path
                self[robot_id].cruise_speed = cmd.cruise_speed

                self[robot_id].target_orientation = cmd.target_orientation
        except Empty:
            pass

    def update_robot_path(self, robot):
        # The pathfinder was coded with Pose/Position in mind. So the dict pose of Robot must be converted
        pose = Pose.from_dict(robot.pose)
        # TODO: This is really ugly... We need to juggle between Path and it's  dict representation.
        raw_path = Path.from_dict(robot.raw_path)
        raw_path = raw_path.quick_update_path(pose.position)
        robot.path = raw_path
        robot.path = path_smoother(robot)
        robot.raw_path = raw_path.to_dict()


class PositionControl:

    def __init__(self, control_setting: Dict):
        self.control_setting = control_setting
        self.controllers = {'x': PID(**self.control_setting['translation']),
                            'y': PID(**self.control_setting['translation']),
                            'orientation': PID(**self.control_setting['rotation'], wrap_error=True)}

    def execute(self, robot, target):
        pose = robot.pose
        error = {state: target[state] - pose[state] for state in pose}
        command = {state: self.controllers[state].execute(error[state]) for state in self.controllers}
        command['x'], command['y'] = rotate(command['x'], command['y'], -pose['orientation'])

        overspeed_factor = sqrt(command['x'] ** 2 + command['y'] ** 2) / MAX_LINEAR_SPEED
        if overspeed_factor > 1:
            command['x'], command['y'] = command['x'] / overspeed_factor, command['y'] / overspeed_factor
        return command

    def reset(self):
        for controller in self.controllers.values():
            controller.reset()


def is_time_to_break(robots_pose, destination, cruise_speed):
    # TODO: we assume that the end speed is zero, which is not always the case
    dist_to_target = sqrt((destination[0] - robots_pose["x"])**2 +
                          (destination[1] - robots_pose["y"]) ** 2)
    return dist_to_target < cruise_speed ** 2 / MAX_LINEAR_ACCELERATION

def optimal_speed(robots_pose, destination, cruise_speed):
    # TODO: we assume that the end speed is zero, which is not always the case
    dist_to_target = sqrt((destination[0] - robots_pose["x"])**2 +
                          (destination[1] - robots_pose["y"]) ** 2)
    return max(cruise_speed, sqrt(MAX_LINEAR_ACCELERATION * dist_to_target))

class VelocityControl:

    def __init__(self, control_setting: Dict):
        self.orientation_controller = PID(**control_setting['rotation'], wrap_error=True)
        self.control_setting = control_setting
        self.controllers = {'x': PID(**self.control_setting['translation']),
                            'y': PID(**self.control_setting['translation']),
                            'orientation': PID(**self.control_setting['rotation'], wrap_error=True)}

    # TODO: Adapte those argument to the other controler
    def execute(self, robot: Robot, path, target_orientation):
        pose = robot.pose
        target = Pose(path.points[1], target_orientation).to_dict()
        error = {state: target[state] - pose[state] for state in pose}

        speed_norm = robot.cruise_speed
        if is_time_to_break(robot.pose, path.points[-1], robot.cruise_speed):
            speed_norm = MIN_LINEAR_SPEED  # Near zero, but not quite
        #speed_norm = optimal_speed(robot.pose, path.points[-1], robot.cruise_speed) # TODO: test this IRL
        norm = sqrt(error["x"]**2 + error["y"]**2)
        vel_x = speed_norm * error["x"] / norm
        vel_y = speed_norm  * error["y"] / norm

        cmd_x, cmd_y = rotate(vel_x, vel_y, -pose["orientation"])

        cmd_theta = self.orientation_controller.execute(error['orientation'])

        command = {'x': cmd_x, 'y': cmd_y, 'orientation': cmd_theta}
        return command


def rotate(x: float, y: float, angle: float):
    return [cos(angle) * x - sin(angle) * y, sin(angle) * x + cos(angle) * y]
