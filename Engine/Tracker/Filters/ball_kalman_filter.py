
import numpy as np

from Engine.Tracker.Filters import KalmanFilter


class BallFilter(KalmanFilter):

    @property
    def position(self):
        if self.is_active:
            return self.x[0::2]

    @property
    def velocity(self):
        if self.is_active:
            return self.x[1::2]

    def transition_model(self, dt):
        return np.array([[1, dt, 0,  0],   # Position x
                         [0,  1, 0,  0],   # Speed x
                         [0,  0, 1, dt],   # Position y
                         [0,  0, 0,  1]])  # Speed y

    def process_covariance(self, dt):
        sigma_acc_x = 10
        sigma_acc_y = sigma_acc_x
        process_covariance = \
            np.array([
                np.array([0.25 * dt ** 4, 0.50 * dt ** 3, 0, 0]) * sigma_acc_x ** 2,
                np.array([0.50 * dt ** 3, 1.00 * dt ** 2, 0, 0]) * sigma_acc_x ** 2,
                np.array([0, 0, 0.25 * dt ** 4, 0.50 * dt ** 3]) * sigma_acc_y ** 2,
                np.array([0, 0, 0.50 * dt ** 3, 1.00 * dt ** 2]) * sigma_acc_y ** 2
            ])

        return process_covariance

    def observation_covariance(self):
        return np.diag([1, 1])

    def initial_state_covariance(self):
        return np.diag([10 ** 3, 0, 10 ** 3, 0])

