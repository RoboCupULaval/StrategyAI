from abc import abstractmethod
import numpy as np
import logging

class KalmanFilter:

    def __init__(self, _id=None):

        self._id = _id
        self.is_active = False
        self.last_update_time = 0
        self.first_update_time = 0
        self.observation_covariance = np.diag([1, 1])
        self.observation_model = np.array([[1, 0, 0, 0],   # Position x
                                          [0, 0, 1, 0]])  # Position y
        self.transition_model = np.zeros(0)
        self.control_input_model = np.zeros(0)
        self.state_number = int(np.size(self.transition_model, 0))
        self.observable_state = int(np.size(self.observation_model, 0))

        self.x = np.zeros(self.state_number)

        self.Q = self.process_covariance
        self.P = self.initial_state_covariance()
        self.logger = logging.getLogger(self.__class__.__name__)


    @property
    def id(self):
        return self._id

    @abstractmethod
    def update_transition_model(self, dt):
        pass

    def update_control_input_model(self, dt):
        pass

    @abstractmethod
    def initial_state_covariance(self):
        return 10 ** 6 * np.eye(self.state_number)

    @abstractmethod
    def process_covariance(self, dt):
        return np.zeros(0)

    def _update(self, error, update_time):
        self.is_active = True

        if not self.first_update_time: self.first_update_time = update_time

        if self.last_update_time > update_time:
            return

        self.last_update_time = update_time

        m = self.observation_model @ self.P @ self.observation_model.T + self.observation_covariance
        s = self.P @ self.observation_model.T
        m_diag = np.diagonal(m)

        # If the matrix is a diagonal
        if np.count_nonzero(m - np.diag(m_diag)) == 0:
            # Since the matrix is most of the time a diagonal,
            # we can compute its inverse way faster with this optimisation
            gain = np.divide(s, m_diag)
        else:
            gain = s @ np.linalg.inv(m)
            self.logger.debug('Regular inverse expression used, performance maybe bad. (non-diagonal matrix)')
        # Compute Kalman gain from states covariance and observation model

        # Update the states vector
        self.x = self.x + gain @ error

        # Update the states covariance matrix
        self.P = self.P - gain @ self.observation_model @ self.P

    def _predict(self, dt, input_command=None):
        self.update_transition_model(dt)
        self.update_control_input_model(dt)
        # Predict the next state from states vector and input commands
        if input_command is not None:
            self.x = self.transition_model @ self.x + self.control_input_model @ input_command
        else:
            self.x = self.transition_model @ self.x

        # Update the state covariance matrix from the transition model
        self.P = self.transition_model @ self.P @ self.transition_model.T + self.Q(dt)

    def update(self, observation, t_capture):
        error = observation - self.observation_model @ self.x
        self._update(error, t_capture)

    def predict(self, dt, input_command=None):
        self._predict(dt, input_command)

    def reset(self):
        self.is_active = False
        self.P = self.initial_state_covariance()
        self.x = np.zeros(self.state_number)
        self.last_update_time = 0
        self.first_update_time = 0
