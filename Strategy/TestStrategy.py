__author__ = 'mathieu'
import math

from Command import Command
from Strategy.Strategy import Strategy
from Util.Position import Position
import time


class TestStrategy(Strategy):
    def __init__(self, field, referee, team, opponent_team):
        super().__init__(field, referee, team, opponent_team)

    def on_start(self):
        self._send_command(Command.MoveTo(self.team.players[0], Position(100, 0, 0)))

    def on_halt(self):
        self._send_command(Command.MoveTo(self.team.players[0], Position(200, 0, 0)))

    def on_stop(self):
        self._send_command(Command.MoveTo(self.team.players[0], Position(300, 0, 0)))

