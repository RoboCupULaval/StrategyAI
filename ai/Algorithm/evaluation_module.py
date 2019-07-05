# Under MIT License, see LICENSE.txt
import logging
from typing import List

import numpy as np

from Util.geometry import Line, angle_between_three_points, perpendicular, wrap_to_pi, closest_point_on_line, normalize
from Util.position import Position
from Util.role import Role
from Util.constant import ROBOT_RADIUS, BALL_RADIUS
from ai.Algorithm.path_partitionner import Obstacle
from ai.GameDomainObjects import Player
from ai.states.game_state import GameState


class PlayerPosition(object):
    def __init__(self, player, distance):
        self.player = player
        self.distance = distance


def player_with_ball(min_dist_from_ball=1.2 * ROBOT_RADIUS, our_team=None):
    # Retourne le joueur qui possède la balle, NONE si balle libre
    closest_player = closest_player_to_point(GameState().ball_position, our_team)
    if closest_player.distance < min_dist_from_ball:
        return closest_player.player
    else:
        return None


def player_pointing_toward_point(player: Player, point: Position, angle_tolerance=90 * np.pi / 180):
    return abs((player.pose.orientation - (point - player.position).angle)) < angle_tolerance / 2


def object_pointing_toward_point(object_position, object_orientation, point, angle_tolerance=90 * np.pi / 180):
    return abs((object_orientation - (point - object_position).angle)) < angle_tolerance / 2


def player_pointing_toward_segment(player: Player, segment: Line):
    angle_bisection = angle_between_three_points(segment.p1, player.position, segment.p2) / 2
    angle_reference = angle_bisection + (segment.p2 - player.position).angle
    return abs(player.pose.orientation - angle_reference) < angle_bisection


def player_covered_from_goal(player: Player):
    ball_position = GameState().ball.position
    their_goal_line = GameState().field.their_goal_line.copy()
    # In Sydney, we found that our kick hit the wall around the goal quite often
    if their_goal_line.p1.y > their_goal_line.p2.y:
        their_goal_line.p1.y -= BALL_RADIUS
        their_goal_line.p2.y += BALL_RADIUS
    else:
        their_goal_line.p2.y -= BALL_RADIUS
        their_goal_line.p1.y += BALL_RADIUS

    shooting_angle = angle_between_three_points(their_goal_line.p1, ball_position, their_goal_line.p2)
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
    nb_beam = 45
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
# TODO: Change 'our_team' to 'is_our_team'
def closest_players_to_point(point: Position, our_team=None):
    # Retourne une liste de tuples (player, distance) en ordre croissant de distance,
    # our_team pour obtenir une liste contenant une équipe en particulier
    list_player = []
    if our_team or our_team is None:
        for i in GameState().our_team.available_players.values():
            # les players friends
            player_distance = (i.pose.position - point).norm
            list_player.append(PlayerPosition(i, player_distance))
    if not our_team:
        for i in GameState().enemy_team.available_players.values():
            # les players ennemis
            player_distance = (i.pose.position - point).norm
            list_player.append(PlayerPosition(i, player_distance))
    list_player = sorted(list_player, key=lambda x: x.distance)
    return list_player


def closest_player_to_point(point: Position, our_team=None):
    # Retourne le player le plus proche,
    # our_team pour obtenir une liste contenant une équipe en particulier
    return closest_players_to_point(point, our_team)[0]


def closest_players_to_point_except(point: Position, except_roles=[], except_players=[]):
    closests = closest_players_to_point(point, our_team=True)
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
    for r, p in GameState().assigned_roles.items():
        if p != passing_player and r != Role.GOALKEEPER:
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


# noinspection PyUnusedLocal
def line_of_sight_clearance_ball(player, targets, distances=None):
    # Retourne un score en fonction du dégagement de la trajectoire de la target vers la ball excluant le robot actuel
    # (plus c'est dégagé plus le score est petit)
    ball_position = GameState().ball_position
    if distances is None:
        # la maniere full cool de calculer la norme d'un matrice verticale de vecteur horizontaux:
        scores = np.sqrt(((targets - np.array(ball_position)) *
                          (targets - np.array(ball_position))).sum(axis=1))
    else:
        scores = distances
    # for j in GameState().my_team.available_players.values():
    #     # Obstacle : les players friends
    #     if not (j.id == player.id or j.pose.position == target):
    #         score *= trajectory_score(GameState().get_ball_position(), target, j.pose.position)
    for j in GameState().enemy_team.available_players.values():
        # Obstacle : les players ennemis
        scores *= trajectory_score(GameState().ball_position, targets, j.pose.position)
        # print(scores)
        # print(scores_temp)
    return scores


