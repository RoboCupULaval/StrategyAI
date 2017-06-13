# Under MIT License, see LICENSE.txt
import time

from RULEngine.Debug.debug_command import DebugCommand
from RULEngine.Util.singleton import Singleton
from RULEngine.Game.OurPlayer import OurPlayer
from config.config_service import ConfigService


class Color(object):
    # FIXME: hack
    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    def repr(self):
        return (self.r, self.g, self.b)

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


def wrap_command(raw_command):
    command = DebugCommand(raw_command['type'], raw_command['link'], raw_command['data'])
    command.name = 'ui'
    return command


class DebugInterface(metaclass=Singleton):

    def __init__(self):
        self.debug_state = []
        self.team_color = str(ConfigService().config_dict["GAME"]["our_color"])
        self.send_team_color()

    def add_log(self, level, message):
        log = DebugCommand(2, {'level': level, 'message': message})
        self.debug_state.append(log)

    def add_point(self, point, color=VIOLET, width=5, link=None, timeout=DEFAULT_DEBUG_TIMEOUT):
        int_point = int(point[0]), int(point[1])
        data = {'point': int_point,
                'color': color.repr(),
                'width': width,
                'timeout': timeout}
        point = DebugCommand(3004, data, p_link=link)
        self.debug_state.append(point)

    def add_multiple_points(self, points, color=VIOLET, width=5, link=None, timeout=DEFAULT_DEBUG_TIMEOUT):
        points_as_tuple = []
        for point in points:
            points_as_tuple.append((int(point[0]), int(point[1])))

        data = {'points': points_as_tuple,
                'color': color.repr(),
                'width': width,
                'timeout': timeout}
        point = DebugCommand(3005, data, p_link=link)
        self.debug_state.append(point)

    def add_circle(self, center, radius):
        data = {'center': center,
                'radius': radius,
                'color': CYAN.repr(),
                'is_fill': True,
                'timeout': 0}
        circle = DebugCommand(3003, data)
        self.debug_state.append(circle)

    def add_line(self, start_point, end_point, timeout=DEFAULT_DEBUG_TIMEOUT):
        data = {'start': start_point,
                'end': end_point,
                'color': MAGENTA.repr(),
                'timeout': timeout}
        command = DebugCommand(3001, data)
        self.debug_state.append(command)

    def add_rectangle(self, top_left, bottom_right):
        data = {'top_left': top_left,
                'bottom_right': bottom_right,
                'color': YELLOW.repr(),
                'is_fill': True}
        command = DebugCommand(3006, data)
        self.debug_state.append(command)

    def add_influence_map(self, influence_map):

        data = {'field_data': influence_map,
                'coldest_numb': -100,
                'hottest_numb': 100,
                'coldest_color': (0, 255, 0),
                'hottest_color': (255, 0, 0),
                'timeout': 2}
        command = DebugCommand(3007, data)
        self.debug_state.append(command)

    def add_text(self, position, text, color=DEFAULT_TEXT_COLOR):
        data = {'position': position,
                'text': text,
                'size': DEFAULT_TEXT_SIZE,
                'font': DEFAULT_TEXT_FONT,
                'align': DEFAULT_TEXT_ALIGN,
                'color': color,
                'has_bold': False,
                'has_italic': False,
                'timeout': DEFAULT_DEBUG_TIMEOUT}
        text = DebugCommand(3008, data)
        self.debug_state.append(text)

    # todo see if that goes here could go in RobotCommandManager!
    def send_books(self, cmd_tactics_dict):
        """
        of the form:
        cmd_tactics = {'strategy': strategybook.get_strategies_name_list(),
                       'tactic': tacticbook.get_tactics_name_list(),
                       'action': ['None']}
        """
        cmd = DebugCommand(1001, cmd_tactics_dict)
        self.debug_state.append(cmd)

    def send_robot_strategic_state(self, player: OurPlayer, tactic, action, target="not implemented"):
        teamcolor_str = player.team.team_color.__str__()
        data = {teamcolor_str: {player.id: {'tactic': tactic,
                                            'action': action,
                                            'target': target}}}
        cmd = DebugCommand(1002, data)
        self.debug_state.append(cmd)

    def send_robot_state(self, player_id, battery_volt, time_last_response):
        MAX_BAT = 16.4
        MIN_BAT = 12.0
        battery_lvl = (battery_volt - MIN_BAT) / (MAX_BAT - MIN_BAT) * 100
        time_since_last_response = time.time() - time_last_response
        if time_since_last_response > 5.0:
            battery_lvl = 0
        data = {'blue': {player_id: {'battery_lvl': battery_lvl,
                                     'time_since_last_response': time_since_last_response
                                     }}}
        cmd = DebugCommand(1006, data)
        self.debug_state.append(cmd)

    def send_team_color(self):
        cmd = DebugCommand(1004, {'team_color': self.team_color})
        self.debug_state.append(cmd)

    def send_play_info(self, referee_info, referee_team_info, auto_play_info, auto_flag):
        cmd = DebugCommand(1005, {'referee': referee_info,
                                  'referee_team': referee_team_info,
                                  'auto_play': auto_play_info,
                                  'auto_flag': auto_flag})
        self.debug_state.append(cmd)

