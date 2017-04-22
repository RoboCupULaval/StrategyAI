# Under MIT licence, see LICENCE.txt
import math
from .Action import Action
# from ...Util.types import AICommand
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.area import stayOutsideCircle
from RULEngine.Util.geometry import get_angle, get_distance
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.Util.ai_command import AICommand, AICommandType
from RULEngine.Debug.debug_interface import DebugInterface
import numpy as np
__author__ = 'Robocup ULaval'


class GoBehind(Action):
    """
    Action GoBehind: Déplace le robot au point le plus proche sur la droite, derrière un objet dont la position
    est passée en paramètre, de sorte que cet objet se retrouve entre le robot et la seconde position passée en paramètre
    Méthodes :
        exec(self): Retourne la pose où se rendre
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
        position1 : La position de l'objet derrière lequel le robot doit se placer (exemple: le ballon)
        position2 : La position par rapport à laquelle le robot doit être "derrière" l'objet de la position 1 (exemple: le but)
    """
    def __init__(self, p_game_state, p_player_id, p_position1, p_position2,
                 p_distance_behind, robot_speed=None, pathfinding=False):
        """
            :param p_game_state: L'état courant du jeu.
            :param p_player_id: Identifiant du joueur qui doit se déplacer
            :param p_position1: La position de l'objet derrière lequel le robot doit se placer (exemple: le ballon)
            :param p_position2: La position par rapport à laquelle le robot doit être "derrière" l'objet de la position 1 (exemple: le but)
            :param p_distance_behind: La distance a atteindre derriere la position 1
        """
        Action.__init__(self, p_game_state)
        assert(isinstance(p_player_id, int))
        assert PLAYER_PER_TEAM >= p_player_id >= 0
        assert(isinstance(p_position1, Position))
        assert(isinstance(p_position2, Position))
        self.p_game_state = p_game_state
        self.player_id = p_player_id
        self.position1 = p_position1
        self.position2 = p_position2
        self.distance_behind = 250
        self.pathfind = pathfinding
        self.rayon_avoid = 300 #(mm)
        self.robot_speed = robot_speed

    def get_destination(self):
        """
            Calcule le point situé à  x pixels derrière la position 1 par rapport à la position 2
            :return: Un tuple (Pose, kick) où Pose est la destination du joueur et kick est nul (on ne botte pas)
            """

        delta_x = self.position2.x - self.position1.x
        delta_y = self.position2.y - self.position1.y
        theta = math.atan2(delta_y, delta_x)

        x = self.position1.x - self.distance_behind * math.cos(theta)
        y = self.position1.y - self.distance_behind * math.sin(theta)

        player_x = self.p_game_state.game.friends.players[self.player_id].pose.position.x
        player_y = self.p_game_state.game.friends.players[self.player_id].pose.position.y

        norm_player_2_position2 = math.sqrt((player_x - self.position2.x) ** 2+(player_y - self.position2.y) ** 2)
        norm_position1_2_position2 = math.sqrt((self.position1.x - self.position2.x) ** 2 + (self.position1.y - self.position2.y) ** 2)

        if norm_player_2_position2 < norm_position1_2_position2:
            # print(norm_player_2_position2)
            # print(norm_position1_2_position2)
            #on doit contourner l'objectif

            vecteur_position1_2_position2 = np.array([self.position1.x - self.position2.x,
                                                      self.position1.y - self.position2.y, 0])
            vecteur_vertical = np.array([0, 0, 1])

            vecteur_player_2_position1 = np.array([self.position1.x - player_x,
                                                   self.position1.y - player_y, 0])

            vecteur_perp = np.cross(vecteur_position1_2_position2, vecteur_vertical)
            vecteur_perp /= np.linalg.norm(vecteur_perp)

            if np.dot(vecteur_perp, vecteur_player_2_position1) > 0:
                vecteur_perp = -vecteur_perp

            position_intermediaire_x = x + vecteur_perp[0] * self.rayon_avoid
            position_intermediaire_y = y + vecteur_perp[1] * self.rayon_avoid
            if math.sqrt((player_x-position_intermediaire_x)**2+(player_y-position_intermediaire_y)**2) < 50:
                position_intermediaire_x += vecteur_perp[0] * self.rayon_avoid * 2
                position_intermediaire_y += vecteur_perp[1] * self.rayon_avoid * 2

            destination_position = Position(position_intermediaire_x, position_intermediaire_y)
        else:
            if math.sqrt((player_x-x)**2+(player_y-y)**2) < 50:
                x -= math.cos(theta) * 2
                y -= math.sin(theta) * 2
            destination_position = Position(x, y)

        # Calcul de l'orientation de la pose de destination
        destination_orientation = get_angle(destination_position, self.position1)

        destination_pose = Pose(destination_position, destination_orientation)
        DebugInterface().add_log(1, "orientation go behind {}".format(destination_orientation))
        return destination_pose

    def exec(self):
        destination_pose = {}
        destination_pose["pose_goal"] = self.get_destination()
        destination_pose["robot_speed"] = self.robot_speed
        if self.pathfind:
            destination_pose["pathfinder_on"] = True
        return AICommand(self.player_id, AICommandType.MOVE, **destination_pose)
