import numpy as np

class Kalman:
    def __init__(self, type, ncameras, observation):

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
            self.H = []
            self.H.append([1, 0, 0, 0, 0, 0] for i in range(ncameras)) # Position x
            self.H.append([0, 1, 0, 0, 0, 0] for i in range(ncameras)) # Position y
            self.H.append([0, 0, 0, 0, 1, 0] for i in range(ncameras)) # Orientation
            self.H = np.array(self.H)
            # Process covariance
            self.Q = 10 ** (1) * np.eye(6)
            # Observation covariance
            self.R = 10 ** (0) * np.eye(3*4) # Pose * 4 cameras
            # Initial state covariance
            self.P = 10 ** (3) * np.eye(6)
            # Initial state estimation
            self.x = np.array([observation.x, observation.y, 0, 0, observation.orientation])

        elif self.type == 'ennemi':
            # Transition model
            self.F = np.array([[1, 0, dt, 0, 0, 0],  # Position x
                               [0, 1, 0, dt, 0, 0],  # Position y
                               [0, 0, 1, 0, 0, 0],  # Speed x
                               [0, 0, 0, 1, 0, 0],  # Speed y
                               [0, 0, 0, 0, 1, dt],  # Orientation
                               [0, 0, 0, 0, 0, 1]])  # Speed w
            # Observation model
            self.H = []
            self.H.append([1, 0, 0, 0, 0, 0] for i in range(ncameras))  # Position x
            self.H.append([0, 1, 0, 0, 0, 0] for i in range(ncameras))  # Position y
            self.H.append([0, 0, 0, 0, 1, 0] for i in range(ncameras))  # Orientation
            self.H = np.array(self.H)
            # Process covariance
            self.Q = 10 ** (1) * np.eye(6)
            # Observation covariance
            self.R = 10 ** (0) * np.eye(3 * 4)  # Pose * 4 cameras
            # Initial state covariance
            self.P = 10 ** (3) * np.eye(6)
            # Initial state estimation
            self.x = np.array([observation.x, observation.y, 0, 0, observation.orientation])

        elif self.type == 'ball':
            # Transition model
            self.F = np.array([[1, 0, dt, 0],  # Position x
                               [0, 1, 0, dt],  # Position y
                               [0, 0, 1, 0],  # Speed x
                               [0, 0, 0, 1]])  # Speed y
            # Observation model
            self.H = []
            self.H.append([1, 0, 0, 0] for i in range(ncameras))  # Position x
            self.H.append([0, 1, 0, 0] for i in range(ncameras))  # Position y
            self.H = np.array(self.H)
            # Process covariance
            self.Q = 10 ** (1) * np.eye(4)
            # Observation covariance
            self.R = 10 ** (0) * np.eye(2 * 4)  # Position * 4 cameras
            # Initial state covariance
            self.P = 10 ** (3) * np.eye(4)
            # Initial state estimation
            self.x = np.array([observation.x, observation.y, 0, 0])

    def predict(self, command):
        if command == None:
            self.x = np.dot(self.F, self.x)
        else:
            self.x = np.dot(self.F, self.x) + np.dot(self.B, np.array(command))
        self.P = np.dot(np.dot(self.F, self.P), np.transpose(self.F)) + self.Q

    def update(self, observation):
        observation = np.array(observation)
        mask = [obs != None for obs in observation]
        observation_wmask = observation[mask]
        H = self.H[mask]

        y = np.array(observation_wmask) - np.dot(H, self.x)
        S = np.dot(np.dot(H, self.P), np.transpose(H)) + self.R
        K = np.dot(np.dot(self.P, np.transpose(H)), np.linalg.inv(S))

        self.x += np.dot(K, y)
        self.P = np.dot((np.eye(self.P.shape[0]) - np.dot(K, H)), self.P)

    def transition_model(self, dt):
        if (self.type == 'friend') | (self.type == 'ennemi'):
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
        self.transition_model(dt)
        self.predict(command)
        if observation != None:
            self.update(observation)
        return self.x
