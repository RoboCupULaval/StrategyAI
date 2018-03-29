# Under MIT License, see LICENSE.txt

import logging
from multiprocessing.managers import DictProxy

from Util import Position
from Util.constant import TeamColor
from Util.role_mapper import RoleMapper
from Util.singleton import Singleton
from Util.team_color_service import TeamColorService
from ai.GameDomainObjects import Ball, Team, Field, Referee
from ai.GameDomainObjects.ShittyField import FieldSide


class GameState(metaclass=Singleton):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.reset()

    def reset(self):
        self._role_mapper = RoleMapper()

        self._ball = Ball()
        self._field = Field(self._ball)

        self._referee = Referee()

        self._blue_team = Team(team_color=TeamColor.BLUE)
        self._yellow_team = Team(team_color=TeamColor.YELLOW)

        self._our_team = self._yellow_team if TeamColorService().is_our_team_yellow else self._blue_team
        self._enemy_team = self._blue_team if TeamColorService().is_our_team_yellow else self._yellow_team

    def update(self, new_game_state):
        if new_game_state:
            # Game State is a shared dict with the Engine. Might cause a race condition
            game_state = new_game_state.copy()  # FIX: this is a shallow copy. is it okay?
            self._blue_team.update(game_state['blue'])
            self._yellow_team.update(game_state['yellow'])

            if game_state['balls']:
                self._ball.update(game_state['balls'][0])

    # FIXME
    def get_player_position(self, player_id):
        if player_id not in self.our_team.available_players:
            raise RuntimeError("No player available with that player_id {}".format(player_id))
        return self.our_team.available_players[player_id].position


    def get_player_by_role(self, role):
        return self._role_mapper.roles_translation[role]

    def get_role_by_player_id(self, player_id: int):
        for r, p in self._role_mapper.roles_translation.items():
            if p is not None and p.id == player_id:
                return r

    def map_players_to_roles_by_player_id(self, mapping_by_player_id):
        mapping_by_player = {role: self.our_team.available_players[player_id]
                             for role, player_id in mapping_by_player_id.items()}
        self._role_mapper.map_by_player(mapping_by_player)

    def map_players_to_roles_by_player(self, mapping):
        self._role_mapper.map_by_player(mapping)

    def map_player_to_first_available_role(self, player_id):
        player = self.our_team.available_players[player_id]
        return self._role_mapper.map_player_to_first_available_role(player)

    @property
    def our_side(self):
        return FieldSide.POSITIVE # FIXME HACK

    @property
    def role_mapping(self):
        return self._role_mapper.roles_translation

    @property
    def ball_position(self) -> Position:
        return self._field.ball.position

    @property
    def ball_velocity(self) -> Position:
        return self._field.ball.velocity

    @property
    def our_team(self) -> Team:
        return self._our_team

    @property
    def enemy_team(self) -> Team:
        return self._enemy_team

    @property
    def ball(self) -> Ball:
        return self._field.ball

    @property
    def const(self):
        return self._field.constant

    @const.setter
    def const(self, field: DictProxy):
        self._field.constant = field

    @ball.setter
    def ball(self, ball: Ball):
        """
        Should only used by PerfectSim or other testing utility
        """
        self._field = Field(ball)

    @property
    def is_ball_on_field(self):
        return self._field.ball is not None

    @property
    def referee(self) -> Referee:
        return self._referee
