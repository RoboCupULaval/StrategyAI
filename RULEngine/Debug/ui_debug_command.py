# Under MIT License, see LICENSE.txt
__author__ = "Maxime Gagnon-Legault, and others"

STRATEGY_COMMAND_TYPE = 5002
TACTIC_COMMAND_TYPE = 5003
AUTO_PLAY_COMMAND_TYPE = 5008


class UIDebugCommand(object):

    def __init__(self, raw_cmd):
        self.data = raw_cmd['data']
        self.cmd_type = raw_cmd['type']

    def is_strategy_cmd(self):
        return self.cmd_type == STRATEGY_COMMAND_TYPE

    def is_tactic_cmd(self):
        return self.cmd_type == TACTIC_COMMAND_TYPE

    def is_auto_play_cmd(self):
        return self.cmd_type == AUTO_PLAY_COMMAND_TYPE



