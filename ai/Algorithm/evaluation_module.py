# Under MIT License, see LICENSE.txt

from RULEngine.Util.constant import ROBOT_RADIUS
from RULEngine.Util.geometry import *
from ai.states.game_state import GameState
import time

class PlayerPosition(object):
    def __init__(self, player, distance):
        self.player = player
        self.distance = distance


def player_with_ball(min_dist_from_ball=1.2*ROBOT_RADIUS):
    # Retourne le joueur qui possède la balle, NONE si balle libre
    closest_player = closest_player_to_point(GameState().get_ball_position())
    if closest_player[0][1] < min_dist_from_ball:
        return closest_player[0][0]
    else:
        return None


def closest_players_to_point(point: Position, our_team=None):
    # Retourne une liste de tuples (player, distance) en ordre croissant de distance,
    # our_team pour obtenir une liste contenant une équipe en particulier
    list_player = []
    if our_team or our_team is None:
        for i in GameState().my_team.available_players.values():
            # les players friends
            player_distance = (i.pose.position - point).norm()
            list_player.append(PlayerPosition(i, player_distance))
    if not our_team:
        for i in GameState().other_team.available_players.values():
            # les players ennemis
            player_distance = (i.pose.position - point).norm()
            list_player.append(PlayerPosition(i, player_distance))
    list_player = sorted(list_player, key=lambda x: x.distance)
    return list_player


def closest_player_to_point(point: Position, our_team=None):
    # Retourne le player le plus proche,
    # our_team pour obtenir une liste contenant une équipe en particulier
    return closest_players_to_point(point, our_team)[0].player


def is_ball_moving(min_speed=0.1):
    return GameState().get_ball_velocity().norm() > min_speed


def is_ball_our_side():
    # Retourne TRUE si la balle est dans notre demi-terrain
    if GameState().field.our_side == 0: # POSITIVE
        return GameState().get_ball_position().x > 0
    else:
        return GameState().get_ball_position().x < 0


def is_target_reached(player, target: Position, min_dist=0.01):
    # Retourne TRUE si dans un rayon de l'objectif
    return get_distance(target, player.pose.position) < min_dist


def best_position_option(player, pointA: Position, pointB: Position):
    # Retourne la position (entre pointA et pointB) la mieux placée pour une passe
    ncounts = 11
    points_projection = zip([pointA.x + i * (pointB.x - pointA.x)/(ncounts-1) for i in range(ncounts)],
                            [pointA.y + i * (pointB.y - pointA.y)/(ncounts-1) for i in range(ncounts)])
    score_min = float("inf")

    best_position = Position((pointA + pointB) / 2)
    for x, y in points_projection:
        i = Position(x, y)
        score = line_of_sight_clearance(player, i)
        if score_min > score:
            score_min = score
            best_position = i
    return best_position


def best_passing_option(passing_player):
    # Retourne l'ID du player ou le but le mieux placé pour une passe, NONE si but est la meilleure possibilité

    score_min = float("inf")
    goal = Position(GameState().field.constant["FIELD_THEIR_GOAL_X_EXTERNAL"], 0)

    receiver_id = None
    for i in GameState().my_team.available_players.values():

        if i.id != passing_player.id:
            # Calcul du score pour passeur vers receveur
            score = line_of_sight_clearance(passing_player, np.array(i.pose.position))

            # Calcul du score pour receveur vers but
            score += line_of_sight_clearance(i, goal)
            if (score_min > score).any():
                score_min = score
                receiver_id = i.id

    score = (line_of_sight_clearance(passing_player, np.array(goal)))
    if score_min > score:
        receiver_id = None

    return receiver_id


def line_of_sight_clearance(player, target):
    # Retourne un score en fonction du dégagement de la trajectoire (plus c'est dégagé plus le score est petit)
    score = np.linalg.norm(player.pose.position - target)
    for j in GameState().my_team.available_players.values():
        # Obstacle : les players friends
        if not (j.id == player.id or j.pose.position == target):
            score *= trajectory_score(player.pose.position, target, j.pose.position)
    for j in GameState().other_team.available_players.values():
        # Obstacle : les players ennemis
        score *= trajectory_score(player.pose.position, target, j.pose.position)
    return score


