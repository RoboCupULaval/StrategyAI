# Under MIT License, see LICENSE.txt

from enum import IntEnum

from config.config_service import ConfigService


class RefereeCommand(IntEnum):
    HALT = 0
    STOP = 1
    NORMAL_START = 2
    FORCE_START = 3

    #raw commands
    PREPARE_KICKOFF_YELLOW = 4
    PREPARE_KICKOFF_BLUE = 5
    PREPARE_PENALTY_YELLOW = 6
    PREPARE_PENALTY_BLUE = 7
    DIRECT_FREE_YELLOW = 8
    DIRECT_FREE_BLUE = 9
    INDIRECT_FREE_YELLOW = 10
    INDIRECT_FREE_BLUE = 11
    TIMEOUT_YELLOW = 12
    TIMEOUT_BLUE = 13
    GOAL_YELLOW = 14
    GOAL_BLUE = 15
    BALL_PLACEMENT_YELLOW = 16
    BALL_PLACEMENT_BLUE = 17

    #internal commands
    PREPARE_KICKOFF_US = 34
    PREPARE_KICKOFF_THEM = 35
    PREPARE_PENALTY_US = 36
    PREPARE_PENALTY_THEM = 37
    DIRECT_FREE_US = 38
    DIRECT_FREE_THEM = 39
    INDIRECT_FREE_US = 40
    INDIRECT_FREE_THEM = 41
    TIMEOUT_US = 42
    TIMEOUT_THEM = 43
    GOAL_US = 44
    GOAL_THEM = 45
    BALL_PLACEMENT_US = 46
    BALL_PLACEMENT_THEM = 47


class Stage(IntEnum):
    NORMAL_FIRST_HALF_PRE = 0
    NORMAL_FIRST_HALF = 1
    NORMAL_HALF_TIME = 2
    NORMAL_SECOND_HALF_PRE = 3
    NORMAL_SECOND_HALF = 4
    EXTRA_TIME_BREAK = 5
    EXTRA_FIRST_HALF_PRE = 6
    EXTRA_FIRST_HALF = 7
    EXTRA_HALF_TIME = 8
    EXTRA_SECOND_HALF_PRE = 9
    EXTRA_SECOND_HALF = 10
    PENALTY_SHOOTOUT_BREAK = 11
    PENALTY_SHOOTOUT = 12
    POST_GAME = 13


class Referee:
    def __init__(self):
        self.command = RefereeCommand.STOP
        self.prepare_command = None
        self.stage = Stage.NORMAL_FIRST_HALF_PRE
        self.ball_placement_point = (0,0)
        self.our_color = ConfigService().config_dict["GAME"]["our_color"]

    def update(self, frames):
        if frames != []:
            self.stage = frames[-1].stage
            raw_command = frames[-1].command
            self.command = self._parse_command(raw_command)
            if self.command == RefereeCommand.BALL_PLACEMENT_US or self.command == RefereeCommand.BALL_PLACEMENT_THEM:
                self.ball_placement_point = (frames[-1].point.x, frames[-1].point.y)

    def _parse_command(self, command):
        # Color wise commands
        if command >= RefereeCommand.PREPARE_KICKOFF_YELLOW:
            if self._is_our_team_command(command):
                return self._convert_raw_to_us(command)
            else:
                return self._convert_raw_to_them(command)
        # None color wise commands
        else:
            return command

    def _convert_raw_to_us(self, command):
        if self.our_color == 'yellow':
            return command + 30
        else:
            return command + 29

    def _convert_raw_to_them(self, command):
        if self.our_color == 'yellow':
            return command + 30
        else:
            return command + 31

    def _is_our_team_command(self, command):
        return (self._is_yellow_command(command) and self.our_color == 'yellow') or\
                (self._is_blue_command(command) and self.our_color == 'blue')

    def _is_yellow_command(self, command):
        return (command % 2) == 0 # even commands are yellow commands

    def _is_blue_command(self, command):
        return not self._is_yellow_command(command)