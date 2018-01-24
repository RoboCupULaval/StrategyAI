# Under MIT License, see LICENSE.txt
__author__ = "Maxime Gagnon-Legault"


import logging
from multiprocessing import Queue
from queue import Empty

from RULEngine.GameDomainObjects.ball import Ball
from RULEngine.GameDomainObjects.game import Game
from RULEngine.GameDomainObjects.team import Team
from Util.constant import TeamColor
from Util.role import Role
from Util.role_mapper import RoleMapper
from Util.singleton import Singleton
from config.config_service import ConfigService


class GameState(object, metaclass=Singleton):
    UPDATE_TIMEOUT = 0.5

    def __init__(self, game_state_queue: Queue):
        """
        initialise le GameState, initialise les variables avec des valeurs nulles
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        self._game = Game()
        self._role_mapper = RoleMapper()
        self._game_state_queue = game_state_queue

        self.our_team_color = None
        self.field = None

    def update(self, new_game_state):
        self._game.blue_team.update(new_game_state['blue'])
        self._game.yellow_team.update(new_game_state['blue'])

        self.game._balls = [Ball.from_dict(msg_ball) for msg_ball in new_game_state['balls']]

    def get_player_by_role(self, role: Role):
        return self._role_mapper.roles_translation[role]

    def get_role_by_player_id(self, player_id: int):
        for r, p in self._role_mapper.roles_translation.items():
            if p.id == player_id:
                return r

    def map_players_to_roles_by_player_id(self, mapping_by_player_id):
        mapping_by_player = {role: self.our_team.available_players[player_id] for role, player_id in mapping_by_player_id.items()}
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

    @property
    def delta_t(self) -> float:
        return self._delta_t

    @delta_t.setter
    def delta_t(self, value) -> None:

        self._delta_t = value

    @property
    def game(self) -> Game:
        return self._game

    @property
    def our_team(self) -> Team:
        return self._game.our_team

    @property
    def other_team(self) -> Team:
        return self._game.their_team

    @property
    def ball(self) -> Ball:
        return self._game.ball
