from abc import abstractmethod
import numpy as np
from time import time

MAX_DT = 1


class KalmanFilter:

    def __init__(self):

        self.is_active = False
        self.last_update_time = 0
        self.last_predict_time = time()
        self.dt = 0

        self.state_number = int(np.size(self.transition_model(), 0))
        self.observable_state = int(np.size(self.observation_model(), 0))

        self.x = np.zeros(self.state_number)

        self.R = self.observation_covariance()
        self.Q = self.process_covariance()
        self.P = self.initial_state_covariance()

    @abstractmethod
    def transition_model(self):
        return np.zeros(0)

    def control_input_model(self):
        return np.zeros(0)

    @abstractmethod
    def observation_model(self):
        return np.zeros(0)

    @abstractmethod
    def initial_state_covariance(self):
        return np.zeros(0)

    @abstractmethod
    def process_covariance(self):
        return np.zeros(0)

    @abstractmethod
    def observation_covariance(self):
        return np.zeros(0)

    def _update(self, error, t_capture):

        self.is_active = True
        self.last_update_time = t_capture

        # Compute Kalman gain from states covariance and observation model
        gain = self.P @ self.observation_model().T \
            @ np.linalg.inv(self.observation_model() @ self.P @ self.observation_model().T + self.R)

        # Update the states vector
        self.x = self.x + gain @ error

        # Update the states covariance matrix
        self.P = self.P - gain @ self.observation_model() @ self.P

    def _predict(self, input_command):
        self.dt = time() - self.last_predict_time
        self.last_predict_time = time()
        print(self.dt)
        # Predict the next state from states vector and input commands
        if False:
            self.x = self.transition_model() @ self.x + self.control_input_model() @ input_command
        else:
            self.x = self.transition_model() @ self.x

        # Update the state covariance matrix from the transition model
        self.P = self.transition_model() @ self.P @ self.transition_model().T + self.Q

    def update(self, observation, t_capture) -> None:
        error = observation - self.observation_model() @ self.x
        self._update(error, t_capture)

    def predict(self, input_command=None):
        self._predict(input_command)

    def reset(self):
        self.is_active = False
        self.P = self.initial_state_covariance()
        self.x = np.zeros(self.state_number)
