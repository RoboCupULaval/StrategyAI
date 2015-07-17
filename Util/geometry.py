from ..Util.Position import Position
import math as m

__author__ = 'jbecirovski'


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
    Angle between position1 and position2 between 0 and 360 degrees
    :param main_position: Position of reference
    :param other: Position of object
    :return: int angle between two positions
    """
    assert isinstance(main_position, Position), "TypeError main_position"
    assert isinstance(other, Position), "TypeError other"

    position_x = float(other.x - main_position.x)
    position_y = float(other.y - main_position.y)
    if position_x == 0:
        if position_y > 0:
            return 90
        else:
            return 270
    else:
        final_angle = cvt_angle_360(m.atan2(position_y, position_x) * 180 / m.pi)
        return int(final_angle)

def cvt_angle_360(orientation):
    """
    Convert angle with 0 to 360 degrees
    :param orientation: float angle
    :return: int angle with 0 to 360 range.
    """
    assert isinstance(orientation, (int, float)), "TypeError orientation"

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
    :param orientation: float angle
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

def get_theta(x, y):
    assert(isinstance(x, (int, float)))
    assert(isinstance(y, (int, float)))

    if x == 0:
        if y > 0:
            return 270
        else:
            return 90
    else:
        angleReturned = int(m.degrees(m.atan(y/x)))
        if x > 0:
            if y > 0:
                return int(180+angleReturned)
            else:
                return int(180+angleReturned)
        else:
            if y > 0:
                return int(360+angleReturned)
            else:
                return int(m.fabs(angleReturned))

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