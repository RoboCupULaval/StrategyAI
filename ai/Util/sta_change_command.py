# Under MIT License, see LICENSE.txt
from enum import Enum
from typing import Dict

__author__ = "Maxime Gagnon-Legault"

STRATEGY_COMMAND_TYPE = 5002
TACTIC_COMMAND_TYPE = 5003
AUTO_PLAY_COMMAND_TYPE = 5008


class STAType(Enum):
    NONE = 0
    STRATEGY = 1
    TACTIC = 2
    ACTION = 3
    AUTONOMOUS_PLAY = 4


class STAChangeCommand:
    def __init__(self, cmd: Dict):
        self._type = self._parse_cmd_type(cmd)
        self.data = cmd["data"]

    @property
    def type(self):
        return self._type

    def is_valid_cmd(self):
        return self.type != STAType.NONE

    @staticmethod
    def _parse_cmd_type(cmd: Dict):
        type_str = cmd["type"]
        if type_str == STRATEGY_COMMAND_TYPE:
            return STAType.STRATEGY
        elif type_str == TACTIC_COMMAND_TYPE:
            return STAType.TACTIC
        elif type_str == AUTO_PLAY_COMMAND_TYPE:
            return STAType.AUTONOMOUS_PLAY
        else:
            return STAType.NONE

    def is_tactic_change_command(self):
        return self.type == STAType.TACTIC

    def is_strategy_change_command(self):
        return self.type == STAType.STRATEGY