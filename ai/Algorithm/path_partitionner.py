

from typing import Optional, List


import numpy as np

from Util import Position
from Util.path import Path

from abc import ABCMeta

MIN_PATH_LENGTH = 250  # mm
RECURSION_LIMIT = 3
SUB_TARGET_RESOLUTION_FACTOR = 10
ELLIPSE_HALF_WIDTH = 500


class Obstacle(metaclass=ABCMeta):
    BASE_AVOID_DISTANCE = 100  # in mm
    def __init__(self, avoid_distance):
        self.avoid_distance = avoid_distance if avoid_distance is not None else self.BASE_AVOID_DISTANCE
    def __repr__(self):
        return self.__str__()

class PointObstacle(Obstacle):
    def __init__(self, position: np.ndarray, *, avoid_distance: Optional[float] = None, avoid_direction: Optional[int] = 1):
        super().__init__(avoid_distance)
        self.position = position
        self.avoid_direction = avoid_direction
    def __str__(self):

        return self.__class__.__name__ + '({})'.format(self.position)

class LineObstacle(Obstacle):
    def __init__(self, start, end, *, avoid_distance=None):
        super().__init__(avoid_distance)
        self.start = start
        self.end = end
    def __str__(self):
        return self.__class__.__name__ + '(start={}, end={})'.format(self.start, self.end)
    def intersection(self, other_start, other_end) -> Optional[PointObstacle]:

        s1 = self.end - self.start
        s2 = other_end - other_start

        s = (-s1[1] * (self.start[0] - other_start[0]) + s1[0] * (self.start[1] - other_start[1])) / (-s2[0] * s1[1] + s1[0] * s1[1])
        t = ( s2[0] * (self.start[1] - other_start[1]) - s2[1] * (self.start[0] - other_start[0])) / (-s2[0] * s1[1] + s1[0] * s2[1])

        if 0 <= s <= 1 and 0 <= t <= 1:
            point = np.array([self.start[0] + (t * s1[0]), self.start[1] + (t * s1[1])])
            intersection = PointObstacle(point, avoid_distance=300, avoid_direction=1)
        else:
            intersection = None

        return intersection


class PathPartitionner:

    def __init__(self):
        self.obstacles = []
        self.lines = []

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

        self.obstacles = [obs for obs in obstacles if isinstance(obs, PointObstacle)]
        self.lines = np.array([obs for obs in obstacles if isinstance(obs, LineObstacle)])
        self.filter_obstacles(start.array, target.array)

        for line in self.lines:
            intersection = line.intersection(start, target)
            if intersection is not None:
                self.obstacles.append(intersection)

        if any(self.obstacles):
            path = self.path_planner(start.array, target.array)
        else:
            path = Path(start, target)

        path.filter(threshold=10)

        return path

    def path_planner(self, start, target, avoid_dir=None, depth=0) -> Path:

        for line in self.lines:
            intersection = line.intersection(start, target)
            if intersection is not None:
                self.obstacles.append(intersection)

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
        collisions = [obs for obs, will_collide in zip(self.obstacles, is_collision) if will_collide]
        return collisions, robot_to_obstacle_norm[is_collision]

    def next_sub_target(self, start, target, avoid_dir=None):
        collisions, distances = self.find_collisions(start, target)

        sub_target = target

        if any(collisions):
            closest_collision = collisions[np.argmin(distances).view(int)]
            segment_direction = normalize(target - start)
            len_along_path = np.inner(closest_collision.position - start, segment_direction)
            if len_along_path > 0:
                avoid_dir = perpendicular(segment_direction) * closest_collision.avoid_direction
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
