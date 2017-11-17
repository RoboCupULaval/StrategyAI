from abc import abstractmethod
import numpy as np


class KalmanFilter:

    def __init__(self):

        self.is_active = False
        self.last_t_capture = 0
        self.last_observation = None
        self.last_prediction = None

        self.F = self.transition_model()
        self.H = self.observation_model()

        self.state_number = int(np.size(self.F, 0))
        self.observable_state = int(np.size(self.H, 0))

        self.B = self.control_input_model()

        self.R = self.observation_covariance()
        self.Q = self.process_covariance()
        self.P = self.initial_state_covariance()

        self.S = np.zeros((self.observable_state, self.observable_state))
        self.x = np.zeros(self.state_number)
        self.u = np.zeros(self.observable_state)

    @abstractmethod
    def pose(self):
        pass

    @abstractmethod
    def velocity(self):
        pass

    @abstractmethod
    def transition_model(self, dt):
        pass

    @abstractmethod
    def control_input_model(self, dt):
        pass

    @abstractmethod
    def observation_model(self):
        pass

    @abstractmethod
    def initial_state_covariance(self):
        pass

    @abstractmethod
    def process_covariance(self):
        pass

    @abstractmethod
    def observation_covariance(self):
        pass

    @abstractmethod
    def update(self, observation, t_capture) -> None:
        pass

    @abstractmethod
    def predict(self, dt):
        pass
