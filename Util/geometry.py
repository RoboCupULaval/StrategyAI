# Under MIT License, see LICENSE.txt
from ..Util.Position import Position
from ..Game.Player import Player
import math as m

__author__ = 'RoboCupULaval'


def get_distance(position_1, position_2):
    """
    Distance between two positions.
    :param position_1: Position
    :param position_2: Position
    :return: float - distance in millimeter
    """
    assert(isinstance(position_1, Position))
    assert(isinstance(position_2, Position))
    return m.sqrt((position_2.x - position_1.x) ** 2 + (position_2.y - position_1.y) ** 2)


def get_angle(main_position, other):
    """
    Angle between position1 and position2 between -pi and pi
    :param main_position: Position of reference
    :param other: Position of object
    :return: float angle between two positions in radians
    """
    assert isinstance(main_position, Position), "TypeError main_position"
    assert isinstance(other, Position), "TypeError other"

    position_x = float(other.x - main_position.x)
    position_y = float(other.y - main_position.y)
    return m.atan2(position_y, position_x)


def cvt_angle_360(orientation):
    """
    Convert radians angle to 0-360 degrees
    :param orientation: float angle in radians
    :return: int angle with 0 to 360 range.
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
    return int(orientation)


def cvt_angle_180(orientation):
    """
    Convert radians angle to -180-180 degrees (same as m.degrees())
    :param orientation: float angle in radians
    :return: int angle with 180 to -179 range.
    """
    assert isinstance(orientation, (int, float)), "TypeError orientation"

    orientation = cvt_angle_360(orientation)
    if orientation > 180:
        return orientation-360
    elif orientation <= -180:
        return orientation+360
    else:
        return int(orientation)


def get_nearest(ref_position, list_of_position, number=1):
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
    Convert the time in seconds represented as a float into milliseconds int
    :param time_sec: The time as seconds float
    :return: The time as milliseconds int
    """
    assert isinstance(time_sec, float)
    return int(round(time_sec * 1000))


def det(a, b):
    """
    Compute the determinant of the matrix
    [a.x  a.y]
    [b.x  b.y]
    :param a: The first position
    :param b: The second position
    :return: The determinant as a float
    """
    assert(isinstance(a, Position))
    assert(isinstance(b, Position))
    return a.x * b.y - a.y * b.x


def get_line_equation(point1, point2):
    """
    Calcul l'équation de la droite formée par deux points.
    :param point1: Le premier point de la droite.
    :param point2: Le second point de la droite.
    :exception ZeroDivisionError: Une exception est soulevée si la droite est verticale.
    :return: Un tuple contenant la pente et l'ordonnée à l'origine (a, b).
    """
    assert isinstance(point1, Position)
    assert isinstance(point2, Position)

    delta_x = point2.x - point1.x
    delta_y = point2.y - point1.y

    a = delta_y / delta_x
    b = point1.y - a * point1.x

    return a, b


def get_lines_intersection(point_a1, point_a2, point_b1, point_b2):
    """
    Compute the position of the intersection of the two lines given by the four points.
    :param point_a1: Point 1 on line A
    :param point_a2: Point 2 on line A
    :param point_b1: Point 1 on line B
    :param point_b2: Point 2 on line B
    :return: The position of the intersection of the two lines. Infinity if the lines are parallels.
    """
    assert isinstance(point_a1, Position)
    assert isinstance(point_a2, Position)
    assert isinstance(point_b1, Position)
    assert isinstance(point_b2, Position)

    delta_x_a = point_a1.x - point_a2.x
    delta_y_a = point_a1.y - point_a2.y
    delta_x_b = point_b1.x - point_b2.x
    delta_y_b = point_b1.y - point_b2.y

    denominator = delta_x_a * delta_y_b - delta_y_a * delta_x_b
    if denominator == 0:
        # Les lignes sont parallèles
        return Position(9999999, 9999999)

    # The purpose of the determinant det1 and det2 is to reduce the number of multiplications
    det1 = point_a1.x * point_a2.y - point_a1.y * point_a2.x
    det2 = point_b1.x * point_b2.y - point_b1.y * point_b2.x

    x = (det1 * delta_x_b - det2 * delta_x_a)
    y = (det1 * delta_y_b - det2 * delta_y_a)
    return Position(x, y)


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


def get_time_to_travel(dist, speed, accel):
    """
    Compute the time required to travel a given distance at the current speed and acceleration
    :param dist: The distance to travel
    :param speed: The current speed
    :param accel: The current acceleration
    :return: The time required to travel the distance as a float
    """
    assert isinstance(dist, (int, float))
    assert isinstance(speed, (int, float))
    assert isinstance(accel, (int, float))

    if accel == 0:
        if speed == 0:
            return 9999999
        else:
            return dist / speed
    else:
        time1 = (-speed + m.sqrt(speed ** 2 - 4 * accel * dist)) / (2 * accel)
        time2 = (-speed - m.sqrt(speed ** 2 - 4 * accel * dist)) / (2 * accel)

        return time2 if time1 < time2 else time1


def get_first_to_arrive(distance1, speed1, acceleration1, distance2, speed2, acceleration2):
    """
    Determine which object will arrive first to its destination
    :param distance1: The distance to be completed by the object 1
    :param speed1: The current speed of the object 1
    :param acceleration1: The current acceleration of the object 1
    :param distance2: The distance to be completed by the object 2
    :param speed2: The current speed of the object 2
    :param acceleration2: The current acceleration of the object 2
    :return: 1 if the object 1 will arrive first to the destination, 2 otherwise
    """
    assert isinstance(distance1, (int, float))
    assert isinstance(speed1, (int, float))
    assert isinstance((acceleration1, (int, float)))
    assert isinstance(distance2, (int, float))
    assert isinstance(speed2, (int, float))
    assert isinstance((acceleration2, (int, float)))

    time1 = get_time_to_travel(distance1, speed1, acceleration1)
    time2 = get_time_to_travel(distance2, speed2, acceleration2)

    if time1 == time2:
        return 0
    else:
        return 2 if time1 < time2 else 1
