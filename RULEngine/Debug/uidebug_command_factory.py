# Under MIT License, see LICENSE.txt
__author__ = "Maxime Gagnon-Legault, Philippe Babin, and others"

from typing import Dict

from RULEngine.Debug.debug_command import DebugCommand
from RULEngine.GameDomainObjects.player import Player
from RULEngine.Util.constant import TeamColor
from RULEngine.Util.singleton import Singleton
from RULEngine.services.team_color_service import TeamColorService


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


class UIDebugCommandFactory(metaclass=Singleton):

    @staticmethod
    def log_cmd(level: int, message: str) -> DebugCommand:
        assert isinstance(level, int)
        assert isinstance(message, str)

        return DebugCommand(2, {'level': level, 'message': message})

    # TODO make this better maybe?
    @staticmethod
    def send_books(cmd_tactics_dict: Dict) -> DebugCommand:
        """
        of the form:
        cmd_tactics = {'strategy': strategybook.get_strategies_name_list(),
                       'tactic': tacticbook.get_tactics_name_list(),
                       'action': ['None']}
        """
        return DebugCommand(1001, cmd_tactics_dict)

    # todo finish
    @staticmethod
    def send_robot_strategic_state(player: Player, tactic: str, action: str, target: str="not implemented"):
        teamcolor_str = player.team.team_color.__str__()
        data = {teamcolor_str: {player.id: {'tactic': tactic,
                                            'action': action,
                                            'target': target}}}
        return DebugCommand(1002, data)

    # TODO see what we do with this
    # def robot_state_cmd(self, player_id: int) -> DebugCommand:
    #     data = {'blue': {player_id: {'battery_lvl': battery_lvl,
    #                                  'time_since_last_response': time_since_last_response
    #                                  }}}
    #     cmd = DebugCommand(1006, data)
    #     self.debug_state.append(cmd)

    @staticmethod
    def team_color_cmd(team_color: TeamColor = None) -> DebugCommand:
        assert isinstance(team_color, TeamColor) or team_color is None

        if team_color is None:
            return DebugCommand(1004, {'team_color': TeamColorService().our_team_color.name.lower()})

        return DebugCommand(1004, {'team_color': team_color.name.lower()})

    # TODO this method
    @staticmethod
    def play_info_cmd(referee_info, referee_team_info, auto_play_info, auto_flag):
        return DebugCommand(1005, {'referee': referee_info,
                                   'referee_team': referee_team_info,
                                   'auto_play': auto_play_info,
                                   'auto_flag': auto_flag})

    # TODO do the rest
    # def add_point_cmd(self, point: Position, color=VIOLET, width=5, link=None, timeout=DEFAULT_DEBUG_TIMEOUT):
    #     int_point = int(point[0]), int(point[1])
    #     data = {'point': int_point,
    #             'color': color.repr(),
    #             'width': width,
    #             'timeout': timeout}
    #     point = DebugCommand(3004, data, p_link=link)
    #     self.debug_state.append(point)
    #
    # def add_multiple_points(self,
    #                         points: Position,
    #                         color: Color = VIOLET,
    #                         width: int = 5,
    #                         link: int = None,
    #                         timeout: int = DEFAULT_DEBUG_TIMEOUT):
    #     assert
    #     points_as_tuple = []
    #     for point in points:
    #         points_as_tuple.append((int(point[0]), int(point[1])))
    #
    #     data = {'points': points_as_tuple,
    #             'color': color.repr(),
    #             'width': width,
    #             'timeout': timeout}
    #     point = DebugCommand(3005, data, p_link=link)
    #     self.debug_state.append(point)
    #
    # def add_circle(self, center, radius, color=CYAN.repr(), is_fill=True, timeout=DEFAULT_DEBUG_TIMEOUT):
    #     data = {'center': center,
    #             'radius': radius,
    #             'color': color,
    #             'is_fill': is_fill,
    #             'timeout': timeout}
    #     circle = DebugCommand(3003, data)
    #     self.debug_state.append(circle)
    #
    # def add_line(self, start_point, end_point, timeout=DEFAULT_DEBUG_TIMEOUT):
    #     data = {'start': start_point,
    #             'end': end_point,
    #             'color': MAGENTA.repr(),
    #             'timeout': timeout}
    #     command = DebugCommand(3001, data)
    #     self.debug_state.append(command)
    #
    # def add_vector(self, vector: Position(), start_point=Position(), timeout=DEFAULT_DEBUG_TIMEOUT):
    #
    #     end_point = start_point + vector
    #     start_point = (start_point.x, start_point.y)
    #     end_point = (end_point.x, end_point.y)
    #     data = {'start': start_point,
    #             'end': end_point,
    #             'color': CYAN.repr(),
    #             'timeout': timeout}
    #     command = DebugCommand(3001, data)
    #     self.debug_state.append(command)
    #
    # def add_rectangle(self, top_left, bottom_right):
    #     data = {'top_left': top_left,
    #             'bottom_right': bottom_right,
    #             'color': YELLOW.repr(),
    #             'is_fill': True}
    #     command = DebugCommand(3006, data)
    #     self.debug_state.append(command)
    #
    # def add_text(self, position, text, color=DEFAULT_TEXT_COLOR):
    #     data = {'position': position,
    #             'text': text,
    #             'size': DEFAULT_TEXT_SIZE,
    #             'font': DEFAULT_TEXT_FONT,
    #             'align': DEFAULT_TEXT_ALIGN,
    #             'color': color,
    #             'has_bold': False,
    #             'has_italic': False,
    #             'timeout': DEFAULT_DEBUG_TIMEOUT}
    #     text = DebugCommand(3008, data)
    #     self.debug_state.append(text)