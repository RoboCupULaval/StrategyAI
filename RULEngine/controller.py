
import logging
from math import cos, sin, sqrt
from multiprocessing import Queue
from queue import Empty
from typing import Dict

from collections import namedtuple

from Util.PID import PID
from config.config_service import ConfigService

MAX_ROBOT = 12
MAX_LINEAR_SPEED = 2000  # mm/s


RobotState = namedtuple('RobotState', 'robot_id command kick_type kick_force dribbler_active')
RobotPacket = namedtuple('RobotPacket', 'timestamp is_team_yellow robots_states')


class Robot:

    __slots__ = ('_robot_id', 'controller', 'target', 'pose', 'velocity', 'kick_type', 'kick_force', 'dribbler_active')

    def __init__(self, robot_id, controller):
        self._robot_id = robot_id
        self.controller = controller
        self.target = None
        self.pose = None
        self.velocity = None
        self.kick_type = None
        self.kick_force = 0
        self.dribbler_active = False

    @property
    def robot_id(self):
        return self._robot_id


def get_control_setting(game_type: str):

    if game_type == 'sim':
        translation = {'kp': .7, 'ki': 0.000001, 'kd': 0.001}
        rotation = {'kp': 0.5, 'ki': 0, 'kd': 0.00001}
    elif game_type == 'real':
        translation = {'kp': .01, 'ki': 0.0005, 'kd': 0}
        rotation = {'kp': .01, 'ki': 0.0035, 'kd': 0.0001}
    else:
        raise TypeError('No matching game type found in control setting')

    return {'translation': translation, 'rotation': rotation}


class Controller(list):
    def __init__(self, ai_queue: Queue):

        self.ai_queue = ai_queue

        self.timestamp = None

        logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger("Controller")

        self.cfg = ConfigService()
        self.team_color = self.cfg.config_dict['GAME']['our_color']

        control_setting = get_control_setting(self.cfg.config_dict['GAME']['type'])

        super().__init__(Robot(robot_id, PositionControl(control_setting)) for robot_id in range(MAX_ROBOT))

    def update(self, track_frame: Dict):
        self.timestamp = track_frame['timestamp']
        our_robots = track_frame[self.team_color]

        for robot in our_robots:
            robot_id = robot['id']
            self[robot_id].pose = robot['pose']
            self[robot_id].velocity = robot['velocity']

        try:
            ai_commands = self.ai_queue.get(block=False)
            for cmd in ai_commands:
                robot_id = cmd.robot_id
                self[robot_id].target = cmd.target
                self[robot_id].kick_type = cmd.kick_type
                self[robot_id].kick_force = cmd.kick_force
                self[robot_id].dribbler_active = cmd.dribbler_active

        except Empty:
            pass

    def execute(self) -> RobotPacket:

        packet = RobotPacket(timestamp=self.timestamp,
                             is_team_yellow=True if self.team_color == 'yellow' else False,
                             robots_states=[])

        active_robots = iter(robot for robot in self
                             if robot.pose is not None and robot.target is not None)

        for robot in active_robots:
            command = robot.controller.execute(robot.target, robot.pose)
            packet.robots_states.append(RobotState(robot_id=robot.robot_id,
                                                   command=command,
                                                   kick_type=robot.kick_type,
                                                   kick_force=robot.kick_force,
                                                   dribbler_active=robot.dribbler_active))

        return packet


class PositionControl:
    def __init__(self, control_setting: Dict):
        self.control_setting = control_setting
        self.controllers = {'x': PID(**self.control_setting['translation']),
                            'y': PID(**self.control_setting['translation']),
                            'orientation': PID(**self.control_setting['rotation'], wrap_error=True)}

    def execute(self, target, pose) -> Dict:

        error = {state: target[state] - pose[state] for state in pose}
        command = {state: self.controllers[state].execute(error[state]) for state in self.controllers}
        command['x'], command['y'] = rotate(command['x'], command['y'], -pose['orientation'])

        overspeed_factor = sqrt(command['x'] ** 2 + command['y'] ** 2) / MAX_LINEAR_SPEED
        if overspeed_factor > 1:
            command['x'], command['y'] = command['x'] / overspeed_factor, command['y'] / overspeed_factor

        return command  # TODO: change dict to Pose

    def reset(self):
        for controller in self.controllers.values():
            controller.reset()


class VelocityControl:
    pass


def rotate(x: float, y: float, angle: float):
    return [cos(angle) * x - sin(angle) * y, sin(angle) * x + cos(angle) * y]
