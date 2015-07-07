from ..Util.Position import Position
import math as m

__author__ = 'jbecirovski'


def distance(position_1, position_2):
    """
    Distance between two positions.
    :param position_1: Position
    :param position_2: Position
    :return: float - distance in millimeter
    """
    assert(isinstance(position_1, Position))
    assert(isinstance(position_2, Position))
    return m.sqrt((position_2.x - position_1.x) ** 2 + (position_2.y - position_1.y) ** 2)

def angle(position1, position2):
    """
    Angle between position1 and position2 between 0 and 360 degrees
    :param position1: Position of reference
    :param position2: Position of object
    :return: int angle between two positions
    """
    assert isinstance(position1, Position), "TypeError position1"
    assert isinstance(position2, Position), "TypeError position2"

    position_x = position1.x-position2.x
    position_y = position1.y-position2.y

    if position_x == 0:
        if position_y > 0:
            return 270
        else:
            return 90
    else:
        angleReturned = int(m.degrees(m.atan((position1.y-position2.y)/(position1.x-position2.x))))
        if position_x > 0:
            if position_y > 0:
                return int(180+angleReturned)
            else:
                return int(180+angleReturned)
        else:
            if position_y > 0:
                return int(360+angleReturned)
            else:
                return int(m.fabs(angleReturned))

def convertAngle360(orientation):
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

def convertAngle180(orientation):
    """
    :param orientation: float angle
    :return: int angle with 180 to -179 range.
    """
    assert isinstance(orientation, (int, float)), "TypeError orientation"

    orientation = convertAngle360(orientation)
    if orientation > 180:
        return orientation-360
    elif orientation <= -180:
        return orientation+360
    else:
        return int(orientation)

def theta(x, y):
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
