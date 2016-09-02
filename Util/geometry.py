# Under MIT License, see LICENSE.txt
from ..Util.Position import Position
from ..Game.Player import Player
import math as m
from .constant import *

__author__ = 'RoboCupULaval'


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


def cvt_angle_360(orientation):
    """
    Convertit un angle en radians en degrés 0-359.
    :param orientation: L'angle à convertir, en radians.
    :return: L'angle entre 0 et 359 degrés, sous forme de float.
    """
    assert isinstance(orientation, (int, float)), "TypeError orientation"
    orientation = m.degrees(orientation)

    if orientation < 0:
        while True:
            if orientation >= 0:
                break
            else:
                orientation += 360
    elif orientation > 359:
        while True:
            if orientation < 360:
                break
            else:
                orientation -= 360
    return orientation


def cvt_angle_180(orientation):
    """
    Convertit un angle en radians en degrés -180-180.
    :param orientation: L'angle en radians, sous forme d'un int ou d'un float.
    :return: L'angle entre  -179 et 180 degrés, sous forme d'un float.
    """
    assert isinstance(orientation, (int, float)), "TypeError orientation"

    orientation = cvt_angle_360(orientation)
    if orientation > 180:
        return orientation-360
    elif orientation <= -180:
        return orientation+360
    else:
        return orientation


def get_nearest(ref_position, list_of_position, number=1):
    """
    Classe une liste de positions en ordre croissant de distance par rapport à une position de référence et retourne le
    nombre de positions voulu. Mettre le nombre de positions voulu à 1 permet de trouver la position la plus proche.
    :param ref_position: La position de référence.
    :param list_of_position: Une liste de positions.
    :param number: Le nombre de positions à retourner.
    :return: Une liste contenant le nombre de positions voulu, classée en ordre croissant de distance par rapport à la
    position de référence.
    """
    assert isinstance(ref_position, Position)
    assert isinstance(list_of_position, list)
    assert isinstance(number, int)

    dict_position_distance = {}
    for bot_position in list_of_position:
        dst = get_distance(ref_position, bot_position)

        while dst in dict_position_distance.keys():
            dst += 0.1
        dict_position_distance[dst] = bot_position

    list_sorted = []
    for i, bot_dst in enumerate(sorted(dict_position_distance.keys())):
        if i < number:
            list_sorted.append(dict_position_distance[bot_dst])
        else:
            return list_sorted


def get_milliseconds(time_sec):
    """
    Convertit un temps en secondes sous forme de float en millisecondes sous forme d'un int.
    :param time_sec: Le temps en secondes, sous forme de float.
    :return: Le temps en millisecondes, sous forme de int.
    """
    assert isinstance(time_sec, float)
    return int(round(time_sec * 1000))


def det(a, b):
    """
    Calcul le déterminant de la matrice
    [a.x  a.y]
    [b.x  b.y]
    :param a: La première position.
    :param b: La seconde position.
    :return: Le déterminant, sous forme d'un float.
    """
    assert(isinstance(a, Position))
    assert(isinstance(b, Position))
    return a.x * b.y - a.y * b.x


def get_line_equation(position1, position2):
    """
    Calcul l'équation de la droite formée par deux positions.
    :param position1: La première position de la droite.
    :param position2: La seconde position de la droite.
    :exception ZeroDivisionError: Une exception est soulevée si la droite est verticale.
    :return: Un tuple contenant la pente et l'ordonnée à l'origine (a, b).
    """
    assert isinstance(position1, Position)
    assert isinstance(position2, Position)

    delta_x = position2.x - position1.x
    delta_y = position2.y - position1.y

    a = delta_y / delta_x
    b = position1.y - a * position1.x

    return a, b


def get_lines_intersection(position_a1, position_a2, position_b1, position_b2):
    """
    Calcul la position de l'intersection de deux lignes, données chacune par deux positions.
    :param position_a1: Position 1 sur la ligne A.
    :param position_a2: Position 2 sur la ligne A.
    :param position_b1: Position 1 sur la ligne B.
    :param position_b2: Position 2 sur la ligne B.
    :return: La position de l'intersection des deux lignes. La position est située à l'infinie si les lignes
    sont parallèles.
    """
    assert isinstance(position_a1, Position)
    assert isinstance(position_a2, Position)
    assert isinstance(position_b1, Position)
    assert isinstance(position_b2, Position)

    delta_x_a = position_a1.x - position_a2.x
    delta_y_a = position_a1.y - position_a2.y
    delta_x_b = position_b1.x - position_b2.x
    delta_y_b = position_b1.y - position_b2.y

    denominator = delta_x_a * delta_y_b - delta_y_a * delta_x_b
    if denominator == 0:
        # Les lignes sont parallèles
        return Position(m.inf, m.inf)

    det1 = position_a1.x * position_a2.y - position_a1.y * position_a2.x
    det2 = position_b1.x * position_b2.y - position_b1.y * position_b2.x

    x = (det1 * delta_x_b - det2 * delta_x_a)
    y = (det1 * delta_y_b - det2 * delta_y_a)
    return Position(x, y)


