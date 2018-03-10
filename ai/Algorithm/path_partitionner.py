

import numpy as np

from Util import Position
from Util.geometry import perpendicular, normalize
from Util.path import Path

MIN_PATH_LENGTH = 250  # mm
RECURSION_LIMIT = 3
SUB_TARGET_RESOLUTION_FACTOR = 10
ELLIPSE_HALF_WIDTH = 500


class CollisionBody:

    def __init__(self, position: Position, avoid_radius=1):
        self.position = position
        self.avoid_radius = avoid_radius


class PathPartitionner:

    @staticmethod
    def get_path(start: Position, target: Position, obstacles=np.array([])):

        obstacles = np.array(obstacles)

        if np.any(obstacles):
            path = PathPartitionner.path_planner(start, target, obstacles)
        else:
            path = Path(start, target)

        path.filter(threshold=10)

        return path

    @staticmethod
    def path_planner(start, target, obstacles, avoid_dir=None, depth=0) -> Path:
        if start == target or depth >= RECURSION_LIMIT:
            return Path(start, target)

        if (start - target).norm <= MIN_PATH_LENGTH:
            return Path(start, target)

        if not np.any(obstacles):
            return Path(start, target)

        if not PathPartitionner.is_path_colliding(start, target, obstacles):
            return Path(start, target)

        sub_target, avoid_dir = PathPartitionner.next_sub_target(start, target, obstacles, avoid_dir)
        path_1 = PathPartitionner.path_planner(start, sub_target, obstacles, avoid_dir, depth=depth+1)
        path_2 = PathPartitionner.path_planner(sub_target, target, obstacles, avoid_dir, depth=depth+1)

        return path_1 + path_2

    @staticmethod
    def is_path_colliding(start, target, obstacles) -> bool:
        collision_position, _ = PathPartitionner.find_collisions(start, target, obstacles)
        return np.any(collision_position)

    @staticmethod
    def find_collisions(start, target, obstacles):
        obstacles = PathPartitionner.filter_obstacles(start, target, obstacles)

        if np.any(obstacles):
            obstacles_pos = np.array([obstacle.position for obstacle in obstacles])
            avoid_radius = np.array([obstacle.avoid_radius for obstacle in obstacles])
            robot_to_obstacles = obstacles_pos - start
            robot_to_obstacle_norm = np.linalg.norm(robot_to_obstacles, axis=1)
            segment_direction = normalize(target - start)
            dists_from_path = np.abs(np.cross(segment_direction, robot_to_obstacles))
            is_collision = dists_from_path < avoid_radius
        else:
            return None, 0

        return obstacles[is_collision], robot_to_obstacle_norm[is_collision]

    @staticmethod
    def filter_obstacles(start, target, obstacles):
        obstacles_position = np.array([obstacle.position for obstacle in obstacles])
        temp = np.linalg.norm(start - obstacles_position + target - obstacles_position, axis=1)
        is_inside_ellipse = temp <= np.sqrt((start - target).norm ** 2 + ELLIPSE_HALF_WIDTH ** 2)
        return obstacles[is_inside_ellipse]

    @staticmethod
    def next_sub_target(start, target, obstacles, avoid_dir=None):
        collisions, distances = PathPartitionner.find_collisions(start, target, obstacles)

        sub_target = target

        if np.any(collisions):
            closest_collision = collisions[np.argmin(distances)]
            segment_direction = normalize(target - start)
            len_along_path = np.inner(closest_collision.position - start, segment_direction)
            if len_along_path > 0:
                avoid_dir = perpendicular(segment_direction)
                sub_target = start + segment_direction * len_along_path + avoid_dir * SUB_TARGET_RESOLUTION_FACTOR
                while not PathPartitionner.is_valid_sub_target(sub_target, obstacles):
                    sub_target += avoid_dir * SUB_TARGET_RESOLUTION_FACTOR

        return sub_target, avoid_dir

    @staticmethod
    def is_valid_sub_target(sub_target, obstacles):
        obstacles_position = np.array([obstacle.position for obstacle in obstacles])
        avoid_radius = np.array([obstacle.avoid_radius for obstacle in obstacles])
        dist_sub_2_obs = np.linalg.norm(obstacles_position - sub_target, axis=1)
        return not np.any(dist_sub_2_obs < avoid_radius)
