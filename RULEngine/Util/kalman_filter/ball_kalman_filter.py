import numpy as np
import warnings

from RULEngine.Util.constant import BALL_RADIUS, ROBOT_RADIUS
from ai.Algorithm.evaluation_module import closest_players_to_point
from ai.states.game_state import GameState
from config.config_service import ConfigService

warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)


class BallKalmanFilter:
    def __init__(self):
        cfg = ConfigService()
        self.default_dt = float(cfg.config_dict["GAME"]["ai_timestamp"])
        ncameras = int(cfg.config_dict["IMAGE"]["number_of_camera"])
        self.game_state = GameState()
        # Transition model
        self.transition_model(self.default_dt)

        # Observation model
        self.H = [[1, 0, 0, 0] for _ in range(ncameras)]  # Position x
        self.H += [[0, 1, 0, 0] for _ in range(ncameras)]  # Position y
        self.H = np.array(self.H)

        # Process covariance
        self.Q = np.diag([10 ** 0, 10 ** 0, 10 ** 0, 10 ** 0])

        # Observation covariance
        self.R = 10 ** 0 * np.eye(2*ncameras)  # Pose * ncameras

        # Initial state covariance
        self.P = 10 ** 3 * np.eye(4)

        # Initial state estimation
        self.x = np.zeros(4)

    def predict(self):
        self.x = np.dot(self.F, self.x)
        self.P = np.dot(np.dot(self.F, self.P), np.transpose(self.F)) + self.Q

    def update(self, observation):

        obsx = []
        obsy = []
        for obs in observation:
            if obs is None:
                obsx.append(None)
                obsy.append(None)
            else:
                obsx.append(obs.x)
                obsy.append(obs.y)

        observation = np.array(obsx + obsy)

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
        last_ball_pose = self.game_state.field.ball.position
        if not dt:
            dt = self.default_dt
        self.transition_model(dt)
        if observation is not None:
            self.update(observation)
        else:
            players_my_team = closest_players_to_point(last_ball_pose)
            players_their_team = closest_players_to_point(last_ball_pose, False)
            if players_my_team[0].player_distance < players_their_team[0].player_distance:
                closest_player = players_my_team[0].player
                closest_player_distance_to_ball = players_my_team[0].player_distance
            else:
                closest_player = players_their_team[0].player
                closest_player_distance_to_ball = players_their_team[0].player_distance
            if closest_player_distance_to_ball < 150:
                #self.x[2] = closest_player.velocity.position[0]
                #self.x[3] = closest_player.velocity.position[1]
                player_to_ball = (last_ball_pose - closest_player.position).normalized() * (BALL_RADIUS + ROBOT_RADIUS)
                self.x[0] = closest_player.position[0] + player_to_ball.x
                self.x[1] = closest_player.position[1] + player_to_ball.y
                self.x[2] = 0
                self.x[3] = 0
        self.predict()
        output_state = self.x
        #print("speed", self.x[2], self.x[3])
        return output_state
