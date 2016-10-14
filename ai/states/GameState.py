# Under MIT License, see LICENSE.txt


"""
    Ce module garde en mémoire l'état du jeu
"""
from ai.states.singleton import singleton

from RULEngine.Util.constant import PLAYER_PER_TEAM
import RULEngine.Game.Ball
import RULEngine.Game.Field
import RULEngine.Game.Team
import RULEngine.Util.geometry


@singleton
class GameState:
    """
        Gère l'état du jeu.
    """
    instance = None

    def __new__(cls):
        """
        S'assure qu'il n'y a qu'un seul ModuleManager
        :return: L'instance du ModuleManager
        """
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self, is_team_yellow=False):
        self.field = RULEngine.Game.Field.Field(RULEngine.Game.Ball.Ball())
        self.my_team = RULEngine.Game.Team.Team(is_team_yellow)
        self.other_team = RULEngine.Game.Team.Team(not is_team_yellow)
        self.timestamp = 0
        self.debug_information_in = []
        self.ui_debug_commands = []

    def _update_ball_position(self, new_ball_position):
        """
            Met à jour la position de la balle
            :param new_ball_position: Nouvelles position de la balle, de type Position
        """
        delta = RULEngine.Util.geometry.get_angle(self.field.ball.position, new_ball_position)
        self.field.move_ball(new_ball_position, delta)

    def _update_field(self, new_field):
        """
            Met à jour les informations du terrain
            :param new_field: Nouvelles information du terrain, de type Field
        """
        new_ball_position = new_field.ball.position
        self._update_ball_position(new_ball_position)

    def _update_player(self, player_id, player_pose, is_my_team=True):
        """
            Met à jour les informations du joueur
            :param is_my_team: Booléen avec valeur 1vrai par défaut, l'équipe du joueur est mon équipe
            :param player_id: identifiant du joueur, en int
            :param player_pose: Nouvelle Pose à donner au joueur
        """
        if is_my_team:
            self.my_team.move_and_rotate_player(player_id, player_pose)
        else:
            self.other_team.move_and_rotate_player(player_id, player_pose)

    def _update_team(self, new_team_info, is_my_team=True):
        """
            Met à jour une équipe
            :param is_my_team: Booléen avec valeur vrai par défaut, l'équipe du joueur est mon équipe
            :param new_team_info: Team, info de l'équipe à mettre à jour
        """
        for i in range(PLAYER_PER_TEAM):
            self._update_player(i, new_team_info.players[i].pose, is_my_team)

    def _update_timestamp(self, new_timestamp):
        """
            Met à jour le timestamp
            :param new_timestamp: float, valeur du nouveau timestamp
        """
        self.timestamp = new_timestamp

    def update(self, new_game_state):
        """
            Met à jour le jeu
            :param new_game_state: État du jeu, sous forme de named tuple
            Pour le format du tuple, voir RULEngine/framework.py
        """
        is_my_team = True
        self._update_field(new_game_state.field)
        self._update_team(new_game_state.friends, is_my_team)
        self._update_team(new_game_state.enemies, not is_my_team)
        self._update_timestamp(new_game_state.timestamp)

    def get_my_team_player(self, player_id):
        pass

    def get_player_pose(self, player_id, is_my_team=True):
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

    def get_ball_position(self):
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
