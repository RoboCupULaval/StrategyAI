from ..Util.Position import Position
from ..Game.Player import Player
import math as m
import numpy as np
from . import area  #this is a circular import

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
"""
def get_theta(x, y):

    Note : this function is now useless as it does the same as m.atan2(y,x)

    :param x:
    :param y:
    :return: int angle with 0 to 360 range.

    assert(isinstance(x, (int, float)))
    assert(isinstance(y, (int, float)))

    if x == 0:
        if y > 0:
            return 90
        else:
            return 270
    else:
        angleReturned = int(m.degrees(m.atan(y/x)))
        if x > 0:
            if y > 0:
                return angleReturned
            else:
                return 360+angleReturned
        else:
            return 180+angleReturned
"""
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

def intercept(player, target1, target2, threshold = 0):
    #TODO : test this function
    """
    :param player: the current robot
    :param target1: the position of the ball
    :param target2: the position of the object to cover
    :param treshold: the minimum distance between player and target2
    :return: the nearest position from the current robot on the line between target1 and target2
    this position must be between target1 and target2
    """
    assert(isinstance(player, Player))
    assert(isinstance(target1, Position))
    assert(isinstance(target2, Position))
    assert(isinstance(threshold, (int, float)))

    #linear algebra for finding closest point on the line
    position = player.pose.position
    d1 = target1.x - target2.x
    d2 = target1.y - target2.y
    c1 = d2*target1.x - d1*target1.y
    c2 = d1*position.x + d2*position.y
    a = np.array([[d2, -1*d1], [d1, d2]])
    b = np.array([c1, c2])
    try:
        X = np.linalg.solve(a,b)
        destination = Position(X[0], X[1])
        if (get_distance(target1, destination) >= get_distance(target1, target2)):      #if target2 between target1 and destination
            norme = m.hypot(d1,d2)
            destination = Position(300*d1/norme + target2.x, 300*d2/norme + target2.y)  #go 300 unit in front of target2 on the line
        elif (get_distance(target2, destination) >= get_distance(target1, target2)):    #if target1 between target2 and destination
            norme = m.hypot(d1,d2)
            destination = Position(-300*d1/norme + target1.x, -300*d2/norme + target1.y)#go 300 unit in front of target1 on the line
        return area.stayOutsideCircle(destination, target2, threshold)
    except np.linalg.linalg.LinAlgError:
        return position         #return the robot's current position
