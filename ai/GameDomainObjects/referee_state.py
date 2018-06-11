# Under MIT License, see LICENSE.txt

from enum import IntEnum
from typing import Dict

import logging

from Engine.Communication.protobuf.referee_pb2 import SSL_Referee
from Util.constant import TeamColor
from Util.position import Position
from Util.team_color_service import TeamColorService
from ai.GameDomainObjects.field import FieldSide
from config.config import Config


class RawRefereeCommand(IntEnum):
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


class RefereeCommand(IntEnum):
    HALT = 0
    STOP = 1
    NORMAL_START = 2
    FORCE_START = 3

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


class RefereeState:
    
    last_packet = None
    logger = logging.getLogger('RefereeState')
    
    def __init__(self, referee_info: Dict):
        self.command = RawRefereeCommand.STOP
        self.stage = Stage.NORMAL_FIRST_HALF_PRE
        self.stage_time_left = 0
        self.ball_placement_position = None
        self.team_info = {"ours": dict(new_team_info), "theirs": dict(new_team_info)}

        self.blue_team_is_positive = None

        self._update(referee_info)

        RefereeState.log_change(referee_info)

    @property
    def info(self) -> Dict:
        return {
            "command": self.command.name,
            "stage": self.stage.name,
            "stage_time_left": self.stage_time_left
        }

    def _update(self, referee_info: Dict) -> None:
        self.stage = Stage(referee_info["stage"])

        # TODO: Currently the only optional field that we might rely on is the time left
        # since most packet don't specify it we need a additional state to track it
        if "stage_time_left" in referee_info:
            self.stage_time_left = referee_info["stage_time_left"]

        if "blueTeamOnPositiveHalf" in referee_info:
            self.blue_team_is_positive = referee_info["blueTeamOnPositiveHalf"]

        if "designated_position" in referee_info:
            self.ball_placement_position = self._convert_vision_position_to_ai_position(
                                                    Position(referee_info["designated_position"]["x"],
                                                             referee_info["designated_position"]["y"]))

        raw_command = RawRefereeCommand(referee_info["command"])

        if "blueTeamOnPositiveHalf" in referee_info and Config()['GAME']['competition_mode']:
            self._validate_field_side(referee_info["blueTeamOnPositiveHalf"])

        self.command = self._parse_command(raw_command)
        self._parse_team_info(referee_info)

    def _parse_command(self, command: RawRefereeCommand):
        # Color wise commands
        parsed_cmd = command
        if command >= RawRefereeCommand.PREPARE_KICKOFF_YELLOW:
            if self._is_our_team_command(command):
                parsed_cmd = self._convert_raw_to_us(command)
            else:
                parsed_cmd = self._convert_raw_to_them(command)
        # Not color wise commands
        return RefereeCommand(parsed_cmd)

    def _parse_team_info(self, frame):

        if TeamColorService().our_team_color is TeamColor.YELLOW:
            self.team_info['ours'] = frame['yellow']
            self.team_info['theirs'] = frame['blue']
        else:
            self.team_info['ours'] = frame['blue']
            self.team_info['theirs'] = frame['yellow']

        # Fixme : Since referee state is state-less, we can not keep track of the time since last yellow card
        # Currently only ui-debug use it
        for team in self.team_info:
            self.team_info[team]["yellow_card_times"] = []

    @staticmethod
    def _convert_vision_position_to_ai_position(designated_position: Position):
        if Config()["GAME"]["on_negative_side"]:
            designated_position.x *= -1
        return designated_position

    @staticmethod
    def _convert_raw_to_us(command):
        if TeamColorService().our_team_color is TeamColor.YELLOW:
            return command
        else:
            return command - 1

    @staticmethod
    def _convert_raw_to_them(command):
        if TeamColorService().our_team_color is TeamColor.YELLOW:
            return command
        else:
            return command + 1

    @staticmethod
    def _is_our_team_command(command):
        return (RefereeState._is_yellow_command(command) and TeamColorService().our_team_color is TeamColor.YELLOW) or \
               (RefereeState._is_blue_command(command) and TeamColorService().our_team_color is TeamColor.BLUE)

    @staticmethod
    def _is_yellow_command(command):
        return (command % 2) == 0  # even commands are yellow commands

    @staticmethod
    def _is_blue_command(command):
        return not RefereeState._is_yellow_command(command)

    @staticmethod
    def _validate_field_side(is_blue_positive):
        truth_table = {
            True: {
                TeamColor.BLUE: FieldSide.POSITIVE,
                TeamColor.YELLOW: FieldSide.NEGATIVE
            },
            False: {
                TeamColor.BLUE: FieldSide.NEGATIVE,
                TeamColor.YELLOW: FieldSide.POSITIVE
            }
        }
        expected = truth_table[is_blue_positive][TeamColorService().our_team_color]
        current = FieldSide.NEGATIVE if Config()["GAME"]["on_negative_side"] else FieldSide.POSITIVE
        assert expected == current, \
            "The referee is expecting that team {our_team} is {expected}, but currently it's {current}, CHANGE IT!!!"\
                .format(our_team=TeamColorService().our_team_color.name,
                        expected=expected.name,
                        current=current.name)

    @classmethod
    def log_change(cls, packet: SSL_Referee):

        if cls.last_packet:
            last_team_names = [cls.last_packet['blue']['name'], cls.last_packet['yellow']['name']]
            last_stage = cls.last_packet['stage']
            last_blue_team_info = cls.last_packet['blue']
            last_yellow_team_info = cls.last_packet['yellow']
        else:
            last_team_names = None
            last_stage = None
            last_blue_team_info = {'score': 0, 'red_cards': 0, 'yellow_cards': 0, 'timeouts': 4}
            last_yellow_team_info = {'score': 0, 'red_cards': 0, 'yellow_cards': 0, 'timeouts': 4}

        cls.last_packet = packet

        new_team_names = [packet['blue']['name'], packet['yellow']['name']]
        new_blue_team_info = packet['blue']
        new_yellow_team_info = packet['yellow']
        new_stage = packet['stage']

        is_name_change = last_team_names != new_team_names
        is_state_change = last_stage != new_stage

        scoring_team = {'blue': None, 'yellow': None}
        score_change = {'blue': 0, 'yellow': 0}
        if last_blue_team_info['score'] != new_blue_team_info['score']:
            scoring_team['blue'] = new_blue_team_info['name']
            score_change['blue'] = new_blue_team_info['score'] - last_blue_team_info['score']
        if last_yellow_team_info['score'] != new_yellow_team_info['score']:
            scoring_team['yellow'] = new_yellow_team_info['name']
            score_change['yellow'] = new_yellow_team_info['score'] - last_yellow_team_info['score']

        red_card_team = {'blue': None, 'yellow': None}
        red_card_change = {'blue': 0, 'yellow': 0}
        if last_blue_team_info['red_cards'] != new_blue_team_info['red_cards']:
            red_card_team['blue'] = new_blue_team_info['name']
            red_card_change['blue'] = new_blue_team_info['red_cards'] - last_blue_team_info['red_cards']
        if last_yellow_team_info['red_cards'] != new_yellow_team_info['red_cards']:
            red_card_team['yellow'] = new_yellow_team_info['name']
            red_card_change['yellow'] = new_yellow_team_info['red_cards'] - last_yellow_team_info['red_cards']

        yellow_card_team = {'blue': None, 'yellow': None}
        yellow_card_change = {'blue': 0, 'yellow': 0}
        if last_blue_team_info['yellow_cards'] != new_blue_team_info['yellow_cards']:
            yellow_card_team['blue'] = new_blue_team_info['name']
            yellow_card_change['blue'] = new_blue_team_info['yellow_cards'] - last_blue_team_info['yellow_cards']
        if last_yellow_team_info['yellow_cards'] != new_yellow_team_info['yellow_cards']:
            yellow_card_team['yellow'] = new_yellow_team_info['name']
            yellow_card_change['yellow'] = new_yellow_team_info['yellow_cards'] - last_yellow_team_info['yellow_cards']

        timeout_team = {'blue': None, 'yellow': None}
        timeout_time = {'blue': 0, 'yellow': 0}
        timeout_left = {'blue': 0, 'yellow': 0}
        timeout_change = {'blue': 0, 'yellow': 0}
        if last_blue_team_info['timeouts'] != new_blue_team_info['timeouts']:
            timeout_team['blue'] = new_blue_team_info['name']
            timeout_time['blue'] = new_blue_team_info['timeout_time']
            timeout_left['blue'] = new_blue_team_info['timeouts']
            timeout_change['blue'] = new_blue_team_info['timeouts'] - last_blue_team_info['timeouts']
        if last_yellow_team_info['timeouts'] != new_yellow_team_info['timeouts']:
            timeout_team['yellow'] = new_yellow_team_info['name']
            timeout_time['yellow'] = new_yellow_team_info['timeout_time']
            timeout_left['yellow'] = new_yellow_team_info['timeouts']
            timeout_change['yellow'] = new_yellow_team_info['timeouts'] - new_yellow_team_info['timeouts']

        if is_name_change:
            new_team_names[0] = 'unknown' if new_team_names[0] == '' else new_team_names[0]
            new_team_names[1] = 'unknown' if new_team_names[1] == '' else new_team_names[1]

            cls.logger.info('Team change detected.\n\n' + '-' * 40 + '\n' +
                             '  {} (BLUE) vs. {} (YELLOW)'.format(*new_team_names) + '\n' + '-' * 40 + '\n\n')

        if is_state_change:
            stage = Stage(new_stage)
            cls.logger.info('Stage change detected. Now at {}.'.format(stage.name))
            if stage is Stage.NORMAL_FIRST_HALF:
                cls.logger.info('A new game is starting!')
            elif stage is Stage.POST_GAME:
                cls.logger.info('The game has ended. Final score: ({}: {} - {}: {})'.format(new_blue_team_info['name'],
                                                                                            new_blue_team_info['score'],
                                                                                            new_yellow_team_info['name'],
                                                                                            new_yellow_team_info['score']))

        for team_color in ('blue', 'yellow'):
            if scoring_team[team_color] is not None:
                if score_change[team_color] == 1:
                    cls.logger.info('A goal was score by {}'.format(scoring_team[team_color]))
                elif score_change[team_color] > 1:
                    cls.logger.info('{} goals were score by {}.'.format(score_change[team_color], scoring_team[team_color]))
                else:
                    cls.logger.info('A goal was remove to {}'.format(scoring_team[team_color]))

                cls.logger.info('Current score: ({}: {} - {}: {})'.format(new_blue_team_info['name'],
                                                                      new_blue_team_info['score'],
                                                                      new_yellow_team_info['name'],
                                                                      new_yellow_team_info['score']))

            if red_card_team[team_color] is not None:
                if red_card_change[team_color] == 1:
                    cls.logger.info('A red card was taken by {}.'.format(red_card_team[team_color]))
                elif red_card_change[team_color] > 1:
                    cls.logger.info('{} red cards were taken by {}.'.format(red_card_change[team_color], red_card_team[team_color]))
                else:
                    cls.logger.info('A red card was remove to {}'.format(red_card_team[team_color]))

            if yellow_card_team[team_color] is not None:
                if yellow_card_change[team_color] == 1:
                    cls.logger.info('A yellow card was taken by {}.'.format(yellow_card_team[team_color]))
                elif yellow_card_change[team_color] > 1:
                    cls.logger.info('{} yellow cards were taken by {}.'.format(yellow_card_change[team_color], yellow_card_team[team_color]))
                else:
                    cls.logger.info('A yellow card was remove to {}'.format(yellow_card_team[team_color]))

            if timeout_team[team_color] is not None:
                if timeout_change[team_color] == -1:
                    cls.logger.info('A timeout was ask by {}.'.format(timeout_team[team_color]))
                elif timeout_change[team_color] < -1:
                    cls.logger.info('{} timeout calls were given to {}'.format(timeout_change[team_color], timeout_team[team_color]))
                else:
                    cls.logger.info('A timeout call was given to {}'.format(timeout_team[team_color]))
                cls.logger.info('Timeout left: {}. Time left: {:.1f} seconds'.format(timeout_left[team_color],
                                                                                      timeout_time[team_color]/1000000))
