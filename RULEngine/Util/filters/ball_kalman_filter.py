import numpy as np
from RULEngine.Util.filters.kalman_filter import KalmanFilter
from math import fabs

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
        return np.diag([.5, 50, .5, 50])

    def observation_covariance(self):
        if fabs(self.x[0]) < 30 or fabs(self.x[2]) < 30:
            R = np.diag([50, 50])
        else:
            R = np.diag([10, 10])
        return R

