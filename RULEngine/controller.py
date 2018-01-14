
from multiprocessing import Queue
from queue import Empty
import logging
from math import cos, sin, sqrt

from RULEngine.Util.PID import PID

from config.config_service import ConfigService

from typing import Dict

MAX_ROBOT = 12
MAX_LINEAR_SPEED = 2000  # mm/s


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

        super().__init__(Robot(control_setting, robot_id) for robot_id in range(MAX_ROBOT))

    def update(self, track_frame: Dict):
        self.timestamp = track_frame['timestamp']
        our_robots = track_frame[self.team_color]

        for robot in our_robots:
            robot_id = robot['id']
            self[robot_id].update(robot)
            self[robot_id]['is_active'] = True

        try:
            ai_commands = self.ai_queue.get(block=False)
            for cmd in ai_commands:
                robot_id = cmd['id']
                self[robot_id]['target'] = cmd.get('target', None)
                self[robot_id]['control_type'] = cmd.get('control_type', {'x': 'position', 'y': 'position', 'orientation': 'position'})
                self[robot_id]['kick_type'] = cmd.get('kick_type', None)
                self[robot_id]['kick_force'] = cmd.get('kick_force', 0)
                self[robot_id]['dribbler_active'] = cmd.get('dribbler_active', False)
                self[robot_id]['has_target'] = True if cmd['target'] else False

        except Empty:
            pass

    def execute(self) -> Dict:

        is_team_yellow = True if self.team_color == 'yellow' else False
        cmds = {'timestamp': self.timestamp, 'is_team_yellow': is_team_yellow, 'commands': {}}

        active_robots = iter(robot for robot in self if robot['is_active'] and robot['has_target'])

        for robot in active_robots:
            error = {state: robot['target'][state] - robot['pose'][state] for state in robot['pose']}
            command = robot['controller'].execute(error)
            command['x'], command['y'] = rotate(command['x'], command['y'], -robot['pose']['orientation'])

            overspeed_factor = sqrt(command['x'] ** 2 + command['y'] ** 2)/MAX_LINEAR_SPEED
            if overspeed_factor > 1:
                command['x'], command['y'] = command['x']/overspeed_factor, command['y']/overspeed_factor

            robot['command'] = command

            # Create robot command
            cmds['commands'][robot['id']] = robot['command']
            cmds['commands'][robot['id']]['kick'] = robot['kick_force']
            cmds['commands'][robot['id']]['dribbler_active'] = robot['dribbler_active']

        return cmds


class Robot(dict):
    def __init__(self, control_setting, robot_id):
        super().__init__()
        self['controller'] = MotionControl(control_setting)
        self['command'] = {'x': None, 'y': None, 'orientation': None}
        self['target'] = {'x': None, 'y': None, 'orientation': None}
        self['pose'] = {'x': None, 'y': None, 'orientation': None}
        self['velocity'] = {'x': None, 'y': None, 'orientation': None}
        self['control_type'] = {'x': 'position', 'y': 'position', 'orientation': 'position'}
        self['kick_type'] = None
        self['kick_force'] = 0
        self['dribbler_active'] = False
        self['is_active'] = False
        self['has_target'] = False
        self['id'] = robot_id


class MotionControl(object):
    def __init__(self, control_setting: Dict):
        self.control_setting = control_setting
        self.controllers = {'x': PID(**self.control_setting['translation']),
                            'y': PID(**self.control_setting['translation']),
                            'orientation': PID(**self.control_setting['rotation'], wrap_error=True)}

    def execute(self, error: Dict) -> Dict:
        return {state: self.controllers[state].execute(error[state]) for state in self.controllers}

    def reset(self):
        for controller in self.controllers.values():
            controller.reset()


def rotate(x: float, y: float, angle: float):
    return [cos(angle) * x - sin(angle) * y, sin(angle) * x + cos(angle) * y]
