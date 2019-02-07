# Under MIT License, see LICENSE.txt
import logging
from typing import List

import numpy as np

from Util.geometry import Line, angle_between_three_points, perpendicular, wrap_to_pi, closest_point_on_line, normalize
from Util.position import Position
from Util.role import Role
from Util.constant import ROBOT_RADIUS
from ai.Algorithm.path_partitionner import Obstacle
from ai.GameDomainObjects import Player
from ai.states.game_state import GameState


class PlayerPosition(object):
    def __init__(self, player, distance):
        self.player = player
        self.distance = distance


def player_with_ball(min_dist_from_ball, is_our_team: bool):
    # Retourne le joueur qui possède la balle, NONE si balle libre
    closest_player = closest_player_to_point(GameState().ball_position, is_our_team)
    if closest_player.distance < min_dist_from_ball:
        return closest_player.player
    else:
        return None


def object_pointing_toward_point(object_position, object_orientation, point, angle_tolerance=90 * np.pi / 180):
    return abs((object_orientation - (point - object_position).angle)) < angle_tolerance / 2


def player_pointing_toward_segment(player: Player, segment: Line):
    angle_bisection = angle_between_three_points(segment.p1, player.position, segment.p2) / 2
    angle_reference = angle_bisection + (segment.p2 - player.position).angle
    return abs(player.pose.orientation - angle_reference) < angle_bisection


