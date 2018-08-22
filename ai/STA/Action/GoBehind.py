# Under MIT licence, see LICENCE.txt
from typing import Optional

from Util.ai_command import MoveTo

__author__ = "Maxime Gagnon-Legault"

import math
import numpy as np

from Util import Pose

from Util.position import Position
from Util.geometry import wrap_to_pi
from ai.GameDomainObjects import Player

RAYON_AVOID = 300  # (mm)

def GoBehind(player: Player, position1: Position, position2: Optional[Position]=None,
             distance_behind: float=250,
             orientation: str= 'front'):
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
    delta_x = position2.x - position1.x
    delta_y = position2.y - position1.y
    theta = math.atan2(delta_y, delta_x)

    x = position1.x - distance_behind * math.cos(theta)
    y = position1.y - distance_behind * math.sin(theta)

    player_x = player.pose.position.x
    player_y = player.pose.position.y

    norm_player_2_position2 = math.sqrt((player_x - position2.x) ** 2+(player_y - position2.y) ** 2)
    norm_position1_2_position2 = math.sqrt((position1.x - position2.x) ** 2 +
                                           (position1.y - position2.y) ** 2)

    if norm_player_2_position2 < norm_position1_2_position2:
        # on doit contourner l'objectif

        vecteur_position1_2_position2 = np.array([position1.x - position2.x,
                                                  position1.y - position2.y, 0])
        vecteur_vertical = np.array([0, 0, 1])

        vecteur_player_2_position1 = np.array([position1.x - player_x,
                                               position1.y - player_y, 0])

        vecteur_perp = np.cross(vecteur_position1_2_position2, vecteur_vertical)
        vecteur_perp /= np.linalg.norm(vecteur_perp)

        if np.dot(vecteur_perp, vecteur_player_2_position1) > 0:
            vecteur_perp = -vecteur_perp

        position_intermediaire_x = x + vecteur_perp[0] * RAYON_AVOID
        position_intermediaire_y = y + vecteur_perp[1] * RAYON_AVOID
        if math.sqrt((player_x-position_intermediaire_x)**2+(player_y-position_intermediaire_y)**2) < 50:
            position_intermediaire_x += vecteur_perp[0] * RAYON_AVOID * 2
            position_intermediaire_y += vecteur_perp[1] * RAYON_AVOID * 2

        destination_position = Position(position_intermediaire_x, position_intermediaire_y)
    else:
        if math.sqrt((player_x-x)**2+(player_y-y)**2) < 50:
            x -= math.cos(theta) * 2
            y -= math.sin(theta) * 2
        destination_position = Position(x, y)

    # Calcul de l'orientation de la pose de destination
    destination_orientation = 0
    if orientation == 'front':
        destination_orientation = wrap_to_pi((position1 - destination_position).angle)
    elif orientation == 'back':
        destination_orientation = wrap_to_pi((position1 - destination_position).angle + np.pi)

    destination_pose = Pose(destination_position, destination_orientation)
    return MoveTo(destination_pose)
