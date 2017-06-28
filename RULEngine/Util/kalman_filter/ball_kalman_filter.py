import numpy as np
import warnings

from config.config_service import ConfigService

warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)


class BallKalmanFilter:
    def __init__(self):
        cfg = ConfigService()
        self.default_dt = float(cfg.config_dict["GAME"]["ai_timestamp"])
        ncameras = int(cfg.config_dict["IMAGE"]["number_of_camera"])

        # Transition model
        self.F = np.array([[1, 0, self.default_dt, 0, 0, 0],  # Position x
                           [0, 1, 0, self.default_dt, 0, 0],  # Position y
                           [0, 0, 1, 0, 0, 0],  # Speed x
                           [0, 0, 0, 1, 0, 0],  # Speed y
                           [0, 0, 0, 0, 1, self.default_dt],  # Orientation
                           [0, 0, 0, 0, 0, 1]])  # Speed w
        # Observation model
        self.H = [[1, 0, 0, 0] for _ in range(ncameras)]  # Position x
        self.H += [[0, 1, 0, 0] for _ in range(ncameras)]  # Position y
        self.H = np.array(self.H)
        # Process covariance
        values = np.array([10 ** 0, 10 ** 0, 10 ** 0, 10 ** 0])
        self.Q = np.diag(values)
        # Observation covariance
        values = [10 ** 0 for _ in range(ncameras)]
        values += [10 ** 0 for _ in range(ncameras)]
        self.R = np.diag(values)  # Pose * ncameras
        # Initial state covariance
        self.P = 10 ** 3 * np.eye(4)
        # Initial state estimation
        # self.x = np.array([observation.x, observation.y, 0, 0])
        self.x = np.array([0, 0, 0, 0])

    def predict(self):
        self.x = np.dot(self.F, self.x)
        self.P = np.dot(np.dot(self.F, self.P), np.transpose(self.F)) + self.Q

    def update(self, observation):
        obsx = []
        obsy = []
        for obs in observation:
            if obs is not None:
                obsx.append(obs.x)
                obsy.append(obs.y)
            if obs is None:
                obsx.append(None)
                obsy.append(None)
        observation = np.array(obsx + obsy)

        observation = np.array(observation)
        mask = np.array([obs is not None for obs in observation])
        observation_wmask = observation[mask]
        if len(observation_wmask) != 0:
            H = self.H[mask]
            R = np.transpose(self.R[mask])
            R = np.transpose(R[mask])

            y = np.array(observation_wmask) - np.dot(H, self.x)

            S = np.dot(np.dot(H, self.P), np.transpose(H)) + R
            K = np.dot(np.dot(self.P, np.transpose(H)), np.linalg.inv(S))
            self.x = self.x + np.dot(K, np.transpose(y))
            self.P = np.dot((np.eye(self.P.shape[0]) - np.dot(K, H)), self.P)

    def transition_model(self, dt):
        self.F = np.array([[1, 0, dt, 0],  # Position x
                           [0, 1, 0, dt],  # Position y
                           [0, 0, 1, 0],  # Speed x
                           [0, 0, 0, 1]])  # Speed y

    def filter(self, observation=None, dt=0.05):
        if not dt:
            dt = self.default_dt
        self.transition_model(dt)
        if observation is not None:
            self.update(observation)
        self.predict()
        output_state = self.x
        return output_state
