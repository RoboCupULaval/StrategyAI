# Under MIT License, see LICENSE.txt
from RULEngine.GameDomainObjects.ball import Ball
from RULEngine.GameDomainObjects.game import Game
from RULEngine.GameDomainObjects.team import Team
from Util.constant import TeamColor
from Util.role import Role
from Util.role_mapper import RoleMapper
from Util.singleton import Singleton
from config.config_service import ConfigService


class GameState(object, metaclass=Singleton):

    def __init__(self):
        """
        initialise le GameState, initialise les variables avec des valeurs nulles
        """
        self._game = Game()
        self.our_team_color = None
        self.field = None
        self.timestamp = 0
        self.const = None
        self._role_mapper = RoleMapper()
        self.delta_t = None

        cfg = ConfigService()
        if cfg.config_dict["GAME"]["our_color"] == "blue":
            self.my_team = self._game.blue_team
            self.their_team = self._game.yellow_team
        else:
            self.my_team = self._game.blue_team
            self.their_team = self._game.yellow_team


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
        mapping_by_player = {role: self.my_team.available_players[player_id] for role, player_id in mapping_by_player_id.items()}
        self._role_mapper.map_by_player(mapping_by_player)

    def map_players_to_roles_by_player(self, mapping):
        self._role_mapper.map_by_player(mapping)

    def get_role_mapping(self):
        return self._role_mapper.roles_translation

    def update_player_for_locked_role(self, player_id, role):
        player = self._get_player_from_all_possible_player(player_id)
        return self._role_mapper.update_player_for_locked_role(player, role)

    def _get_player_from_all_possible_player(self, player_id):
        return self.my_team.players[player_id]

    @property
    def delta_t(self):
        return self._delta_t

    @delta_t.setter
    def delta_t(self, value):

        self._delta_t = value

    @property
    def game(self):
        return self._game
