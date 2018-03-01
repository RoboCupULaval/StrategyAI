from math import fabs

import numpy as np

from RULEngine.filters.kalman_filter import KalmanFilter


class RobotFilter(KalmanFilter):

    @property
    def pose(self):
        if self.is_active:
            return self.x[0::2]

    @property
    def velocity(self):
        if self.is_active:
            return self.x[1::2]

    def get_orientation(self):
        if self.is_active:
            return self.x[4]

    def transition_model(self):
        dt = self._dt
        return np.array([[1, dt, 0, 0,  0, 0],   # Position x
                         [0, 1,  0, 0,  0, 0],   # Speed x
                         [0, 0,  1, dt, 0, 0],   # Position y
                         [0, 0,  0, 1,  0, 0],   # Speed y
                         [0, 0,  0, 0,  1, dt],  # Position Theta
                         [0, 0,  0, 0,  0, 1]])  # Speed Theta

    def observation_model(self):
        return np.array([[1, 0, 0, 0, 0, 0],   # Position x
                         [0, 0, 1, 0, 0, 0],   # Position y
                         [0, 0, 0, 0, 1, 0]])  # Orientation

    def control_input_model(self):
        dt = self._dt
        return np.array([[0,  0,  0],  # Position x
                         [dt, 0,  0],  # Speed x
                         [0,  0,  0],  # Position y
                         [0, dt,  0],  # Speed y
                         [0,  0,  0],  # Position Theta
                         [0,  0, dt]])  # Speed Theta

    def process_covariance(self):
        dt = self._dt
        sigma_acc_x = 100
        sigma_acc_y = 100
        sigma_acc_o = 5 * np.pi/180
        G = np.array([
                np.array([0.25 * dt ** 4, 0.50 * dt ** 3,              0,              0,              0,              0]) * sigma_acc_x ** 2,
                np.array([0.50 * dt ** 3, 1.00 * dt ** 2,              0,              0,              0,              0]) * sigma_acc_x ** 2,
                np.array([             0,              0, 0.25 * dt ** 4, 0.50 * dt ** 3,              0,              0]) * sigma_acc_y ** 2,
                np.array([             0,              0, 0.50 * dt ** 3, 1.00 * dt ** 2,              0,              0]) * sigma_acc_y ** 2,
                np.array([             0,              0,              0,              0, 0.25 * dt ** 4, 0.50 * dt ** 3]) * sigma_acc_o ** 2,
                np.array([             0,              0,              0,              0, 0.50 * dt ** 3, 1.00 * dt ** 2]) * sigma_acc_o ** 2])

        return G

    def observation_covariance(self):
        # SB: This need to be tweak to the new fps
        #if fabs(self.x[0]) < 30 or fabs(self.x[2]) < 30:
        #    R = np.diag([50, 50, 0.01])
        #else:

        R = np.diag([1, 1, .00001])

        return R

    def initial_state_covariance(self):
        return np.diag([10000, 1, 10000, 1, 90 * np.pi/180, 1 * np.pi/180])

    def predict(self, input_command=None):
        orientation = self.get_orientation()
        if input_command is not None and orientation is not None:
            input_command = RobotFilter.rotate(input_command, orientation)
        self._predict(input_command)
        self.x[4] = self.wrap_to_pi(self.x[4])

    @staticmethod
    def rotate(vec, angle):
        rotation = np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
        return rotation @ vec

    @staticmethod
    def wrap_to_pi(angle):
        return (angle + np.pi) % (2 * np.pi) - np.pi
