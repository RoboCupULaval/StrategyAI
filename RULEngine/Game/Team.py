# Under MIT License, see LICENSE.txt
import time

from RULEngine.Game.Player import Player
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.team_color_service import TeamColor
from config.config_service import ConfigService

# todo Change this constant place
MIN_TIME_BEFORE_MOVING_OUT = 2


class Team:
    def __init__(self, team_color: TeamColor):
        assert isinstance(team_color, TeamColor)
        self.team_color = team_color
        self.score = 0

        self.players = {}
        self.available_players = {}
        self.players_time_tracker = {}
        for player_id in range(PLAYER_PER_TEAM):
            self.players[player_id] = Player(self, player_id)
            if player_id < 6:
                self.players[player_id].in_play = True
                self.available_players[player_id] = self.players[player_id]

        self.update_player = self._update_player
        if ConfigService().config_dict["IMAGE"]["kalman"] == "true":
            self.update_player = self._kalman_update

    def has_player(self, player):
        has_player = False

        for team_player in self.players.values():
            if team_player is player:
                has_player = True

        return has_player

    def is_team_yellow(self):
        return self.team_color == TeamColor.YELLOW

    def update_available_players(self):
        for player_id, time_last_seen in self.players_time_tracker.items():
            if time.time() - time_last_seen > MIN_TIME_BEFORE_MOVING_OUT:
                del(self.available_players[player_id])

    def _update_player(self, player_id, pose, delta=0):
        try:
            self.players[player_id].update(pose, delta)
            self.players_time_tracker[player_id] = time.time()
            self.available_players[player_id] = self.players[player_id]
        except KeyError as err:
            raise err

    def _kalman_update(self, player_id, pose_list, delta=0):
        try:
            print(player_id, "  ->  ",pose_list)
            self.players[player_id].update(pose_list, delta)
            self.players_time_tracker[player_id] = time.time()
            self.available_players[player_id] = self.players[player_id]
        except KeyError as err:
            raise err

    def _update_player_command(self, player_id, cmd):
        try:
            self.players[player_id].set_command(cmd)
        except KeyError as err:
            raise err
