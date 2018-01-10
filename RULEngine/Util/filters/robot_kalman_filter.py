import numpy as np
from RULEngine.Util.filters.kalman_filter import KalmanFilter


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
        return np.array([[1, self.dt, 0, 0,       0,       0],   # Position x
                         [0, 1,       0, 0,       0,       0],   # Speed x
                         [0, 0,       1, self.dt, 0,       0],   # Position y
                         [0, 0,       0, 1,       0,       0],   # Speed y
                         [0, 0,       0, 0,       1, self.dt],   # Position Theta
                         [0, 0,       0, 0,       0,       1]])  # Speed Theta

    def observation_model(self):
        return np.array([[1, 0, 0, 0, 0, 0],   # Position x
                         [0, 0, 1, 0, 0, 0],   # Position y
                         [0, 0, 0, 0, 1, 0]])  # Orientation

    def control_input_model(self):
        return np.array([[0, 0, 0],   # Position x
                         [1, 0, 0],   # Speed x
                         [0, 0, 0],   # Position y
                         [0, 1, 0],   # Speed y
                         [0, 0, 0],   # Position Theta
                         [0, 0, 1]])  # Speed Theta

    def initial_state_covariance(self):
        return 1 ** 3 * np.eye(self.state_number)

    def process_covariance(self):
        return np.diag([1, 10, 1, 10, 0.05, 1])

    def observation_covariance(self):
        return np.diag([0.05, 0.05, 0.01])

    def update(self, observation, t_capture):
        error = observation - self.observation_model() @ self.x
        error[2] = RobotFilter.wrap_to_pi(error[2])

        self._update(error, t_capture)

    def predict(self, input_command=0):
        self._predict(input_command)
        self.x[4] = self.wrap_to_pi(self.x[4])

    @staticmethod
    def wrap_to_pi(angle):
        return (angle + np.pi) % (2 * np.pi) - np.pi
