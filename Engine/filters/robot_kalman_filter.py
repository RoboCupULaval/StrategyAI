
import numpy as np

from Engine.filters.kalman_filter import KalmanFilter


class RobotFilter(KalmanFilter):

    @property
    def pose(self):
        if self.is_active:
            return self.x[0::2]

    @property
    def velocity(self):
        if self.is_active:
            return self.x[1::2]

    @property
    def orientation(self):
        if self.is_active:
            return self.x[4]

    def transition_model(self, dt):
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

    def control_input_model(self, dt):
        return np.array([[0,  0,  0],  # Position x
                         [dt, 0,  0],  # Speed x
                         [0,  0,  0],  # Position y
                         [0,  dt, 0],  # Speed y
                         [0,  0,  0],  # Position Theta
                         [0,  0, dt]])  # Speed Theta

    def process_covariance(self, dt):
        sigma_acc_x = 1000
        sigma_acc_y = 1000
        sigma_acc_o = 20000 * np.pi/180

        process_covariance = \
            np.array([
                np.array([0.25 * dt ** 4, 0.50 * dt ** 3,              0,              0,              0,              0]) * sigma_acc_x ** 2,
                np.array([0.50 * dt ** 3, 1.00 * dt ** 2,              0,              0,              0,              0]) * sigma_acc_x ** 2,
                np.array([             0,              0, 0.25 * dt ** 4, 0.50 * dt ** 3,              0,              0]) * sigma_acc_y ** 2,
                np.array([             0,              0, 0.50 * dt ** 3, 1.00 * dt ** 2,              0,              0]) * sigma_acc_y ** 2,
                np.array([             0,              0,              0,              0, 0.25 * dt ** 4, 0.50 * dt ** 3]) * sigma_acc_o ** 2,
                np.array([             0,              0,              0,              0, 0.50 * dt ** 3, 1.00 * dt ** 2]) * sigma_acc_o ** 2])

        return process_covariance

    def observation_covariance(self):
        return np.diag([100, 100, 0.1 * np.pi/180])

    def initial_state_covariance(self):
        return np.diag([10000, 10, 10000, 10, 90 * np.pi/180, 1 * np.pi/180])

    def update(self, observation, t_capture):
        error = observation - self.observation_model() @ self.x
        error[2] = RobotFilter.wrap_to_pi(error[2])
        self._update(error, t_capture)
        self.x[4] = RobotFilter.wrap_to_pi(self.x[4])

    def predict(self, dt, next_velocity=None):

        if next_velocity is not None:
            acceleration = (next_velocity - self.velocity)/dt
        else:
            acceleration = None

        self._predict(dt, acceleration)
        self.x[4] = RobotFilter.wrap_to_pi(self.x[4])

    @staticmethod
    def rotate(vec, angle):
        rotation = np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
        return rotation @ vec

    @staticmethod
    def wrap_to_pi(angle):
        return (angle + np.pi) % (2 * np.pi) - np.pi
