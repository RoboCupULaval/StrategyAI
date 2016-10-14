# Under MIT license, see LICENSE.txt

from math import cos, sin

from RULEngine.Util.Position import Position
from RULEngine.Util.constant import PLAYER_PER_TEAM, ROBOT_RADIUS,BALL_RADIUS
from RULEngine.Util.geometry import get_closest_point_on_line, get_distance
from ai.states.InfoManager import InfoManager

__author__ = 'RoboCupULaval'


def raycast(info_manager, initial_position, length, direction, width, blue_players_ignored, yellow_players_ignored,
            is_ball_ignored=True):
    assert isinstance(info_manager, InfoManager)
    assert isinstance(initial_position, Position)
    assert isinstance(length, (int, float))
    assert isinstance(direction, (int, float))
    assert isinstance(width, (int, float))
    assert isinstance(blue_players_ignored, list)
    assert isinstance(yellow_players_ignored, list)
    assert isinstance(is_ball_ignored, bool)

    final_position = Position(initial_position.x + length*cos(direction), initial_position.y + length*sin(direction))
    return raycast2(info_manager, initial_position, final_position, width, blue_players_ignored, yellow_players_ignored,
                    is_ball_ignored)


def raycast2(info_manager, initial_position, final_position, width, blue_players_ignored, yellow_players_ignored,
             is_ball_ignored=True):
    assert isinstance(info_manager, InfoManager)
    assert isinstance(initial_position, Position)
    assert isinstance(final_position, Position)
    assert isinstance(width, (int, float))
    assert isinstance(blue_players_ignored, list)
    assert isinstance(yellow_players_ignored, list)
    assert isinstance(is_ball_ignored, bool)

    for i in range(0, PLAYER_PER_TEAM):
        if i not in blue_players_ignored:
            player_position = info_manager.get_player_position(i)
            pos = get_closest_point_on_line(player_position, initial_position, final_position)
            if get_distance(player_position, pos) <= width + ROBOT_RADIUS:
                return True

        if i not in yellow_players_ignored:
            enemy_position = info_manager.get_enemy_position(i)
            pos = get_closest_point_on_line(enemy_position, initial_position, final_position)
            if get_distance(enemy_position, pos) <= width + ROBOT_RADIUS:
                return True

    if not is_ball_ignored:
        ball_position = info_manager.get_ball_position()
        pos = get_closest_point_on_line(ball_position, initial_position, final_position)
        if get_distance(ball_position, pos) <= width + BALL_RADIUS:
            return True

    return False
