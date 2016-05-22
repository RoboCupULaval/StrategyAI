#Under MIT License, see LICENSE.txt
from ..Util.Position import Position
from ..Util.geometry import * #this is a circular import
import math as m
from ..Util.constant import *

__author__ = 'RoboCupULaval'

# Question
def isInsideSquare(position, Y_TOP, Y_BOTTOM, X_LEFT, X_RIGHT):
    # Parameters assertions
    assert(isinstance(position, Position))
    assert(isinstance(Y_TOP, (int, float)))
    assert(isinstance(Y_BOTTOM, (int, float)))
    assert(isinstance(X_LEFT, (int, float)))
    assert(isinstance(X_RIGHT, (int, float)))
    assert(Y_TOP > Y_BOTTOM)
    assert(X_RIGHT > X_LEFT)

    if not Y_BOTTOM < position.y < Y_TOP:
        return False
    if not X_LEFT < position.x < X_RIGHT:
        return False
    return True

def isInsideCircle(position, center, radius):
    # Parameters assertions
    assert(isinstance(position, Position))
    assert(isinstance(center, Position))
    assert(isinstance(radius, (int, float)))
    assert(radius >= 0)

    if get_distance(position, center) < radius:
        return True
    else:
        return False

def isOutsideSquare(position, X_TOP, X_BOTTOM, Y_LEFT, Y_RIGHT):
    return not isInsideSquare(position, X_TOP, X_BOTTOM, Y_LEFT, Y_RIGHT)

def isOutsideCircle(position, center, radius):
    return not isInsideCircle(position, center, radius)

# Reform
def stayInsideSquare(position, Y_TOP, Y_BOTTOM, X_LEFT, X_RIGHT):
    # Parameters assertions
    assert(isinstance(position, Position))
    assert(isinstance(Y_TOP, (int, float)))
    assert(isinstance(Y_BOTTOM, (int, float)))
    assert(isinstance(X_LEFT, (int, float)))
    assert(isinstance(X_RIGHT, (int, float)))
    assert(Y_TOP > Y_BOTTOM)
    assert(X_RIGHT > X_LEFT)

    if isInsideSquare(position, Y_TOP, Y_BOTTOM, X_LEFT, X_RIGHT):
        return Position(position.x, position.y)
    else:
        pos_x = position.x
        pos_y = position.y

        if pos_y > Y_TOP:
            pos_y = Y_TOP
        elif pos_y < Y_BOTTOM:
            pos_y = Y_BOTTOM

        if pos_x > X_RIGHT:
            pos_x = X_RIGHT
        elif pos_x < X_LEFT:
            pos_x = X_LEFT

        return Position(pos_x, pos_y)

def stayInsideCircle(position, center, radius):
    # Parameters assertions
    if isInsideCircle(position, center, radius):
        return Position(position.x, position.y)
    else:
        pos_angle = get_angle(center, position)
        pos_x = radius * m.cos(pos_angle) + center.x
        pos_y = radius * m.sin(pos_angle) + center.y
        return Position(pos_x, pos_y)


def stayOutsideSquare(position, Y_TOP, Y_BOTTOM, X_LEFT, X_RIGHT):
    # Parameters assertions
    assert(isinstance(position, Position))
    assert(isinstance(Y_TOP, (int, float)))
    assert(isinstance(Y_BOTTOM, (int, float)))
    assert(isinstance(X_LEFT, (int, float)))
    assert(isinstance(X_RIGHT, (int, float)))
    assert(Y_TOP > Y_BOTTOM)
    assert(X_RIGHT > X_LEFT)

    if isOutsideSquare(position, Y_TOP, Y_BOTTOM, X_LEFT, X_RIGHT):
        return Position(position.x, position.y)
    else:
        pos_x = position.x
        pos_y = position.y

        if pos_y < Y_TOP:
            pos_y = Y_TOP
        elif pos_y > Y_BOTTOM:
            pos_y = Y_BOTTOM

        if pos_x < X_RIGHT:
            pos_x = X_RIGHT
        elif pos_x > X_LEFT:
            pos_x = X_LEFT

        return Position(pos_x, pos_y)

