# Under MIT License, see LICENSE.txt

import numpy as np

from RULEngine.Util import Position
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.geometry import *
from ai.states.game_state import GameState


def player_with_ball():
    # Retourne le joueur qui possède la balle, NONE si balle libre
    pass

def closest_player_to_ball():
    # Retourne le joueur le plus près de la balle,
    pass

def is_ball_moving(min_speed=0.1):
    pass

def is_ball_our_side():
    # Retourne TRUE si la balle est dans notre demi-terrain
    pass


def best_passing_option(passing_id):
    # Retourne l'ID du player ou le but le mieux placé pour une passe, NONE si aucune possibilité
    passing = GameState().get_player_position(passing_id).conv_2_np()
    score_max = 0
    if not GameState().our_team_color :# YELLOW_TEAM
        goal = (Pose(Position(GameState().const["FIELD_GOAL_YELLOW_X_LEFT"], 0), 0))
    else:
        goal = (Pose(Position(GameState().const["FIELD_GOAL_BLUE_X_LEFT"], 0), 0))

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


def line_of_sight_clearance(player_ID, target: Position):
    # Retourne un score en fonction du dégagement de la trajectoire (plus c'est dégagé plus le score est grand),
    # NONE si obstacle dans l'ellipse
    score = 0
    for j in range(PLAYER_PER_TEAM):
        # Obstacle : les players friends
        if not j == player_ID:
            obstacle = GameState().get_player_position(j, True)
            score += trajectory_ellipse_score(GameState().get_player_position(player_ID), target, obstacle)
    for j in range(PLAYER_PER_TEAM):
        # Obstacle : les players ennemis
        obstacle = GameState().get_player_position(j, False)
        score += trajectory_ellipse_score(GameState().get_player_position(player_ID), target, obstacle)
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
    pass


