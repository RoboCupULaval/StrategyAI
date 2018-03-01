from math import fabs

import numpy as np

from RULEngine.filters.kalman_filter import KalmanFilter


class BallFilter(KalmanFilter):

    @property
    def pose(self):
        if self.is_active:
            return self.x[0::2]

    @property
    def velocity(self):
        if self.is_active:
            return self.x[1::2]

    def transition_model(self):
        dt = self._dt
        return np.array([[1, dt, 0,  0],   # Position x
                         [0,  1, 0,  0],   # Speed x
                         [0,  0, 1, dt],   # Position y
                         [0,  0, 0,  1]])  # Speed y

    def observation_model(self):
        return np.array([[1, 0, 0, 0],   # Position x
                         [0, 0, 1, 0]])  # Position y

    def process_covariance(self):
        dt = self._dt
        sigma_acc_x = 100
        sigma_acc_y = 100
        G = np.array([
            np.array([0.25 * dt ** 4, 0.50 * dt ** 3, 0, 0]) * sigma_acc_x ** 2,
            np.array([0.50 * dt ** 3, 1.00 * dt ** 2, 0, 0]) * sigma_acc_x ** 2,
            np.array([0, 0, 0.25 * dt ** 4, 0.50 * dt ** 3]) * sigma_acc_y ** 2,
            np.array([0, 0, 0.50 * dt ** 3, 1.00 * dt ** 2]) * sigma_acc_y ** 2
        ])

        return G

    def observation_covariance(self):
        # SB: This need to be tweak to the new fps
        # if fabs(self.x[0]) < 30 or fabs(self.x[2]) < 30:
        #    R = np.diag([50, 50])
        #else:
        #    R = np.diag([10, 10])
        return np.diag([10, 10])

    def initial_state_covariance(self):
        return 10000 * np.eye(self.state_number)

