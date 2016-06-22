#Under MIT License, see LICENSE.txt
from abc import abstractmethod
from abc import ABCMeta


class Strategy(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, is_team_yellow):
        self.is_team_yellow = is_team_yellow
        self.commands = []

    @abstractmethod
    def on_start(self, game_state):
        pass

    @abstractmethod
    def on_halt(self, game_state):
        pass

    @abstractmethod
    def on_stop(self, game_state):
        pass

    def send_command(self, command):
        self.commands.append(command)

    def _get_ball(self):
        return self.field.ball
