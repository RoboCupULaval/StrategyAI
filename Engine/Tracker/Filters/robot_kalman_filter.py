
import numpy as np

from Engine.Tracker.Filters import KalmanFilter
from config.config import Config

config = Config()


class RobotFilter(KalmanFilter):

    def __init__(self, id):
        super().__init__(id)
        initial_dt = 1 / config['ENGINE']['fps']
        self.observation_model = np.array([[1, 0, 0, 0, 0, 0],   # Position x
                                          [0, 0, 1, 0, 0, 0],   # Position y
                                          [0, 0, 0, 0, 1, 0]])  # Orientation
        self.observation_covariance = np.diag([100, 100, 0.1 * np.pi / 180])
        self.observable_state = int(np.size(self.observation_model, 0))
        self.transition_model = np.array([[1, initial_dt, 0, 0,  0, 0],   # Position x
                                          [0, 1,  0, 0,  0, 0],   # Speed x
                                          [0, 0,  1, initial_dt, 0, 0],   # Position y
                                          [0, 0,  0, 1,  0, 0],   # Speed y
                                          [0, 0,  0, 0,  1, initial_dt],  # Position Theta
                                          [0, 0,  0, 0,  0, 1]])  # Speed Theta
        self.state_number = int(np.size(self.transition_model, 0))
        self.observable_state = int(np.size(self.observation_model, 0))

        self.control_input_model = np.array([[0,  0,  0],  # Position x
                                             [initial_dt, 0,  0],  # Speed x
                                             [0,  0,  0],  # Position y
                                             [0,  initial_dt, 0],  # Speed y
                                             [0,  0,  0],  # Position Theta
                                             [0,  0, initial_dt]])  # Speed Theta

        self.x = np.zeros(self.state_number)

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

    def update_transition_model(self, dt):
        # The position (0,1), (2,3) and (4, 5) is the position in the transition model that contains the dt
        self.transition_model[[0, 2, 4], [1, 3, 5]] = dt

    def update_control_input_model(self, dt):
        # The position (1,0), (2,1) and (5, 2) is the position in the transition model that contains the dt
        self.control_input_model[[1, 3, 5], [0, 1, 2]] = dt

    def process_covariance(self, dt):
        sacc_x = 400 ** 2  # sigma_acc_x
        sacc_y = 400 ** 2  # sigma_acc_y
        sacc_o = (400 * np.pi/180) ** 2  # sigma_acc_o
        process_covariance = \
            np.array([
                [0.25 * dt ** 4 * sacc_x, 0.50 * dt ** 3 * sacc_x,                       0,                       0,                       0,                       0],
                [0.50 * dt ** 3 * sacc_x, 1.00 * dt ** 2 * sacc_x,                       0,                       0,                       0,                       0],
                [             0,                                0, 0.25 * dt ** 4 * sacc_y, 0.50 * dt ** 3 * sacc_y,                       0,                       0],
                [             0,                                0, 0.50 * dt ** 3 * sacc_y, 1.00 * dt ** 2 * sacc_y,                       0,                       0],
                [             0,                                0,                       0,                       0, 0.25 * dt ** 4 * sacc_o, 0.50 * dt ** 3 * sacc_o],
                [             0,                                0,                       0,                       0, 0.50 * dt ** 3 * sacc_o, 1.00 * dt ** 2 * sacc_o]])

        return process_covariance

    def initial_state_covariance(self):
        return np.diag([10000, 10, 10000, 10, 90 * np.pi/180, 1 * np.pi/180])

    def update(self, observation, t_capture):

        error = observation - self.observation_model @ self.x
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