def stayOutsideCircle(position, center, radius):
    # Parameters assertions
    if isOutsideCircle(position, center, radius):
        return Position(position.x, position.y)
    else:
        pos_angle = get_angle(center, position)
        pos_x = radius * m.cos(pos_angle) + center.x
        pos_y = radius * m.sin(pos_angle) + center.y
        return Position(pos_x, pos_y)

def isInsideGoalArea(position, is_yellow):
    assert(isinstance(position, Position))
    assert(isinstance(is_yellow, bool))
    x_left = FIELD_GOAL_YELLOW_X_LEFT if is_yellow else FIELD_GOAL_BLUE_X_LEFT
    x_right = FIELD_GOAL_YELLOW_X_RIGHT if is_yellow else FIELD_GOAL_BLUE_X_RIGHT
    top_circle = FIELD_GOAL_YELLOW_TOP_CIRCLE if is_yellow else FIELD_GOAL_BLUE_TOP_CIRCLE
    bot_circle = FIELD_GOAL_YELLOW_BOTTOM_CIRCLE if is_yellow else FIELD_GOAL_BLUE_BOTTOM_CIRCLE
    if isInsideSquare(position, FIELD_GOAL_Y_TOP, FIELD_GOAL_Y_BOTTOM, x_left, x_right):
        if isInsideCircle(position, top_circle, FIELD_GOAL_RADIUS):
            return True
        elif isInsideCircle(position, bot_circle, FIELD_GOAL_RADIUS):
            return True
        return False
    else:
        return False

def isOutsideGoalArea(position, is_yellow):
    return not isInsideGoalArea(position, is_yellow)

def stayInsideGoalArea(position, is_yellow):
    # TODO Not tested: stayInsideGoalArea
    if isInsideGoalArea(position, is_yellow):
        return Position(position.x, position.y)
    else:
        x_left = FIELD_GOAL_YELLOW_X_LEFT if is_yellow else FIELD_GOAL_BLUE_X_LEFT
        x_right = FIELD_GOAL_YELLOW_X_RIGHT if is_yellow else FIELD_GOAL_BLUE_X_RIGHT
        position = stayInsideSquare(position, FIELD_GOAL_Y_TOP, FIELD_GOAL_Y_BOTTOM, x_left, x_right)
        if isInsideSquare(position, FIELD_GOAL_Y_TOP, FIELD_GOAL_Y_BOTTOM, x_left, x_right):
            return position
        else:
            circle_top = FIELD_GOAL_YELLOW_TOP_CIRCLE if is_yellow else FIELD_GOAL_BLUE_TOP_CIRCLE
            circle_bot = FIELD_GOAL_YELLOW_BOTTOM_CIRCLE if is_yellow else FIELD_GOAL_BLUE_BOTTOM_CIRCLE
            dst_top = get_distance(circle_top, position)
            dst_bot = get_distance(circle_bot, position)

            if dst_top >= dst_bot:
                return stayInsideCircle(position, circle_top, FIELD_GOAL_RADIUS)
            else:
                return stayInsideCircle(position, circle_bot, FIELD_GOAL_RADIUS)

def stayOutsideGoalArea(position, is_yellow):
    # TODO Not tested: stayOutsideGoalArea
    if isOutsideGoalArea(position, is_yellow):
        return Position(position.x, position.y)
    else:
        x_left = FIELD_GOAL_YELLOW_X_LEFT if is_yellow else FIELD_GOAL_BLUE_X_LEFT
        x_right = FIELD_GOAL_YELLOW_X_RIGHT if is_yellow else FIELD_GOAL_BLUE_X_RIGHT
        y_top = FIELD_GOAL_SEGMENT / 2
        y_bottom = (FIELD_GOAL_SEGMENT / 2) * -1
        circle_top = FIELD_GOAL_YELLOW_TOP_CIRCLE if is_yellow else FIELD_GOAL_BLUE_TOP_CIRCLE
        circle_bot = FIELD_GOAL_YELLOW_BOTTOM_CIRCLE if is_yellow else FIELD_GOAL_BLUE_BOTTOM_CIRCLE
        position = stayOutsideSquare(position, y_top, y_bottom, x_left, x_right)
        position = stayOutsideCircle(position, circle_top, FIELD_GOAL_RADIUS)
        position = stayOutsideCircle(position, circle_bot, FIELD_GOAL_RADIUS)
        return Position(position.x, position.y)
