# Under MIT License, see LICENSE.txt


"""
    Ce module garde en mémoire l'état du jeu
"""
from RULEngine.Game.Player import Player
from RULEngine.Util.game_world import GameWorld
from RULEngine.Util.constant import TeamColor
from RULEngine.Util.singleton import Singleton
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position


class GameState(object, metaclass=Singleton):

    def __init__(self):
        """
        initialise le GameState, initialise les variables avec des valeurs nulles
        """
        self.game = None
        self.our_team_color = None
        self.field = None
        self.my_team = None
        self.other_team = None
        self.timestamp = 0
        self.last_timestamp = 0
        self.const = None

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
        if is_my_team:
            return self.my_team.players[player_id]
        else:
            return self.other_team.players[player_id]

    def get_player_pose(self, player_id: int, is_my_team=True) -> Pose:
        """
            Retourne la pose d'un joueur d'une équipe

            :param is_my_team: Booléen avec valeur vrai par défaut, l'équipe du joueur est mon équipe
            :param player_id: identifiant du joueur, en int
            :return: L'instance Pose de la pose du joueur
        """
        if is_my_team:
            return self.my_team.players[player_id].pose
        else:
            return self.other_team.players[player_id].pose

    def get_player_position(self, player_id: int, is_my_team=True) -> Position:
        """
            Retourne la position d'un joueur d'une équipe

            :param is_my_team: Booléen avec valeur vrai par défaut, l'équipe du joueur est mon équipe
            :param player_id: identifiant du joueur, en int
            :return: L'instance Position de la position du joueur
        """
        if is_my_team:
            return self.my_team.players[player_id].pose.position
        else:
            return self.other_team.players[player_id].pose.position

    def get_ball_position(self) -> Position:
        """
            Retourne la position de la balle
            :return: L'instance de Position, la position de la balle
        """
        return self.field.ball.position

    def set_ball_position(self, newPosition : Position, delta_t) -> None:
        self.field.ball.set_position(newPosition, delta_t)

    def get_ball_velocity(self):
        """
        Retourne le vecteur vélocité de la balle.
        Use with care, probably not implemented correctly

        :return: la vélocité de la balle.
        """
        return self.field.ball.velocity

    def get_timestamp(self) -> float:
        """
            Retourne le timestamp de la state

            :return: float: le timestamp
        """
        return self.timestamp

    def set_reference(self, world_reference: GameWorld) -> None:
        """
        Ajoute les références des objets du monde.

        :param world_reference: GameWorld instance avec les références mise dedans
        :return: None.
        """
        assert isinstance(world_reference, GameWorld), \
            "setting reference to the gamestate require an instance of RULEngine.Util.GameWorld"
        assert world_reference.game.referee is not None, \
            "setting the game_state reference with an invalid (None) referee!"
        assert world_reference.team_color_svc is not None, \
            "setting the game_state reference with an invalid (None) team_color_service!"

        self.game = world_reference.game
        self.field = self.game.field
        self.my_team = self.game.friends
        self.other_team = self.game.enemies
        self.our_team_color = world_reference.team_color_svc.OUR_TEAM_COLOR
        self.const = self.game.field.constant
        self.timestamp = world_reference.timestamp
