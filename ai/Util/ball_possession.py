# Under MIT License, see LICENSE.txt

from RULEngine.Util.area import isInsideCircle
from RULEngine.Util.geometry import *


def player_can_grab_ball(game_state, player_id, target):
    player_position = game_state.get_player_pose(player_id).position
    ball_position = game_state.get_ball_position()

    if isInsideCircle(player_position, ball_position, RADIUS_TO_GRAB_BALL):

        if angle_to_ball_is_tolerated(player_position, ball_position, target, ANGLE_TO_GRAB_BALL):
            return True

    return False


def player_grabbed_ball(game_state, player_id, target):
    player_position = game_state.get_player_pose(player_id).position
    ball_position = game_state.get_ball_position()

    if isInsideCircle(player_position, ball_position, RADIUS_TO_HALT):

        if angle_to_ball_is_tolerated(player_position, ball_position, target, ANGLE_TO_HALT):
            return True

    return False
