
from ai.managers.PlayManager import STAStatus
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.STA.Tactic.tactic_constants import DEFAULT_TIME_TO_LIVE
from ai.Debug.UIDebugCommand import UIDebugCommand
from ai.Debug.DebugCommand import DebugCommand


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


class DebugManager:

    def __init__(self, p_gamestatemanager, p_playmanager):
        self.GameStateManager = p_gamestatemanager
        self.PlayManager = p_playmanager

        self.commands = []
        self.ui_commands = []
        self.human_control = False
        self.tactic_control = False

        self._send_books()

    def _send_commands(self):
        packet_represented_commands = [c.get_packet_repr() for c in self.commands]
        self.commands.clear()
        return packet_represented_commands

    def add_log(self, level, message):
        log = DebugCommand(2, {'level': level, 'message': message})
        self.commands.append(log)

    def add_point(self, point, color=VIOLET, width=5, link=None, timeout=DEFAULT_DEBUG_TIMEOUT):
        int_point = int(point[0]), int(point[1])
        data = {'point': int_point,
                'color': color.repr(),
                'width': width,
                'timeout': timeout}
        point = DebugCommand(3004, data, p_link=link)
        self.commands.append(point)

    def add_multiple_points(self, points, color=VIOLET, width=5, link=None, timeout=DEFAULT_DEBUG_TIMEOUT):
        points_as_tuple = []
        for point in points:
            points_as_tuple.append((int(point[0]), int(point[1])))

        data = {'points': points_as_tuple,
                'color': color.repr(),
                'width': width,
                'timeout': timeout}
        point = DebugCommand(3005, data, p_link=link)
        self.commands.append(point)

    def add_circle(self, center, radius):
        data = {'center': center,
                'radius': radius,
                'color': CYAN.repr(),
                'is_fill': True,
                'timeout': 0}
        circle = DebugCommand(3003, data)
        self.commands.append(circle)

    def add_line(self, start_point, end_point, timeout=DEFAULT_DEBUG_TIMEOUT):
        data = {'start': start_point,
                'end': end_point,
                'color': MAGENTA.repr(),
                'timeout': timeout}
        command = DebugCommand(3001, data)
        self.commands.append(command)

    def add_rectangle(self, top_left, bottom_right):
        data = {'top_left': top_left,
                'bottom_right': bottom_right,
                'color': YELLOW.repr(),
                'is_fill': True}
        command = DebugCommand(3006, data)
        self.commands.append(command)

    def add_influence_map(self, influence_map):

        data = {'field_data': influence_map,
                'coldest_numb': -100,
                'hottest_numb': 100,
                'coldest_color': (0, 255, 0),
                'hottest_color': (255, 0, 0),
                'timeout': 2}
        command = DebugCommand(3007, data)
        self.commands.append(command)

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
        self.commands.append(text)

    def update(self):
        self._update_incomming_debug_command()

        self._execute_incomming_debug_command()

        self.GameStateManager.debug_information_in.clear()

        return self._send_commands()

    # todo see if that goes here could go in RobotCommandManager!
    def _send_books(self):
        cmd_tactics = {'strategy': self.PlayManager.strategybook.get_strategies_name_list(),
                       'tactic': self.PlayManager.tacticbook.get_tactics_name_list(),
                       'action': ['None']}
        cmd = DebugCommand(1001, cmd_tactics)
        self.commands.append(cmd)

    def _update_incomming_debug_command(self):
        # make sure gamestate debug send nothing if they is no ui debug command

        for command in self.GameStateManager.debug_information_in:
            print(command)
            self.ui_commands.append(UIDebugCommand(command))

        if self.ui_commands:
            self.human_control = True

    def _execute_incomming_debug_command(self):
        if self.human_control:
            for command in self.ui_commands:
                self._parse_command(command)

    def _parse_command(self, cmd):
        if cmd.is_strategy_cmd():
            self.PlayManager.set_strategy_status(STAStatus.LOCKED)
            self.PlayManager.set_all_tactic_status(STAStatus.FREE)
            self._parse_strategy(cmd)

        elif cmd.is_tactic_cmd():
            self._parse_tactic(cmd)
        else:
            pass

    def _parse_strategy(self, cmd):
        # TODO revise this function please, thank you!
        strategy_key = cmd.data['strategy']
        if strategy_key == 'pStop':
            self.PlayManager.set_strategy(self.PlayManager.get_new_strategy("DoNothing")(self.GameStateManager,
                                                                                         self.PlayManager))
        else:
            self.PlayManager.set_strategy(self.PlayManager.get_new_strategy(strategy_key)(self.GameStateManager,
                                                                                          self.PlayManager))

    def _parse_tactic(self, cmd):
        # TODO make implementation for other tactic packets! And finish this please
        pid = self._sanitize_pid(cmd.data['id'])
        self.PlayManager.set_tactic_status(pid, STAStatus.LOCKED)

        tactic_name = cmd.data['tactic']
        target = cmd.data['target']
        target = Pose(Position(target[0], target[1]))
        tactic = self.PlayManager.get_new_tactic(tactic_name)(self.GameStateManager, self.PlayManager, pid,
                                                              target=target, time_to_live=DEFAULT_TIME_TO_LIVE)
        self.PlayManager.set_tactic(pid, tactic)
        self.PlayManager.set_tactic_status(pid, STAStatus.LOCKED)

    @staticmethod
    def _sanitize_pid(pid):
        # TODO find something better for this whole scheme
        if 0 <= pid < 6:
            return pid
        elif 6 <= pid < 12:
            return pid - 6
        else:
            return 0


