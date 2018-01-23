
import logging
from multiprocessing import Queue
from queue import Empty
from typing import Dict, List

import numpy as np

from RULEngine.filters.multiballservice import MultiBallService
from RULEngine.filters.robot_kalman_filter import RobotFilter

from config.config_service import ConfigService


class Tracker:

    MAX_ROBOT_PER_TEAM = 12
    MAX_BALL_ON_FIELD = 1
    MAX_UNDETECTED_DELAY = 1

    def __init__(self, vision_queue: Queue):

        logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger('Tracker')

        self.cfg = ConfigService()
        self.team_color = self.cfg.config_dict['GAME']['our_color']

        self.vision_queue = vision_queue

        self._blue_team = [RobotFilter() for _ in range(Tracker.MAX_ROBOT_PER_TEAM)]
        self._yellow_team = [RobotFilter() for _ in range(Tracker.MAX_ROBOT_PER_TEAM)]
        self._balls = MultiBallService(Tracker.MAX_BALL_ON_FIELD)

        self._current_timestamp = None

    def update(self) -> Dict:

        try:
            vision_frame = self.vision_queue.get(block=False)
            detection_frame = vision_frame['detection']
            self._current_timestamp = detection_frame['t_capture']
            self._update(detection_frame)
        except Empty:
            pass
        except KeyError:
            pass

        self.remove_undetected()

        return self.track_frame

    def _update(self, detection_frame: Dict):

        for robot_obs in detection_frame.get('robots_blue', ()):
            obs = np.array([robot_obs['x'], robot_obs['y'], robot_obs['orientation']])
            self._blue_team[robot_obs['robot_id']].update(obs, self._current_timestamp)

        for robot_obs in detection_frame.get('robots_yellow', ()):
            obs = np.array([robot_obs['x'], robot_obs['y'], robot_obs['orientation']])
            self._yellow_team[robot_obs['robot_id']].update(obs, self._current_timestamp)

        for ball_obs in detection_frame.get('balls', ()):
            obs = np.array([ball_obs['x'], ball_obs['y']])
            self._balls.update(obs, self._current_timestamp)

    def predict(self, robot_packet):

        input_commands = [None for _ in range(12)]
        for packet in robot_packet:
            input_commands[packet.robot_id] = packet.command

        if self.team_color == 'yellow':
            for robot, input_cmd in zip(self._yellow_team, input_commands):
                input_cmd = [input_cmd[state] for state in ['x', 'y', 'orientation']] if input_cmd else None
                robot.predict(np.array(input_cmd))
            for robot in self._blue_team:
                robot.predict()
        else:
            for robot in self._yellow_team:
                robot.predict()
            for robot, input_cmd in zip(self._blue_team, input_commands):
                input_cmd = [input_cmd[state] for state in ['x', 'y', 'orientation']] if input_cmd else None
                robot.predict(np.array(input_cmd))

        self._balls.predict()

    def remove_undetected(self):
        active_robots = iter(robot for robot in self._yellow_team + self._blue_team if robot.is_active)
        for robot in active_robots:
            if self._current_timestamp - robot.last_update_time > Tracker.MAX_UNDETECTED_DELAY:
                robot.reset()

        self._balls.remove_undetected()

    @property
    def track_frame(self) -> Dict:
        track_fields = dict()
        track_fields['timestamp'] = self._current_timestamp
        track_fields['blue'] = self.blue_team
        track_fields['yellow'] = self.yellow_team
        track_fields['balls'] = self.balls
        return track_fields

    @property
    def balls(self) -> List[Dict]:
        return Tracker.format_list(self._balls, 'x y')

    @property
    def blue_team(self) -> List[Dict]:
        return Tracker.format_list(self._blue_team, 'x y orientation')

    @property
    def yellow_team(self) -> List[Dict]:
        return Tracker.format_list(self._yellow_team, 'x y orientation')

    @staticmethod
    def format_list(entities: List, states) -> List[Dict]:
        formatted_list = []
        for entity_id, entity in enumerate(entities):
            if entity.is_active:
                fields = dict()
                fields['pose'] = {state: value for state, value in zip(states.split(), entity.pose)}
                fields['velocity'] = {state: value for state, value in zip(states.split(), entity.velocity)}
                fields['id'] = entity_id
                formatted_list.append(fields)
        return formatted_list
