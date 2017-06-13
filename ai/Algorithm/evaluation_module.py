# Under MIT License, see LICENSE.txt

import numpy as np

from RULEngine.Util import Position
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import PLAYER_PER_TEAM, TeamColor
from RULEngine.Util.geometry import *
from RULEngine.Util.team_color_service import TeamColorService
from ai.states.game_state import GameState


def player_with_ball(min_dist_from_ball):
    # Retourne le joueur qui possède la balle, NONE si balle libre
    closest_player = closest_player_to_point(GameState().get_ball_position())
    if closest_player[0][1] < min_dist_from_ball:
        return closest_player[0][0]
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
            list_player.append((i, player_distance))
    if not our_team or our_team == None:
        for i in GameState().other_team.available_players.values():
            # les players ennemis
            player_distance = get_distance(i.pose.position, point)
            list_player.append((i, player_distance))

    list_player = sorted(list_player, key=lambda x: x[1])

    return list_player


def is_ball_moving(min_speed=0.1):
    return np.norm(GameState().get_ball_velocity().conv_2_np() ) > min_speed


def is_ball_our_side():
    # Retourne TRUE si la balle est dans notre demi-terrain
    if GameState().const["FIELD_GOAL_YELLOW_X_LEFT"] > 0:
        if TeamColorService().OUR_TEAM_COLOR is TeamColor.BLUE_TEAM: # BLUE_TEAM
            return GameState().get_ball_position().x < 0
        else: # YELLOW_TEAM
            return GameState().get_ball_position().x > 0
    else:
        if TeamColorService().OUR_TEAM_COLOR is TeamColor.BLUE_TEAM: # BLUE_TEAM
            return GameState().get_ball_position().x > 0
        else: # YELLOW_TEAM
            return GameState().get_ball_position().x < 0


def is_target_reached(player, target: Position, min_dist=0.01):
    # Retourne TRUE si dans un rayon de l'objectif
    return get_distance(target, player.pose.position) < min_dist


def best_passing_option(passing_player):
    # Retourne l'ID du player ou le but le mieux placé pour une passe, NONE si but est la meilleure possibilité

    score_min = float("inf")
    if TeamColorService().OUR_TEAM_COLOR is TeamColor.YELLOW_TEAM :# YELLOW_TEAM
        goal = Position(GameState().field.constant["FIELD_GOAL_BLUE_X_LEFT"], 0)
    else:
        goal = Position(GameState().field.constant["FIELD_GOAL_YELLOW_X_RIGHT"], 0)

    for i in GameState().my_team.available_players.values():
        if i is not passing_player:
            # Calcul du score pour passeur vers receveur
            score = line_of_sight_clearance(passing_player, i.pose.position)

            # Calcul du score pour receveur vers but
            score += line_of_sight_clearance(i, goal)
            score = np.log(score)
            if score_min > score:
                score_min = score
                receiver_id = i
            print('player position :', i.pose.position, score, i.id)

    score = np.log(line_of_sight_clearance(passing_player, goal))
    if score_min > score:
        receiver_id = None
    print(score, 'but')


    return receiver_id


def line_of_sight_clearance(player, target: Position):
    # Retourne un score en fonction du dégagement de la trajectoire (plus c'est dégagé plus le score est petit),
    # NONE si obstacle dans l'ellipse
    score = np.linalg.norm(player.pose.position - target)
    for j in GameState().my_team.available_players.values():
        # Obstacle : les players friends
        if not j.id == player.id:
            score *= trajectory_score(player.pose.position, target, j.pose.position)
    # for j in GameState().other_team.available_players.values():
    #     # Obstacle : les players ennemis
    #     score *= trajectory_score(player.pose.position, target, j.pose.position)
    return score


def trajectory_score(pointA : Position, pointB: Position, obstacle: Position):
    # Retourne un score en fonction de la distance de l'obstacle par rapport à la trajectoire AB
    AB = pointB - pointA
    AO = obstacle - pointA
    normAC = np.dot(AB, AO) / np.linalg.norm(AB)
    normOC = np.sqrt(np.linalg.norm(AO) ** 2 - (normAC) ** 2)
    if (normAC < 0) or (normAC > 1.1 * np.linalg.norm(AB)):
        return 1
    else:
        return max(1, min(normAC / normOC, 100000))


def is_player_facing_target(player, target_position: Position, tolerated_angle: float) -> bool:
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

    player_front = Position(player.pose.position.x + np.cos(player.pose.orientation),
                            player.pose.position.y + np.sin(player.pose.orientation))
    return get_angle_between_three_points(player_front, player.pose.position, target_position)< tolerated_angle


def ballDirection(self):
    pass # TODO :


