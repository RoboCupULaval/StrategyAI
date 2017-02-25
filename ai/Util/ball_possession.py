# Under MIT License, see LICENSE.txt
from math import fabs

from RULEngine.Util.area import isInsideCircle
from RULEngine.Util.geometry import *
from RULEngine.Util.constant import *


def can_get_ball(game_state, player_id, target):
    player_position = game_state.get_player_pose(player_id).position
    ball_position = game_state.get_ball_position()

    if isInsideCircle(player_position, ball_position, RADIUS_TO_GRAB_BALL):

        if isFacingPointAndTarget(player_position, ball_position, target, ANGLE_TO_GRAB_BALL):
            return True

    return False


def has_ball(game_state, player_id):
    player_position = game_state.get_player_position(player_id)
    player_orientation = game_state.get_player_pose(player_id).orientation
    ball_position = game_state.get_ball_position()
    if fabs(player_orientation - get_angle(player_position, ball_position)) <= ANGLE_TO_GRAB_BALL:
        # si la balle est sur le kicker
        if isInsideCircle(player_position, ball_position, RADIUS_TO_HALT + 3):
            # si la balle est proche du robot
            return True
        else:
            return False


def has_ball_facing_target(game_state, player_id, target_position):
    player_position = game_state.get_player_position(player_id)
    ball_position = game_state.get_ball_position()

    if has_ball(game_state, player_id):
        if isFacingPointAndTarget(player_position, ball_position, target_position, ANGLE_TO_HALT):
            return True

    return False