def object_going_toward_other_object(object_1, object_2, max_angle_of_approach=25):
    if object_1.is_mobile(50):  # to avoid division by zero and unstable ball_directions
        object_1_approach_angle = np.arccos(np.dot(normalize(object_2.position - object_1.position).array,
                                                   normalize(object_1.velocity).array)) * 180 / np.pi
        return object_1_approach_angle < max_angle_of_approach
    return False


def ball_going_toward_player(game_state, player, max_angle_of_approach=25):
    return object_going_toward_other_object(game_state.ball, player, max_angle_of_approach=max_angle_of_approach)


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

    if len(pointsB.shape) == 1:
        scores = np.array([0])
    else:
        scores = np.zeros(pointsB.shape[0])
    AB = pointsB - pointA
    AO = obstacle - pointA
    # la maniere full cool de calculer la norme d'un matrice verticale de vecteur horizontaux:
    normsAB = np.sqrt(np.transpose((AB * AB)).sum(axis=0))
    normsAC = np.divide(np.dot(AB, AO), normsAB)
    normsOC = np.sqrt(np.abs(np.linalg.norm(AO) ** 2 - normsAC ** 2))
    if scores.size == 1:
        if normsAC < 0 or normsAC > 1.1 * normsAB:
            scores = 1
        else:
            min_proportion = proportion_max if normsOC == 0 else min(normsAC / normsOC, proportion_max)
            scores = max(1, min_proportion)
    else:
        scores[normsAC < 0] = 1
        scores[normsAC > 1.1 * normsAB] = 1
        temp = np.divide(normsAC[scores == 0], normsOC[scores == 0])
        temp[temp > proportion_max] = proportion_max
        temp[temp < 1] = 1
        scores[scores == 0] = temp
    return scores


# noinspection PyPep8Naming,PyUnresolvedReferences
def best_position_in_region(player, A, B):
    # Retourne la position (dans un rectangle aux points A et B) la mieux placée pour une passe
    ncounts = 5
    bottom_left = Position(min(A.x, B.x), min(A.y, B.y))
    top_right = Position(max(A.x, B.x), max(A.y, B.y))
    ball_position = GameState().ball_position

    positions = []
    for i in range(ncounts):
        x_point = bottom_left.x + i * (top_right.x - bottom_left.x) / (ncounts - 1)
        for j in range(ncounts):
            y_point = bottom_left.y + j * (top_right.y - bottom_left.y) / (ncounts - 1)
            positions += [Position(x_point, y_point).array]
    positions = np.stack(positions)
    # la maniere full cool de calculer la norme d'un matrice verticale de vecteur horizontaux:
    dists_from_ball_raw = np.sqrt(((positions - ball_position.array) *
                                   (positions - ball_position.array)).sum(axis=1))
    positions = positions[dists_from_ball_raw > 1000, :]
    dists_from_ball = dists_from_ball_raw[dists_from_ball_raw > 1000]
    scores = line_of_sight_clearance_ball(player, positions, dists_from_ball)
    our_side = GameState().field.our_goal_x
    if abs(A.x - our_side) < abs(B.x - our_side):
        x_closest_to_our_side = A.x
    else:
        x_closest_to_our_side = B.x

    width = abs(A.x - B.x)

    saturation_modifier = np.clip((positions[:, 0] - x_closest_to_our_side) / width, 0.05, 1)
    scores /= saturation_modifier
    try:
        best_score_index = np.argmin(scores)
        best_position = positions[best_score_index, :]
    except IndexError:
        best_position = Position()

    return best_position


def get_away_from_trajectory(position, start, end, min_distance):
    try:
        point = closest_point_on_line(position, start, end)
        dist = position - point
    except ZeroDivisionError:
        point = position
        dist = perpendicular(end - start) * min_distance / 2
    if dist.norm < min_distance:
        return point - dist.norm * min_distance
    else:
        return position
