
import numpy as np

from Engine.filters.kalman_filter import KalmanFilter


class RobotFilter(KalmanFilter):

    def __init__(self, robot_id):
        self._id = robot_id
        super().__init__()

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

    @property
    def id(self):
        return self._id

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
        sigma_acc_x = 80
        sigma_acc_y = 80
        sigma_acc_o = 100 * np.pi/180

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
        return np.diag([10, 10, 0.1 * np.pi/180])

    def initial_state_covariance(self):
        return np.diag([10000, 1, 10000, 1, 90 * np.pi/180, 10 * np.pi/180])

    def update(self, observation, t_capture) -> None:

        error = observation - self.observation_model() @ self.x
        error[2] = RobotFilter.wrap_to_pi(error[2])
        self._update(error, t_capture)
        self.x[4] = RobotFilter.wrap_to_pi(self.x[4])

    def predict(self, input_command=None):
        if input_command is not None and self.orientation is not None:
            input_command = RobotFilter.rotate(input_command, self.orientation)
        self._predict(input_command)
        self.x[4] = RobotFilter.wrap_to_pi(self.x[4])


    @staticmethod
    def rotate(vec, angle):
        rotation = np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
        return rotation @ vec

    @staticmethod
    def wrap_to_pi(angle):
        return (angle + np.pi) % (2 * np.pi) - np.pi
