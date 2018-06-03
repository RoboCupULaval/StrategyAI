# Under MIT License, see LICENSE.txt

from Util.position import Position
from Util.constant import ROBOT_RADIUS
from ai.states.game_state import GameState
from ai.GameDomainObjects.field import FieldSide

import numpy as np


class PlayerPosition(object):
    def __init__(self, player, distance):
        self.player = player
        self.distance = distance


def player_with_ball(min_dist_from_ball=1.2*ROBOT_RADIUS, our_team=None):
    # Retourne le joueur qui possède la balle, NONE si balle libre
    closest_player = closest_player_to_point(GameState().ball_position, our_team)
    if closest_player.distance < min_dist_from_ball:
        return closest_player.player
    else:
        return None


# noinspection PyUnusedLocal
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


def is_ball_moving(min_speed=0.1):
    return GameState().ball_velocity.norm > min_speed


# noinspection PyUnresolvedReferences
def is_ball_our_side():
    # Retourne TRUE si la balle est dans notre demi-terrain
    if GameState().our_side == FieldSide.POSITIVE: # POSITIVE
        return GameState().ball_position.x > 0
    else:
        return GameState().ball_position.x < 0


# noinspection PyUnresolvedReferences
def best_passing_option(passing_player, consider_goal=True):
    # Retourne l'ID du player ou le but le mieux placé pour une passe, NONE si but est la meilleure possibilité

    score_min = float("inf")
    goal = Position(GameState().field.their_goal_x, 0)

    receiver_id = None
    for p in GameState().our_team.available_players.values():

        if p.id != passing_player.id:
            # Calcul du score pour passeur vers receveur
            score = line_of_sight_clearance(passing_player, p.pose.position)

            # Calcul du score pour receveur vers but
            score += line_of_sight_clearance(p, goal)
            if score_min > score:
                score_min = score
                receiver_id = p.id

    if consider_goal and not is_ball_our_side():
        score = (line_of_sight_clearance(passing_player, goal))
        if score_min > score:
            receiver_id = None

    return receiver_id


def line_of_sight_clearance(player, targets):
    # Retourne un score en fonction du dégagement de la trajectoire (plus c'est dégagé plus le score est petit)
    score = (player.pose.position - targets).norm
    for j in GameState().our_team.available_players.values():
        # Obstacle : les players friends
        condition = []
        if not (j.id == player.id):
            condition += [target is not j.pose.position for target in targets]
            if any(condition):
                score *= trajectory_score(player.pose.position, Position.from_array(targets[condition]), j.pose.position)
    for j in GameState().enemy_team.available_players.values():
        # Obstacle : les players ennemis
        score *= trajectory_score(player.pose.position, targets, j.pose.position)
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
        #print(scores)
        #print(scores_temp)
    return scores



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
    normsAB = np.sqrt(np.transpose((AB*AB)).sum(axis=0))
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
    dists_from_ball = np.sqrt(((positions - ball_position.array) *
                               (positions - ball_position.array)).sum(axis=1))
    positions = positions[dists_from_ball > 1000, :]
    dists_from_ball = dists_from_ball[dists_from_ball > 1000]
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