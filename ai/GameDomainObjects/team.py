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
        self._available_players = {}

    def update(self, players: Dict):
        self._available_players = {player['id']: self._players[player['id']] for player in players}
        for p in players:
            self._players[p['id']].update(p['pose'], p['velocity'])

    @property
    def team_color(self) -> TeamColor:
        return self._team_color

    @property
    def players(self) -> Dict:
        return self._players

    @property
    def available_players(self):
        return self._available_players

    @property
    def team_color(self):
        return self._team_color

    def is_team_yellow(self):
        return self.team_color == TeamColor.YELLOW
