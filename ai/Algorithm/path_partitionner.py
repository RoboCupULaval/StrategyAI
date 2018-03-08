from enum import Enum

import numpy as np
import numpy.matlib

from Util import Position
from Util.geometry import perpendicular, normalize
from Util.path import Path


class CollisionType(Enum):
    PLAYER = 0
    BALL = 1
    ZONE = 2


class CollisionBody:
    UNCOLLIDABLE = 0
    COLLIDABLE = 1

    def __init__(self, position: Position, velocity: Position=Position(), avoid_radius=150,
                 collision_type: CollisionType = CollisionType.PLAYER):
        self.position = position
        self.velocity = velocity
        self.avoid_radius = avoid_radius
        self.type = collision_type


class PathPartitionner():

    def __init__(self):
        self.path = Path()
        self.res = 100
        self.max_recurs = 3
        self.collision_body = []
        self.pose_obstacle = None
        self.player = None
        self.end_speed = 0
        self.avoid_radius = np.array([])
        self.collidable_objects = None
        self.target = CollisionBody(Position(), avoid_radius=1)

    def fast_path_planner(self, path, depth=0, avoid_dir=None):
        self.fast_update_pertinent_collision_objects()
        if depth < self.max_recurs and not(path.start == path.goal):
            if self.is_path_colliding(path):
                sub_target, avoid_dir = self.next_sub_target(path, avoid_dir)
                if sub_target != path.goal and sub_target != path.start:
                    path_1 = self.fast_path_planner(Path(path.start, sub_target), depth + 1, avoid_dir)
                    path_2 = self.fast_path_planner(Path(sub_target, path.goal), depth + 1, avoid_dir)
                    path = path_1.join_segments(path_2)

        return path

    def get_path(self, player: CollisionBody, pose_target: CollisionBody, end_speed=0, collidable_objects=None):

        self.target = pose_target
        self.collidable_objects = collidable_objects
        self.end_speed = end_speed
        self.player = player
        self.update_pertinent_collision_objects()
        self.path = Path(self.player.position, self.target.position, self.player.velocity.norm, self.end_speed * 1000)

        if any(self.collision_body):
            self.path = self.fast_path_planner(self.path)

        return self.path

    def update_pertinent_collision_objects(self):
        factor = 1.1
        for collidable_object in self.collidable_objects:
            dist_player_to_obstacle = (self.player.position - collidable_object.position).norm
            dist_target_to_obstacle = (self.target.position - collidable_object.position).norm
            dist_target_to_player = (self.target.position - self.player.position).norm
            if dist_player_to_obstacle + dist_target_to_obstacle < dist_target_to_player * factor:
                self.collision_body.append(collidable_object)
        self.pose_obstacle = np.array([obstacle.position for obstacle in self.collision_body])
        self.avoid_radius = np.array([obstacle.avoid_radius for obstacle in self.collision_body])

    def fast_update_pertinent_collision_objects(self):
        temp = (self.path.start - self.pose_obstacle) + (self.path.goal - self.pose_obstacle)
        norm = np.sqrt((temp * temp).sum(axis=1))
        condition = norm < (self.path.goal - self.path.start).norm
        self.pose_obstacle = self.pose_obstacle[condition, :]
        self.collision_body = np.array(self.collision_body)[condition]
        self.avoid_radius = self.avoid_radius[condition]

    def is_path_colliding(self, path: Path, tolerance=1):
        if path is None:
            return False

        obstacles = self.pose_obstacle
        start_to_goal = path.goal - path.start

        if start_to_goal.norm < 50 or not obstacles.any():
            return False

        closest_obstacle_pos, distance = self.find_closest_obstacle(path, tolerance=tolerance)

        return closest_obstacle_pos is not None

    def find_closest_obstacle(self, path: Path, tolerance=1):

        if not any(self.collision_body):
            return [None, np.inf]

        if path is None:
            return [None, np.inf]

        if path.length < 0.001:
            return [None, np.inf]

        if not self.pose_obstacle.any():
            return [None, np.inf]

        collision_bodies, distances = self.find_obstacles(path, tolerance=tolerance)

        if not collision_bodies.any():
            return [None, np.inf]

        idx = np.argmin(distances)
        return collision_bodies[idx], distances[idx]

    def find_obstacles(self, path, tolerance=1):

        obstacles = self.pose_obstacle

        tolerances = self.avoid_radius / tolerance

        start_to_goal = path.goal - path.start

        if start_to_goal.norm < 0.0001 or not obstacles.any():
            return [None, 0]

        points = np.array(path.points)
        points_start = points[:-1]
        points_target = points[1:]
        paths_len = np.sqrt(((points_target - points_start) * (points_target - points_start)).sum(axis=1))
        big_enough_paths = paths_len > 0.000001

        directions = np.array((points_target - points_start)[big_enough_paths])
        norm_directions = np.sqrt((directions * directions).sum(axis=1))
        norm_directions = np.matlib.repmat(norm_directions.reshape(norm_directions.shape[0], 1), 1, 2)
        directions = directions / norm_directions
        points_start = points_start[big_enough_paths]
        positions_obstacles = np.matlib.repmat(obstacles, 1, points_start.shape[0]).reshape((obstacles.shape[0] *
                                                                                             points_start.shape[0],
                                                                                             obstacles.shape[1]))
        tolerances = np.matlib.repmat(tolerances, 1, points_start.shape[0]).reshape((len(tolerances) *
                                                                                     points_start.shape[0],
                                                                                     1))

        vecs_robot_2_obs = positions_obstacles - np.matlib.repmat(points_start, obstacles.shape[0], 1)
        directions = np.matlib.repmat(directions, obstacles.shape[0], 1)
        dist_robot_2_obs = np.sqrt((vecs_robot_2_obs * vecs_robot_2_obs).sum(axis=1))

        big_enough_dists = dist_robot_2_obs > 0.0000001
        dist_robot_2_obs = dist_robot_2_obs[big_enough_dists]
        dist_robot_2_obs = dist_robot_2_obs.reshape(dist_robot_2_obs.shape[0], 1)
        vec_robot_2_obs = vecs_robot_2_obs[big_enough_dists]

        directions_valid = directions[big_enough_dists]
        tolerances = tolerances[big_enough_dists]
        dists_from_path = np.abs(np.cross(directions_valid, vec_robot_2_obs))
        projection_obs_on_direction = (directions_valid * vec_robot_2_obs / dist_robot_2_obs).sum(axis=1)

        points_to_consider = np.abs(projection_obs_on_direction) < 1
        dists_to_consider = dists_from_path[points_to_consider]
        dists_to_consider = dists_to_consider.reshape(dists_to_consider.shape[0], 1)
        dists_to_consider_condition = np.abs(dists_to_consider) < tolerances

        collision_body = np.array(self.collision_body)
        collision_body = np.array([collision_body[points_to_consider]]).T
        collision_body = collision_body[dists_to_consider_condition]

        dist_robot_2_obs = dist_robot_2_obs[dists_to_consider_condition]

        return collision_body, dist_robot_2_obs

    def next_sub_target(self, path, avoid_dir=None):

        closest_collision_body, dist_point_obs = self.find_closest_obstacle(path)

        pose_obstacle_closest = closest_collision_body.position
        if pose_obstacle_closest is None:
            return path.goal, avoid_dir

        start_to_goal = path.goal - path.start
        start_to_goal_direction = normalize(start_to_goal)
        start_to_closest_obstacle = pose_obstacle_closest - path.start
        len_along_path = np.dot(start_to_closest_obstacle, start_to_goal_direction)

        resolution = closest_collision_body.avoid_radius / 10.
        if 0 < len_along_path < start_to_goal.norm:

            vec_perp = perpendicular(start_to_goal_direction)
            avoid_dir = vec_perp

            if closest_collision_body.type == CollisionType.BALL or closest_collision_body.type == CollisionType.ZONE:

                # This code is never reach.

                sub_target_1 = path.start.position + start_to_goal_direction * len_along_path - avoid_dir * self.res
                sub_target_2 = path.start.position + start_to_goal_direction * len_along_path + avoid_dir * self.res

                sub_target_1 = self.optimize_sub_target(sub_target_1, -avoid_dir, res=resolution)
                sub_target_2 = self.optimize_sub_target(sub_target_2, avoid_dir, res=resolution)

                start_to_target_1 = normalize(sub_target_1 - path.start)
                start_to_target_2 = normalize(sub_target_2 - path.start)

                if self.player.velocity.norm < 0.1:
                    sub_target = sub_target_1
                else:
                    target_1_projection_toward_goal = np.dot(start_to_goal_direction, start_to_target_1)
                    target_2_projection_toward_goal = np.dot(start_to_goal_direction, start_to_target_2)

                    if target_1_projection_toward_goal > target_2_projection_toward_goal:
                        sub_target = sub_target_1
                    else:
                        sub_target = sub_target_2

            else:
                sub_target = path.start + start_to_goal_direction * len_along_path - avoid_dir * self.res
                sub_target = self.optimize_sub_target(sub_target, -avoid_dir, res=resolution)

        else:
            sub_target = path.goal

        return [sub_target, avoid_dir]

    def verify_sub_target(self, sub_target):
        dist_sub_2_obs = np.sqrt(((self.pose_obstacle - sub_target) * (self.pose_obstacle - sub_target)).sum(axis=1))
        if dist_sub_2_obs[dist_sub_2_obs < self.avoid_radius].any():
            return True
        return False

    def optimize_sub_target(self, initial_sub_target, avoid_dir, res):
        bool_sub_target_1 = self.verify_sub_target(initial_sub_target)
        sub_target = initial_sub_target
        while bool_sub_target_1:
            sub_target -= avoid_dir * res
            bool_sub_target_1 = self.verify_sub_target(sub_target)
            sub_target -= avoid_dir * 0.01 * res
        return sub_target.view(Position)
