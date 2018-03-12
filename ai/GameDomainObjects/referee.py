# Under MIT License, see LICENSE.txt

from enum import IntEnum
from typing import Dict

from Util.constant import TeamColor
from Util.position import Position
from Util.team_color_service import TeamColorService


class RefereeCommand(IntEnum):
    HALT = 0
    STOP = 1
    NORMAL_START = 2
    FORCE_START = 3

    # raw commands
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


class InternalRefereeCommand(IntEnum):
    PREPARE_KICKOFF_US = 4
    PREPARE_KICKOFF_THEM = 5
    PREPARE_PENALTY_US = 6
    PREPARE_PENALTY_THEM = 7
    DIRECT_FREE_US = 8
    DIRECT_FREE_THEM = 9
    INDIRECT_FREE_US = 10
    INDIRECT_FREE_THEM = 11
    TIMEOUT_US = 12
    TIMEOUT_THEM = 13
    GOAL_US = 14
    GOAL_THEM = 15
    BALL_PLACEMENT_US = 16
    BALL_PLACEMENT_THEM = 17


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


new_team_info = {"name": "",
                 "score": 0,
                 "red_cards": 0,
                 "yellow_cards": 0,
                 "yellow_card_times": [],
                 "timeouts": 4,
                 "timeout_time": 0,
                 "goalie": 0}


class Referee:

    def __init__(self):
        self.command = RefereeCommand.STOP
        self.stage = Stage.NORMAL_FIRST_HALF_PRE
        self.stage_time_left = 0
        self.ball_placement_point = Position()
        self.team_info = {"ours": dict(new_team_info), "theirs": dict(new_team_info)}

    @property
    def info(self) -> str:
        return "command {}\nstage {}\nstage_time_left {}".format(str(self.command),
                                                                 str(self.stage),
                                                                 self.stage_time_left)

    def update(self, referee_info: Dict) -> None:

        self.stage = Stage(referee_info["stage"])
        self.stage_time_left = referee_info["stage_time_left"]

        raw_command = RefereeCommand(referee_info["command"])
        self.command = self._parse_command(raw_command)
        if self.command == RefereeCommand.BALL_PLACEMENT_US or self.command == RefereeCommand.BALL_PLACEMENT_THEM:
            self.ball_placement_point = (referee_info["point"]["x"], referee_info["point"]["y"])

        self._parse_team_info(referee_info)

    def _parse_command(self, command: RefereeCommand):
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
        if TeamColorService().our_team_color is TeamColor.YELLOW:
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

    # def _convert_raw_to_us(self, command):
    #     if TeamColorService().OUR_TEAM_COLOR is TeamColor.YELLOW:
    #         return command + 30
    #     else:
    #         return command + 29
    #
    # def _convert_raw_to_them(self, command):
    #     if TeamColorService().OUR_TEAM_COLOR is TeamColor.YELLOW:
    #         return command + 30
    #     else:
    #         return command + 31

    # def _is_our_team_command(self, command):
    #     return (self._is_yellow_command(command) and TeamColorService().OUR_TEAM_COLOR is TeamColor.YELLOW) or\
    #             (self._is_blue_command(command) and TeamColorService().OUR_TEAM_COLOR is TeamColor.BLUE)
    #
    # def _is_yellow_command(self, command):
    #     return (command % 2) == 0 # even commands are yellow commands
    #
    # def _is_blue_command(self, command):
    #     return not self._is_yellow_command(command)
