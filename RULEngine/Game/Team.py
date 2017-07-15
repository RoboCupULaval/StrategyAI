# Under MIT License, see LICENSE.txt

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
        self.entering_players = {}
        self.exiting_players = {}
        for player_id in range(PLAYER_PER_TEAM):
            self.players[player_id] = Player(self, player_id)

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

    def _update_availability_player(self, player: Player):
        player_is_playing = self.available_players.get(player.id, None)

        if player.check_if_on_field():
            if player_is_playing:
                self.exiting_players[player.id] = player
        else:
            if player_is_playing is None:
                self.entering_players[player.id] = player

        if len(self.available_players) > 6 and self.exiting_players:
            out_player = self.exiting_players.popitem()[1]
            del(self.available_players[out_player.id])
        elif len(self.available_players) < 6 and self.entering_players:
            in_player = self.entering_players.popitem()[1]
            self.available_players[in_player.id] = in_player
        else:
            if self.entering_players and self.exiting_players:
                in_player = self.entering_players.popitem()[1]
                out_player = self.exiting_players.popitem()[1]
                del(self.available_players[out_player.id])
                self.available_players[in_player.id] = in_player
            elif self.exiting_players:
                out_player = self.exiting_players.popitem()[1]
                del(self.available_players[out_player.id])

    def _update_player(self, player_id, pose, delta=0):
        try:
            self.players[player_id].update(pose, delta)
            self._update_availability_player(self.players[player_id])
        except KeyError as err:
            raise err

    def _kalman_update(self, player_id, pose_list, delta=0):
        try:
            self.players[player_id].update(pose_list, delta)
            self._update_availability_player(self.players[player_id])
        except KeyError as err:
            raise err
