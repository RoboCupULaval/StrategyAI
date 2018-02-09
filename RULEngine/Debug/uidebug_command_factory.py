# Under MIT License, see LICENSE.txt

from math import sin, cos
from typing import Dict

from RULEngine.services.team_color_service import TeamColorService
from Util.constant import TeamColor
from Util.position import position_to_tuple
from Util.singleton import Singleton
from ai.GameDomainObjects.player import Player

__author__ = "Maxime Gagnon-Legault, Philippe Babin, and others"


class Color(object):
    # FIXME: hack
    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    def repr(self):
        return self.r, self.g, self.b


# Solarized color definition
YELLOW = Color(181, 137, 0)
ORANGE = Color(203, 75, 22)
RED = Color(220, 50, 47)
MAGENTA = Color(211, 54, 130)
VIOLET = Color(108, 113, 196)
BLUE = Color(38, 139, 210)
CYAN = Color(42, 161, 152)
GREEN = Color(133, 153, 0)

# Alias pour les identifiants des robots
COLOR_ID0 = YELLOW
COLOR_ID1 = ORANGE
COLOR_ID2 = RED
COLOR_ID3 = MAGENTA
COLOR_ID4 = VIOLET
COLOR_ID5 = BLUE

COLOR_ID_MAP = {0: COLOR_ID0,
                1: COLOR_ID1,
                2: COLOR_ID2,
                3: COLOR_ID3,
                4: COLOR_ID4,
                5: COLOR_ID5}

DEFAULT_TEXT_SIZE = 14  # px
DEFAULT_TEXT_FONT = 'Arial'
DEFAULT_TEXT_ALIGN = 'Left'
DEFAULT_TEXT_COLOR = Color(0, 0, 0)

# Debug timeout (seconds)
DEFAULT_DEBUG_TIMEOUT = 1
DEFAULT_PATH_TIMEOUT = 0


class DebugCommand(dict):

    def __new__(cls, p_type, p_data, p_link=None, p_version="1.0"):
        command = dict()
        command['name'] = 'Engine'
        command['version'] = p_version
        command['type'] = p_type
        command['link'] = p_link
        command['data'] = p_data

        return command


class UIDebugCommandFactory(metaclass=Singleton):

    @staticmethod
    def log_cmd(level: int, message: str):
        assert isinstance(level, int)
        assert isinstance(message, str)

        return DebugCommand(2, {'level': level, 'message': message})

    # TODO make this better maybe?
    @staticmethod
    def books(cmd_tactics_dict: Dict):
        """
        of the form:
        cmd_tactics = {'strategy': strategybook.get_strategies_name_list(),
                       'tactic': tacticbook.get_tactics_name_list(),
                       'action': ['None']}
        """
        return DebugCommand(1001, cmd_tactics_dict)

    @staticmethod
    def send_robot_strategic_state(player: Player, tactic: str, action: str, target: str="not implemented"):
        teamcolor_str = player.team.team_color.__str__()
        data = {teamcolor_str: {player.id: {'tactic': tactic,
                                            'action': action,
                                            'target': target}}}
        return DebugCommand(1002, data)

    @staticmethod
    def autoplay_info(referee_info, referee_team_info, auto_play_info, auto_flag):
        return DebugCommand(1005, {'referee': referee_info,
                                   'referee_team': referee_team_info,
                                   'auto_play': auto_play_info,
                                   'auto_flag': auto_flag})

    @staticmethod
    def track_frame(track_frame):
        cmd = []
        cmd += UIDebugCommandFactory.robots(track_frame['blue'])
        cmd += UIDebugCommandFactory.robots(track_frame['yellow'])
        cmd += UIDebugCommandFactory.balls(track_frame['balls'])
        return cmd

    @staticmethod
    def robots_path(robots):
        cmds = []
        for robot in robots:
            if not robot.path or len(robot.path) < 2:
                continue
            path = [position_to_tuple(p) for p in robot.path]

            for start_point, end_point in zip(path, path[1:]):
                cmds.append(UIDebugCommandFactory.line(start_point,
                                                       end_point,
                                                       timeout=0.1))

            # MultiplePoints is weird, it has a special behavior were an unique ID link must be provided
            cmds.append(UIDebugCommandFactory.multiple_points(path[1:],
                                                              ORANGE,
                                                              width=5,
                                                              link="path - " + str(robot.robot_id),
                                                              timeout=0.0))
        return cmds

    @staticmethod
    def line(start_point, end_point, color=MAGENTA.repr(), timeout=DEFAULT_DEBUG_TIMEOUT):
        return DebugCommand(3001, {'start': (float(start_point[0]), float(start_point[1])),
                                   'end':  (float(end_point[0]), float(end_point[1])),
                                   'color': color,
                                   'timeout': timeout})
    @staticmethod
    def multiple_points(points, color=VIOLET, width=5, link=None, timeout=DEFAULT_DEBUG_TIMEOUT):
        points_as_tuple = [(int(point[0]), int(point[1])) for point in points]

        return DebugCommand(3005, {'points': points_as_tuple,
                                   'color': color.repr(),
                                   'width': width,
                                   'timeout': timeout}, p_link=link)

    @staticmethod
    def robots(robots):
        cmd = []
        for robot in robots:
            circle, line = UIDebugCommandFactory.robot(robot['pose'])
            cmd += [circle, line]
        return cmd

    @staticmethod
    def balls(balls):
        return [UIDebugCommandFactory.ball(ball['pose']) for ball in balls]

    @staticmethod
    def team_color_cmd(team_color: TeamColor = None):
        assert isinstance(team_color, TeamColor) or team_color is None

        if team_color is None:
            return DebugCommand(1004, {'team_color': TeamColorService().our_team_color.name.lower()})
        return DebugCommand(1004, {'team_color': team_color.name.lower()})

    @staticmethod
    def robot(pose: Dict, color=(0, 255, 0), color_angle=(255, 0, 0), radius=120, timeout=0.05):
        player_center = (pose['x'], pose['y'])
        data_circle = {'center': player_center,
                       'radius': radius,
                       'color': color,
                       'is_fill': True,
                       'timeout': timeout}

        end_point = (pose['x'] + radius * cos(pose['orientation']),
                     pose['y'] + radius * sin(pose['orientation']))

        return DebugCommand(3003, data_circle), UIDebugCommandFactory.line(player_center, end_point, color_angle, timeout)

    @staticmethod
    def ball(pose: dict, color=(255, 127, 80), timeout=0.05):
        data_circle = {'center': (pose['x'], pose['y']),
                       'radius': 150,
                       'color': color,
                       'is_fill': True,
                       'timeout': timeout}

        return DebugCommand(3003, data_circle)
