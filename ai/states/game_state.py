# Under MIT License, see LICENSE.txt

import logging

from RULEngine.services.team_color_service import TeamColorService
from Util import Position
from ai.GameDomainObjects import Ball, Team, Field, Referee
from Util.constant import TeamColor
from Util.role import Role
from Util.role_mapper import RoleMapper
from Util.singleton import Singleton


class GameState(object, metaclass=Singleton):
    UPDATE_TIMEOUT = 0.5

    def __init__(self):
        """
        initialise le GameState, initialise les variables avec des valeurs nulles
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.reset()

    def reset(self):
        self._role_mapper = RoleMapper()
        self._delta_t = 0
        self.our_team_color = None

        self._balls = []
        self._field = Field(self._balls)
        self._referee = Referee()
        self._blue_team = Team(team_color=TeamColor.BLUE)
        self._yellow_team = Team(team_color=TeamColor.YELLOW)
        self._our_team = None
        self._enemy_team = None
        self._assign_teams()

    def _assign_teams(self):
        if TeamColorService().our_team_color == TeamColor.BLUE:
            self._our_team = self._blue_team
            self._enemy_team = self._yellow_team
        elif TeamColorService().our_team_color == TeamColor.YELLOW:
            self._our_team = self._yellow_team
            self._enemy_team = self._blue_team

    def update(self, new_game_state):
        self._blue_team.update(new_game_state['blue'])
        self._yellow_team.update(new_game_state['yellow'])

        self._balls = [Ball.from_dict(msg_ball) for msg_ball in new_game_state['balls']]
        self._field = Field(self._balls)

    def get_player_by_role(self, role: Role):
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

    def get_role_mapping(self):
        return self._role_mapper.roles_translation

    def update_player_for_locked_role(self, player_id, role):
        player = self._get_player_from_all_possible_player(player_id)
        return self._role_mapper.update_player_for_locked_role(player, role)

    def _get_player_from_all_possible_player(self, player_id):
        return self.our_team.players[player_id]

    def get_player(self, id: int):
        return self.our_team.players[id]  # tODO

    def get_ball_position(self) -> Position:
        """
            Retourne la position de la balle
            :return: L'instance de Position, la position de la balle
        """
        return self._field.ball.position

    @property
    def delta_t(self) -> float:
        return self._delta_t

    def get_ball_velocity(self) -> Position:
        """
        Retourne le vecteur vélocité de la balle.
        Use with care, probably not implemented correctly

        :return: la vélocité de la balle.
        """
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

    @ball.setter
    def ball(self, ball: Ball) -> Ball:
        self._field = Field([ball])

    @property
    def referee(self) -> Referee:
        return self._referee
