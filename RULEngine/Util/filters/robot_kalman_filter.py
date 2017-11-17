import numpy as np
from RULEngine.Util.filters.kalman_filter import KalmanFilter


class RobotFilter(KalmanFilter):

    INITIAL_STATE_COVARIANCE = 1000

    POSITION_PROCESS_COVARIANCE = 1
    VELOCITY_PROCESS_COVARIANCE = 10
    ORIENTATION_PROCESS_COVARIANCE = 0.05
    ANGULAR_VELOCITY_PROCESS_COVARIANCE = 0.5

    POSITION_OBSERVATION_COVARIANCE = 2
    ORIENTATION_OBSERVATION_COVARIANCE = 0.05

    def __init__(self):
        self.tau = [0.3, 0.3, 0.3]
        super().__init__()

    @property
    def pose(self):
        if self.is_active:
            return np.array([self.x[0], self.x[2], self.x[4]]).flatten()

    @property
    def velocity(self):
        if not self.is_active:
            return None
        else:
            return np.array([self.x[1], self.x[3], self.x[5]]).flatten()

    def get_orientation(self):
        if not self.is_active:
            return None
        else:
            return self.x[4]

    def transition_model(self, dt=0):
        return np.array([[1,                    dt, 0,  0,                    0,  0],   # Position x
                         [0,  1 - dt / self.tau[0], 0,  0,                    0,  0],   # Speed x
                         [0,                     0, 1, dt,                    0,  0],   # Position y
                         [0,                     0, 0,  1 - dt / self.tau[1], 0,  0],   # Speed y
                         [0,                     0, 0,  0,                    1, dt],   # Position Theta
                         [0,                     0, 0,  0,                    0,  1 - dt / self.tau[2]]])  # Speed Theta

    def observation_model(self):
        return np.array([[1, 0, 0, 0, 0, 0],   # Position x
                         [0, 0, 1, 0, 0, 0],   # Position y
                         [0, 0, 0, 0, 1, 0]])  # Orientation

    def control_input_model(self, dt=0):
        return np.array([[0,                0,                0],  # Position x
                         [dt / self.tau[0], 0,                0],  # Speed x
                         [0,                0,                0],  # Position y
                         [0,                dt / self.tau[1], 0],  # Speed y
                         [0,                0,                0],  # Position Theta
                         [0,                0,                dt / self.tau[2]]])  # Speed Theta

    def initial_state_covariance(self):
        return RobotFilter.INITIAL_STATE_COVARIANCE * np.eye(self.state_number)

    def process_covariance(self):
        return np.diag([RobotFilter.POSITION_PROCESS_COVARIANCE,
                        RobotFilter.VELOCITY_PROCESS_COVARIANCE,
                        RobotFilter.POSITION_PROCESS_COVARIANCE,
                        RobotFilter.VELOCITY_PROCESS_COVARIANCE,
                        RobotFilter.ORIENTATION_PROCESS_COVARIANCE,
                        RobotFilter.ANGULAR_VELOCITY_PROCESS_COVARIANCE])

    def observation_covariance(self):
        return np.diag([RobotFilter.POSITION_OBSERVATION_COVARIANCE,
                        RobotFilter.POSITION_OBSERVATION_COVARIANCE,
                        RobotFilter.ORIENTATION_OBSERVATION_COVARIANCE])

    def update(self, observation, t_capture):
        self.is_active = True

        dt = t_capture - self.last_t_capture
        if dt < 0:
            return
        self.last_t_capture = t_capture
        self.last_observation = observation

        self.F = self.transition_model(dt)
        y = observation - np.dot(self.H, self.x)
        y[2] = RobotFilter.wrap_to_pi(y[2])
        self.S = np.dot(np.dot(self.H, self.P), self.H.T) + self.R
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(self.S))

        self.x = self.x + np.dot(K, y)
        self.P = np.dot((np.eye(self.state_number) - np.dot(K, self.H)), self.P)

    def predict(self, dt=0):
        if not self.is_active:
            return
        self.F = self.transition_model(dt)
        self.B = self.control_input_model(dt)
        self.x = np.dot(self.F, self.x) + np.dot(self.B, self.u)
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q

    @staticmethod
    def wrap_to_pi(angle):
        return (angle + np.pi) % (2 * np.pi) - np.pi
