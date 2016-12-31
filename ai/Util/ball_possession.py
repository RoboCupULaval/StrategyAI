# Under MIT License, see LICENSE.txt

from RULEngine.Util.area import isInsideCircle
from RULEngine.Util.geometry import *
from RULEngine.Util.constant import *


def canGetBall(game_state, player_id, target):
    player_position = game_state.get_player_pose(player_id).position
    ball_position = game_state.get_ball_position()

    if isInsideCircle(player_position, ball_position, RADIUS_TO_GRAB_BALL):

        if isFacingPointAndTarget(player_position, ball_position, target, ANGLE_TO_GRAB_BALL):
            return True

    return False


def hasBall(info_manager, player_id):
    player_position = info_manager.get_player_position(player_id)
    ball_position = info_manager.get_ball_position()
    if isInsideCircle(player_position, ball_position, RADIUS_TO_HALT + POSITION_DEADZONE):
        return True


def hasBallFacingTarget(info_manager, player_id, point):
    player_position = info_manager.get_player_position(player_id)
    target_position = info_manager.get_player_target(player_id)

    if hasBall(info_manager, player_id):

        if isFacingPointAndTarget(player_position, point, target_position, ANGLE_TO_HALT):
            return True

    return False