

import numpy as np

from Util import Position
from Util.geometry import perpendicular, normalize
from Util.path import Path

MIN_PATH_LENGTH = 250  # mm
RECURSION_LIMIT = 3
SUB_TARGET_RESOLUTION_FACTOR = 10
ELLIPSE_HALF_WIDTH = 500


class PathPartitionner:

    def __init__(self, avoid_radius):
        self.avoid_radius = avoid_radius

    # noinspection PyUnusedLocal
    def get_path(self, start: Position, target: Position, obstacles=np.array([]), last_path=None):

        obstacles = np.array(obstacles)

        if np.any(obstacles):
            path = self.path_planner(start, target, obstacles)
        else:
            path = Path(start, target)

        path.filter(threshold=10)

        return path

    def path_planner(self, start, target, obstacles: np.ndarray, avoid_dir=None, depth=0) -> Path:

        if start == target or depth >= RECURSION_LIMIT:
            return Path(start, target)

        if (start - target).norm <= MIN_PATH_LENGTH:
            return Path(start, target)

        if not np.any(obstacles):
            return Path(start, target)

        if not self.is_path_colliding(start, target, obstacles):
            return Path(start, target)

        sub_target, avoid_dir = self.next_sub_target(start, target, obstacles, avoid_dir)
        path_1 = self.path_planner(start, sub_target, obstacles, avoid_dir, depth=depth+1)
        path_2 = self.path_planner(sub_target, target, obstacles, avoid_dir, depth=depth+1)

        return path_1 + path_2

    def is_path_colliding(self, start: Position, target: Position, obstacles: np.ndarray) -> bool:
        collisions, _ = self.find_collisions(start, target, obstacles)
        return np.any(collisions)

    def find_collisions(self, start, target, obstacles: np.ndarray) -> (np.ndarray, np.ndarray):
        obstacles = PathPartitionner.filter_obstacles(start, target, obstacles)

        if np.any(obstacles):
            robot_to_obstacles = obstacles - start
            robot_to_obstacle_norm = np.linalg.norm(robot_to_obstacles, axis=1)
            segment_direction = normalize(target - start)
            dists_from_path = np.abs(np.cross(segment_direction, robot_to_obstacles))
            is_collision = dists_from_path < self.avoid_radius
        else:
            return None, 0

        return obstacles[is_collision], robot_to_obstacle_norm[is_collision]

    @staticmethod
    def filter_obstacles(start, target, obstacles: np.ndarray) -> np.ndarray:
        temp = np.linalg.norm(start - obstacles + target - obstacles, axis=1)
        is_inside_ellipse = temp <= np.sqrt((start - target).norm ** 2 + ELLIPSE_HALF_WIDTH ** 2)
        return obstacles[is_inside_ellipse]

    def next_sub_target(self, start, target, obstacles: np.ndarray, avoid_dir=None):
        collisions, distances = self.find_collisions(start, target, obstacles)

        sub_target = target

        if np.any(collisions):
            closest_collision = collisions[np.argmin(distances)]
            segment_direction = normalize(target - start)
            len_along_path = np.inner(closest_collision - start, segment_direction)
            if len_along_path > 0:
                avoid_dir = perpendicular(segment_direction)
                sub_target = start + segment_direction * len_along_path + avoid_dir * SUB_TARGET_RESOLUTION_FACTOR
                while not self.is_valid_sub_target(sub_target, obstacles):
                    sub_target += avoid_dir * SUB_TARGET_RESOLUTION_FACTOR

        return sub_target, avoid_dir

    def is_valid_sub_target(self, sub_target: Position, obstacles: np.ndarray) -> bool:
        dist_sub_2_obs = np.linalg.norm(obstacles - sub_target, axis=1)
        return not np.any(dist_sub_2_obs < self.avoid_radius)

    def path_is_valid(self, path: Path, obstacles):

        if not path:
            return False
        obstacles = np.array(obstacles)
        for start, target in zip(path, path[1:]):
            print('allo')
            if self.is_path_colliding(start, target, obstacles):
                path_valid = False
                break
        else:
            path_valid = True

        return path_valid
