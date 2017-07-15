# Under MIT License, see LICENSE.txt


"""
    Ce module garde en mémoire l'état du jeu
"""
from typing import Union

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Game.Player import Player
from RULEngine.Util.reference_transfer_object import ReferenceTransferObject
from RULEngine.Util.constant import TeamColor
from RULEngine.Util.singleton import Singleton
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Debug.debug_interface import DebugInterface, COLOR_ID_MAP
from ai.Util.role import Role
from ai.Util.role_mapper import RoleMapper


class GameState(object, metaclass=Singleton):

    def __init__(self, for_unitest_pls_remove_debug_interface_oh_god=True):
        """
        initialise le GameState, initialise les variables avec des valeurs nulles
        """
        self.game = None
        self.our_team_color = None
        self.field = None
        self.my_team = None
        self.other_team = None
        self.timestamp = 0
        self.const = None
        # FIXME: Gamestate should not have a debug interface
        if for_unitest_pls_remove_debug_interface_oh_god:
            self.debug_interface = DebugInterface()
        self._role_mapper = RoleMapper()

    def get_player_by_role(self, role: Role) -> OurPlayer:
        return self._role_mapper.roles_translation[role]

    def get_role_by_player_id(self, player_id: int) -> Union[Role, None]:
        for r, p in self._role_mapper.roles_translation.items():
            if p.id == player_id:
                return r

    def bind_random_available_players_to_role(self) -> OurPlayer:
        pass

    def print_role_mapping(self):
        # Testing purposes only
        for key, value in self._role_mapper.roles_translation.items():
            print(key, value)

    def map_players_to_roles_by_player_id(self, mapping_by_player_id):
        mapping_by_player = {role: self.my_team.available_players[player_id] for role, player_id in mapping_by_player_id.items()}
        self._role_mapper.map_by_player(mapping_by_player)

    def map_players_to_roles_by_player(self, mapping):
        self._role_mapper.map_by_player(mapping)

    def get_role_mapping(self):
        return self._role_mapper.roles_translation

    def get_our_team_color(self) -> TeamColor:
        """
        Retourne la couleur de notre équipe TeamColor Enum

        :return: TeamColor(Enum) la couleur de notre équipe
        """
        return self.our_team_color

    def get_player(self, player_id: int, is_my_team=True) -> Player:
        """
        Retourne l'instance du joueur avec id player_id dans l'équipe choisit

        :param player_id: id of the desired player
        :param is_my_team: True for ally team, False for opponent team
        :return: the player instance
        """
        try:
            if is_my_team:
                return self.my_team.available_players[player_id]
            else:
                return self.other_team.available_players[player_id]
        except Exception as e:
            print(e)
            raise e

    def get_player_pose(self, player_id: int, is_my_team=True) -> Pose:
        """
            Retourne la pose d'un joueur d'une équipe

            :param is_my_team: Booléen avec valeur vrai par défaut, l'équipe du joueur est mon équipe
            :param player_id: identifiant du joueur, en int
            :return: L'instance Pose de la pose du joueur
        """
        if is_my_team:
            return self.my_team.available_players[player_id].pose
        else:
            return self.other_team.available_players[player_id].pose

    def get_player_position(self, player_id: int, is_my_team=True) -> Position:
        """
            Retourne la position d'un joueur d'une équipe

            :param is_my_team: Booléen avec valeur vrai par défaut, l'équipe du joueur est mon équipe
            :param player_id: identifiant du joueur, en int
            :return: L'instance Position de la position du joueur
        """
        if is_my_team:
            return self.my_team.available_players[player_id].pose.position
        else:
            return self.other_team.available_players[player_id].pose.position

    def get_ball_position(self) -> Position:
        """
            Retourne la position de la balle
            :return: L'instance de Position, la position de la balle
        """
        return self.field.ball.position

    def set_ball_position(self, newPosition: Position, delta_t) -> None:
        self.field.ball.set_position(newPosition, delta_t)

    def get_ball_velocity(self) -> Position:
        """
        Retourne le vecteur vélocité de la balle.
        Use with care, probably not implemented correctly

        :return: la vélocité de la balle.
        """
        return self.field.ball.velocity

    def get_delta_t(self) -> float:
        """
            Retourne le delta_t de la state

            :return: float: le timestamp
        """
        return self.game.delta_t

    def set_reference(self, reference_transfer_object: ReferenceTransferObject) -> None:
        """
        Ajoute les références des objets du monde.

        :param reference_transfer_object: reference_transfer_object instance avec les références mise dedans
        :return: None.
        """
        assert isinstance(reference_transfer_object, ReferenceTransferObject), \
            "setting reference to the gamestate require an instance of RULEngine.Util.GameWorld"
        assert reference_transfer_object.game.referee is not None, \
            "setting the game_state reference with an invalid (None) referee!"
        assert reference_transfer_object.team_color_svc is not None, \
            "setting the game_state reference with an invalid (None) team_color_service!"

        self.game = reference_transfer_object.game
        self.field = self.game.field
        self.my_team = self.game.friends
        self.other_team = self.game.enemies
        self.our_team_color = reference_transfer_object.team_color_svc.OUR_TEAM_COLOR
        self.const = self.game.field.constant

    def display_player_kalman(self):
        for player in self.my_team.available_players.values():
            pose = player.pose
            self.debug_interface.add_circle(center=(pose[0], pose[1]), radius=90, timeout=0.06)
