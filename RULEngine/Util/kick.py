# Under MIT License, see LICENSE.txt

from RULEngine.Util.constant import *
from RULEngine.Util.geometry import get_distance
import math as m

def getRequiredKickForce(position1: Position, position2: Position):
    """
        Calcul la force nécessaire pour que le botteur du joueur puisse envoyer
        la balle à destination. On assume que les joueur est capable de botter
        la balle
        Args:
            position1: La position du joueur
            position2: La destination
        Returns:
            La force nécessaire, en mm/s.
    """
    assert isinstance(position1, Position)
    assert isinstance(position2, Position)
    distance = get_distance(position1, position2)
    max_field_distance_possible = m.sqrt((FIELD_X_RIGHT - FIELD_X_LEFT)**2 +
                                         (FIELD_Y_TOP - FIELD_Y_BOTTOM)**2)

    kick_force = distance * KICK_MAX_SPD / max_field_distance_possible
    return kick_force