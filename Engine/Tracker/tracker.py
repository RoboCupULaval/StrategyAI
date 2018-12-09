
import logging
from multiprocessing import Queue
from multiprocessing.managers import DictProxy
from time import time
from typing import Dict, List, Union, Any, Iterable

import numpy as np

from Engine.Communication.robot_state import RobotState
from Engine.Tracker.Filters import RobotFilter
from Engine.Tracker.Filters.ball_kalman_filter import BallFilter
from Util import Pose, Position
from Util.geometry import rotate, wrap_to_pi
from config.config import Config

config = Config()


class Tracker:

    def __init__(self, vision_state: DictProxy, ui_send_queue: Queue):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ui_send_queue = ui_send_queue

        self.vision_state = vision_state

        self._blue_team = [RobotFilter(robot_id) for robot_id in range(config['ENGINE']['max_robot_id'])]
        self._yellow_team = [RobotFilter(robot_id) for robot_id in range(config['ENGINE']['max_robot_id'])]
        self._balls = [BallFilter(ball_id) for ball_id in range(config['ENGINE']['max_ball_on_field'])]

        self._camera_capture_time = [-1 for _ in range(config['ENGINE']['number_of_camera'])]
        self.neg_side = True if config['COACH']['on_negative_side'] else False
        self.our_color = config['COACH']['our_color']

    def update(self) -> Dict[str, List[Dict[str, Any]]]:

        for frame in self.camera_frames:
            self._log_new_robots_on_field(frame)
            self._camera_capture_time[frame['camera_id']] = frame['t_capture']
            self._update(frame)

        self._remove_undetected()

        return self.game_state

    def _update(self, detection_frame: Dict[str, List[Dict[str, Any]]]):

        for robot_obs in detection_frame.get('robots_blue', ()):
            obs = np.array([robot_obs['x'], robot_obs['y'], robot_obs['orientation']])
            self._blue_team[robot_obs['robot_id']].update(obs, detection_frame['t_capture'])

        for robot_obs in detection_frame.get('robots_yellow', ()):
            obs = np.array([robot_obs['x'], robot_obs['y'], robot_obs['orientation']])
            self._yellow_team[robot_obs['robot_id']].update(obs, detection_frame['t_capture'])

        for ball_obs in detection_frame.get('balls', ()):
            obs = np.array([ball_obs['x'], ball_obs['y']])
            closest_ball = self.find_closest_ball_to_observation(obs)
            if closest_ball:
                closest_ball.update(obs, detection_frame['t_capture'])
            else:
                self.logger.debug('The tracker is not able to assign some observations to a ball. '
                                  'Try to increase the maximal number of ball on the field or recalibrate the vision.')

    def predict(self, robot_state: RobotState, dt: float):

        velocity_commands = [Pose() for _ in range(len(self._our_team))]
        for packet in robot_state.packet:
            velocity_commands[packet.robot_id] = packet.command

        for robot in self._our_team:
            if robot.orientation is not None:
                velocity = self._put_in_world_referential(robot.orientation, velocity_commands[robot.id])
                robot.predict(dt, next_velocity=velocity.to_array())

        for robot in self._their_team:
            robot.predict(dt)

        for ball in self._balls:
            ball.predict(dt)

    def _remove_undetected(self):

        for team_color, robots in self.active_robots.items():
            undetected_robots = set()
            for robot in robots:
                if time() - robot.last_update_time > config['ENGINE']['max_undetected_robot_time']:
                    undetected_robots.add(robot.id)
                    robot.reset()

            if undetected_robots:
                self.logger.debug('%s robot(s) undetected for more than %.2f seconds: %r',
                                  team_color.capitalize(),
                                  config['ENGINE']['max_undetected_robot_time'],
                                  undetected_robots)

        for ball in self.active_balls:
            if time() - ball.last_update_time > config['ENGINE']['max_undetected_ball_time']:
                ball.reset()
                self.logger.debug('Ball %d was undetected for more than %.2f seconds.',
                                  ball.id,
                                  config['ENGINE']['max_undetected_ball_time'])

    def _put_in_world_referential(self, orientation: float, cmd: Pose) -> Pose:
        if self.neg_side:
            cmd.position = rotate(cmd.position, -np.pi - orientation)
            cmd.x *= -1
            cmd.orientation *= -1
        else:
            cmd.position = rotate(cmd.position, orientation)
        return cmd

    def _log_new_robots_on_field(self, detection_frame: Dict[str, List[Dict[str, Any]]]):
        new_robots = {'blue': set(), 'yellow': set()}

        for robot_obs in detection_frame.get('robots_blue', ()):
            if not self._blue_team[robot_obs['robot_id']].is_active: new_robots['blue'].add(robot_obs['robot_id'])

        if new_robots['blue']:
            self.logger.debug('Blue robot(s) detected: %r', new_robots['blue'])

        for robot_obs in detection_frame.get('robots_yellow', ()):
            if not self._yellow_team[robot_obs['robot_id']].is_active: new_robots['yellow'].add(robot_obs['robot_id'])
        if new_robots['yellow']:
            self.logger.debug('Yellow robot(s) detected: %r', new_robots['yellow'])

    @property
    def camera_frames(self) -> List[Dict[str, Any]]:

        valid_frames = [frame for frame in self.vision_state if self._is_valid_frame(frame)]

        if self.neg_side:
            valid_frames = [Tracker._change_frame_side(frame) for frame in valid_frames]

        return sorted(valid_frames, key=lambda frame: frame['t_capture'])

    @staticmethod
    def _change_frame_side(detection_frame: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:

        for robot_obs in detection_frame.get('robots_blue', []) + detection_frame.get('robots_yellow', []):
            robot_obs['x'] *= -1
            robot_obs['orientation'] = wrap_to_pi(np.pi - robot_obs['orientation'])

        for ball_obs in detection_frame.get('balls', ()):
            ball_obs['x'] *= -1

        return detection_frame

    def _is_valid_frame(self, frame):
        if frame:
            disabled_camera_id = config['ENGINE']['disabled_camera_id']
            cam_id = frame['camera_id']
            last_capture_time = self._camera_capture_time[cam_id]
            return frame['t_capture'] > last_capture_time and cam_id not in disabled_camera_id

    @property
    def _our_team(self):
        if self.our_color == 'yellow':
            our_team = self._yellow_team
        else:
            our_team = self._blue_team
        return our_team

    @property
    def _their_team(self):
        if self.our_color == 'yellow':
            their_team = self._blue_team
        else:
            their_team = self._yellow_team
        return their_team

    @property
    def active_robots(self):
        return {'blue': [robot for robot in self._blue_team if robot.is_active],
                'yellow': [robot for robot in self._yellow_team if robot.is_active]}

    @property
    def active_balls(self):
        return [ball for ball in self._balls if ball.is_active]

    @property
    def inactive_balls(self):
        return [ball for ball in self._balls if not ball.is_active]

    @property
    def game_state(self) -> Dict[str, Union[float, List[Dict[str, Any]]]]:
        game_fields = dict()
        game_fields['timestamp'] = time()
        game_fields['blue'] = self.blue_team
        game_fields['yellow'] = self.yellow_team
        game_fields['balls'] = self.balls
        return game_fields

    @property
    def balls(self) -> List[Dict[str, Any]]:
        return Tracker._format_entities(sorted(self.active_balls, key=lambda b: b.first_update_time))

    @property
    def blue_team(self) -> List[Dict[str, Any]]:
        return Tracker._format_entities(self.active_robots['blue'])

    @property
    def yellow_team(self) -> List[Dict[str, Any]]:
        return Tracker._format_entities(self.active_robots['yellow'])

    @staticmethod
    def _format_entities(entities: Iterable[Union[RobotFilter, BallFilter]]) -> List[Dict[str, Any]]:
        formatted_list = []
        for entity in entities:
            fields = dict()
            if type(entity) is RobotFilter:
                fields['pose'] = Pose.from_values(*entity.pose)
                fields['velocity'] = Pose.from_values(*entity.velocity)
            elif type(entity) is BallFilter:
                fields['position'] = Position(*entity.position)
                fields['velocity'] = Position(*entity.velocity)
            else:
                raise TypeError('Invalid type provided: {}'.format(type(entity)))

            fields['id'] = entity.id
            formatted_list.append(fields)
        return formatted_list

    def find_closest_ball_to_observation(self, obs: np.ndarray) -> BallFilter:

        if any(self.active_balls):
            balls_position = np.array([ball.position for ball in self.active_balls])
            dists = np.linalg.norm(balls_position - obs, axis=1)
            idx = np.argmin(dists).view(int)
            closest_ball = self.active_balls[idx]
            if dists[idx] > config['ENGINE']['max_ball_separation']:
                if len(self.inactive_balls) > 0:
                    closest_ball = self.inactive_balls[0]
                    self.logger.debug('New ball detected: ID %d.', closest_ball.id)
                else:
                    closest_ball = None
        else:
            closest_ball = self.inactive_balls[0]
            self.logger.debug('A ball was detected on the field.')

        return closest_ball


