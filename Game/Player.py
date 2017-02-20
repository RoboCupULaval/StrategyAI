# Under MIT License, see LICENSE.txt
from ..Util.Pose import Pose
from ..Util.Vector import Vector
from ..Util.constant import DELTA_T

import numpy as np


class Player:
    def __init__(self, team, id):

        self.cmd = [0, 0, 0]
        self.id = id

        self.team = team

        self.pose = Pose()
        dt = DELTA_T
        self.transition_model = [[1, 0, dt, 0, 0, 0], [0, 1, 0, dt, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 1, dt], [0, 0, 0, 0, 0, 0]]
        control_input_model = [[0, 0, 0], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0], [0, 0, 1]]
        observation_model = [[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0]]

        process_covariance = 10 ** (3) * np.eye(6)
        observation_covariance = np.eye(3) * 10 ** (-3)

        initial_state_estimation = [self.pose.position.x, self.pose.position.y, 0, 0, self.pose.orientation, 0]
        initial_state_covariance = np.eye(6) * 1000
        self.kf = Kalman(self.transition_model, control_input_model, observation_model, process_covariance,
                         observation_covariance, initial_state_estimation, initial_state_covariance)

        self.velocity = [0, 0, 0]
        self.filtered_state_means = [self.pose.position.x, self.pose.position.y, 0, 0, self.pose.orientation, 0]
        self.filtered_state_covariances = np.eye(6)
        self.observations = [self.pose.position.x, self.pose.position.y, self.pose.orientation]

        # if self.id == 1:
        #     self.val_unfiltered = open('unfiltered.txt', 'w')
        #     self.val_filtered = open('filtered.txt', 'w')

    def has_id(self, pid):
        return self.id == pid

    def update(self, pose, delta=DELTA_T):
        # if self.id == 1 and not self.team.is_team_yellow():
        #     self.val_unfiltered.write("{}, {}, {}\n".format(pose.position.x, pose.position.y, pose.orientation))
        old_pose=self.pose
        new_pose = pose
        #print(self.id)
        #print("#1", pose.position.x, pose.position.y, pose.orientation)
        self.observations = [pose.position.x, pose.position.y, pose.orientation]
        self.transition_model = [[1., 0., delta, 0., 0., 0.], [0., 1., 0., delta, 0., 0.], [0., 0., 1, 0., 0., 0.],
                                 [0., 0., 0., 1, 0., 0.],
                                 [0., 0., 0., 0., 1., delta], [0., 0., 0., 0., 0., 1]]
        output = self.kf.filter(self.observations, self.cmd, self.transition_model)
        new_pose.position.x = float(output[0])
        new_pose.position.y = float(output[1])
        self.velocity = [output[2], output[3], output[5]]
        #print(self.velocity)
        # if np.linalg.norm(self.velocity) != 0:
        #     print(self.velocity)
        new_pose.orientation = float(output[4])
        #print("#2", new_pose.position.x, new_pose.position.y, new_pose.orientation)
        # old_pose = self.pose
        #delta_position = new_pose.position - old_pose.position
        # if self.id == 1 and not self.team.is_team_yellow():
        #     print(self.pose.position.x, self.pose.position.y)
        # try:
        #     self.velocity[0] = -(new_pose.position.x - old_pose.position.x) / delta / 1000
        #     self.velocity[1] = -(new_pose.position.y - old_pose.position.y) / delta / 1000
        #     self.velocity[2] = 0
        # except ZeroDivisionError:
        #     self.velocity = [0, 0, 0]

        self.pose = new_pose
        # if self.id == 1 and not self.team.is_team_yellow():
        #     self.val_filtered.write("{}, {}, {}\n".format(self.pose.position.x, self.pose.position.y,
        #                                                     self.pose.orientation))

    def set_command(self, cmd):
        self.cmd = [cmd.pose.position.x, cmd.pose.position.y, cmd.pose.orientation]
        #self.cmd = [0, 0, 0]

class Kalman:
    def __init__(self, transition_model, control_input_model, observation_model, process_covariance,
                 observation_covariance, initial_state_estimation, initial_state_covariance):
        self.F = np.array(transition_model)
        self.B = np.array(control_input_model)
        self.H = np.array(observation_model)
        self.Q = np.array(process_covariance)
        self.R = np.array(observation_covariance)

        self.x = np.array(initial_state_estimation)
        self.P = np.array(initial_state_covariance)

    def predict(self, command):
        self.x = np.dot(self.F, self.x) + np.dot(self.B, np.array(command))
        self.P = np.dot(np.dot(self.F, self.P), np.transpose(self.F)) + self.Q

    def update(self, observation):
        y = np.array(observation) - np.dot(self.H, self.x)
        #print(y)
        S = np.dot(np.dot(self.H, self.P), np.transpose(self.H)) + self.R
        K = np.dot(np.dot(self.P, np.transpose(self.H)), np.linalg.inv(S))

        self.x += np.dot(K, y)
        self.P = np.dot((np.eye(self.P.shape[0]) - np.dot(K, self.H)), self.P)

    def filter(self, observation, command, transition_model = None, ):
        if transition_model is None:
            self.F = np.array(transition_model)

        self.predict(command)
        self.update(observation)
        return self.x
