import numpy as np


class Kalman:
    def __init__(self, type, ncameras=4, observation=None):

        dt = 0.03
        self.type = type

        if self.type == 'friend':
            # Transition model
            self.F = np.array([[1, 0, dt,  0, 0, 0], # Position x
                               [0, 1,  0, dt, 0, 0], # Position y
                               [0, 0,  0,  0, 0, 0], # Speed x
                               [0, 0,  0,  0, 0, 0], # Speed y
                               [0, 0,  0,  0, 1, dt], # Orientation
                               [0, 0,  0,  0, 0, 0]]) # Speed w
            # Control input model
            self.B = np.array([[0, 0, 0],
                               [0, 0, 0],
                               [1, 0, 0], # Speed x
                               [0, 1, 0], # Speed y
                               [0, 0, 0],
                               [0, 0, 1]]) # Speed w
            # Observation model
            self.H = [[1, 0, 0, 0, 0, 0] for i in range(ncameras)] # Position x
            self.H += [[0, 1, 0, 0, 0, 0] for i in range(ncameras)] # Position y
            self.H += [[0, 0, 0, 0, 1, 0] for i in range(ncameras)] # Orientation
            self.H = np.array(self.H)
            # Process covariance
            self.Q = 10 ** (1) * np.eye(6)
            # Observation covariance
            self.R = 10 ** (0) * np.eye(3*4) # Pose * 4 cameras
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

        elif self.type == 'ennemi':
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
            self.Q = 10 ** (1) * np.eye(6)
            # Observation covariance
            self.R = 10 ** (0) * np.eye(3 * 4)  # Pose * 4 cameras
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
            self.Q = 10 ** (1) * np.eye(4)
            # Observation covariance
            self.R = 10 ** (0) * np.eye(2 * 4)  # Position * 4 cameras
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
        if command == None:
            self.x = np.dot(self.F, self.x)
        else:
            self.x = np.dot(self.F, self.x) + np.dot(self.B, np.array(command))
        self.P = np.dot(np.dot(self.F, self.P), np.transpose(self.F)) + self.Q

    def update(self, observation):
        if self.type == 'friend' or self.type == 'ennemi':
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
                    obsx.append(obs.position.x)
                    obsy.append(obs.position.y)
                if obs is None:
                    obsx.append(None)
                    obsy.append(None)
            observation = np.array(obsx + obsy)

        observation = np.array(observation)
        mask = np.array([obs is not None for obs in observation])
        observation_wmask = observation[mask]
        print(observation_wmask)
        if len(observation_wmask) is not 0:
            H = self.H[mask]
            print(H)
            print(self.P)
            y = np.array(observation_wmask) - np.dot(H, self.x)
            S = np.dot(np.dot(H, self.P), np.transpose(H)) + self.R
            K = np.dot(np.dot(self.P, np.transpose(H)), np.linalg.inv(S))

            self.x += np.dot(K, y)
            self.P = np.dot((np.eye(self.P.shape[0]) - np.dot(K, H)), self.P)

    def transition_model(self, dt):
        if (self.type == 'friend') or (self.type == 'ennemi'):
            self.F = np.array([[1, 0, dt, 0, 0, 0],  # Position x
                               [0, 1, 0, dt, 0, 0],  # Position y
                               [0, 0, 0, 0, 0, 0],  # Speed x
                               [0, 0, 0, 0, 0, 0],  # Speed y
                               [0, 0, 0, 0, 1, dt],  # Orientation
                               [0, 0, 0, 0, 0, 0]])  # Speed w
        elif (self.type == 'ball'):
            self.F = np.array([[1, 0, dt, 0, 0, 0],  # Position x
                               [0, 1, 0, dt, 0, 0],  # Position y
                               [0, 0, 0, 0, 0, 0],  # Speed x
                               [0, 0, 0, 0, 0, 0]])  # Speed y

    def filter(self, observation=None, command=None, dt=0.03):
        print(observation)
        self.transition_model(dt)
        self.predict(command)
        if observation != None:
            self.update(observation)
        return self.x
