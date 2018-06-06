
import logging
from multiprocessing.managers import DictProxy
from typing import Dict, List, Union, Any, Iterable
import numpy as np
from multiprocessing import Queue

# from Debug.debug_command_factory import DebugCommandFactory
from Engine.Communication.robot_state import RobotState
from Engine.filters.ball_kalman_filter import BallFilter
from Engine.filters.robot_kalman_filter import RobotFilter

from Util.geometry import rotate
from Util import Pose

from config.config import Config
config = Config()


class Tracker:

    MAX_ROBOT_ID = 12
    MAX_BALL_ON_FIELD = 1
    MAX_UNDETECTED_DELAY = 3

    def __init__(self, vision_state: DictProxy, ui_send_queue: Queue):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ui_send_queue = ui_send_queue

        self.vision_state = vision_state

        self._blue_team = [RobotFilter(robot_id) for robot_id in range(config['ENGINE']['max_robot_id'])]
        self._yellow_team = [RobotFilter(robot_id) for robot_id in range(config['ENGINE']['max_robot_id'])]
        self._balls = [BallFilter(ball_id) for ball_id in range(config['ENGINE']['max_ball_on_field'])]

        self._camera_frame_number = [-1 for _ in range(config['ENGINE']['number_of_camera'])]
        self.current_timestamp = -1

    def update(self) -> Dict[str, List[Dict[str, Any]]]:

        for frame in self.camera_frames:
            if config['GAME']['on_negative_side']: frame = Tracker._change_frame_side(frame)
            self._camera_frame_number[frame['camera_id']] = frame['frame_number']
            self._update(frame, frame['timestamp'])
            self.current_timestamp = max(self.current_timestamp, frame['timestamp'])

        self.remove_undetected()

        return self.game_state

    def _update(self, detection_frame: Dict[str, List[Dict[str, Any]]], timestamp: float):

        self._log_new_robots_on_field(detection_frame)

        for robot_obs in detection_frame.get('robots_blue', ()):
            obs = np.array([robot_obs['x'], robot_obs['y'], robot_obs['orientation']])
            self._blue_team[robot_obs['robot_id']].update(obs, timestamp)

        for robot_obs in detection_frame.get('robots_yellow', ()):
            obs = np.array([robot_obs['x'], robot_obs['y'], robot_obs['orientation']])
            self._yellow_team[robot_obs['robot_id']].update(obs, timestamp)

        for ball_obs in detection_frame.get('balls', ()):
            obs = np.array([ball_obs['x'], ball_obs['y']])
            self._balls[0].update(obs, timestamp)  # TODO: add ball ID assignement

    def predict(self, robot_state: RobotState):

        velocity_commands = [Pose() for _ in range(len(self._our_team))]
        for packet in robot_state.packet:
            velocity_commands[packet.robot_id] = packet.command

        for robot, velocity_command in zip(self._our_team, velocity_commands):
            robot.predict(self._put_in_world_referential(robot, velocity_command).to_array())

        for robot in self._their_team:
            robot.predict()
            
        for ball in self._balls:
            ball.predict()

    def remove_undetected(self):

        for team_color, robots in self.active_robots.items():
            for robot in robots:
                if self.current_timestamp - robot.last_update_time > config['ENGINE']['max_undetected_robot_time']:
                    robot.reset()
                    self.logger.debug('Robot %d of %s team was undetected for more than %d seconds.',
                                      robot.id,
                                      team_color,
                                      config['ENGINE']['max_undetected_robot_time'])

        for ball in self.active_balls:
            if self.current_timestamp - ball.last_update_time > config['ENGINE']['max_undetected_ball_time']:
                ball.reset()
                self.logger.debug('Ball %d was undetected for more than %d seconds.',
                                  ball.id,
                                  config['ENGINE']['max_undetected_ball_time'])

    @staticmethod
    def _put_in_world_referential(robot, cmd):
        if config['GAME']['on_negative_side']:
            cmd.position = rotate(cmd.position, -np.pi - robot.orientation)
            cmd.x *= -1
            cmd.orientation *= -1
        else:
            cmd.position = rotate(cmd.position, robot.orientation)
        return cmd


    @staticmethod
    def _change_frame_side(detection_frame: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:

        for robot_obs in detection_frame.get('robots_blue', []) + detection_frame.get('robots_yellow', []):
            robot_obs['x'] *= -1
            robot_obs['orientation'] *= -1

        for ball_obs in detection_frame.get('balls', ()):
            ball_obs['x'] *= -1

        return detection_frame

    def _log_new_robots_on_field(self, detection_frame: Dict[str, List[Dict[str, Any]]]):
        new_robots = {'blue': set(), 'yellow': set()}

        for robot_obs in detection_frame.get('robots_blue', ()):
            if not self._blue_team[robot_obs['robot_id']].is_active: new_robots['blue'].add(robot_obs['robot_id'])
        if new_robots['blue']:
            self.logger.debug('New blue robot(s) detected: %r', new_robots['blue'])

        for robot_obs in detection_frame.get('robots_yellow', ()):
            if not self._yellow_team[robot_obs['robot_id']].is_active: new_robots['yellow'].add(robot_obs['robot_id'])
        if new_robots['yellow']:
            self.logger.debug('New yellow robot(s) detected: %r', new_robots['yellow'])

    @property
    def camera_frames(self) -> List[Dict[str, Any]]:
        if config['GAME']['on_negative_side']:
            camera_frames = [Tracker._change_frame_side(frame) for frame in self.vision_state if self._is_valid_frame(frame)]
        else:
            camera_frames = [frame for frame in self.vision_state if self._is_valid_frame(frame)]
        return sorted(camera_frames, key=lambda frame: frame['t_capture'])

    def _is_valid_frame(self, frame):
        return frame and frame['frame_number'] > self._camera_frame_number[frame['camera_id']]

    @property
    def _our_team(self):
        if config['GAME']['our_color'] == 'yellow':
            our_team = self._yellow_team
        else:
            our_team = self._blue_team
        return our_team

    @property
    def _their_team(self):
        if config['GAME']['our_color'] == 'yellow':
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
    def game_state(self) -> Dict[str, Union[float, List[Dict[str, Any]]]]:
        game_fields = dict()
        game_fields['timestamp'] = self.current_timestamp
        game_fields['blue'] = self.blue_team
        game_fields['yellow'] = self.yellow_team
        game_fields['balls'] = self.balls
        return game_fields

    @property
    def balls(self) -> List[Dict[str, Any]]:
        return Tracker._format_entities(self.active_balls)

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
            elif type(entity) is BallFilter:
                fields['position'] = Pose.from_values(*entity.position)
            else:
                raise TypeError('Invalid type provided: {}'.format(type(entity)))
            fields['velocity'] = Pose.from_values(*entity.velocity)
            fields['id'] = entity.id
            formatted_list.append(fields)
        return formatted_list

