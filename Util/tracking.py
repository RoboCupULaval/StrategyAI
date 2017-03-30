import numpy as np


class Kalman:
    def __init__(self, type, ncameras=4, observation=None):

        dt = 0.03
        self.type = type

        if self.type == 'friend':
            # Transition model
            self.F = np.array([[1, 0, dt,  0, 0, 0], # Position x
                               [0, 1,  0, dt, 0, 0], # Position y
                               [0, 0,  1,  0, 0, 0], # Speed x
                               [0, 0,  0,  1, 0, 0], # Speed y
                               [0, 0,  0,  0, 1, dt], # Orientation
                               [0, 0,  0,  0, 0, 1]]) # Speed w
            # Control input model
            self.B = np.array([[0, 0, 0],
                               [0, 0, 0],
                               [0, 0, 0], # Speed x
                               [0, 0, 0], # Speed y
                               [0, 0, 0],
                               [0, 0, 0]]) # Speed w
            # Observation model
            self.H = [[1, 0, 0, 0, 0, 0] for i in range(ncameras)] # Position x
            self.H += [[0, 1, 0, 0, 0, 0] for i in range(ncameras)] # Position y
            self.H += [[0, 0, 0, 0, 1, 0] for i in range(ncameras)] # Orientation
            self.H = np.array(self.H)
            # Process covariance
            values = np.array([10 ** (0), 10 ** (0), 10 ** (1), 10 ** (1), 10 ** (-2), 10 ** (-1)])
            self.Q = np.diag(values)
            # Observation covariance
            values = [10 ** (0), 10 ** (0), 10 ** (-2)]
            for i in range(ncameras-1):
                values += values
            self.R = np.diag(values)  # Pose * ncameras
            # Initial state covariance
            self.P = 10 ** (3) * np.eye(6)

            self.x = np.array([0, 0, 0, 0, 0, 0])
            i = 0
            if observation is not None:
                for obs in observation:
                    if obs is not None:
                        self.x += [obs.x, obs.y, 0, 0, obs.orientation, 0]
                        i += 1
                if i > 0:
                    self.x = self.x / i
                else:
                    self.x = self.x

        elif self.type == 'enemi':
            # Transition model
            self.F = np.array([[1, 0, dt, 0, 0, 0],  # Position x
                               [0, 1, 0, dt, 0, 0],  # Position y
                               [0, 0, 1, 0, 0, 0],  # Speed x
                               [0, 0, 0, 1, 0, 0],  # Speed y
                               [0, 0, 0, 0, 1, dt],  # Orientation
                               [0, 0, 0, 0, 0, 1]])  # Speed w
            # Observation model
            self.H = [[1, 0, 0, 0, 0, 0] for i in range(ncameras)]  # Position x
            self.H += [[0, 1, 0, 0, 0, 0] for i in range(ncameras)]  # Position y
            self.H += [[0, 0, 0, 0, 1, 0] for i in range(ncameras)]  # Orientation
            self.H = np.array(self.H)
            # Process covariance
            values = np.array([10 ** (0), 10 ** (0), 10 ** (0), 10 ** (0), 10 ** (-2),  10 ** (-2)])
            self.Q = np.diag(values)
            # Observation covariance
            values = [10 ** (0), 10 ** (0), 10 ** (-2)]
            for i in range(ncameras - 1):
                values += values
            self.R = np.diag(values)  # Pose * ncameras
            # Initial state covariance
            self.P = 10 ** (3) * np.eye(6)

            self.x = np.array([0, 0, 0, 0, 0, 0])
            i = 0
            if observation is not None:
                for obs in observation:
                    if obs is not None:
                        self.x += [obs.x, obs.y, 0, 0, obs.orientation, 0]
                        i += 1
                if i > 0:
                    self.x = self.x/i
                else:
                    self.x = self.x

        elif self.type == 'ball':
            # Transition model
            self.F = np.array([[1, 0, dt, 0],  # Position x
                               [0, 1, 0, dt],  # Position y
                               [0, 0, 1, 0],  # Speed x
                               [0, 0, 0, 1]])  # Speed y
            # Observation model
            self.H = [[1, 0, 0, 0] for i in range(ncameras)]  # Position x
            self.H += [[0, 1, 0, 0] for i in range(ncameras)]  # Position y
            self.H = np.array(self.H)
            # Process covariance
            values = np.array([10 ** (0), 10 ** (0), 10 ** (0), 10 ** (0)])
            self.Q = np.diag(values)
            # Observation covariance
            values = [10 ** (0), 10 ** (0)]
            for i in range(ncameras - 1):
                values += values
            self.R = np.diag(values)  # Pose * ncameras
            # Initial state covariance
            self.P = 10 ** (3) * np.eye(4)
            # Initial state estimation
            # self.x = np.array([observation.x, observation.y, 0, 0])
            self.x = np.array([0, 0, 0, 0])
            i = 0
            if observation is not None:
                for obs in observation:
                    if obs is not None:
                        self.x += [obs.x, obs.y, 0, 0]
                        i += 1
                if i > 0:
                    self.x = self.x/i
                else:
                    self.x = self.x

    def predict(self, command):
        if command == None or self.type == 'enemi' or self.type == 'ball':
            self.x = np.dot(self.F, self.x)
        else:
            self.x = np.dot(self.F, self.x) + np.dot(self.B, np.array(command))
        self.P = np.dot(np.dot(self.F, self.P), np.transpose(self.F)) + self.Q

    def update(self, observation):
        if self.type == 'friend' or self.type == 'enemi':
            obsx = []
            obsy = []
            obsth = []
            for obs in observation:
                if obs is not None:
                    obsx.append(obs.position.x)
                    obsy.append(obs.position.y)
                    obsth.append(obs.orientation)
                if obs is None:
                    obsx.append(None)
                    obsy.append(None)
                    obsth.append(None)
            observation = np.array(obsx + obsy + obsth)
        elif self.type == 'ball':
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
        if len(observation_wmask) is not 0:
            H = self.H[mask]
            R = np.transpose(self.R[mask])
            R = np.transpose(R[mask])

            y = np.array(observation_wmask) - np.dot(H, self.x)
            S = np.dot(np.dot(H, self.P), np.transpose(H)) + R
            K = np.dot(np.dot(self.P, np.transpose(H)), np.linalg.inv(S))
            self.x = self.x + np.dot(K, np.transpose(y))
            self.P = np.dot((np.eye(self.P.shape[0]) - np.dot(K, H)), self.P)

    def transition_model(self, dt):
        if (self.type == 'friend') or (self.type == 'enemi'):
            self.F = np.array([[1, 0, dt, 0, 0, 0],  # Position x
                               [0, 1, 0, dt, 0, 0],  # Position y
                               [0, 0, 1, 0, 0, 0],  # Speed x
                               [0, 0, 0, 1, 0, 0],  # Speed y
                               [0, 0, 0, 0, 1, dt],  # Orientation
                               [0, 0, 0, 0, 0, 1]])  # Speed w
        elif (self.type == 'ball'):
            self.F = np.array([[1, 0, dt, 0],  # Position x
                               [0, 1, 0, dt],  # Position y
                               [0, 0, 1, 0],  # Speed x
                               [0, 0, 0, 1]])  # Speed y

    def filter(self, observation=None, command=None, dt=0.03):
        self.transition_model(dt)
        self.predict(command)
        if observation != None:
            self.update(observation)
        #print(dt, '   ', self.x)
        if self.type == 'friend' or self.type == 'enemi':
            self.x[4] = (self.x[4] + np.pi) % (2 * np.pi) - np.pi
        return self.x
