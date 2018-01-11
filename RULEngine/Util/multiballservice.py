import logging
from typing import Dict

import numpy as np

from RULEngine.Util.filters.ball_kalman_filter import BallFilter


class MultiBallService(list):

    MAX_BALL_ON_FIELD = 1
    BALL_CONFIDENCE_THRESHOLD = 1
    BALL_SEPARATION_THRESHOLD = 1000
    STATE_PREDICTION_TIME = 0.1
    MAX_UNDETECTED_DELAY = 1

    def __init__(self, max_ball: int=1):
        self.logger = logging.getLogger('MultiBallService')
        self.max_ball = max_ball
        self._current_timestamp = None

        self.logger.info(' initiated with {} balls'.format(max_ball))
        super().__init__(BallFilter() for _ in range(max_ball))
        
    def update(self, obs: np.array, timestamp: float) -> None:
        self._current_timestamp = timestamp
        closest_ball = self.find_closest_ball_to_observation(obs)

        if closest_ball is not None:
            closest_ball.update(obs, self._current_timestamp)
        else:
            self.logger.info('New ball detected')
            inactive_balls = [ball for ball in self if not ball.is_active]
            if inactive_balls:
                inactive_balls[0].update(obs, self._current_timestamp)

    def predict(self) -> None:
        map(lambda ball: ball.predict(), self)

    def remove_undetected(self) -> None:
        undetected_balls = [ball for ball in self
                            if ball.is_active and
                            self._current_timestamp - ball.last_t_capture > MultiBallService.MAX_UNDETECTED_DELAY]

        map(lambda ball: ball.reset(), undetected_balls)

        if undetected_balls:
            self.logger.info('Deactivating {} ball(s)'.format(len(undetected_balls)))

    def find_closest_ball_to_observation(self, obs: np.ndarray) -> BallFilter:
        position_differences = self.compute_distances_ball_to_observation(obs)

        closest_ball = None
        if position_differences is not None and np.min(position_differences) < self.BALL_SEPARATION_THRESHOLD:
            idx = np.argmin(position_differences)
            closest_ball = self[idx]

        return closest_ball

    def compute_distances_ball_to_observation(self, obs: np.ndarray) -> np.array:

        balls_poses = np.array([ball.pose for ball in self if ball.is_active])
        if balls_poses.size != 0:
            position_differences = np.linalg.norm(balls_poses - obs)
        else:
            position_differences = None

        return position_differences if position_differences else None
