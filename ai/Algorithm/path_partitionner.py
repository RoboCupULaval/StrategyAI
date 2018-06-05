

from typing import Optional, List


import numpy as np

from Util import Position
from Util.path import Path


MIN_PATH_LENGTH = 250  # mm
RECURSION_LIMIT = 3
SUB_TARGET_RESOLUTION_FACTOR = 30
ELLIPSE_HALF_WIDTH = 1000


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
        self.old_path = None
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
        is_not_self = start_to_obs > 0  # remove self if present
        self.obstacles = obstacles[is_inside_ellipse & is_not_self].tolist()

    def get_path(self, start: Position, target: Position, obstacles: List[Obstacle], last_path: Optional[Path]=None):

        self.obstacles = obstacles
        self.filter_obstacles(start.array, target.array)
        self.old_path = last_path

        if any(self.obstacles):
            if last_path and not self.is_full_path_colliding(last_path):
                path = self.update_last_path(start, target)
                path.filter(threshold=50)
            else:
                path = self.path_planner(start.array, target.array)
                path.filter(threshold=10)
        else:
            path = Path(start, target)

        return path

    def path_planner(self, start, target, depth=0) -> Path:

        if start is target or depth >= RECURSION_LIMIT:
            return Path.from_array(start, target)

        if np.linalg.norm(start - target) <= MIN_PATH_LENGTH:
            return Path.from_array(start, target)

        if not self.is_path_colliding(start, target):
            return Path.from_array(start, target)
        sub_target = self.next_sub_target(start, target)

        path_1 = self.path_planner(start, sub_target, depth=depth+1)
        path_2 = self.path_planner(sub_target, target, depth=depth+1)

        return path_1 + path_2

    def is_path_colliding(self, start, target) -> bool:
        collisions, _ = self.find_collisions(start, target)
        return any(collisions)

    def find_collisions(self, start, target):
        robot_to_obstacles = self.obstacles_position - start
        robot_to_obstacle_norm = np.linalg.norm(robot_to_obstacles, axis=1)
        obstacles = self.obstacles
        obstacles_avoid_distance = self.obstacles_avoid_distance
        segment_direction = normalize(target - start)
        dists_from_path = np.abs(np.cross(segment_direction, robot_to_obstacles))
        is_collision = dists_from_path < obstacles_avoid_distance
        obstacles = np.array(obstacles)
        return obstacles[is_collision].tolist(), robot_to_obstacle_norm[is_collision]

    def next_sub_target(self, start, target):
        collisions, distances = self.find_collisions(start, target)
        sub_target = target

        if any(collisions):
            closest_collision = collisions[np.argmin(distances).view(int)]
            resolution_sub_target = SUB_TARGET_RESOLUTION_FACTOR
            segment_direction = normalize(target - start)
            len_along_path = np.inner(closest_collision.position - start, segment_direction)
            if len_along_path > 0:
                avoid_dir = perpendicular(segment_direction)
                # if np.dot(avoid_dir, segment_direction) < np.dot(-avoid_dir, segment_direction):
                #     avoid_dir *= -1
                sub_target_1 = start + segment_direction * len_along_path + avoid_dir * resolution_sub_target
                while not self.is_valid_sub_target(sub_target_1, self.obstacles_position):
                    sub_target_1 += avoid_dir * resolution_sub_target
                sub_target_2 = start + segment_direction * len_along_path - avoid_dir * resolution_sub_target
                while not self.is_valid_sub_target(sub_target_2, self.obstacles_position):
                    sub_target_2 -= avoid_dir * resolution_sub_target
                #on maximise l'angle entre les segments pour avoir un path plus rectiligne
                val_1 = np.dot((sub_target_1-start)/np.linalg.norm(sub_target_1-start),
                               (target - sub_target_1)/np.linalg.norm(target - sub_target_1))
                val_2 = np.dot((sub_target_2 - start) / np.linalg.norm(sub_target_2 - start),
                               (target - sub_target_2) / np.linalg.norm(target - sub_target_2))
                if val_1 > val_2: #le segment 1 est plus aligne avec le path precedant que le segment2
                    sub_target = sub_target_1.copy()
                    sub_target_potential = sub_target_1.copy()
                    while np.linalg.norm(sub_target - sub_target_1) < 100:
                        sub_target_potential += avoid_dir * resolution_sub_target
                        if not self.is_valid_sub_target(sub_target_potential, self.obstacles_position):
                            break
                        sub_target_1 = sub_target_potential
                    sub_target = sub_target_1
                else:
                    sub_target = sub_target_2.copy()
                    sub_target_potential = sub_target_2.copy()
                    while np.linalg.norm(sub_target - sub_target_2) < 100:
                        sub_target_potential -= avoid_dir * resolution_sub_target
                        if not self.is_valid_sub_target(sub_target_potential, self.obstacles_position):
                            break
                        sub_target_2 = sub_target_potential
                    sub_target = sub_target_2

        return sub_target

    def is_valid_sub_target(self, sub_target: Position, obstacles: np.ndarray) -> bool:
        dist_sub_2_obs = np.linalg.norm(obstacles - sub_target, axis=1)
        return not np.any(dist_sub_2_obs < self.obstacles_avoid_distance)

    def is_full_path_colliding(self, full_path):
        old_path_points = full_path.points[1:]
        start = full_path.start
        for point in old_path_points:
            if self.is_path_colliding(start.array, point.array):
                return True
            start = point
        return False

    def update_last_path(self, start, target):
        distance_from_old_target = (self.old_path.target - target).norm
        self.old_path.start = start
        self.old_path.points[0] = start
        self.old_path = self.verify_first_points_of_path(self.old_path)
        if distance_from_old_target < 50:
            self.old_path.target = target
            self.old_path.points[-1] = target
            return self.old_path
        else:
            return self.path_planner(start.array, target.array)

    def verify_first_points_of_path(self, path):
        if len(path.points) > 2:
            if not self.is_path_colliding(path.start.array, path.points[2].array):
                del path.points[1]
        return path


def normalize(vec: np.ndarray) -> np.ndarray:
    return vec.copy() / np.linalg.norm(vec)


def perpendicular(vec: np.ndarray) -> np.ndarray:
    """Return the orthonormal vector to the np.array([0,0,1]) with right hand rule."""
    return normalize(np.array([-vec[1], vec[0]]))

