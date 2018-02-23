import logging

import numpy as np

from RULEngine.filters.ball_kalman_filter import BallFilter


# TODO doesnt really work. Broken since merge

class MultiBallService(list):

    BALL_SEPARATION_THRESHOLD = 20000
    MAX_UNDETECTED_DELAY = 20

    def __init__(self, max_ball: int=1):
        self.logger = logging.getLogger('MultiBallService')
        self.max_ball = max_ball
        self._current_timestamp = None

        self.logger.debug(' initiated with {} balls'.format(max_ball))
        super().__init__(BallFilter() for _ in range(max_ball))
        
    def update(self, obs: np.array, timestamp: float) -> None:
        self._current_timestamp = timestamp
        if self.filter_ball_observation(obs) or not self[0].is_active:
            self[0].update(obs, self._current_timestamp)

    def predict(self) -> None:
        for ball in self:
            ball.predict()

    def remove_undetected(self) -> None:
        undetected_balls = [ball for ball in self
                            if ball.is_active and
                            self._current_timestamp - ball.last_update_time > MultiBallService.MAX_UNDETECTED_DELAY]

        for ball in undetected_balls:
            ball.reset()
            self.logger.info('Deactivating ball')

    def filter_ball_observation(self, obs: np.ndarray) -> bool:
        position_differences = self.compute_distances_ball_to_observation(obs)

        is_valid = False
        if position_differences is not None and np.min(position_differences) < self.BALL_SEPARATION_THRESHOLD:
            is_valid = True

        return is_valid

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
