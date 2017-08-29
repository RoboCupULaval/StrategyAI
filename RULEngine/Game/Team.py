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

        if not player.check_if_on_field():
            if player_is_playing:
                del(self.available_players[player.id])
        else:
            if player_is_playing is None:
                self.available_players[player.id] = player


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
