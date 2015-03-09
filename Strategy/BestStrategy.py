import math

from Command import Command
from Strategy.Strategy import Strategy
from Util.Position import Position


class BestStrategy(Strategy):
    def __init__(self, field, referee, team, opponent_team):
        super().__init__(field, referee, team, opponent_team)

    def update(self):
        for player in self.team.players:
            x = 1000 - player.pose.position.x
            y = 1000 - player.pose.position.y

            move_x = x / math.sqrt(x * x + y * y)
            move_y = y / math.sqrt(x * x + y * y)

            position = Position(move_x, move_y)

            self._send_command(Command.MoveTo(player, position))