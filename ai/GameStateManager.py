# Under MIT License, see LICENSE.txt
"""
    Ce module garde en mémoire l'état du jeu
    NOTE: Il manque les getters
"""
from RULEngine.Util.constant import PLAYER_PER_TEAM
import RULEngine.Game.Ball
import RULEngine.Game.Field
import RULEngine.Game.Team
import RULEngine.Util.geometry


class GameStateManager:
    """ Constructeur """
    def __init__(self):
        self.field = RULEngine.Game.Field.Field(RULEngine.Game.Ball.Ball())
        self.my_team = RULEngine.Game.Team.Team(True)
        self.other_team = RULEngine.Game.Team.Team(False)
        self.timestamp = 0

    def _update_ball(self, new_ball):
        """
            Met à jour la position de la balle
            :param new_ball: Nouvelles informations de la balle, de type Ball
        """
        delta = RULEngine.Util.geometry.get_angle(self.field.ball.position, new_ball.position)
        self.field.move_ball(new_ball.position, delta)

    def _update_field(self, new_field):
        """
            Met à jour les informations du terrain
            :param new_field: Nouvelles information du terrain, de type Field
        """
        new_ball = new_field.ball
        self._update_ball(new_ball)

    def _update_player(self, player_id, player_pose, is_my_team=True):
        """
            Met à jour les informations du joueur
            :param is_my_team: Booléen avec valeur vrai par défaut, l'équipe du joueur est mon équipe
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
            self._update_player(is_my_team, i)

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
        self._update_team(is_my_team, new_game_state.friends)
        self._update_team(not is_my_team, new_game_state.enemies)
        self._update_timestamp(new_game_state.timestamp)

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
