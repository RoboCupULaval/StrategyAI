
import logging
from multiprocessing.managers import DictProxy
from typing import Dict, List, Union, Any, Iterable
import numpy as np
from multiprocessing import Queue

import time

from Debug.debug_command_factory import DebugCommandFactory
from Engine.Communication.robot_state import RobotState
from Engine.filters.ball_kalman_filter import BallFilter
from Engine.filters.robot_kalman_filter import RobotFilter

from Util.geometry import wrap_to_pi, rotate
from Util import Pose, Position
from Util.team_color_service import TeamColorService
from config.config import Config


class Tracker:

    MAX_ROBOT_ID = 12
    MAX_BALL_ON_FIELD = 1
    MAX_UNDETECTED_DELAY = 3
    NUMBER_OF_CAMERA = 4

    def __init__(self, vision_state: DictProxy, ui_send_queue: Queue):

        logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger('Tracker')
        self.ui_send_queue = ui_send_queue
        self.on_negative_side = Config()["GAME"]["on_negative_side"]

        self.vision_state = vision_state

        self._blue_team = [RobotFilter(robot_id) for robot_id in range(Tracker.MAX_ROBOT_ID)]
        self._yellow_team = [RobotFilter(robot_id) for robot_id in range(Tracker.MAX_ROBOT_ID)]
        self._ball = BallFilter()

        self._camera_frame_number = [-1 for _ in range(Tracker.NUMBER_OF_CAMERA)]
        self._current_timestamp = 0

    def update(self) -> Dict[str, List[Dict[str, Any]]]:

        camera_frames = [frame for frame in self.vision_state
                         if frame and frame['frame_number'] > self._camera_frame_number[frame['camera_id']]]

        if any(camera_frames):

            for frame in sorted(camera_frames, key=lambda frame: frame['t_capture']):
                if self.on_negative_side:
                    frame = Tracker.change_reference(frame)

                self._camera_frame_number[frame['camera_id']] = frame['frame_number']
                self._update(frame, time.time())

            self._current_timestamp = max(frame['t_capture'] for frame in camera_frames)
            self.remove_undetected()

        return self.game_state

    def _update(self, detection_frame: Dict[str, List[Dict[str, Any]]], timestamp: int):

        new_robots = {'blue': set(), 'yellow': set()}

        for robot_obs in detection_frame.get('robots_blue', ()):
            if not self._blue_team[robot_obs['robot_id']].is_active:
                new_robots['blue'].add(robot_obs['robot_id'])
            obs = np.array([robot_obs['x'], robot_obs['y'], robot_obs['orientation']])
            self._blue_team[robot_obs['robot_id']].update(obs, timestamp)

        for robot_obs in detection_frame.get('robots_yellow', ()):
            if not self._yellow_team[robot_obs['robot_id']].is_active:
                new_robots['yellow'].add(robot_obs['robot_id'])
            obs = np.array([robot_obs['x'], robot_obs['y'], robot_obs['orientation']])
            self._yellow_team[robot_obs['robot_id']].update(obs, timestamp)

        if self._yellow_team[5]._dt < 0.1:
            self.ui_send_queue.put_nowait(DebugCommandFactory.plot_point("s", "robot 5 update time",
                                                                         [time.time()],
                                                                         [self._yellow_team[5]._dt]))

        for ball_obs in detection_frame.get('balls', ()):
            obs = np.array([ball_obs['x'], ball_obs['y']])
            self._ball.update(obs, timestamp)

        if new_robots['blue']:
            self.logger.debug('New blue robot(s) detected: %r', new_robots['blue'])
        if new_robots['yellow']:
            self.logger.debug('New yellow robot(s) detected: %r', new_robots['yellow'])

    def predict(self, robot_state: RobotState):

        velocity_commands = [None for _ in range(12)]
        for packet in robot_state.packet:
            velocity_commands[packet.robot_id] = packet.command

        for robot, velocity_command in zip(self._our_team, velocity_commands):
            if velocity_command is not None:
                velocity_command = self._put_in_world_referential(robot, velocity_command).to_array()
            robot.predict(velocity_command)
        for robot in self._their_team:
            robot.predict()

        # if self._yellow_team[5]._dt < 0.1:
        #     self.ui_send_queue.put_nowait(DebugCommandFactory.plot_point("s", "robot 5 predict time",
        #                                                                  [time.time()],
        #                                                                  [self._yellow_team[5]._dt]))

        self._ball.predict()

    def remove_undetected(self):
        active_robots = (robot for robot in self._yellow_team + self._blue_team if robot.is_active)
        for robot in active_robots:
            if self._current_timestamp - robot.last_capture_time > Tracker.MAX_UNDETECTED_DELAY:
                robot.reset()
                self.logger.debug('Robot %d was undetected for more than %d seconds.',
                                 robot.id,
                                 Tracker.MAX_UNDETECTED_DELAY)

        if self._ball.is_active:
            if self._current_timestamp - self._ball.last_capture_time > Tracker.MAX_UNDETECTED_DELAY:
                self._ball.reset()
                self.logger.debug('The ball was undetected for more than %d seconds.',
                                 Tracker.MAX_UNDETECTED_DELAY)

    @staticmethod
    def _put_in_world_referential(robot, cmd):
        if Config()["GAME"]["on_negative_side"]:
            cmd.position = rotate(cmd.position, -np.pi - robot.orientation)
            cmd.x *= -1
            cmd.orientation *= -1
        else:
            cmd.position = rotate(cmd.position, robot.orientation)
        return cmd


    @staticmethod
    def change_reference(detection_frame: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:

        teams = detection_frame.get('robots_blue', []) \
              + detection_frame.get('robots_yellow', [])

        for robot_obs in teams:
            robot_obs['x'] *= -1
            robot_obs['orientation'] = wrap_to_pi(np.pi - robot_obs['orientation'])

        for ball_obs in detection_frame.get('balls', ()):
            ball_obs['x'] *= -1

        return detection_frame

    @property
    def _our_team(self):
        if TeamColorService().is_our_team_yellow:
            our_team = self._yellow_team
        else:
            our_team = self._blue_team
        return our_team

    @property
    def _their_team(self):
        if TeamColorService().is_our_team_yellow:
            their_team = self._blue_team
        else:
            their_team = self._yellow_team
        return their_team

    @property
    def game_state(self) -> Dict[str, Union[float, List[Dict[str, Any]]]]:
        game_fields = dict()
        game_fields['timestamp'] = self._current_timestamp
        game_fields['blue'] = self.blue_team
        game_fields['yellow'] = self.yellow_team
        game_fields['balls'] = self.balls
        return game_fields

    @property
    def balls(self) -> List[Dict[str, Any]]:
        return Tracker.format_balls([self._ball]) if self._ball.is_active else []

    @property
    def blue_team(self) -> List[Dict[str, Any]]:
        active_players = (p for p in self._blue_team if p.is_active)
        return Tracker.format_team(active_players)

    @property
    def yellow_team(self) -> List[Dict[str, Any]]:
        active_players = (p for p in self._yellow_team if p.is_active)
        return Tracker.format_team(active_players)

    @staticmethod
    def format_team(team: Iterable[RobotFilter]) -> List[Dict[str, Any]]:
        formatted_list = []
        for robot in team:
            fields = dict()
            fields['pose'] = Pose.from_values(*robot.pose)
            fields['velocity'] = Pose.from_values(*robot.velocity)
            fields['id'] = robot.id
            formatted_list.append(fields)
        return formatted_list

    @staticmethod
    def format_balls(entities: Iterable[BallFilter]) -> List[Dict[str, Any]]:
        formatted_list = []
        for entity_id, entity in enumerate(entities):
            fields = dict()
            fields['position'] = Position(*entity.pose)
            fields['velocity'] = Position(*entity.velocity)
            fields['id'] = entity_id
            formatted_list.append(fields)
        return formatted_list
