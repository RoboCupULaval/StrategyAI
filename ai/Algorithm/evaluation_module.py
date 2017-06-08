# Under MIT License, see LICENSE.txt

import numpy as np

from RULEngine.Util import Position
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.geometry import *
from ai.states.game_state import GameState


def player_with_ball(min_dist_from_ball):
    # Retourne le joueur qui possède la balle, NONE si balle libre
    closest_player = closest_player_to_point(GameState().get_ball_position())
    if closest_player[2] < min_dist_from_ball:
        return closest_player
    else:
        return None


def closest_player_to_point(point: Position, our_team = None):
    # Retourne une liste de tuples (player, distance) en ordre croissant de distance,
    # our_team pour obtenir une liste contenant une équipe en particulier
    list_player = []
    if our_team or our_team == None:
        for i in GameState().my_team.available_players.values():
            # les players friends
            player_distance = get_distance(i.pose.position, point)
            list_player.append(i, player_distance)
    if not our_team or our_team == None:
        for i in GameState().other_team.available_players.values():
            # les players ennemis
            player_distance = get_distance(i.pose.position, point)
            list_player.append(i, player_distance)

    list_player = sorted(list_player, key=lambda x: x[1])

    return list_player


def is_ball_moving(min_speed=0.1):
    return GameState().get_ball_velocity() > min_speed


def is_ball_our_side():
    # Retourne TRUE si la balle est dans notre demi-terrain
    pass # TODO :


def is_target_reached(player_id, target: Position, min_dist=0.01):
    # Retourne TRUE si dans un rayon de l'objectif
    return get_distance(target, GameState().get_player_position(player_id)) < min_dist


def best_passing_option(passing_player):
    # Retourne l'ID du player ou le but le mieux placé pour une passe, NONE si aucune possibilité
    passing = GameState().get_player_position(passing_id).conv_2_np()

    score_max = 0
    if not GameState().our_team_color :# YELLOW_TEAM
        goal = (Pose(Position(GameState().const["FIELD_GOAL_BLUE_X_LEFT"], 0), 0))
    else:
        goal = (Pose(Position(GameState().const["FIELD_GOAL_YELLOW_X_LEFT"], 0), 0))

    for i in range(PLAYER_PER_TEAM):
        # Calcul du score pour passeur vers receveur
        score = line_of_sight_clearance(passing_id, GameState().get_player_position(i))

        # Calcul du score pour receveur vers but
        score += line_of_sight_clearance(i, goal)
        if score_max < score:
            score_max = score
            receiver_id = i

    score = line_of_sight_clearance(i, goal) *2
    if score_max < score:
        score_max = score
        receiver_id = i

    return receiver_id


def line_of_sight_clearance(player, target: Position):
    # Retourne un score en fonction du dégagement de la trajectoire (plus c'est dégagé plus le score est grand),
    # NONE si obstacle dans l'ellipse
    score = 0
    for j in GameState().my_team.available_players.values():
        # Obstacle : les players friends
        if not j.id == player.id:
            score += trajectory_ellipse_score(player.pose.position, target, j.pose.position)
    for j in GameState().other_team.available_players.values():
        # Obstacle : les players ennemis
        score += trajectory_ellipse_score(player.pose.position, target, j.pose.position)
    return score


def trajectory_ellipse_score(pointA : Position, pointB: Position, obstacle: Position):
    # Retourne un score en fonction de la distance de l'obstacle par rapport à la trajectoire AB
    pointA = pointA.conv_2_np()
    pointB = pointB.conv_2_np()
    obstacle = obstacle.conv_2_np()
    return np.linalg.norm(obstacle - pointA) + np.linalg.norm(pointB - obstacle) - np.linalg.norm(pointB - pointA)


def is_player_facing_target(player_ID, target_position: Position, tolerated_angle: float) -> bool:
    """
        Détermine si l'angle entre le devant du joueur et la cible est suffisamment petit
        Args:
            player_ID: Le joueur
            target_position: La position où le joueur veut faire face
            tolerated_angle: Angle en radians
        Returns:
            Si le joueur est face à la cible.
    """
    assert isinstance(target_position, Position), "target_position is not a Position"
    assert isinstance(tolerated_angle, (int, float)), "tolerated_angle is neither a int nor a float"

    player_pose = GameState().get_player_pose()
    player_position = player_pose.position
    player_front = Position(player_position.x + np.cos(player_pose.orientation),
                            player_position.y + np.sin(player_pose.orientation))
    return get_angle_between_three_points(player_front, player_position, target_position)< tolerated_angle


def ballDirection(self):
    pass # TODO :


