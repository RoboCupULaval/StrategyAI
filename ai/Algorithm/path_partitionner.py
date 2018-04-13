

from typing import Optional, List


import numpy as np

from Util import Position
from Util.path import Path


MIN_PATH_LENGTH = 250  # mm
RECURSION_LIMIT = 3
SUB_TARGET_RESOLUTION_FACTOR = 10
ELLIPSE_HALF_WIDTH = 500


class Obstacle:
    BASE_AVOID_DISTANCE = 100  # in mm
    def __init__(self, position: np.ndarray, *, avoid_distance: Optional[float] = None):
        self.position = position
        self.avoid_distance = avoid_distance if avoid_distance is not None else self.BASE_AVOID_DISTANCE
    def __repr__(self):
        return self.__class__.__name__ + '({})'.format(self.position)


class PathPartitionner:

    def __init__(self):
        self.obstacles = []

    @property
    def obstacles_position(self):
        return np.array([obs.position for obs in self.obstacles])

    @property
    def obstacles_avoid_distance(self):
        return np.array([obs.avoid_distance for obs in self.obstacles])

    def filter_obstacles(self, start, target):
        obstacles = np.array(self.obstacles)
        start_to_obs = np.linalg.norm(start - self.obstacles_position, axis=1)
        target_to_obs = np.linalg.norm(target - self.obstacles_position, axis=1)
        is_inside_ellipse = (start_to_obs + target_to_obs) <= np.sqrt(np.linalg.norm(start - target) ** 2 + ELLIPSE_HALF_WIDTH ** 2)
        is_not_self = start_to_obs > 0 # remove self if present
        self.obstacles = obstacles[is_inside_ellipse & is_not_self].tolist()

    def get_path(self, start: Position, target: Position, obstacles: List[Obstacle], last_path: Optional[Path]=None):

        self.obstacles = obstacles
        self.filter_obstacles(start.array, target.array)

        if any(self.obstacles):
            path = self.path_planner(start.array, target.array)
        else:
            path = Path(start, target)

        path.filter(threshold=10)

        return path

    def path_planner(self, start, target, avoid_dir=None, depth=0) -> Path:

        if start is target or depth >= RECURSION_LIMIT:
            return Path.from_array(start, target)

        if np.linalg.norm(start - target) <= MIN_PATH_LENGTH:
            return Path.from_array(start, target)

        if not self.is_path_colliding(start, target):
            return Path.from_array(start, target)

        sub_target, avoid_dir = self.next_sub_target(start, target, avoid_dir)
        path_1 = self.path_planner(start, sub_target, avoid_dir, depth=depth+1)
        path_2 = self.path_planner(sub_target, target, avoid_dir, depth=depth+1)

        return path_1 + path_2

    def is_path_colliding(self, start, target) -> bool:
        collisions, _ = self.find_collisions(start, target)
        return any(collisions)

    def find_collisions(self, start, target):
        robot_to_obstacles = self.obstacles_position - start
        robot_to_obstacle_norm = np.linalg.norm(robot_to_obstacles, axis=1)
        segment_direction = normalize(target - start)
        dists_from_path = np.abs(np.cross(segment_direction, robot_to_obstacles))
        is_collision = dists_from_path < self.obstacles_avoid_distance
        obstacles = np.array(self.obstacles)
        return obstacles[is_collision].tolist(), robot_to_obstacle_norm[is_collision]

    def next_sub_target(self, start, target, avoid_dir=None):
        collisions, distances = self.find_collisions(start, target)

        sub_target = target

        if any(collisions):
            closest_collision = collisions[np.argmin(distances).view(int)]
            segment_direction = normalize(target - start)
            len_along_path = np.inner(closest_collision.position - start, segment_direction)
            if len_along_path > 0:
                avoid_dir = perpendicular(segment_direction) # TODO: choose the avoid direction which make the most sense
                sub_target = start + segment_direction * len_along_path + avoid_dir * SUB_TARGET_RESOLUTION_FACTOR
                while not self.is_valid_sub_target(sub_target, self.obstacles_position):
                    sub_target += avoid_dir * SUB_TARGET_RESOLUTION_FACTOR

        return sub_target, avoid_dir

    def is_valid_sub_target(self, sub_target: Position, obstacles: np.ndarray) -> bool:
        dist_sub_2_obs = np.linalg.norm(obstacles - sub_target, axis=1)
        return not np.any(dist_sub_2_obs < self.obstacles_avoid_distance)


def normalize(vec: np.ndarray) -> np.ndarray:
    return vec.copy() / np.linalg.norm(vec)


def perpendicular(vec: np.ndarray) -> np.ndarray:
    """Return the orthonormal vector to the np.array([0,0,1]) with right hand rule."""
    return normalize(np.array([-vec[1], vec[0]]))
