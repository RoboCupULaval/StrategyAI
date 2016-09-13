# Under MIT License, see LICENSE.txt
"""
    Ce module garde en mémoire l'état du jeu
"""
from RULEngine.Util.constant import *
import RULEngine.Game.Ball
import RULEngine.Game.Field
import RULEngine.Game.Team
import RULEngine.Util.geometry

class GameState:
    """
        Constructeur
        :param my_team_is_yellow: Booléen, la couleur de notre équipe est-elle jaune?
    """
    def __init__(self):
        self.field = RULEngine.Game.Field.Field(RULEngine.Game.Ball.Ball())
        self.my_team = RULEngine.Game.Team.Team(True)
        self.other_team = RULEngine.Game.Team.Team(False)

    """
        Met à jour la position de la balle
        :param new_ball: Nouvelles informations de la balle, de type Ball
    """
    def _update_ball(self, new_ball):
        delta = RULEngine.Util.geometry.get_angle(self.field.ball.position, new_ball.position)
        self.field.move_ball(new_ball.position, delta)

    """
        Met à jour les informations du terrain
        :param new_field: Nouvelles information du terrain, de type Field
    """
    def _update_field(self, new_field):
        new_ball = new_field.ball
        self.update_ball(new_ball)

    """
        Met à jour les informations du joueur
        :param is_my_team: Booléen, l'équipe du joueur est mon équipe
        :param player_id: identifiant du joueur, en int
        :param player_pose: Nouvelle Pose à donner au joueur
    """
    def _update_player(self, is_my_team, player_id, player_pose):
        if is_my_team:
            self.my_team.move_and_rotate_player(player_id, player_pose)
        else:
            self.other_team.move_and_rotate_player(player_id, player_pose)

    """
        Met à jour une équipe
        :param is_my_team: Booléen, l'équipe du joueur est mon équipe
        :param new_team_info: Team, info de l'équipe à mettre à jour
    """
    def _update_team(self, is_my_team, new_team_info):
        for i in range (0, )
    """
    """
    def update(self, new_game_state):

