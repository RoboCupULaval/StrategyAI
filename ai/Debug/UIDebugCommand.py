# Under MIT License, see LICENSE.txt

STRATEGY_COMMAND_TYPE = 5002
TACTIC_COMMAND_TYPE = 5003


class UIDebugCommand(object):

    def __init__(self, raw_cmd):
        print(raw_cmd)
        self.data = raw_cmd['data']
        self.cmd_type = raw_cmd['type']

    def is_strategy_cmd(self):
        return self.cmd_type == STRATEGY_COMMAND_TYPE

    def is_tactic_cmd(self):
        return self.cmd_type == TACTIC_COMMAND_TYPE



