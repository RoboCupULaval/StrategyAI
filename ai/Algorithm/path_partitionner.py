from enum import Enum

import numpy as np
import numpy.matlib

from Util import Pose, Position
from Util.geometry import conv_position_2_list, remove_duplicates
from ai.GameDomainObjects import Player
from Util.geometry import conv_position_2_list, remove_duplicates
from Util.path import Path


class CollisionType(Enum):
    PLAYER = 0
    BALL = 1
    ZONE = 2


class CollisionBody:
    UNCOLLIDABLE = 0
    COLLIDABLE = 1

    def __init__(self, body_position=Position, body_velocity=Position, body_avoid_radius=150,
                 collision_type: CollisionType = CollisionType.PLAYER, body_pose=Pose, max_acc=2, ident_num=-1):
        self.position = body_position
        self.velocity = body_velocity
        self.avoid_radius = body_avoid_radius
        self.type = collision_type
        # object's maxmimum acceleration, needed for path_reshaper
        self.max_acc = max_acc
        # only for retro compatibility and to allow future usage
        self.pose = body_pose
        # only for retro compatibility
        self.id = ident_num


class PathPartitionner():
    def __init__(self):
        self.path = Path(Position(0, 0), Position(0, 0))
        self.res = 100
        self.gap_proxy = 200
        self.max_recurs = 3
        self.collision_body = []
        self.pose_obstacle = None
        self.cruise_speed = 1
        self.player = None
        self.closest_obs_speed = np.array([0, 0])
        self.path_appendice = None
        self.end_speed = 0
        self.ball_collision = False
        self.avoid_radius = np.array([])
        self.optional_collision = None
        self.collidable_objects = None
        self.pose_target = CollisionBody(body_avoid_radius=1)

    def fastpathplanner(self, path, depth=0, avoid_dir=None):
        self.get_pertinent_collision_objects(False)
        if self.is_path_collide(path) and depth < self.max_recurs and not(path.start == path.goal):
            sub_target, avoid_dir = self.search_point(path, avoid_dir)
            if sub_target == path.goal or sub_target == path.start:
                return path
            path_1 = Path(path.start, sub_target)

            path_1 = self.fastpathplanner(path_1, depth + 1, avoid_dir)

            path_2 = Path(sub_target, path.goal)
            path_2 = self.fastpathplanner(path_2, depth + 1, avoid_dir)

            path = path_1.join_segments(path_2)
        return path

    def get_path(self, player: CollisionBody, pose_target: CollisionBody, cruise_speed=1,
                 old_path=None, end_speed=0, collidable_objects=None):
        self.cruise_speed = cruise_speed
        self.pose_target = pose_target
        self.collidable_objects = collidable_objects
        self.end_speed = end_speed
        self.player = player
        # compatibilite avec ancienne version de get_pertinent_collision_objects()
        self.ball_collision = False
        self.optional_collision = None
        # Debug code pls no remove
        # if old_path is not None:
        self.get_pertinent_collision_objects()
        self.path = Path(self.player.position, self.pose_target.position, self.player.velocity.norm(), self.end_speed * 1000)
        if len(self.collision_body) <= 0:
            return self.path
        #if old_raw_path is not None:
            # print(old_raw_path.points)
            # start_1 = time.time()
            # self.is_path_collide(old_raw_path, tolerance=self.gap_proxy-50)
            # end_1 = time.time()
            # start_2 = time.time()
            # self.is_path_collide_legacy(old_raw_path, tolerance=self.gap_proxy - 50)
            # end_2 = time.time()
            #print(end_1 - start_1, end_2 - start_2)
            #print("is_path_colide", self.is_path_collide(old_raw_path, tolerance=8))
            # print("meme goal?", (np.linalg.norm(pose_target.position - old_raw_path.goal) < 200))
            # print("quel goal?", pose_target.position, old_raw_path.goal)


        if self.end_speed == 0:
            hysteresis = 50 * cruise_speed
        else:
            hysteresis = 50 * cruise_speed
        if False:
        # if (old_path is not None) and (not self.is_path_collide(old_path,
        #                                                         tolerance=8)) and \
        #         ((self.pose_target.position - old_path.goal).norm() < hysteresis):
            if False:
                old_path.quick_update_path(self.player.position)
                self.path_appendice = Path(old_path.goal, self.path.goal)
                self.path_appendice = self.fastpathplanner(self.path_appendice)
            else:
                old_path.quick_update_path(self.player.position)
                self.path = old_path

        else:
            if self.path.get_path_length() < 0.1:
                """
                hack shady pour eviter une erreur shady (trop fatiguer pour dealer ak ste shit la)
                
                File "/home/phil/robocup/StrategyIA/RULEngine/Util/position.py", line 68, in __eq__
                    min_abs_tol = min(self.abs_tol, other.position.abs_tol)
                    AttributeError: 'numpy.ndarray' object has no attribute 'position'
                """
                return self.path
            self.closest_obs_speed = self.find_closest_obstacle(self.player.position, self.path)
            self.path = self.fastpathplanner(self.path)

        return self.path

    def get_pertinent_collision_objects(self, first_call=True):
        factor = 1.1
        if first_call:
            for collidable_object in self.collidable_objects:
                if (self.player.position - collidable_object.position).norm() + \
                        (self.pose_target.position - collidable_object.position).norm() < \
                        (self.pose_target.position - self.player.position).norm() * factor:
                    self.collision_body.append(collidable_object)
            self.pose_obstacle = np.array([obj.position for obj in self.collision_body])
            self.avoid_radius = np.array([obj.avoid_radius for obj in self.collision_body])
        else:
            temp = (self.path.start - self.pose_obstacle) + (self.path.goal - self.pose_obstacle)
            norm = np.sqrt((temp * temp).sum(axis=1))
            conditon = norm < (self.path.goal - self.path.start).norm()
            self.pose_obstacle = self.pose_obstacle[conditon, :]
            self.collision_body = np.array(self.collision_body)[conditon]
            self.avoid_radius = self.avoid_radius[conditon]

    def is_path_collide_legacy(self, path, obstacles=None, tolerance=None):
        if obstacles is None:
            obstacles = self.pose_obstacle
        if tolerance is None:
            tolerance = self.gap_proxy
        for idx, points in enumerate(path.points[:-1]):
            pose_start = path.points[idx]
            pose_target = path.points[idx + 1]
            direction = (pose_target - pose_start)
            if (direction).norm() < 0.00001:
                return False
            else:
                direction = direction / direction.norm()
            distance_sub_path = (pose_start - pose_target).norm()
            if distance_sub_path > 0.01:
                for pose_obs in obstacles:
                    vec_robot_2_obs = pose_obs - pose_start
                    if (vec_robot_2_obs).norm() < 0.00001:
                        continue
                    dist_from_path = abs(np.cross(direction, vec_robot_2_obs))
                    projection_obs_on_direction = \
                        np.dot(direction, vec_robot_2_obs / (vec_robot_2_obs).norm())
                    if projection_obs_on_direction < 0.00001 or projection_obs_on_direction > 1:
                        dist_from_path_temp = (pose_start - pose_obs).norm()
                        if dist_from_path_temp > (pose_target - pose_obs).norm():
                            dist_from_path = (pose_target - pose_obs).norm()
                        else:
                            dist_from_path = dist_from_path_temp
                    if tolerance > dist_from_path:
                        return True
        return False

    def is_path_collide(self, path=None, obstacles=None, tolerance=None, flag_closest_obs=False):
        if path is None:
            return False
        if obstacles is None:
            obstacles = self.pose_obstacle
        if tolerance is None:
            tolerances = self.avoid_radius
        else:
            tolerances = self.avoid_radius / tolerance
        if path.start == path.goal or len(obstacles) == 0:
            return False
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
        if (dist_robot_2_obs == 0).all() and (path.start - path.goal).norm() > 50:
            return True
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
        if flag_closest_obs:
            dists_to_consider_condition = np.abs(dists_to_consider) < tolerances
            collision_body = np.array(self.collision_body)
            collision_body = np.array([collision_body[points_to_consider]]).T
            collision_body = collision_body[dists_to_consider_condition]
            dist_robot_2_obs = dist_robot_2_obs[dists_to_consider_condition]
            idx = np.argmin(dist_robot_2_obs)
            closest_collision_body = collision_body[idx]
            return closest_collision_body.position, dist_robot_2_obs[idx], closest_collision_body

        else:
            tolerances = tolerances[points_to_consider]
            if dists_to_consider[np.abs(dists_to_consider) < tolerances].any() and (path.start - path.goal).norm() > 50:
                return True
            return False

    def find_closest_obstacle_legacy(self, point, path):
        assert(isinstance(point, Position))
        dist_point_obs = np.inf
        closest_obs = None
        closest_collision_body = self.collision_body[0].position
        if (path.start - path.goal).norm() < 0.001:
            return [closest_obs, dist_point_obs, closest_collision_body]
        if point == path.start:
            return [closest_obs, dist_point_obs, closest_collision_body]
        pose_start = path.start
        direction = (point - pose_start).normalized()

        for idx, pose_obs in enumerate(self.pose_obstacle):
            vec_robot_2_obs_temp = pose_obs - pose_start
            dist_from_path_temp = (np.cross(direction, vec_robot_2_obs_temp)).norm()
            if self.avoid_radius[idx] > dist_from_path_temp:
                obstacle_pos = Position(pose_obs)
                dist = (path.start - obstacle_pos).norm()
                if dist < dist_point_obs:
                    dist_point_obs = dist
                    closest_obs = obstacle_pos
                    closest_collision_body = self.collision_body[idx]
        return [closest_obs, dist_point_obs, closest_collision_body]

    def find_closest_obstacle(self, point, path):
        assert(isinstance(point, Position))
        dist_point_obs = np.inf
        closest_obs = None
        if len(self.collision_body) <= 0:
            return False
        closest_collision_body = self.collision_body[0].position
        if (path.start - path.goal).norm() < 0.001:
            return [closest_obs, dist_point_obs, closest_collision_body]
        if point == path.start:
            return [closest_obs, dist_point_obs, closest_collision_body]
        path.goal = point
        return self.is_path_collide(path, tolerance=None, flag_closest_obs=True)

    # TODO: Remove when the new one is well tested
    def verify_sub_target_legacy(self, sub_target):
        for collision_body in self.collision_body:
            pose_obs = collision_body.position
            dist_sub_2_obs = (Position(pose_obs) - sub_target).norm()
            if dist_sub_2_obs < collision_body.avoid_radius:
                return True
        return False

    def verify_sub_target(self, sub_target):
        dist_sub_2_obs = np.sqrt(((self.pose_obstacle - sub_target) * (self.pose_obstacle - sub_target)).sum(axis=1))
        if dist_sub_2_obs[dist_sub_2_obs < self.avoid_radius].any():
            return True
        return False

    def search_point(self, path, avoid_dir=None):

        pose_robot = path.start
        pose_target = path.goal
        pose_obstacle_closest, dist_point_obs, closest_collision_body = self.find_closest_obstacle(pose_target, path)
        if pose_obstacle_closest is None:
            sub_target = pose_target
            return sub_target, avoid_dir

        direction = (pose_target - pose_robot) / (pose_target - pose_robot).norm()
        vec_robot_2_obs = np.array(conv_position_2_list(pose_obstacle_closest - pose_robot))
        len_along_path = np.dot(vec_robot_2_obs, direction)
        # dist_from_path = (np.cross(direction, vec_robot_2_obs)).norm()
        # projection_obs_on_direction = np.dot(direction, vec_robot_2_obs / vec_robot_2_obs.norm())
        self.res = closest_collision_body.avoid_radius / 10.
        if 0 < len_along_path < (pose_target - pose_robot).norm():
            vec_perp = direction.perpendicular()
            vec_perp = vec_perp[0:2] / vec_perp.norm()
            cruise_speed = self.player.velocity.conv_2_np()
            self.closest_obs_speed = closest_collision_body.velocity
            avoid_dir = -vec_perp
            if closest_collision_body.type == CollisionType.BALL or closest_collision_body.type == CollisionType.ZONE:
                avoid_dir = -vec_perp
                sub_target_1 = np.array(conv_position_2_list(pose_robot)) + \
                    direction * len_along_path + vec_perp * self.res
                sub_target_2 = np.array(conv_position_2_list(pose_robot)) + \
                    direction * len_along_path - vec_perp * self.res
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
                if cruise_speed.norm() < 0.1:
                    sub_target = sub_target_1
                elif np.abs(np.dot(direction, (sub_target_1 - path.start) / (sub_target_1 - path.start).norm())) > \
                        np.abs(np.dot(direction, (sub_target_2 - path.start) / (sub_target_2 - path.start).norm())):
                    sub_target = sub_target_1
                else:
                    sub_target = sub_target_2

            else:
                # if np.dot(avoid_dir, np.transpose(vec_perp)) < 0:
                #     vec_perp = -vec_perp
                if avoid_dir.norm() > 0.001:
                    avoid_dir /= np.linalg.norm(avoid_dir)
                elif np.dot(avoid_dir, np.transpose(vec_perp)) < 0:
                    avoid_dir = -vec_perp
                else:
                    avoid_dir = vec_perp
                sub_target = np.array(conv_position_2_list(pose_robot)) +\
                    direction * len_along_path + vec_perp * self.res

                bool_sub_target = self.verify_sub_target(Position(sub_target[0], sub_target[1]))
                while bool_sub_target:
                    sub_target -= avoid_dir * self.res
                    bool_sub_target = self.verify_sub_target(Position(sub_target[0], sub_target[1]))

                sub_target -= avoid_dir * 0.01 * self.res
                avoid_dir = vec_perp
            sub_target = Position(sub_target[0], sub_target[1])
        else:
            sub_target = Position(pose_target[0], pose_target[1])
        sub_target = Position(sub_target[0], sub_target[1])
        return [sub_target, avoid_dir]

    def get_next_point(self, robot_id=None):
        pass

    def update(self):
        pass

    def remove_redundant_points(self):
        if len(self.path.points) > 2:
            if self.player.velocity.norm() > 1000:
                points, speeds = remove_duplicates(self.path.points, self.path.speeds,
                                                   5 * self.player.velocity.norm() / 500)
            else:
                points, speeds = remove_duplicates(self.path.points, self.path.speeds, 5)
            return Path().generate_path_from_points(points, speeds)
        else:
            return Path().generate_path_from_points(self.path.points, self.path.speeds)



