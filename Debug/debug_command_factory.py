# Under MIT License, see LICENSE.txt

from math import sin, cos
from typing import Dict, Tuple, List

from Engine.Controller.robot import Robot
from Util import Pose, Position
from Util.geometry import Area
from Util.path import Path
from Util.role import Role
from ai.GameDomainObjects.player import Player
from config.config import Config
config = Config()

__author__ = "Maxime Gagnon-Legault, Philippe Babin, Simon Bouchard, and others"


class Color(object):
    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    def repr(self):
        return self.r, self.g, self.b


YELLOW = Color(181, 137, 0)
ORANGE = Color(203, 75, 22)
RED = Color(220, 50, 47)
MAGENTA = Color(211, 54, 130)
VIOLET = Color(108, 113, 196)
BLUE = Color(38, 139, 210)
CYAN = Color(42, 161, 152)
GREEN = Color(133, 153, 0)
LIGHT_GREEN = Color(0, 255, 0)

DEFAULT_DEBUG_TIMEOUT = 0.1


def debug_command(data_type, data, link=None, version='1.0'):
    return {
    'name': 'StrategyAI',
    'version': version,
    'type': data_type,
    'link': link,
    'data': data,
    }


def flip_position(position: Position):
    """
    The AI is side independent, so every position send to the UI-Debug must be flip around the y axis
    """
    assert isinstance(position, Position)
    if not config["COACH"]["on_negative_side"]:
        return position
    return position.flip_x()


def flip_pose(pose: Pose):
    assert isinstance(pose, Pose)
    if not config["COACH"]["on_negative_side"]:
        return pose
    return pose.mirror_x()


class DebugCommandFactory:
    @staticmethod
    def log(level: int, message: str):
        if not isinstance(level, int):
            raise TypeError('Level need to be an int. Type {} given'.format(type(level)))
        if not isinstance(message, str):
            raise TypeError('Message need to be an string. Type {} given'.format(type(message)))

        return debug_command(2, {'level': level, 'message': message})

    @staticmethod
    def books(strategy_book: Dict, strategy_default: Dict, tactic_book: Dict, tactic_default: Dict):
        return debug_command(1001, {'strategy': strategy_book,
                                    'strategy_default': strategy_default,
                                    'tactic': tactic_book,
                                    'tactic_default': tactic_default})

    @staticmethod
    def robots_strategic_state(states: List[Tuple[Player, str, str, Role]]):
        cmd = {}
        for player, tactic_name, state_name, role in states:
            color = str(player.team.team_color)
            if color not in cmd:
                cmd[color] = {}
            if tactic_name != 'Stop INIT':
                cmd[color][player.id] = {'tactic': tactic_name,
                                         'state': state_name,
                                         'role': role.name}
        return debug_command(1002, cmd)

    @staticmethod
    def auto_play_info(referee_info: str, referee_team_info: Dict, auto_play_info: Dict, auto_flag: bool):
        return debug_command(1005, {'referee': referee_info,
                                    'referee_team': referee_team_info,
                                    'auto_play': auto_play_info,
                                    'auto_flag': auto_flag})

    @staticmethod
    def game_state(blue: List[Dict], yellow: List[Dict], balls: List[Dict]):
        return DebugCommandFactory.robots(blue) \
               + DebugCommandFactory.robots(yellow) \
               + DebugCommandFactory.balls(balls)

    @staticmethod
    def paths(robots: List[Robot]):
        raw_path_cmds, path_cmds = [], []
        for robot in robots:
            if robot.raw_path:
                raw_path_cmds += DebugCommandFactory.path(robot.raw_path, robot.id, color=BLUE)
            if robot.path:
                path_cmds += DebugCommandFactory.path(robot.path, robot.id+config['ENGINE']['max_robot_id'], color=RED) # allow multiple point with same function
        return raw_path_cmds + path_cmds

    @staticmethod
    def robots(robots: List[Dict]):
        cmds = []
        for robot in robots:
            cmds += DebugCommandFactory.robot(robot['pose'])
        return cmds

    @staticmethod
    def balls(balls: List[Dict]):
        cmds = []
        for ball in balls:
            cmds += DebugCommandFactory.ball(flip_position(ball['position']))
        return cmds

    @staticmethod
    def path(path: Path, path_id: int, color=BLUE):
        cmds = [DebugCommandFactory._line(flip_position(start), flip_position(end), color=color, timeout=0.1) for start, end in zip(path, path[1:])]
        cmds += [DebugCommandFactory.multiple_points(path[1:], color=color, link=path_id, timeout=0)]
        return cmds

    @staticmethod
    def robot(pose: Pose, color=LIGHT_GREEN, color_angle=RED, radius=120, timeout=0.05):
        pose = flip_pose(pose)
        cmd = [DebugCommandFactory._circle(pose.position, radius, color=color, timeout=timeout)]
        start = pose.position
        end = start + Position(radius * cos(pose.orientation), radius * sin(pose.orientation))
        cmd += [DebugCommandFactory._line(start, end, color_angle, timeout)]

        return cmd

    @staticmethod
    def ball(position: Position, color=ORANGE, timeout=0.05):
        return [DebugCommandFactory._circle(position, 150, color=color, timeout=timeout)]

    @staticmethod
    def line(start: Position, end: Position, color=MAGENTA, timeout=DEFAULT_DEBUG_TIMEOUT):
        return DebugCommandFactory._line(flip_position(start), flip_position(end), color, timeout)

    @staticmethod
    def _line(start: Position, end: Position, color=MAGENTA, timeout=DEFAULT_DEBUG_TIMEOUT):
        return debug_command(3001, {'start': start.to_tuple(),
                                    'end': end.to_tuple(),
                                    'color': color.repr(),
                                    'timeout': timeout})

    @staticmethod
    def circle(center: Position, radius, color=LIGHT_GREEN, is_fill=True, timeout=DEFAULT_DEBUG_TIMEOUT):
        return DebugCommandFactory._circle(flip_position(center), radius, color, is_fill, timeout)

    @staticmethod
    def _circle(center: Position, radius, color=LIGHT_GREEN, is_fill=True, timeout=DEFAULT_DEBUG_TIMEOUT):
        return debug_command(3003, {'center': center.to_tuple(),
                                    'radius': radius,
                                    'color': color.repr(),
                                    'is_fill': is_fill,
                                    'timeout': timeout})

    @staticmethod
    def multiple_points(points: List[Position], color=VIOLET, width=5, link=None, timeout=DEFAULT_DEBUG_TIMEOUT):
        return debug_command(3005, {'points': [flip_position(point).to_tuple() for point in points],
                                    'color': color.repr(),
                                    'width': width,
                                    'timeout': timeout}, link=link)

    @staticmethod
    def area(area: Area, color=VIOLET):
        return list(DebugCommandFactory.line(s.p1, s.p2, color=color) for s in area.segments)

    @staticmethod
    def plot_point(y_unit: str, y_label: str, x: List[float], y: List[float]):
        """
        If the y_unit plot does not exit, the ui will create it. The ui will remember the previously send (x,y) points
        :param y_unit: Name of the plot
        :param y_label: Name of the line that will be plot on the y_unit
        :param x: list of x data to add
        :param y: list of y data to add
        """
        return debug_command(1099, {'y_unit': y_unit,
                                     'y_label': y_label,
                                     'x': x,
                                     'y': y})