def player_covered_from_goal(player: Player):
    ball_position = GameState().ball.position
    shooting_angle = angle_between_three_points(GameState().field.their_goal_line.p1,
                                                ball_position, GameState().field.their_goal_line.p2)
    vec_ball_to_goal = GameState().field.their_goal - ball_position

    our_team = [other_player for other_player in GameState().our_team.available_players.values() if
                other_player is not player]
    enemy_team = [other_player for other_player in GameState().enemy_team.available_players.values()]
    pertinent_collisions = []
    for other_player in our_team + enemy_team:
        if object_pointing_toward_point(ball_position,
                                        vec_ball_to_goal.angle,
                                        other_player.position,
                                        wrap_to_pi(shooting_angle + 5 * np.pi / 180)):
            pertinent_collisions.append(Obstacle(other_player.position.array, avoid_distance=90))

    if not any(pertinent_collisions):
        return GameState().field.their_goal
    pertinent_collisions_positions = np.array([obs.position for obs in pertinent_collisions])
    pertinent_collisions_avoid_radius = np.array([obs.avoid_distance for obs in pertinent_collisions])
    results = []
    nb_beam = 15
    their_goal_line = GameState().field.their_goal_line
    for i in range(0, nb_beam + 1):  # discretisation de la ligne de but
        goal_point = their_goal_line.p1 + their_goal_line.direction * (their_goal_line.length * i / nb_beam)
        is_colliding = is_path_colliding(pertinent_collisions, pertinent_collisions_positions,
                                         pertinent_collisions_avoid_radius, ball_position.array, goal_point.array)
        results.append((is_colliding, goal_point))
    max_len_seg, index_end = find_max_consecutive_bool(results)

    if max_len_seg == 0 and index_end == 0:
        return None
    middle_idx = int(index_end - 1 - max_len_seg // 2)
    return results[middle_idx][1]


def find_max_consecutive_bool(results):
    count = 0
    max_len_seg = 0  # longueur du segment
    index_end = 0

    for i, (is_colliding, _) in enumerate(results):
        if not is_colliding:
            count += 1
        else:
            if count > max_len_seg:
                max_len_seg = count
                index_end = i
            count = 0
    if count > max_len_seg:
        max_len_seg = count
        index_end = i
    return max_len_seg, index_end


def is_path_colliding(obstacles, obstacles_position, obstacles_avoid_radius, start, target) -> bool:
    collisions, _ = find_collisions(obstacles, obstacles_position, obstacles_avoid_radius, start, target)
    return any(collisions)


def find_collisions(obstacles: List[Obstacle], obstacles_position: np.ndarray, obstacles_avoid_radius: np.ndarray,
                    start: np.ndarray, target: np.ndarray):
    # fonction prend en argument des positions converties en array!
    # Position().array par exemple.
    robot_to_obstacles = obstacles_position - start
    robot_to_obstacle_norm = np.linalg.norm(robot_to_obstacles, axis=1)
    obstacles_avoid_distance = obstacles_avoid_radius
    segment_direction = (target - start) / np.linalg.norm(target - start)
    dists_from_path = np.abs(np.cross(segment_direction, robot_to_obstacles))
    is_collision = dists_from_path < obstacles_avoid_distance
    obstacles = np.array(obstacles)

    return obstacles[is_collision].tolist(), robot_to_obstacle_norm[is_collision]


# noinspection PyUnusedLocal
def closest_players_to_point(point: Position, is_our_team: bool):
    # Retourne une liste de tuples (player, distance) en ordre croissant de distance,
    # is_our_team pour obtenir une liste contenant une équipe en particulier
    list_player = []
    if is_our_team:
        for i in GameState().our_team.available_players.values():
            # les players friends
            player_distance = (i.pose.position - point).norm
            list_player.append(PlayerPosition(i, player_distance))
    else:
        for i in GameState().enemy_team.available_players.values():
            # les players ennemis
            player_distance = (i.pose.position - point).norm
            list_player.append(PlayerPosition(i, player_distance))
    list_player = sorted(list_player, key=lambda x: x.distance)
    return list_player


def closest_player_to_point(point: Position, is_our_team: bool):
    # Retourne le player le plus proche,
    # is_our_team pour obtenir une liste contenant une équipe en particulier
    return closest_players_to_point(point, is_our_team)[0]


def closest_players_to_point_except(point: Position, except_roles=[], except_players=[]):
    closests = closest_players_to_point(point, is_our_team=True)
    ban_players = except_players.copy()
    ban_players += [GameState().get_player_by_role(r) for r in except_roles]
    return [player_dist for player_dist in closests if player_dist.player not in ban_players]


# noinspection PyUnresolvedReferences
def is_ball_our_side():
    # Retourne TRUE si la balle est dans notre demi-terrain
    return GameState().ball_position.x > 0


# noinspection PyUnresolvedReferences
def best_passing_option(passing_player, passer_can_kick_in_goal=True):
    # Retourne l'ID du player ou le but le mieux placé pour une passe, NONE si but est la meilleure possibilité

    score_min = float("inf")
    goal = GameState().field.their_goal

    receiver = None
    for p in GameState().our_team.available_players.values():
        try:
            is_goaler = p == GameState().get_player_by_role(Role.GOALKEEPER)
        except KeyError:
            is_goaler = False
        if p != passing_player and not is_goaler:
            # Calcul du score pour passeur vers receveur
            score = line_of_sight_clearance(passing_player, p.pose.position)

            # Calcul du score pour receveur vers but
            score += line_of_sight_clearance(p, goal)
            if score_min > score:
                score_min = score
                receiver = p

    if passer_can_kick_in_goal and not is_ball_our_side():
        score = (line_of_sight_clearance(passing_player, goal))
        if score_min > score:
            receiver = None

    return receiver


def line_of_sight_clearance(player, target):
    # Retourne un score en fonction du dégagement de la trajectoire (plus c'est dégagé plus le score est petit)
    score = (player.pose.position - target).norm
    for p in GameState().our_team.available_players.values():
        # Obstacle : les players friends
        if not (p.id == player.id):
            if target is not p.pose.position:
                score *= trajectory_score(player.pose.position, target, p.pose.position)
    for p in GameState().enemy_team.available_players.values():
        # Obstacle : les players ennemis
        score *= trajectory_score(player.pose.position, target, p.pose.position)
    return score


def ball_going_toward_player(game_state, player):
    if game_state.ball.is_mobile(50):  # to avoid division by zero and unstable ball_directions
        ball_approach_angle = np.arccos(np.dot(normalize(player.position - game_state.ball.position).array,
                                               normalize(game_state.ball.velocity).array)) * 180 / np.pi
        return ball_approach_angle < 25
    return False


def ball_not_going_toward_player(game_state, player):
    return not ball_going_toward_player(game_state, player)


# noinspection PyPep8Naming
def trajectory_score(pointA, pointsB, obstacle):
    # Retourne un score en fonction de la distance de l'obstacle par rapport à la trajectoire AB
    proportion_max = 15  # Proportion du triangle rectancle derrière les robots obstacles

    # FIXME: HACK SALE, je ne comprends pas le fonctionnement de cette partie du code, analyser plus tard!
    if isinstance(pointA, Position):
        pointA = pointA.array
    if isinstance(obstacle, Position):
        obstacle = obstacle.array

    if isinstance(pointsB, Position):
        pointsB = pointsB.array

    scores = np.array([0])
    AB = pointsB - pointA
    AO = obstacle - pointA
    # la maniere full cool de calculer la norme d'un matrice verticale de vecteur horizontaux:
    normsAB = np.sqrt(np.transpose((AB * AB)).sum(axis=0))
    normsAC = np.divide(np.dot(AB, AO), normsAB)
    normsOC = np.sqrt(np.abs(np.linalg.norm(AO) ** 2 - normsAC ** 2))
    if normsAC < 0 or normsAC > 1.1 * normsAB:
        scores = 1
    else:
        min_proportion = proportion_max if normsOC == 0 else min(normsAC / normsOC, proportion_max)
        scores = max(1, min_proportion)
    return scores

