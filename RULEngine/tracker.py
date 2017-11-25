import logging
import time
import numpy as np
from multiprocessing import Queue
from typing import Dict, List

from RULEngine.Util.filters.robot_kalman_filter import RobotFilter
from RULEngine.Util.multiballservice import MultiBallService


class Tracker:

    MAX_ROBOT_PER_TEAM = 12
    MAX_BALL_ON_FIELD = 1
    SEND_DELAY = 0.02
    BALL_CONFIDENCE_THRESHOLD = 1
    BALL_SEPARATION_THRESHOLD = 1000
    STATE_PREDICTION_TIME = 0.1
    MAX_UNDETECTED_DELAY = 2

    def __init__(self, vision_queue: Queue):
        self.logger = logging.getLogger('Tracker')

        self.last_sending_time = time.time()

        self.vision_queue = vision_queue

        self._blue_team = [RobotFilter() for _ in range(Tracker.MAX_ROBOT_PER_TEAM)]
        self._yellow_team = [RobotFilter() for _ in range(Tracker.MAX_ROBOT_PER_TEAM)]
        self._balls = MultiBallService(Tracker.MAX_BALL_ON_FIELD)

        self._current_timestamp = None

    def tracker_main_loop(self):
            detection_frame = self.vision_queue.get()
            self._current_timestamp = detection_frame["t_capture"]

            for robot_obs in detection_frame["robots_blue"]:
                obs_state = np.array([robot_obs["x"], robot_obs["y"], robot_obs["orientation"]])
                self._blue_team[robot_obs["robot_id"]].update(obs_state, self._current_timestamp)
                self._blue_team[robot_obs["robot_id"]].predict(Tracker.STATE_PREDICTION_TIME)

            for robot_obs in detection_frame.robots_yellow:
                obs_state = np.array([robot_obs["x"], robot_obs["y"], robot_obs["orientation"]])
                self._yellow_team[robot_obs["robot_id"]].update(obs_state, detection_frame["t_capture"])
                self._yellow_team[robot_obs["robot_id"]].predict(Tracker.STATE_PREDICTION_TIME)

            for ball_obs in detection_frame.balls:
                self._balls.update_with_observation(ball_obs, detection_frame.t_capture)

            self.remove_undetected_robot()

    def remove_undetected_robot(self):
        for robot in self._yellow_team + self._blue_team:
            if robot.last_t_capture + Tracker.MAX_UNDETECTED_DELAY < self._current_timestamp:
                robot.is_active = False

    @property
    def track_frame(self) -> Dict:
        track_fields = dict()
        track_fields['timestamp'] = self._current_timestamp
        track_fields['robots_blue'] = self.blue_team
        track_fields['robots_yellow'] = self.yellow_team
        track_fields['balls'] = self.balls

        return track_fields

    @property
    def balls(self) -> List:
        return Tracker.format_list(self._balls)

    @property
    def blue_team(self) -> List:
        return Tracker.format_list(self._blue_team)

    @property
    def yellow_team(self) -> List:
        return Tracker.format_list(self._yellow_team)

    @staticmethod
    def format_list(entities: List):
        format_list = []
        for entity_id, entity in enumerate(entities):
            if entity.is_active:
                fields = dict()
                fields['pose'] = tuple(entity.pose)
                fields['velocity'] = tuple(entity.velocity)
                fields['id'] = entity_id
                format_list.append(fields)
        return format_list

    def stop(self):
        self.thread_terminate.set()
        self._thread.join()
        self.thread_terminate.clear()
