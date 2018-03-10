
import numpy as np

from Util import Position
from Util.geometry import perpendicular, normalize
from Util.path import Path

MIN_PATH_LENGTH = 100  # mm
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

        return path

    @staticmethod
    def path_planner(start, target, obstacles, avoid_dir=None, depth=0):

        if start == target or depth >= RECURSION_LIMIT:
            return Path(start, target)

        if (start - target).norm <= MIN_PATH_LENGTH:
            return Path(start, target)

        if not np.any(obstacles):
            return Path(start, target)

        if not PathPartitionner.is_path_colliding(start, target, obstacles):
            return Path(start, target)

        sub_target, avoid_dir = PathPartitionner.next_sub_target(start, target, obstacles, avoid_dir)
        if sub_target is None or sub_target == target or sub_target == start:
            return Path(start, target)

        path_1 = PathPartitionner.path_planner(start, sub_target, obstacles, avoid_dir, depth=depth+1)
        path_2 = PathPartitionner.path_planner(sub_target, target, obstacles, avoid_dir, depth=depth+1)

        return path_1.join_segments(path_2)

    @staticmethod
    def is_path_colliding(start, target, obstacles):
        obstacles = PathPartitionner.filter_obstacles(start, target, obstacles)
        collision_position, _ = PathPartitionner.find_collisions(start, target, obstacles)
        return np.any(collision_position)

    @staticmethod
    def filter_obstacles(start, target, obstacles):
        obstacles_position = np.array([obstacle.position for obstacle in obstacles])
        temp = np.linalg.norm(start - obstacles_position + target - obstacles_position, axis=1)
        is_inside_ellipse = temp <= np.sqrt((start - target).norm ** 2 + ELLIPSE_HALF_WIDTH ** 2)
        return obstacles[is_inside_ellipse]

    @staticmethod
    def find_collisions(start, target, obstacles):

        if not np.any(obstacles):
            return None, 0

        obstacles_pos = np.array([obstacle.position for obstacle in obstacles])
        avoid_radius = np.array([obstacle.avoid_radius for obstacle in obstacles])

        directions = normalize(target - start)

        robot_to_obstacles = obstacles_pos - start
        robot_to_obstacle_norm = np.linalg.norm(robot_to_obstacles, axis=1)
        robot_to_obstacle_norm = robot_to_obstacle_norm.reshape(len(robot_to_obstacles), 1)

        dists_from_path = np.abs(np.cross(directions, robot_to_obstacles))

        valid_obstacles = np.abs(dists_from_path) < avoid_radius

        return obstacles[valid_obstacles], robot_to_obstacle_norm[valid_obstacles]

    @staticmethod
    def next_sub_target(start, target, obstacles, avoid_dir=None):
        collisions, distances = PathPartitionner.find_collisions(start, target, obstacles)

        if np.any(collisions):
            closest_collision = collisions[np.argmin(distances)]
        else:
            return target, avoid_dir

        start_to_goal = target - start
        start_to_goal_direction = normalize(start_to_goal)
        start_to_closest_obstacle = closest_collision.position - start
        len_along_path = np.dot(start_to_closest_obstacle, start_to_goal_direction)

        resolution = closest_collision.avoid_radius / SUB_TARGET_RESOLUTION_FACTOR

        if not (0 < len_along_path < start_to_goal.norm):
            return target, avoid_dir
        else:
            avoid_dir = perpendicular(start_to_goal_direction)
            sub_target = start + start_to_goal_direction * len_along_path - avoid_dir * resolution
            sub_target = PathPartitionner.optimize_sub_target(sub_target, obstacles, -avoid_dir, res=resolution)

        return sub_target, avoid_dir

    @staticmethod
    def optimize_sub_target(initial_sub_target, obstacles, avoid_dir, res):
        bool_sub_target_1 = PathPartitionner.verify_sub_target(initial_sub_target, obstacles)
        sub_target = initial_sub_target
        while bool_sub_target_1:
            sub_target -= avoid_dir * res
            bool_sub_target_1 = PathPartitionner.verify_sub_target(sub_target, obstacles)
            sub_target -= avoid_dir * 0.01 * res
        return sub_target.view(Position)

    @staticmethod
    def verify_sub_target(sub_target, obstacles):
        obstacles_position = np.array([obstacle.position for obstacle in obstacles])
        avoid_radius = np.array([obstacle.avoid_radius for obstacle in obstacles])

        dist_sub_2_obs = np.sqrt((np.square(obstacles_position - sub_target)).sum(axis=1))

        return dist_sub_2_obs[dist_sub_2_obs < avoid_radius].any()
