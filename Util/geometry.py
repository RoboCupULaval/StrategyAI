# Under MIT License, see LICENSE.txt
import math as m

import numpy as np

from ..Util.Position import Position
from ..Util.Pose import Pose

__author__ = 'RoboCupULaval'


def get_distance(position_1: Position, position_2: Position) -> float:
    """
        Calcul la distance entre deux positions (la norme du vecteur reliant les deux points).
        Args:
            position_1: Position 1.
            position_2: Position 2.
        Returns:
            La distance en millimètres entre les deux positions
    """
    assert isinstance(position_1, Position)
    assert isinstance(position_2, Position)
    return m.sqrt((position_2.x - position_1.x) ** 2 +
                  (position_2.y - position_1.y) ** 2)


def get_angle(main_position: Position, other: Position) -> float:
    """
        Calcul l'angle entre deux positions et l'axe abscisses. Le résultat est
        en radians entre -pi et pi.
        Args:
            main_position: La position de référence.
            other: Position de l'objet.
        Returns:
            L'angle entre les deux positions et l'axe des abscisses.
    """
    assert isinstance(main_position, Position), "TypeError main_position"
    assert isinstance(other, Position), "TypeError other"

    position_x = float(other.x - main_position.x)
    position_y = float(other.y - main_position.y)
    return m.atan2(position_y, position_x)


def cvt_angle_360(orientation: float) -> float:
    """
        Convertit un angle en radians en degrés 0-359.
        Args:
            orientation: L'angle à convertir, en radians.
        Returns:
            L'angle entre 0 et 359 degrés.
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
        Convertit un angle en radians en degrés [-180, 180].
        Args:
            orientation: L'angle en radians.
        Returns:
            L'angle entre  -179 et 180 degrés.
    """
    assert isinstance(orientation, (int, float)), "TypeError orientation"

    orientation = cvt_angle_360(orientation)
    if orientation > 180:
        return orientation-360
    elif orientation <= -180:
        return orientation+360
    else:
        return orientation


def get_nearest(ref_position: Position, list_of_position: list, number=1):
    """
        Classe une liste de positions en ordre croissant de distance par
        rapport à une position de référence et retourne le nombre de positions
        voulu. Mettre le nombre de positions voulu à 1 permet de trouver la
        position la plus proche.
        Args:
            ref_position: La position de référence.
            list_of_position: Une liste de positions.
            number: Le nombre de positions à retourner.
        Returns:
            list<Position>: Positions classées en ordre croissant de distance.
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


def get_milliseconds(time_sec: float) -> int:
    """
        Convertit un temps en secondes sous forme de float en millisecondes
        sous forme d'un int.
        Args:
            time_sec: Le temps en secondes.
        Returns:
            Le temps en millisecondes.
    """
    assert isinstance(time_sec, float)
    return int(round(time_sec * 1000))


def det(pos_a: Position, pos_b: Position) -> float:
    """
        Calcul le déterminant de la matrice
        [a.x  a.y]
        [b.x  b.y]
        Args:
            pos_a: La première position.
            pos_b: La seconde position.
        Returns
            Le déterminant.
    """
    assert isinstance(pos_a, Position)
    assert isinstance(pos_b, Position)
    return pos_a.x * pos_b.y - pos_a.y * pos_b.x


def get_line_equation(position1: Position, position2: Position) -> tuple:
    """
        Calcul l'équation de la droite formée par deux positions.
        Args:
            position1: La première position de la droite.
            position2: La seconde position de la droite.
        Exceptions:
            ZeroDivisionError: Une exception est soulevée si la droite est
                               verticale.
        Returns:
            Un tuple contenant la pente et l'ordonnée à l'origine.
    """
    assert isinstance(position1, Position)
    assert isinstance(position2, Position)

    delta_x = position2.x - position1.x
    delta_y = position2.y - position1.y

    pente = delta_y / delta_x
    ordonnee = position1.y - pente * position1.x

    return pente, ordonnee


def get_lines_intersection(position_a1: Position, position_a2: Position,
                           position_b1: Position, position_b2: Position):
    """
        Calcul la position de l'intersection de deux lignes, données chacune
        par deux positions.
        Args:
            position_a1: Position 1 sur la ligne A.
            position_a2: Position 2 sur la ligne A.
            position_b1: Position 1 sur la ligne B.
            position_b2: Position 2 sur la ligne B.
        Returns:
            Position: La position de l'intersection des deux lignes.
                      La position est située à l'infinie si les lignes sont
                      parallèles.
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

    a = np.matrix([[delta_x_a, -delta_x_b], [delta_y_a, -delta_y_b]])
    b = np.matrix([[position_b1.x - position_a1.x], [position_b1.y - position_a1.y]])

    scale = np.linalg.solve(a, b)

    intersection1 = np.matrix([[position_a1.x], [position_a1.y]]) + scale.item((0, 0))*np.matrix([[delta_x_a],
                                                                                                  [delta_y_a]])
    intersection2 = np.matrix([[position_b1.x], [position_b1.y]]) + scale.item((1, 0))*np.matrix([[delta_x_b],
                                                                                                  [delta_y_b]])

    assert np.allclose(intersection1, intersection2)

    x = intersection1.item((0, 0))
    y = intersection1.item((1, 0))

    return Position(x, y)


