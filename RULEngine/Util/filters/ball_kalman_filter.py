import numpy as np
from RULEngine.Util.filters.kalman_filter import KalmanFilter


class BallFilter(KalmanFilter):

    @property
    def pose(self):
        if self.is_active:
            return np.array([self.x[0], self.x[2]]).flatten()

    @property
    def velocity(self):
        if self.is_active:
            return np.array([self.x[1], self.x[3]]).flatten()

    def transition_model(self):
        return np.array([[1, self.dt, 0,       0],   # Position x
                         [0,       1, 0,       0],   # Speed x
                         [0,       0, 1, self.dt],   # Position y
                         [0,       0, 0,       1]])  # Speed y

    def observation_model(self):
        return np.array([[1, 0, 0, 0],   # Position x
                         [0, 0, 1, 0]])  # Position y

    def initial_state_covariance(self):
        return 10 ** 6 * np.eye(self.state_number)

    def process_covariance(self):
        return np.diag([1000, 100, 1000, 100])

    def observation_covariance(self):
        return 20 * np.eye(self.observable_state)
