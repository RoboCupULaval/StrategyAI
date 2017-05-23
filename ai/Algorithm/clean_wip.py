import numpy as np
from typing import List

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.geometry import get_distance, conv_position_2_list
from ai.states.game_state import GameState
from ai.states.world_state import WorldState


GAP_PROXY = 200
MAX_RECURS = 5
DIST_FROM_PATH = 50

def get_path(gameState: GameState, ourPlayer: OurPlayer, target: Pose=Pose()):
    playing_obstacles = _get_playing_obstacles(gameState, ourPlayer)
    path = [ourPlayer.pose.position, ourPlayer.ai_command.pose_goal]


def _fastpathplanner(current_path: List[Position], list_obstacle: List[Player], depth: int=0,
                     avoid_dir=None):
    if _is_path_collide(current_path, list_obstacle) and depth < MAX_RECURS:
        [sub_target, avoid_dir] = _search_point(current_path, avoid_dir)

        path_1 = Path(path.start, sub_target)

        path_1 = self.fastpathplanner(path_1, depth + 1, avoid_dir)

        path_2 = Path(sub_target, path.goal)
        path_2 = self.fastpathplanner(path_2, depth + 1, avoid_dir)

        path = path_1.join_segments(path_2)

    return path


def _search_point(path: List[Position], avoid_dir=None):
    pose_robot = path[0]
    pose_target = path[-1]
    [pose_obstacle_closest, dist_point_obs, closest_player] = _find_closest_obstacle(pose_target, path)
    if pose_obstacle_closest is None:
        sub_target = pose_target
        return sub_target

    direction = np.array(conv_position_2_list(pose_target - pose_robot)) / get_distance(pose_target, pose_robot)
    vec_robot_2_obs = np.array(conv_position_2_list(pose_obstacle_closest - pose_robot))
    len_along_path = np.dot(vec_robot_2_obs, np.transpose(direction))

    if len_along_path > 0 and len_along_path < get_distance(pose_target, pose_robot):
        vec_perp = np.cross(np.append(direction, 0), np.array([0, 0, 1]))
        vec_perp = vec_perp[0:2] / np.linalg.norm(vec_perp)
        # print(self.player.velocity)
        cruise_speed = np.array(self.player.velocity[0:2])
        self.closest_obs_speed = np.array(closest_player.velocity[0:2])
        # if np.dot(self.closest_obs_speed - cruise_speed, vec_perp) < 0:
        #     avoid_dir = vec_perp
        # else:
        avoid_dir = -vec_perp

        # if np.linalg.norm(self.closest_obs_speed) > 0.2:
        #     avoid_dir = self.closest_obs_speed
        # else:
        #     avoid_dir = -vec_perp
        # avoid_dir /= np.linalg.norm(avoid_dir)
        # #avoid_dir = np.dot(self.closest_obs_speed-cruise_speed, vec_perp)*vec_perp
        # #avoid_dir = None
        # #print(cruise_speed)
        # #print(vec_perp)
        # avoid_dir = -vec_perp

        if avoid_dir is None:
            avoid_dir = -vec_perp
            sub_target_1 = np.array(conv_position_2_list(pose_robot)) + direction * len_along_path + vec_perp * self.res
            sub_target_2 = np.array(conv_position_2_list(pose_robot)) + direction * len_along_path - vec_perp * self.res
            bool_sub_target_1 = self.verify_sub_target(Position(sub_target_1[0], sub_target_1[1]))
            bool_sub_target_2 = self.verify_sub_target(Position(sub_target_2[0], sub_target_2[1]))

            while bool_sub_target_1:
                sub_target_1 += vec_perp * self.res
                bool_sub_target_1 = self.verify_sub_target(Position(sub_target_1[0], sub_target_1[1]))

            sub_target_1 += vec_perp * 0.01 * self.res
            while bool_sub_target_2:
                sub_target_2 -= vec_perp * self.res
                bool_sub_target_2 = self.verify_sub_target(Position(sub_target_2[0], sub_target_2[1]))

            sub_target_2 -= vec_perp * 0.01 * self.res

            # if abs(get_distance(path.start, Position(sub_target_1[0], sub_target_1[1])) - get_distance(path.start, Position(sub_target_2[0], sub_target_2[1]))) < 300:
            #
            #     sub_target = sub_target_1
            #     avoid_dir = -vec_perp
            #
            # else:
            #     if get_distance(path.start, Position(sub_target_1[0], sub_target_1[1])) < get_distance(path.start, Position(sub_target_2[0], sub_target_2[1])):
            #         sub_target = sub_target_1
            #         avoid_dir = -vec_perp
            #
            #     else:
            #         sub_target = sub_target_2
            #         avoid_dir = vec_perp
            if np.linalg.norm(cruise_speed) < 0.1:
                sub_target = sub_target_1
            elif abs(np.dot(direction, (sub_target_1 - path.start.conv_2_np()) / np.linalg.norm(
                            sub_target_1 - path.start.conv_2_np()))) > \
                    abs(np.dot(direction, (sub_target_2 - path.start.conv_2_np()) / np.linalg.norm(
                                sub_target_2 - path.start.conv_2_np()))):
                sub_target = sub_target_1
            else:
                sub_target = sub_target_2

        else:
            # if np.dot(avoid_dir, np.transpose(vec_perp)) < 0:
            #     vec_perp = -vec_perp
            if np.linalg.norm(avoid_dir) > 0.001:
                avoid_dir = avoid_dir / np.linalg.norm(avoid_dir)
            elif np.dot(avoid_dir, np.transpose(vec_perp)) < 0:
                avoid_dir = -vec_perp
            else:
                avoid_dir = vec_perp
            sub_target = np.array(conv_position_2_list(pose_robot)) + direction * len_along_path + vec_perp * self.res

            bool_sub_target = self.verify_sub_target(Position(sub_target[0], sub_target[1]))
            while bool_sub_target:
                sub_target -= avoid_dir * self.res
                bool_sub_target = self.verify_sub_target(Position(sub_target[0], sub_target[1]))

            sub_target -= avoid_dir * 0.01 * self.res
            avoid_dir = vec_perp
        sub_target = Position(sub_target[0], sub_target[1])
    else:
        sub_target = pose_target
    return [sub_target, avoid_dir]


