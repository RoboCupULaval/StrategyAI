# Under MIT License, see LICENSE.txt

from math import sin, cos
from typing import Dict, Tuple, List

from Engine.robot import Robot
from Util import Pose, Position
from Util.path import Path
from ai.GameDomainObjects.player import Player

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

DEFAULT_DEBUG_TIMEOUT = 1.0


class DebugCommand:

    def __new__(cls, data_type, data, link=None, version='1.0'):
        command = dict()
        command['name'] = 'StrategyAI'
        command['version'] = version
        command['type'] = data_type
        command['link'] = link
        command['data'] = data

        return command


class DebugCommandFactory:

    @staticmethod
    def log(level: int, message: str):
        if not isinstance(level, int):
            raise TypeError('Level need to be an int. Type {} given'.format(type(level)))
        if not isinstance(message, str):
            raise TypeError('Message need to be an string. Type {} given'.format(type(message)))

        return DebugCommand(2, {'level': level, 'message': message})

    @staticmethod
    def books(strategy_book: Dict, strategy_default: Dict, tactic_book: Dict, tactic_default: Dict, action: List):
        return DebugCommand(1001, {'strategy': strategy_book,
                                     'strategy_default': strategy_default,
                                     'tactic': tactic_book,
                                     'tactic_default': tactic_default,
                                     'action': action})

    @staticmethod
    def robot_strategic_state(player: Player, tactic: str, action: str, target: Tuple[int, int]):
        team_color = str(player.team.team_color)
        player_info = {player.id: {'tactic': tactic, 'action': action, 'target': target, 'role'}}
        team_info = {team_color: player_info}
        return DebugCommand(1002, team_info)

    @staticmethod
    def auto_play_info(referee_info: str, referee_team_info: Dict, auto_play_info: Dict, auto_flag: bool):
        return DebugCommand(1005, {'referee': referee_info,
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
                raw_path_cmds += DebugCommandFactory.path(robot.raw_path, robot.robot_id, color=BLUE)
            if robot.path:
                path_cmds += DebugCommandFactory.path(robot.path, robot.robot_id, color=RED)
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
            cmds += DebugCommandFactory.ball(ball['position'])
        return cmds

    @staticmethod
    def path(path: Path, path_id: int, color=BLUE):
        cmds = [DebugCommandFactory.line(start, end, color=color, timeout=0.1) for start, end in zip(path, path[1:])]
        cmds += [DebugCommandFactory.multiple_points(path[1:], color=color, link=str(path_id), timeout=0)]
        return cmds

    @staticmethod
    def robot(pose: Pose, color=LIGHT_GREEN, color_angle=RED, radius=120, timeout=0.05):
        cmd = [DebugCommandFactory.circle(pose.position, radius, color=color, timeout=timeout)]
        start = pose.position
        end = start + Position(radius * cos(pose.orientation), radius * sin(pose.orientation))
        cmd += [DebugCommandFactory.line(start, end, color_angle, timeout)]

        return cmd

    @staticmethod
    def ball(position: Position, color=ORANGE, timeout=0.05):
        return [DebugCommandFactory.circle(position, 150, color=color, timeout=timeout)]


    @staticmethod
    def line(start: Position, end: Position, color=MAGENTA, timeout=DEFAULT_DEBUG_TIMEOUT):
        return DebugCommand(3001, {'start': start.to_tuple(),
                                   'end': end.to_tuple(),
                                   'color': color.repr(),
                                   'timeout': timeout})


    @staticmethod
    def circle(center: Position, radius, color=LIGHT_GREEN, is_fill=True, timeout=DEFAULT_DEBUG_TIMEOUT):
        return DebugCommand(3003, {'center': center.to_tuple(),
                                   'radius': radius,
                                   'color': color.repr(),
                                   'is_fill': is_fill,
                                   'timeout': timeout})


    @staticmethod
    def multiple_points(points: List[Position], color=VIOLET, width=5, link=None, timeout=DEFAULT_DEBUG_TIMEOUT):
        return DebugCommand(3005, {'points': [point.to_tuple() for point in points],
                                   'color': color.repr(),
                                   'width': width,
                                   'timeout': timeout}, link=link)