def line_of_sight_clearance_ball(player, targets, distances=None):
    # Retourne un score en fonction du dégagement de la trajectoire de la target vers la ball excluant le robot actuel
    # (plus c'est dégagé plus le score est petit)

    ball_position = GameState().get_ball_position()
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
    for j in GameState().other_team.available_players.values():
        # Obstacle : les players ennemis
        scores *= trajectory_score(np.array(GameState().get_ball_position()), targets, np.array(j.pose.position))
        #print(scores)
        #print(scores_temp)
    return scores

def line_of_sight_clearance_ball_legacy(player, target: Position):
    # Retourne un score en fonction du dégagement de la trajectoire de la target vers la ball excluant le robot actuel
    # (plus c'est dégagé plus le score est petit)
    score = np.linalg.norm(GameState().get_ball_position() - target)

    # for j in GameState().my_team.available_players.values():
    #     # Obstacle : les players friends
    #     if not (j.id == player.id or j.pose.position == target):
    #         score *= trajectory_score(GameState().get_ball_position(), target, j.pose.position)
    for j in GameState().other_team.available_players.values():
        # Obstacle : les players ennemis
        score *= trajectory_score_legacy(GameState().get_ball_position(), target, j.pose.position)
    return score


def trajectory_score(pointA, pointsB, obstacle):
    # Retourne un score en fonction de la distance de l'obstacle par rapport à la trajectoire AB
    proportion_max = 15 # Proportion du triangle rectancle derrière les robots obstacles
    if len(pointsB.shape) == 1:
        scores = np.array([0])
    else:
        scores = np.zeros(pointsB.shape[0])
    AB = np.array(pointsB) - np.array(pointA)
    AO = np.array(obstacle - pointA)
    # la maniere full cool de calculer la norme d'un matrice verticale de vecteur horizontaux:
    normsAB = np.sqrt(np.transpose((AB*AB)).sum(axis=0))
    normsAC = np.divide(np.dot(AB, AO), normsAB)
    normsOC = np.sqrt(np.linalg.norm(AO) ** 2 - normsAC ** 2)
    if scores.size == 1:
        if normsAC < 0 or normsAC > 1.1 * normsAB:
            scores = 1
        else:
            scores = max(1, min(normsAC / normsOC, proportion_max))
    else:
        scores[normsAC < 0] = 1
        scores[normsAC > 1.1 * normsAB] = 1
        temp = np.divide(normsAC[scores == 0], normsOC[scores == 0])
        temp[temp > proportion_max] = proportion_max
        temp[temp < 1] = 1
        scores[scores == 0] = temp
    return scores

def is_player_facing_target(player, target_position: Position, tolerated_angle: float) -> bool:
    """
        Détermine si l'angle entre le devant du joueur et la cible est suffisamment petit
        Args:
            player: Le joueur
            target_position: La position où le joueur veut faire face
            tolerated_angle: Angle en radians
        Returns:
            Si le joueur est face à la cible.
    """
    assert isinstance(target_position, Position), "target_position is not a Position"
    assert isinstance(tolerated_angle, (int, float)), "tolerated_angle is neither a int nor a float"

    player_front = Position(player.pose.position.x + np.cos(player.pose.orientation),
                            player.pose.position.y + np.sin(player.pose.orientation))
    return get_angle_between_three_points(player_front, player.pose.position, target_position) < tolerated_angle


def ball_direction(self):
    pass # TODO :


def best_position_in_region(player, A, B):
    # Retourne la position (dans un rectangle aux coins A et B) la mieux placée pour une passe
    ncounts = 5
    bottom_left = Position(min(A.x, B.x), min(A.y, B.y))
    top_right = Position(max(A.x, B.x), max(A.y, B.y))
    ball_position = GameState().get_ball_position()


    positions = []
    for i in range(ncounts):
        x_point = bottom_left.x + i * (top_right.x - bottom_left.x) / (ncounts - 1)
        for j in range(ncounts):
            y_point = bottom_left.y + j * (top_right.y - bottom_left.y) / (ncounts - 1)
            positions += [Position(x_point, y_point)]
    positions = np.stack(positions)
    # la maniere full cool de calculer la norme d'un matrice verticale de vecteur horizontaux:
    dists_from_ball = np.sqrt(((positions - np.array(ball_position)) *
                               (positions - np.array(ball_position))).sum(axis=1))
    positions = positions[dists_from_ball > 1000, :]
    dists_from_ball = dists_from_ball[dists_from_ball > 1000]
    scores = line_of_sight_clearance_ball(player, positions, dists_from_ball)
    best_score_index = np.argmin(scores)
    best_position = positions[best_score_index, :]

    return best_position

