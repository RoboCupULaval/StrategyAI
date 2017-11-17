import logging
from typing import Dict

import numpy as np

from RULEngine.Util.filters.ball_kalman_filter import BallFilter


class MultiBallService:

    MAX_BALL_ON_FIELD = 1
    BALL_CONFIDENCE_THRESHOLD = 1
    BALL_SEPARATION_THRESHOLD = 1000
    STATE_PREDICTION_TIME = 0.1

    def __init__(self, n_ball=1):
        self.logger = logging.getLogger('MultiBallService')

        self.n_ball = n_ball
        self.balls = []
        self.considered_balls = []

        self.logger.info(' initiated with {} balls'.format(n_ball))

    def update_with_observation(self, obs: Dict, t_capture):
        obs_state = np.array([obs["x"], obs["y"]])
        closest_ball = self.find_closest_ball_to_observation(obs_state)

        if closest_ball is None:  # No ball or every balls are too far.
            self.considered_balls.append(BallFilter())
            self.considered_balls[-1].update(obs_state, t_capture)
            self.logger.info('New ball detected: {}.'.format(id(self.considered_balls[-1])))
        else:
            closest_ball.update(obs_state, t_capture)

        self.remove_undetected()
        self.select_best_balls()
        self.predict_next_states()

    def predict_next_states(self):
        for ball in self.considered_balls:
            ball.predict(self.STATE_PREDICTION_TIME)

    def remove_undetected(self):
        for ball in self.considered_balls:
            if ball.confidence < self.BALL_CONFIDENCE_THRESHOLD:
                self.considered_balls.remove(ball)
                self.logger.info('Removing ball {}.'.format(id(ball)))

    def select_best_balls(self):
        if len(self.considered_balls) > 0:
            self.considered_balls.sort(key=lambda x: x.confidence, reverse=True)
            max_ball = min(self.MAX_BALL_ON_FIELD, len(self.considered_balls))
            self.balls = self.considered_balls[0:max_ball]
        else:
            self.balls.clear()

    def find_closest_ball_to_observation(self, obs: np.ndarray):

        position_differences = self.compute_distances_ball_to_observation(obs)

        closest_ball = None
        if position_differences is not None:
            min_diff = float(min(position_differences))
            if min_diff < self.BALL_SEPARATION_THRESHOLD:
                closest_ball_idx = position_differences.index(min_diff)
                closest_ball = self.considered_balls[closest_ball_idx]

        return closest_ball

    def compute_distances_ball_to_observation(self, obs_state: np.ndarray):
        position_differences = []
        for ball in self.considered_balls:
            if ball.last_prediction is not None:
                position_differences.append(float(np.linalg.norm(ball.pose() - obs_state)))
            elif ball.last_observation is not None:  # If we never predict the state, we still need to compare it
                position_differences.append(float(np.linalg.norm(ball.last_observation - obs_state)))
            else:  # This should never happens if ball are updated when create
                position_differences.append(float('inf'))

        if not position_differences:
            position_differences = None
        elif len(position_differences) == 1 and position_differences[0] == float('inf'):
            position_differences = None

        return position_differences

    def __getitem__(self, item):
        return self.balls[item]

    def __iter__(self):
        for ball in self.balls:
            yield ball