def _find_closest_obstacle(point: Position, path: List[Position], list_obstacle: List[Player]):
    dist_point_obs = np.inf
    closest_obs = None
    closest_player = list_obstacle[0].pose.position.conv_2_np()
    if get_distance(path[0], path[-1]) < 0.001:
        return [closest_obs, dist_point_obs, closest_player]
    if point == path[0]:
        return [closest_obs, dist_point_obs, closest_player]
    pose_start = path[0].conv_2_np()
    direction = (point.conv_2_np() - pose_start) / get_distance(point, path[0])

    for idx, pose_obs in enumerate(list_obstacle):
        vec_robot_2_obs_temp = pose_obs.pose.position - pose_start
        len_along_path_temp = np.dot(vec_robot_2_obs_temp, direction)
        dist_from_path_temp = np.sqrt(np.linalg.norm(vec_robot_2_obs_temp) ** 2 - len_along_path_temp ** 2)
        if GAP_PROXY > dist_from_path_temp and len_along_path_temp > 0:
            obstacle_pos = Position.from_np(pose_obs)
            dist = get_distance(path[0], obstacle_pos)
            if dist < dist_point_obs:
                dist_point_obs = dist
                closest_obs = obstacle_pos
                closest_player = list_obstacle[idx]
    return [closest_obs, dist_point_obs, closest_player]


def _is_path_collide(current_path: List[Position], list_obstacle: List[Player]):
    # for everything except the last point in path
    for idx, points in enumerate(current_path[:-1]):
        dist = get_distance(current_path[idx + 1], current_path[idx])
        if dist > 0.001:
            pose_start = current_path[idx].conv_2_np()
            direction = (current_path[idx + 1].conv_2_np() - pose_start) / dist
            for pose_obs in list_obstacle:
                vec_robot_2_obs_temp = pose_obs.pose.position.conv_2_np() - pose_start
                len_along_path_temp = np.dot(vec_robot_2_obs_temp, direction)
                dist_from_path_temp = np.sqrt(np.linalg.norm(vec_robot_2_obs_temp) ** 2 -
                                              len_along_path_temp ** 2)
                if GAP_PROXY > dist_from_path_temp and len_along_path_temp > 0:
                    return True
    return False


def _get_playing_obstacles(gameState: GameState, player_to_remove: OurPlayer):
    temp_array = []
    for p in gameState.my_team.values():
        if p.id != player_to_remove.id:
            temp_array += p

    for p in gameState.other_team.values():
        temp_array += p

    return temp_array


def _reshape_path(points_list_of_path: List[Position], player: OurPlayer):
    path = List(points_list_of_path)
    vel_cruise = player.ai_command.cruise_speed * 1000
    point_list = List(points_list_of_path[0])
    speed_list = [0]
    radius_at_const_speed = (vel_cruise ** 2) / OurPlayer.max_acc
    p1 = path[0].conv_2_np()
    for idx, point in enumerate(path[1:-1]):
        dist_from_path = DIST_FROM_PATH
        p2 = point.conv_2_np()
        p3 = path[idx + 1].conv_2_np()
        theta = np.math.atan2(p3[1] - p2[1], p3[0] - p2[0]) - np.math.atan2(p1[1] - p2[1], p1[0] - p2[0])
        radius = abs(dist_from_path * np.sin(theta / 2) / (1 - np.sin(theta / 2)))
        if radius > radius_at_const_speed:
            radius = radius_at_const_speed
            dist_from_path = -radius + radius / abs(np.math.sin(theta / 2))
        if np.linalg.norm(p1 - p2) < 0.001 or np.linalg.norm(p2 - p3) < 0.001 or np.linalg.norm(p1 - p3) < 0.001:
            # on traite tout le cas ou le problème dégènere
            point_list += [p2]
            speed_list += [vel_cruise / 1000]
        else:
            p4 = p2 + np.sqrt(np.square(dist_from_path + radius) - radius ** 2) * \
                      (p1 - p2) / np.linalg.norm(p1 - p2)
            p5 = p2 + np.sqrt(np.square(dist_from_path + radius) - radius ** 2) * \
                      (p3 - p2) / np.linalg.norm(p3 - p2)
            if np.linalg.norm(p4 - p5) > np.linalg.norm(p3 - p1):
                point_list += [point]
                speed_list += [vel_cruise / 1000]
            else:
                point_list += [Position.from_np(p4), Position.from_np(p5)]
                speed_list += [np.sqrt(radius / (OurPlayer.max_acc * 1000)),
                               np.sqrt(radius / (OurPlayer.max_acc * 1000))]
        p1 = point_list[-1].conv_2_np()

    speed_list.append(0)
    point_list.append(points_list_of_path[-1])
    # print(point_list)
    # print(speed_list)

    return point_list, speed_list
