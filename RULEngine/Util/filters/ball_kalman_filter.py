import numpy as np
from RULEngine.Util.filters.kalman_filter import KalmanFilter


class BallFilter(KalmanFilter):
    INITIAL_CONFIDENCE = 20

    INITIAL_STATE_COVARIANCE = 1000

    POSITION_PROCESS_COVARIANCE = 1
    VELOCITY_PROCESS_COVARIANCE = 10

    POSITION_OBSERVATION_COVARIANCE = 2

    def __init__(self):
        self.confidence = BallFilter.INITIAL_CONFIDENCE
        super().__init__()

    @property
    def pose(self):
        if self.is_active:
            return np.array([self.x[0], self.x[2]]).flatten()

    @property
    def velocity(self):
        if not self.is_active:
            return None
        else:
            return np.array([self.x[1], self.x[3]]).flatten()

    def transition_model(self, dt=0):
        return np.array([[1, dt, 0,  0],   # Position x
                         [0,  1, 0,  0],   # Speed x
                         [0,  0, 1, dt],   # Position y
                         [0,  0, 0,  1]])  # Speed y

    def observation_model(self):
        return np.array([[1, 0, 0, 0],   # Position x
                         [0, 0, 1, 0]])  # Position y

    def control_input_model(self, dt=0):
        return np.zeros((self.state_number, self.observable_state))

    def initial_state_covariance(self):
        return BallFilter.INITIAL_STATE_COVARIANCE * np.eye(self.state_number)

    def process_covariance(self):
        return np.diag([BallFilter.POSITION_PROCESS_COVARIANCE,
                        BallFilter.VELOCITY_PROCESS_COVARIANCE,
                        BallFilter.POSITION_PROCESS_COVARIANCE,
                        BallFilter.VELOCITY_PROCESS_COVARIANCE])

    def observation_covariance(self):
        return BallFilter.POSITION_OBSERVATION_COVARIANCE * np.eye(self.observable_state)

    def update(self, observation, t_capture):
        self.is_active = True

        self._increase_confidence()

        dt = t_capture - self.last_t_capture
        if dt < 0:
            return
        self.last_t_capture = t_capture

        self.last_observation = observation

        self.F = self.transition_model(dt)
        y = observation - np.dot(self.H, self.x)
        self.S = np.dot(np.dot(self.H, self.P), self.H.T) + self.R
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(self.S))

        self.x = self.x + np.dot(K, y)
        self.P = np.dot((np.eye(self.state_number) - np.dot(K, self.H)), self.P)

    def predict(self, dt=0):
        self._decrease_confidence()
        self.F = self.transition_model(dt)
        self.B = self.control_input_model(dt)
        self.x = np.dot(self.F, self.x) + np.dot(self.B, self.u)
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q

    def _increase_confidence(self):
        self.confidence += 1
        if self.confidence > 100:
            self.confidence = 100

    def _decrease_confidence(self):
        self.confidence *= 0.95
        if self.confidence < 0:
            self.confidence = 0
