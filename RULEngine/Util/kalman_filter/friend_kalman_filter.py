import numpy as np
import warnings

from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from config.config_service import ConfigService
# from profilehooks import profile

warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)


class FriendKalmanFilter:
    def __init__(self):
        self.matrix_flag = False
        cfg = ConfigService()
        if cfg.config_dict["GAME"]["kalman_matrix_flag"] == "true":
            self.matrix_flag = True
        self.default_dt = float(cfg.config_dict["GAME"]["ai_timestamp"])
        self.tau_x = 0.3
        self.tau_y = 0.3
        self.tau_orientation = self.default_dt
        ncameras = int(cfg.config_dict["IMAGE"]["number_of_camera"])

        # Transition model
        self.F = np.array([[1, 0, self.default_dt, 0, 0, 0],  # Position x
                           [0, 1, 0, self.default_dt, 0, 0],  # Position y
                           [0, 0, (1 - self.default_dt/self.tau_x), 0, 0, 0],  # Speed x
                           [0, 0, 0, (1 - self.default_dt/self.tau_y), 0, 0],  # Speed y
                           [0, 0, 0, 0, 1, self.default_dt],  # Orientation
                           [0, 0, 0, 0, 0, (1 - self.default_dt/self.tau_orientation)]])  # Speed w
        # Control input model
        self.B = np.array([[0, 0, 0],
                           [0, 0, 0],
                           [self.default_dt/self.tau_x, 0, 0],  # Speed x
                           [0, self.default_dt/self.tau_y, 0],  # Speed y
                           [0, 0, 0],
                           [0, 0, self.default_dt/self.tau_orientation]])  # Speed w
        # Observation model
        self.H = [[1, 0, 0, 0, 0, 0] for _ in range(ncameras)]  # Position x
        self.H += [[0, 1, 0, 0, 0, 0] for _ in range(ncameras)]  # Position y
        self.H += [[0, 0, 0, 0, 1, 0] for _ in range(ncameras)]  # Orientation
        self.H = np.array(self.H)
        # Process covariance
        values = np.array([10 ** 1,
                           10 ** 1,
                           10 ** 2,
                           10 ** 2,
                           10 ** (-1),
                           10 ** (-1)]) # Orientation Covariance was 0.01, SB
        self.Q = np.diag(values)
        # Observation covariance
        values = [10 ** (2) for _ in range(ncameras)]
        values += [10 ** (2) for _ in range(ncameras)]
        values += [10 ** (-1) for _ in range(ncameras)]
        self.R = np.diag(values)  # Pose * ncameras
        # Initial state covariance
        self.eye = np.eye(6)
        self.P = 10 ** 6 * self.eye
        self.x = np.array([9999, 9999, 0, 0, 0, 0])

    def predict(self, command):
        if command is None:
            self.x = np.dot(self.F, self.x)
        else:
            if np.isinf(np.array(self.x, dtype=np.float64)).any():
                raise "FUCK"
            conversion_m_to_mm = 1000
            command = Pose(command[0], command[1], command[2]).scale(conversion_m_to_mm)
            command.position = command.position.rotate(self.x[4])
            oldx = self.x.copy()
            self.x = np.dot(self.F, oldx) + np.dot(self.B, command.to_array())

        self.P = np.dot(np.dot(self.F, self.P), np.transpose(self.F)) + self.Q
        if self.P[0][0] is np.nan:
            exit(0)

        if np.abs(self.x[5]) > 500:
            print("A The estimate of orientation speed is reaching inf!!")
            self.x[5] = 0
            self.P[5][5] = 0


    # @profile(immediate=False)
    def update(self, observation):

        obsx = []
        obsy = []
        obsth = []
        for obs in observation:
            if self.matrix_flag or obs is None:
                obsx.append(None)
                obsy.append(None)
                obsth.append(None)
            else:
                obsx.append(obs.position.x)
                obsy.append(obs.position.y)
                obsth.append(obs.orientation)
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
            self.P = np.dot((self.eye - np.dot(K, H)), self.P)

        if np.abs(self.x[5]) > 500:
            print("B The estimate of orientation speed is reaching inf!!")
            self.x[5] = 0

    def transition_model_with_command(self, dt):
        self.F = np.array([[1, 0, dt, 0, 0, 0],  # Position x
                           [0, 1, 0, dt, 0, 0],  # Position y
                           [0, 0, (1 - dt/self.tau_x), 0, 0, 0],  # Speed x
                           [0, 0, 0, (1 - dt/self.tau_y), 0, 0],  # Speed y
                           [0, 0, 0, 0, 1, dt],  # Orientation
                           [0, 0, 0, 0, 0, (1 - dt/self.tau_orientation)]])  # Speed w
        self.B = np.array([[0, 0, 0],
                           [0, 0, 0],
                           [dt/self.tau_x, 0, 0],  # Speed x
                           [0, dt/self.tau_y, 0],  # Speed y
                           [0, 0, 0],
                           [0, 0, self.default_dt/self.tau_orientation]])  # Speed w

    def transition_model(self, dt):
        self.F = np.array([[1, 0, dt, 0, 0, 0],  # Position x
                           [0, 1, 0, dt, 0, 0],  # Position y
                           [0, 0, 1, 0, 0, 0],  # Speed x
                           [0, 0, 0, 1, 0, 0],  # Speed y
                           [0, 0, 0, 0, 1, dt],  # Orientation
                           [0, 0, 0, 0, 0, 1]])  # Speed w
        self.B = np.array([[0, 0, 0],
                           [0, 0, 0],
                           [0, 0, 0],  # Speed x
                           [0, 0, 0],  # Speed y
                           [0, 0, 0],
                           [0, 0, 0]])  # Speed w

    def filter(self, observation=None, command=None, dt=0.05):
        if not dt:
            dt = self.default_dt
        if np.isinf(np.array(self.x, dtype=np.float64)).any():
            raise "FUCK"
        if command is not None:
            self.transition_model_with_command(dt)
        else:
            self.transition_model(dt)
        if observation is not None:
            self.update(observation)
        self.predict(command)
        output_state = self.x
        output_state[4] = (self.x[4] + np.pi) % (2 * np.pi) - np.pi

        return output_state
