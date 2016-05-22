#Under MIT License, see LICENSE.txt
from abc import abstractmethod
from abc import ABCMeta


class Strategy(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, field, referee, team, opponent_team):
        self.field = field
        self.referee = referee
        self.team = team
        self.opponent_team = opponent_team
        self.commands = []

    @abstractmethod
    def on_start(self):
        pass

    @abstractmethod
    def on_halt(self):
        pass

    @abstractmethod
    def on_stop(self):
        pass

    def _send_command(self, command):
        self.commands.append(command)

    def _get_ball(self):
        return self.field.ball