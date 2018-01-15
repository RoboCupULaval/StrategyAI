# Under MIT License, see LICENSE.txt
import logging

from RULEngine.Util.Pose import Pose

from RULEngine.GameDomainObjects.ball import Ball
from RULEngine.GameDomainObjects.field import Field
from RULEngine.GameDomainObjects.referee import Referee
from RULEngine.GameDomainObjects.team import Team
from RULEngine.services.team_color_service import TeamColor
from Util import Position
from Util.singleton import Singleton


class Game(metaclass=Singleton):
    def __init__(self):
        self.logger = logging.getLogger("Game - DomainObject")

        self._ball = Ball()
        self._field = Field(self._ball)
        self._referee = Referee()
        self._blue_team = Team(team_color=TeamColor.BLUE)
        self._yellow_team = Team(team_color=TeamColor.YELLOW)
        self._our_team = None
        self._their_team = None

    def is_team_yellow(self):
        return self.our_team_color == TeamColor.YELLOW

    @staticmethod
    def _update_players_of_team(players, team, delta):
        for player in players:
            player_position = Position(player.x, player.y, player.height)
            player_pose = Pose(player_position, player.orientation)
            team.update_player(player.robot_id, player_pose, delta)

    @property
    def ball(self):
        return self.field.ball

    @property
    def referee(self):
        return self._referee

    @property
    def yellow_team(self):
        return self._yellow_team

    @property
    def blue_team(self):
        return self._blue_team

    @property
    def our_team(self):
        return self._our_team

    @property
    def their_team(self):
        return self._their_team

    @property
    def our_team_color(self):
        return self._our_team.team_color

    @property
    def field(self):
        return self._field
