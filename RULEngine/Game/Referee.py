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
        self.stage_time_left = 0
        self.ball_placement_point = (0,0)
        self.our_color = ConfigService().config_dict["GAME"]["our_color"]
        self.team_info = {"ours": {
                            "name": "",
                            "score": 0,
                            "red_cards": 0,
                            "yellow_cards": 0,
                            "yellow_card_times": [],
                            "timeouts": 4,
                            "timeout_time": 0,
                            "goalie": 0
                        },
                        "theirs": {
                            "name": "",
                            "score": 0,
                            "red_cards": 0,
                            "yellow_cards": 0,
                            "yellow_card_times": [],
                            "timeouts": 4,
                            "timeout_time": 0,
                            "goalie": 0
                        }}

    @property
    def info(self):
        return  {
            "command": str(self.command),
            "stage": str(self.stage),
            "stage_time_left": self.stage_time_left
        }

    def update(self, frames):
        if frames != []:
            self.stage = Stage(frames[-1].stage)
            self.stage_time_left = frames[-1].stage_time_left

            raw_command = RefereeCommand(frames[-1].command)
            self.command = self._parse_command(raw_command)
            if self.command == RefereeCommand.BALL_PLACEMENT_US or self.command == RefereeCommand.BALL_PLACEMENT_THEM:
                self.ball_placement_point = (frames[-1].point.x, frames[-1].point.y)

            self._parse_team_info(frames[-1])

    def _parse_command(self, command):
        # Color wise commands
        parsed_cmd = command
        if command >= RefereeCommand.PREPARE_KICKOFF_YELLOW:
            if self._is_our_team_command(command):
                parsed_cmd = self._convert_raw_to_us(command)
            else:
                parsed_cmd = self._convert_raw_to_them(command)
        # None color wise commands
        return RefereeCommand(parsed_cmd)

    def _parse_team_info(self, frame):
        info = {}
        if self.our_color == 'yellow':
            info['ours'] = frame.yellow
            info['theirs'] = frame.blue
        else:
            info['ours']  = frame.blue
            info['theirs'] = frame.yellow

        for key in info.keys():
            self.team_info[key]['name'] = info[key].name
            self.team_info[key]['score'] = info[key].score
            self.team_info[key]['red_cards'] = info[key].red_cards
            self.team_info[key]['yellow_cards'] = info[key].yellow_cards
            self.team_info[key]['yellow_card_times'].clear()
            for time in info[key].yellow_card_times:
                self.team_info[key]['yellow_card_times'].append(time)
            self.team_info[key]['timeouts'] = info[key].timeouts
            self.team_info[key]['timeout_time'] = info[key].timeout_time
            self.team_info[key]['goalie'] = info[key].goalie

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