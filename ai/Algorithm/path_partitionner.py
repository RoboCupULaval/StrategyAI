from enum import Enum
from time import sleep

import numpy as np
import numpy.matlib

from Util import Position
from Util.geometry import perpendicular, normalize
from Util.path import Path


MIN_PATH_LENGTH = 50  # mm


class CollisionType(Enum):
    PLAYER = 0
    BALL = 1
    ZONE = 2


class CollisionBody:
    UNCOLLIDABLE = 0
    COLLIDABLE = 1

    def __init__(self, position: Position, velocity: Position=Position(), avoid_radius=1,
                 collision_type: CollisionType = CollisionType.PLAYER):
        self.position = position
        self.velocity = velocity
        self.avoid_radius = avoid_radius
        self.type = collision_type

v_inner = np.vectorize(np.inner)


class PathPartitionner:

    def __init__(self):
        self.path = Path()
        self.res = 100
        self.max_recurs = 3

        self.obstacles_position = None
        self.avoid_radius = np.array([])
        self.obstacles = None

        self.player = None
        self.target = None

    def fast_path_planner(self, path, depth=0, avoid_dir=None):
        self.fast_update_pertinent_collision_objects()
        if depth < self.max_recurs and not path.start == path.goal:
            if self.is_path_colliding(path):
                sub_target, avoid_dir = self.next_sub_target(path, avoid_dir)
                if sub_target != path.goal and sub_target != path.start:
                    path_1 = self.fast_path_planner(Path(path.start, sub_target), depth + 1, avoid_dir)
                    path_2 = self.fast_path_planner(Path(sub_target, path.goal), depth + 1, avoid_dir)
                    path = path_1.join_segments(path_2)

        return path

    def get_path(self, player: CollisionBody, target: CollisionBody, obstacles=None):

        self.target = target
        self.obstacles = obstacles
        self.player = player
        self.update_pertinent_collision_objects()
        self.path = Path(self.player.position, self.target.position)

        if any(self.obstacles):
            self.path = self.fast_path_planner(self.path)

        return self.path

    def update_pertinent_collision_objects(self):
        factor = 1.1
        consider_collision_body = []
        for collidable_object in self.obstacles:
            dist_player_to_obstacle = (self.player.position - collidable_object.position).norm
            dist_target_to_obstacle = (self.target.position - collidable_object.position).norm
            dist_target_to_player = (self.target.position - self.player.position).norm
            if dist_player_to_obstacle + dist_target_to_obstacle < dist_target_to_player * factor:
                consider_collision_body.append(collidable_object)

        self.avoid_radius = np.array([obstacle.avoid_radius for obstacle in consider_collision_body])
        self.obstacles = consider_collision_body

    def fast_update_pertinent_collision_objects(self):
        obstacles_position = np.array([obstacle.position for obstacle in self.obstacles])
        temp = (self.path.start - obstacles_position) + (self.path.goal - obstacles_position)
        norm = np.linalg.norm(temp, axis=1)
        condition = norm < (self.path.goal - self.path.start).norm
        self.obstacles = np.array(self.obstacles)[condition]
        self.avoid_radius = self.avoid_radius[condition]

    def is_path_colliding(self, path: Path, tolerance=1):

        if path.length < MIN_PATH_LENGTH or self.obstacles is None:
            return False

        closest_obstacle_pos = self.find_closest_obstacle(path, tolerance=tolerance)
        return closest_obstacle_pos is not None

    def find_closest_obstacle(self, path: Path, tolerance=1):

        if not any(self.obstacles):
            return None

        if path is None or path.length < 0.001:
            return None

        obstacles, distances = self.find_obstacles(path, tolerance=tolerance)

        if not np.any(obstacles):
            return None

        idx = np.argmin(distances)
        return obstacles[idx]

    def find_obstacles(self, path, tolerance=1):

        obstacles = np.array([obstacle.position for obstacle in self.obstacles])

        if path.length < MIN_PATH_LENGTH or obstacles is None:
            return None, 0

        directions = normalize(path.goal - path.start)

        robot_to_obstacles = self.obstacles_position - path.start
        robot_to_obstacle_norm = np.linalg.norm(robot_to_obstacles, axis=1)
        robot_to_obstacle_norm = robot_to_obstacle_norm.reshape(len(robot_to_obstacles), 1)

        dists_from_path = np.abs(np.cross(directions, robot_to_obstacles))

        dists_to_consider_condition = np.abs(dists_from_path) < self.avoid_radius / tolerance
        robot_to_obstacle_norm = robot_to_obstacle_norm[dists_to_consider_condition]

        obstacles = np.array(self.obstacles)
        obstacles = obstacles[dists_to_consider_condition]

        return obstacles, robot_to_obstacle_norm

    def next_sub_target(self, path, avoid_dir=None):

        closest_obstacle = self.find_closest_obstacle(path)

        if closest_obstacle is None:
            return path.goal, avoid_dir

        start_to_goal = path.goal - path.start
        start_to_goal_direction = normalize(start_to_goal)
        start_to_closest_obstacle = closest_obstacle.position - path.start
        len_along_path = np.dot(start_to_closest_obstacle, start_to_goal_direction)

        resolution = closest_obstacle.avoid_radius / 10.

        if not (0 < len_along_path < start_to_goal.norm):
            sub_target = path.goal
        else:
            avoid_dir = perpendicular(start_to_goal_direction)
            sub_target = path.start + start_to_goal_direction * len_along_path - avoid_dir * self.res
            sub_target = self.optimize_sub_target(sub_target, -avoid_dir, res=resolution)

        return [sub_target, avoid_dir]

    def verify_sub_target(self, sub_target):
        obstacles_position = np.array([obstacle.position for obstacle in self.obstacles])
        dist_sub_2_obs = np.sqrt((np.square(obstacles_position - sub_target)).sum(axis=1))

        return dist_sub_2_obs[dist_sub_2_obs < self.avoid_radius].any()

    def optimize_sub_target(self, initial_sub_target, avoid_dir, res):
        bool_sub_target_1 = self.verify_sub_target(initial_sub_target)
        sub_target = initial_sub_target
        while bool_sub_target_1:
            sub_target -= avoid_dir * res
            bool_sub_target_1 = self.verify_sub_target(sub_target)
            sub_target -= avoid_dir * 0.01 * res
        return sub_target.view(Position)
