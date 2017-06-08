# Under MIT License, see LICENSE.txt
import math as m

import numpy as np

from ..Util.Position import Position
from ..Util.Pose import Pose

__author__ = 'RoboCupULaval'


def remove_duplicates(seq, concurent_list=None, round_up_threshold=1):
    seen = set()
    seen2 = set()
    seen_add = seen.add
    seen2_add = seen2.add
    seq_rounded = round_position_to_number(seq, round_up_threshold)
    if concurent_list is None:
        return [x for idx, x in enumerate(seq) if not seq_rounded[idx] in seen or seen_add(seq_rounded[idx])]
    else:
        return [x for idx, x in enumerate(seq) if not seq_rounded[idx] in seen or seen_add(seq_rounded[idx])], \
               [y for idx, y in enumerate(concurent_list) if not seq[idx] in seen2 or seen2_add(seq[idx])]


def round_position_to_number(positions, base=5):

    for position in positions:
        position.x = int(base * round(float(position.x)/base))
        position.y = int(base * round(float(position.y)/base))
    return positions


def get_distance(position_1: Position, position_2: Position) -> float:
    """
        Calcul la distance entre deux positions (la norme du vecteur reliant les deux points).
        Args:
            position_1: Position 1.
            position_2: Position 2.
        Returns:
            La distance en millimètres entre les deux positions
    """
    # assert isinstance(position_1, Position)
    # assert isinstance(position_2, Position)
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


def get_angle_between_three_points(pointA : Position, pointO : Position, pointB : Position):
    A = pointA.conv_2_np()
    B = pointB.conv_2_np()
    O = pointO.conv_2_np()
    AO = O - A
    OB = B - O
    if np.linalg.norm(AO) != 0 and np.linalg.norm(OB) != 0 :
        AO /= np.linalg.norm(AO)
        OB /= np.linalg.norm(OB)
    return np.arccos(np.linalg.dot(AO, OB))


def conv_position_2_list(position: Position):
    """
    convertit les datas d'un objet position en liste
    :param position:
    :return: liste des datas de l'objet
    """

    return [position.x, position.y]


def normalized(vector: np.ndarray) -> np.ndarray:
    if np.linalg.norm(vector) > 0:
        return vector / np.linalg.norm(vector)
    else:
        return vector


def orientation(vector: np.ndarray) -> np.ndarray:
    return np.arctan2(vector[1], vector[0])


def robot2fixed(vector: np.ndarray, angle: float) -> np.ndarray:
    tform = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return np.dot(tform, vector)


def fixed2robot(vector: np.ndarray, angle: float) -> np.ndarray:
    return robot2fixed(vector, -angle)