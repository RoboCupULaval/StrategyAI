
import logging
from multiprocessing.managers import DictProxy
from typing import Dict, List
import numpy as np

from RULEngine.filters.multiballservice import MultiBallService
from RULEngine.filters.robot_kalman_filter import RobotFilter

from Util.geometry import wrap_to_pi
from Util import Pose, Position

from config.config_service import ConfigService


class Tracker:

    MAX_ROBOT_PER_TEAM = 12
    MAX_BALL_ON_FIELD = 1
    MAX_UNDETECTED_DELAY = 1

    def __init__(self, vision_state: DictProxy):

        logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger('Tracker')

        self.cfg = ConfigService()
        self.team_color = self.cfg.config_dict['GAME']['our_color']
        self.our_side = self.cfg.config_dict['GAME']['our_side']

        self.vision_state = vision_state

        self._blue_team = [RobotFilter() for _ in range(Tracker.MAX_ROBOT_PER_TEAM)]
        self._yellow_team = [RobotFilter() for _ in range(Tracker.MAX_ROBOT_PER_TEAM)]
        self._balls = MultiBallService(Tracker.MAX_BALL_ON_FIELD)

        self._camera_frame_number = [-1 for _ in range(4)]  # TODO: make me a constant somewhere
        self._current_timestamp = 0

    def update(self) -> Dict:

        camera_frames = [frame for frame in self.vision_state
                         if frame and frame['frame_number'] > self._camera_frame_number[frame['camera_id']]]

        if any(camera_frames):

            for frame in camera_frames:

                # if self.our_side == 'negative':
                #     vision_frame = Tracker.change_reference(frame)

                self._camera_frame_number[frame['camera_id']] = frame['frame_number']
                self._update(frame, frame['t_capture'])

            self._current_timestamp = max(frame['t_capture'] for frame in camera_frames)
            self.remove_undetected()

        return self.game_state

    def _update(self, detection_frame: Dict, timestamp):

        for robot_obs in detection_frame.get('robots_blue', ()):
            obs = np.array([robot_obs['x'], robot_obs['y'], robot_obs['orientation']])
            self._blue_team[robot_obs['robot_id']].update(obs, timestamp)

        for robot_obs in detection_frame.get('robots_yellow', ()):
            obs = np.array([robot_obs['x'], robot_obs['y'], robot_obs['orientation']])
            self._yellow_team[robot_obs['robot_id']].update(obs, timestamp)

        for ball_obs in detection_frame.get('balls', ()):
            obs = np.array([ball_obs['x'], ball_obs['y']])
            self._balls.update(obs, timestamp)

    def predict(self, robot_packet):

        input_commands = [None for _ in range(12)]
        for packet in robot_packet:
            input_commands[packet.robot_id] = packet.command.to_array()

        for robot, input_cmd in zip(self._our_team, input_commands):
            robot.predict(input_cmd)
        for robot in self._their_team:
            robot.predict()

        self._balls.predict()

    def remove_undetected(self):
        active_robots = iter(robot for robot in self._yellow_team + self._blue_team if robot.is_active)
        for robot in active_robots:
            if self._current_timestamp - robot.last_update_time > Tracker.MAX_UNDETECTED_DELAY:
                robot.reset()

        self._balls.remove_undetected()

    @staticmethod
    def change_reference(detection_frame):

        teams = detection_frame.get('robots_blue', ())\
                + detection_frame.get('robots_yellow', ())

        for robot_obs in teams:
            robot_obs.position *= -1
            robot_obs.orientation = wrap_to_pi(robot_obs.orientation + np.pi)

        for ball_obs in detection_frame.get('balls', ()):
            ball_obs.position *= -1

        return detection_frame

    @property
    def _our_team(self):
        if self.team_color == 'yellow':
            our_team = self._yellow_team
        else:
            our_team = self._blue_team
        return our_team

    @property
    def _their_team(self):
        if self.team_color == 'yellow':
            their_team = self._blue_team
        else:
            their_team = self._yellow_team
        return their_team

    @property
    def game_state(self) -> Dict:
        game_fields = dict()
        game_fields['timestamp'] = self._current_timestamp
        game_fields['blue'] = self.blue_team
        game_fields['yellow'] = self.yellow_team
        game_fields['balls'] = self.balls
        return game_fields

    @property
    def balls(self) -> List[Position]:
        active_balls = [b for b in self._balls if b.is_active]
        return Tracker.format_ball(active_balls)

    @property
    def blue_team(self) -> List[Pose]:
        active_players = [p for p in self._balls if p.is_active]
        return Tracker.format_team(active_players)

    @property
    def yellow_team(self) -> List[Pose]:
        active_players = [p for p in self._balls if p.is_active]
        return Tracker.format_team(active_players)

    @staticmethod
    def format_team(entities: List) -> List[Pose]:
        formatted_list = []
        for entity_id, entity in enumerate(entities):
            fields = dict()
            fields['pose'] = Pose.from_values(*entity.pose)
            fields['velocity'] = Pose.from_values(*entity.velocity)
            fields['id'] = entity_id
            formatted_list.append(fields)
        return formatted_list

    @staticmethod
    def format_ball(entities: List) -> List[Position]:
        formatted_list = []
        for entity_id, entity in enumerate(entities):
            fields = dict()
            fields['pose'] = Position(*entity.pose)
            fields['velocity'] = Position(*entity.velocity)
            fields['id'] = entity_id
            formatted_list.append(fields)
        return formatted_list
