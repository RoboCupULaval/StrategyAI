# Under MIT License, see LICENSE.txt


"""
    Ce module garde en mémoire l'état du jeu
"""
from RULEngine.Util.game_world import GameWorld
from RULEngine.Util.constant import TeamColor
from RULEngine.Util.singleton import Singleton
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position


class GameState(object, metaclass=Singleton):

    def __init__(self):
        self.game = None
        self.our_team_color = None
        self.field = None
        self.my_team = None
        self.other_team = None
        self.timestamp = 0
        self.last_timestamp = 0
        self.debug_information_in = []
        self.ui_debug_commands = []
        self.const = None

    def get_our_team_color(self) -> TeamColor:
        return self.our_team_color

    def get_player(self, player_id: int, is_my_team=True):
        """
        :param player_id: id of the desired player
        :param is_my_team: True for ally team, False for opponent team
        :return: the player
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
            :return: La pose du joueur
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
            :return: La position du joueur
        """
        if is_my_team:
            return self.my_team.players[player_id].pose.position
        else:
            return self.other_team.players[player_id].pose.position

    def get_ball_position(self) -> Position:
        """
            Retourne la position de la balle
            :return: la position de la balle
        """
        return self.field.ball.position

    def get_timestamp(self):
        """
            Retourne le timestamp de la state
            :return: le timestamp de la state
        """
        return self.timestamp

    def set_reference(self, world_reference: GameWorld):
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
