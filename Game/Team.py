# Under MIT License, see LICENSE.txt

from .Player import Player
from ..Util.constant import PLAYER_PER_TEAM


class Team():
    def __init__(self, is_team_yellow):
        self.players = [Player(self, i) for i in range(PLAYER_PER_TEAM)]
        self.is_team_yellow = is_team_yellow
        self.score = 0

    def has_player(self, player):
        has_player = False

        for team_player in self.players:
            if team_player == player:
                has_player = True

        return has_player

    def move_and_rotate_player(self, player_id, pose):
        for player in self.players:
            if player.has_id(player_id):
                player.pose = pose
