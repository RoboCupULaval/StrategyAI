# Under MIT licence, see LICENCE.txt
import math
import numpy as np

from RULEngine.GameDomainObjects.Player import Player
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.geometry import wrap_to_pi
from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType

__author__ = 'Robocup ULaval'


class GoBehind(Action):
    """
    Action GoBehind: Déplace le robot au point le plus proche sur la droite, derrière un objet dont la position
    est passée en paramètre, de sorte que cet objet se retrouve entre le robot et la seconde position passée
    en paramètre
    Méthodes :
        exec(self): Retourne la pose où se rendre
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
        position1 : La position de l'objet derrière lequel le robot doit se placer (exemple: le ballon)
        position2 : La position par rapport à laquelle le robot doit être "derrière" l'objet de la position 1
                    (exemple: le but)
    """
    def __init__(self, game_state: GameState, player: Player, position1: Position, position2: Position=None,
                 distance_behind: [int, float]=250, cruise_speed: [int, float]=1,
                 pathfinder_on: bool=False, orientation: str= 'front'):
        """
            :param game_state: L'état courant du jeu.
            :param player: Instance du joueur qui doit se déplacer
            :param position1: La position de l'objet derrière lequel le robot doit se placer (exemple: le ballon)
            :param position2: La position par rapport à laquelle le robot doit être "derrière" l'objet
                                de la position 1 (exemple: le but)
            :param distance_behind: La distance a atteindre derriere la position 1
        """
        Action.__init__(self, game_state, player)
        assert(isinstance(position1, Position))
        assert(isinstance(position2, Position))
        self.position1 = position1
        self.position2 = position2
        self.distance_behind = distance_behind
        self.pathfinder_on = pathfinder_on
        self.rayon_avoid = 300  # (mm)
        self.cruise_speed = cruise_speed
        self.orientation = orientation

        # TODO find something better MGL 2017/05/22
        if self.position2 is None:
            self.position2 = game_state.const["FIELD_THEIR_GOAL_MID_GOAL"]

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

        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y

        norm_player_2_position2 = math.sqrt((player_x - self.position2.x) ** 2+(player_y - self.position2.y) ** 2)
        norm_position1_2_position2 = math.sqrt((self.position1.x - self.position2.x) ** 2 +
                                               (self.position1.y - self.position2.y) ** 2)

        # TODO: Remove this part of the logic, since we have a pathfinder to do all of that...
        if norm_player_2_position2 < norm_position1_2_position2:
            # on doit contourner l'objectif

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
        # TODO why?!? MGL 2017/05/22
        destination_orientation = 0
        if self.orientation == 'front':
            destination_orientation = (self.position1 - destination_position).angle()
        elif self.orientation == 'back':
            destination_orientation = wrap_to_pi((self.position1 - destination_position).angle() + np.pi)

        destination_pose = Pose(destination_position, destination_orientation)
        return destination_pose

    def exec(self):
        return AICommand(self.player, AICommandType.MOVE, **{"pose_goal": self.get_destination(),
                                                             "cruise_speed": self.cruise_speed,
                                                             "pathfinder_on": self.pathfinder_on})
