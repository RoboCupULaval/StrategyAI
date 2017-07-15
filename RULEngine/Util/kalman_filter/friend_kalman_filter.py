import numpy as np
import warnings

from config.config_service import ConfigService

warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)


class FriendKalmanFilter:
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
        # Control input model
        self.B = np.array([[0, 0, 0],
                           [0, 0, 0],
                           [0, 0, 0],  # Speed x
                           [0, 0, 0],  # Speed y
                           [0, 0, 0],
                           [0, 0, 0]])  # Speed w
        # Observation model
        self.H = [[1, 0, 0, 0, 0, 0] for _ in range(ncameras)]  # Position x
        self.H += [[0, 1, 0, 0, 0, 0] for _ in range(ncameras)]  # Position y
        self.H += [[0, 0, 0, 0, 1, 0] for _ in range(ncameras)]  # Orientation
        self.H = np.array(self.H)
        # Process covariance
        values = np.array([10 ** 2,
                           10 ** 2,
                           10 ** 2,
                           10 ** 2,
                           10 ** (-1),
                           10 ** (-1)])  # Orientation Covariance was 0.01, SB
        self.Q = np.diag(values)
        # Observation covariance
        values = [10 ** (1) for _ in range(ncameras)]
        values += [10 ** (1) for _ in range(ncameras)]
        values += [10 ** (-1) for _ in range(ncameras)]
        self.R = np.diag(values)  # Pose * ncameras
        # Initial state covariance
        self.P = 10 ** 3 * np.eye(6)
        self.x = np.array([9999, 9999, 0, 0, 0, 0])

        self.empty_frames_counter = 0

    def predict(self, command):
        if command is None:
            self.x = np.dot(self.F, self.x)
        else:
            self.x = np.dot(self.F, self.x) + np.dot(self.B, np.array(command))
        self.P = np.dot(np.dot(self.F, self.P), np.transpose(self.F)) + self.Q

    def update(self, observation):
        obsx = []
        obsy = []
        obsth = []
        # counter to skip the rest of the function if we don't have suffisent info
        observation_is_useful = False
        for obs in observation:
            if obs is not None:
                observation_is_useful = True
                obsx.append(obs.position.x)
                obsy.append(obs.position.y)
                obsth.append(obs.orientation)
            if obs is None:
                obsx.append(None)
                obsy.append(None)
                obsth.append(None)
        # skip if we received an observation contening only Nones
        if observation_is_useful:
            self.empty_frames_counter = 0
            observation = np.array(obsx + obsy + obsth)

            observation = np.array(observation)
            mask = np.array([obs is not None for obs in observation])
            observation_wmask = observation[mask]
            if len(observation_wmask) != 0:
                H = self.H[mask]
                R = np.transpose(self.R[mask])
                R = np.transpose(R[mask])

                y = np.array(observation_wmask) - np.dot(H, self.x)

                idx = int(2 * len(y) / 3)
                y[idx::] = (y[idx::] + np.pi) % (2 * np.pi) - np.pi

                S = np.dot(np.dot(H, self.P), np.transpose(H)) + R
                K = np.dot(np.dot(self.P, np.transpose(H)), np.linalg.inv(S))
                self.x = self.x + np.dot(K, np.transpose(y))
                self.P = np.dot((np.eye(self.P.shape[0]) - np.dot(K, H)), self.P)
        else:
            self.empty_frames_counter += 1

    def transition_model(self, dt):
        self.F = np.array([[1, 0, dt, 0, 0, 0],  # Position x
                           [0, 1, 0, dt, 0, 0],  # Position y
                           [0, 0, 1, 0, 0, 0],  # Speed x
                           [0, 0, 0, 1, 0, 0],  # Speed y
                           [0, 0, 0, 0, 1, dt],  # Orientation
                           [0, 0, 0, 0, 0, 1]])  # Speed w

    def filter(self, observation=None, command=None, dt=0.05):
        if not dt:
            dt = self.default_dt
        self.transition_model(dt)
        if observation is not None:
            self.update(observation)
        self.predict(command)
        self.x[4] = (self.x[4] + np.pi) % (2 * np.pi) - np.pi
        output_state = self.x.tolist()
        if self.empty_frames_counter > 20:
            output_state = [0, 0, 0, 0, 0, 0]
        return output_state