def get_closest_point_on_line(reference, position1, position2):
    """
    Calcul la position du point d'une droite le plus près d'une position de référence. La droite est donnée par deux
    positions. La ligne reliant la position recherchée et la position de référence est perpendiculaire à la droite.
    :param reference: La position de référence
    :param position1: Le premier point formant la droite
    :param position2: Le second point formant la droite
    :return: La position du point de la droite le plus proche de la position de référence.
    """
    assert isinstance(reference, Position)
    assert isinstance(position1, Position)
    assert isinstance(position2, Position)

    delta_x = position2.x - position1.x
    delta_y = position2.y - position1.y

    if delta_x != 0 and delta_y != 0:   # droite quelconque
        # Équation de la droite reliant les deux positions
        a1 = delta_y / delta_x                          # pente
        b1 = position1.y - a1*position1.x                     # ordonnée à l'origine

        # Équation de la droite perpendiculaire
        a2 = -1/a1                                      # pente perpendiculaire à a1
        b2 = reference.y - a2*reference.x               # ordonnée à l'origine

        # Calcul des coordonnées de la destination
        x = (b2 - b1)/(a1 - a2)                         # a1*x + b1 = a2*x + b2
        y = a1*x + b1

    elif delta_x == 0:  # droite verticale
        x = position1.x
        y = reference.y

    elif delta_y == 0:  # droite horizontale
        x = reference.x
        y = position1.y

    return Position(x, y)


def get_time_to_travel(dist, speed, accel):
    """
    Calcul le temps nécessaire pour parcourir la distance, en fonction de la vitesse et de l'accélération actuelles.
    :param dist: La distance à parcourir.
    :param speed: La vitesse actuelle.
    :param accel: L'accélération actuelle.
    :return: Le temps nécessaire pour parcourir la distance, sous forme de float.
    """
    assert isinstance(dist, (int, float))
    assert isinstance(speed, (int, float))
    assert isinstance(accel, (int, float))

    if accel == 0:
        if speed == 0:
            return m.inf
        else:
            return dist / speed
    else:
        time1 = (-speed + m.sqrt(speed ** 2 - 4 * accel * dist)) / (2 * accel)
        time2 = (-speed - m.sqrt(speed ** 2 - 4 * accel * dist)) / (2 * accel)

        return time2 if time1 < time2 else time1


def get_first_to_arrive(distance1, speed1, acceleration1, distance2, speed2, acceleration2):
    """
    Détermine quel objet va arriver en premier à sa destination.
    :param distance1: La distance que l'objet 1 doit franchir.
    :param speed1: La vitesse actuelle de l'objet 1.
    :param acceleration1: L'accélération actuelle de l'objet 1.
    :param distance2: La distance que l'objet 2 doit franchir.
    :param speed2: La vitesse actuelle de l'objet 2.
    :param acceleration2: L'accélération actuelle de l'objet 2.
    :return: 1 si l'objet 1 va arriver en premier à sa destination, 2 sinon.
    """
    assert isinstance(distance1, (int, float))
    assert isinstance(speed1, (int, float))
    assert isinstance(acceleration1, (int, float))
    assert isinstance(distance2, (int, float))
    assert isinstance(speed2, (int, float))
    assert isinstance(acceleration2, (int, float))

    time1 = get_time_to_travel(distance1, speed1, acceleration1)
    time2 = get_time_to_travel(distance2, speed2, acceleration2)

    if time1 == time2:
        return 0
    else:
        return 2 if time1 < time2 else 1

def angle_to_ball_is_tolerated(player_position, ball_position, target_position, tolerated_angle):
    """
    Détermine si le joueur est capable de botter la balle à la destination désirée.
    On assume que le joueur a la balle.
    :param player_position: La position du joueur
    :param ball_position: La position de la balle
    :param target_position: La position où le joueur veut botter la balle
    :param tolerated_angle: L'incertitude d'angle toléré pour que le botté soit possible, en radian sous forme de float,
    :return: Si le joueur est capable de faire le botté ou non, sous forme de booléen.
    """
    assert isinstance(ball_position, Position), "ball_position is not a Position"
    assert isinstance(player_position, Position), "player_position is not a Position"
    assert isinstance(target_position, Position), "target_position is not a Position"
    assert isinstance(tolerated_angle, (int, float)), "tolerated_angle is neither a int nor a float"
    angle_player_to_ball = get_angle(player_position, ball_position)
    angle_ball_to_target = get_angle(ball_position, target_position)
    angle_difference = abs(angle_player_to_ball - angle_ball_to_target)
    if angle_difference < tolerated_angle:
        return True
    return False

def get_required_kick_force(position1, position2): # simple calculation
    """
    Calcul la force nécessaire pour que le botteur du joueur puisse envoyer la balle à destination.
     On assume que les joeur est cappable de botter la balle
    :param position1: La position du joueur
    :param position2: La destination
    :return: la force nécessaire, en mm/s.
    """
    assert isinstance(position1, Position)
    assert isinstance(position2, Position)
    distance = get_distance(position1, position2)
    max_field_distance_possible = m.sqrt((FIELD_X_RIGHT - FIELD_X_LEFT)**2 + (FIELD_Y_TOP - FIELD_Y_BOTTOM)**2)

    kick_force = distance * KICK_MAX_SPD / max_field_distance_possible
    return kick_force
