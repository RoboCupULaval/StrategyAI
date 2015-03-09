from Command import Command
from Strategy.Strategy import Strategy


class WorstStrategy(Strategy):
    def __init__(self, field, referee, team, opponent_team):
        super().__init__(field, referee, team, opponent_team)

    def update(self):
        for player in self.team.players:
            command = Command.Rotate(player, 2)
            self._send_command(command)