def get_closest_point_on_line(reference: Position,
                              position1: Position,
                              position2: Position) -> Position:
    """
        Calcul la position du point d'une droite le plus près d'une position de
        référence. La droite est donnée par deux positions. La ligne reliant la
        position recherchée et la position de référence est perpendiculaire à
        la droite.
        Args:
            reference: La position de référence
            position1: Le premier point formant la droite
            position2: Le second point formant la droite
        Returns:
            La position du point de la droite le plus proche de la position de
            référence.
    """
    assert isinstance(reference, Position)
    assert isinstance(position1, Position)
    assert isinstance(position2, Position)

    delta_x = position2.x - position1.x
    delta_y = position2.y - position1.y

    if delta_x != 0 and delta_y != 0:   # droite quelconque
        pente = delta_y / delta_x
        ordonnee = position1.y - pente*position1.x

        pente_orthogonale = -1/pente
        ordonnee_orthogonale = reference.y - pente_orthogonale*reference.x

        # Calcul des coordonnées de la destination
        pos_x = (ordonnee_orthogonale - ordonnee)/(pente - pente_orthogonale)
        pos_y = pente*pos_x + ordonnee

    elif delta_x == 0:  # droite verticale
        pos_x = position1.x
        pos_y = reference.y

    elif delta_y == 0:  # droite horizontale
        pos_x = reference.x
        pos_y = position1.y

    return Position(pos_x, pos_y)


def get_time_to_travel(dist: float, speed: float, accel: float) -> float:
    """
        Calcul le temps nécessaire pour parcourir la distance, en fonction de
        la vitesse et de l'accélération actuelles.
        Args:
            dist: La distance à parcourir.
            speed: La vitesse actuelle.
            accel: L'accélération actuelle.
        Returns:
            Le temps nécessaire pour parcourir la distance.
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
        time1 = (-speed + m.sqrt(speed ** 2 + 4 * accel * dist)) / (2 * accel)
        time2 = (-speed - m.sqrt(speed ** 2 + 4 * accel * dist)) / (2 * accel)

        return time2 if time1 < time2 else time1


def get_first_to_arrive(distance1: float,
                        speed1: float,
                        acceleration1: float,
                        distance2: float,
                        speed2: float,
                        acceleration2: float):
    """
        Détermine quel objet va arriver en premier à sa destination.
        Args:
            distance1: La distance que l'objet 1 doit franchir.
            speed1: La vitesse actuelle de l'objet 1.
            acceleration1: L'accélération actuelle de l'objet 1.
            distance2: La distance que l'objet 2 doit franchir.
            speed2: La vitesse actuelle de l'objet 2.
            acceleration2: L'accélération actuelle de l'objet 2.
        Returns:
            1 si l'objet 1 va arriver en premier à sa destination, 2 sinon.
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
        return 1 if time1 < time2 else 2


def is_facing_point_and_target(player_position: Position,
                               point_position: Position,
                               target_position:
                               Position,
                               tolerated_angle: float) -> bool:
    """
        Détermine si l'angle entre le joueur et le point est suffisamment proche
        de celui du point à la cible. En d'autres mots, lorsqu'utilisé avec la balle
        comme point, on détermine si le joueur va botter la balle à sa cible.
        Dans ce cas, la stratégie doit assumer que le joueur est suffisamment
        près de la balle.
        Args:
            player_position: La position du joueur
            point_position: La position du point (possiblement la balle)
            target_position: La position où le joueur veut botter la balle
            tolerated_angle: Angle en radians pour que le botter soit possible
        Returns:
            Si le joueur est capable de faire le botté ou non.
    """
    assert isinstance(point_position, Position), "ball_position is not a Position"
    assert isinstance(player_position, Position), "player_position is not a Position"
    assert isinstance(target_position, Position), "target_position is not a Position"
    assert isinstance(tolerated_angle, (int, float)), "tolerated_angle is neither a int nor a float"

    angle_player_to_ball = get_angle(player_position, point_position)
    angle_ball_to_target = get_angle(point_position, target_position)
    angle_difference = abs(angle_player_to_ball - angle_ball_to_target)
    return angle_difference < tolerated_angle


def rotate_point_around_origin(point, origin, angle):
    # TODO: ajouter des unit tests
    sine = m.sin(angle)
    cos = m.cos(angle)

    x = point.x - origin.x
    y = point.y - origin.y

    new_x = x * cos - y * sine
    new_y = x * sine + y * cos

    new_x += origin.x
    new_y += origin.y

    new_point = Position(new_x, new_y)

    return new_point


def conv_position_2_list(position):
    """
    converti les datas d'un objet position en liste
    :param position:
    :return: liste des datas de l'objet
    """

    assert isinstance(position, Position)
    return [position.x, position.y]