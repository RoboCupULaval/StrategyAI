# Under MIT License, see LICENSE.txt

import math as m

from RULEngine.Util.Position import Position
from RULEngine.Util.constant import *


def get_distance(position_1, position_2):
    """
    Calcul la distance entre deux positions.
    :param position_1: Position 1.
    :param position_2: Position 2.
    :return: La distance en millimètres entre les deux positions, sous forme de float.
    """
    assert(isinstance(position_1, Position))
    assert(isinstance(position_2, Position))
    return m.sqrt((position_2.x - position_1.x) ** 2 + (position_2.y - position_1.y) ** 2)


def get_angle(main_position, other):
    """
    Calcul l'angle entre deux positions et l'axe abscisses. Le résultat est en radians entre -pi et pi.
    :param main_position: La position de référence.
    :param other: Position de l'objet.
    :return: L'angle entre les deux positions et l'axe des abscisses, en radians, sous forme de float.
    """
    assert isinstance(main_position, Position), "TypeError main_position"
    assert isinstance(other, Position), "TypeError other"

    position_x = float(other.x - main_position.x)
    position_y = float(other.y - main_position.y)
    return m.atan2(position_y, position_x)


def get_closest_point_on_line(reference, point1, point2):
    """
    Calcul la position du point d'une droite le plus près d'une position de référence. La droite est donnée par deux
    positions. La ligne reliant la position recherchée et la position de référence est perpendiculaire à la droite.
    :param reference: La position de référence
    :param point1: Le premier point formant la droite
    :param point2: Le second point formant la droite
    :return: La position du point de la droite le plus proche de la position de référence.
    """
    assert isinstance(reference, Position)
    assert isinstance(point1, Position)
    assert isinstance(point2, Position)

    delta_x = point2.x - point1.x
    delta_y = point2.y - point1.y

    if delta_x != 0 and delta_y != 0:   # droite quelconque
        # Équation de la droite reliant les deux positions
        a1 = delta_y / delta_x                          # pente
        b1 = point1.y - a1*point1.x                     # ordonnée à l'origine

        # Équation de la droite perpendiculaire
        a2 = -1/a1                                      # pente perpendiculaire à a1
        b2 = reference.y - a2*reference.x               # ordonnée à l'origine

        # Calcul des coordonnées de la destination
        x = (b2 - b1)/(a1 - a2)                         # a1*x + b1 = a2*x + b2
        y = a1*x + b1

    elif delta_x == 0:  # droite verticale
        x = point1.x
        y = reference.y

    elif delta_y == 0:  # droite horizontale
        x = reference.x
        y = point1.y

    return Position(x, y)


def get_required_kick_force(position1,position2): # simple calculation

    distance = get_distance(position1,position2)
    max_field_distance_possible = m.sqrt((FIELD_X_RIGHT - FIELD_X_LEFT)**2 + (FIELD_Y_TOP - FIELD_Y_BOTTOM)**2)

    kick_force = distance * KICK_MAX_SPD / max_field_distance_possible
    return kick_force


def angle_to_ball_is_tolerated(player_position, ball_position, target_position, tolerated_angle):
    assert isinstance(ball_position, Position), "ball_position is not a Position"
    assert isinstance(player_position, Position), "player_position is not a Position"
    assert isinstance(target_position, Position), "target_position is not a Position"
    angle_player_to_ball = get_angle(player_position, ball_position)
    angle_ball_to_target = get_angle(ball_position, target_position)
    angle_difference = abs(angle_player_to_ball - angle_ball_to_target)
    if angle_difference < tolerated_angle:
        return True
    return False
