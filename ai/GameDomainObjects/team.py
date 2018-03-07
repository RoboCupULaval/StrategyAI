# Under MIT License, see LICENSE.txt
from typing import Dict

from Util.constant import PLAYER_PER_TEAM
from Util.team_color_service import TeamColor
from ai.GameDomainObjects.player import Player


class Team:
    def __init__(self, team_color: TeamColor):
        assert isinstance(team_color, TeamColor)

        self._team_color = team_color
        self._players = {i: Player(i, self) for i in range(PLAYER_PER_TEAM)}
        self._onplay_players = {}

    def update(self, players):
        # self._players = {}
        # self._onplay_players = {}
        self._onplay_players = {player["id"]: self._players[player["id"]] for player in players}
        for p in players:
            # p = Player.from_dict(dict_player, team=self)
            self._players[p['id']].update(p['pose'], p['velocity'])
            # self._onplay_players[p.id] = p

    @property
    def team_color(self) -> TeamColor:
        return self._team_color

    @property
    def players(self) -> Dict:
        return self._players

    # TODO: PB: Keep that until we know how the player will be access in the new architecture
    @property
    def available_players(self):
        return self._players

    @property
    def onplay_players(self):
        return self._onplay_players

    @property
    def team_color(self):
        return self._team_color

    def has_player(self, player):
        return player in self.players.values()

    def is_team_yellow(self):
        return self.team_color == TeamColor.YELLOW
