# Under MIT License, see LICENSE.txt

from RULEngine.Game.Player import Player
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.team_color_service import TeamColor


class Team():
    def __init__(self, team_color):
        self.players = {}
        for player_id in range(PLAYER_PER_TEAM):
            self.players[player_id] = Player(self, player_id)
        self.team_color = team_color
        self.score = 0

    def has_player(self, player):
        has_player = False

        for team_player in self.players.values():
            if team_player is player:
                has_player = True

        return has_player

    def is_team_yellow(self):
        return self.team_color == TeamColor.YELLOW_TEAM

    def update_player(self, player_id, pose, delta=0):
        try:
            self.players[player_id].update(pose, delta)
        except KeyError as err:
            raise err
