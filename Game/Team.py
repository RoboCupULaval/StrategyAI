# Under MIT License, see LICENSE.txt

from .Player import Player
from ..Util.constant import PLAYER_PER_TEAM


class Team():
    def __init__(self, is_team_yellow):
        self.players = {}
        for player_id in range(PLAYER_PER_TEAM):
            self.players[player_id] = Player(self, player_id)
        self.is_team_yellow = is_team_yellow
        self.score = 0

    def has_player(self, player):
        has_player = False

        for team_player in self.players.values():
            if team_player is player:
                has_player = True

        return has_player

    def move_and_rotate_player(self, player_id, pose):
        try:
            self.players[player_id].pose = pose
        except KeyError as err:
            raise err
