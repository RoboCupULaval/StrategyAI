# Under MIT License, see LICENSE.txt

import math
import time
import numpy as np


class MNRCFixedSpeed(object):
    def __init__(self):
        self.constants = _set_constants()

        self.kp = self.constants['MNRC_KP']
        self.ki = self.constants['MNRC_KI']
        self.mnrc_dynamic = self.constants['MNRC_SPEED_DYNAMIC']
        self.robot_dynamic = self.constants['ROBOT_DYNAMIC']
        self.coupling_matrix = self.constants['ROBOT_COUPLING']
        self.robot_radius = self.constants['ROBOT_RADIUS']

        self.filtered_reference = np.array([0, 0, 0])
        self.err_sum = np.array([0, 0, 0])

    @staticmethod
    def robot2fixed(robot_angle):
        return np.array(
            [[np.cos(robot_angle), -np.sin(robot_angle), 0], [np.sin(robot_angle), np.cos(robot_angle), 0], [0, 0, 1]])

    def update(self, reference, robot_state, delta_t):
        """
        Update the MNRC of the active player
        """

        robot_speed = robot_state["speed"]
        orientation = robot_state["position"][2]

        k1 = 1 + delta_t * self.mnrc_dynamic
        k2 = delta_t * self.mnrc_dynamic
        self.filtered_reference = k1 * self.filtered_reference - k2 * reference

        # Compute model error correction for zero static error
        err = self.filtered_reference - robot_speed
        self.err_sum = self.err_sum + err * delta_t
        correction = self.kp * err + self.ki * self.err_sum

        # Compute model prediction
        rotation_matrix = self.robot2fixed(orientation)
        inverse_dynamic = -np.linalg.pinv(np.matmul(np.diag(self.robot_dynamic), rotation_matrix))
        model_prediction = self.mnrc_dynamic * (self.filtered_reference - reference) - self.robot_dynamic * robot_speed

        # Return robot speed command
        return np.matmul(inverse_dynamic, model_prediction + correction)


def _set_constants():
    return {
        "MNRC_KP": np.array([14, 14, 14]),
        "MNRC_KI": np.array([50, 50, 50]),
        "MNRC_SPEED_DYNAMIC": np.array([-5, -5, -5]),
        "ROBOT_DYNAMIC": np.array([-10, -10, -10]),
        "ROBOT_COUPLING": np.array([[-0.7071,  0.7071, 0.0850],
                                    [-0.7071, -0.7071, 0.0850],
                                    [ 0.7071, -0.7071, 0.0850],
                                    [ 0.7071,  0.7071, 0.0850]]),
        "ROBOT_RADIUS": 0.025
    }


if __name__ == '__main__':

    MNRC = MNRCFixedSpeed()
    reference = np.array([0, 1, 1])
    robot_state = {"speed": np.array([0, 0, 0]), "position": np.array([0, 0, 0])}
    delta_t = 1 / 30

    speed_command = np.array([0, 0, 0])

    for _ in range(50):
        # Update robot position (Only for test purpose)
        robot_state["position"] = robot_state["position"] + robot_state["speed"] * delta_t

        # Update robot speed (Only for test purpose)
        rotation_matrix = MNRCFixedSpeed.robot2fixed(robot_state["position"][2])
        speed_difference = robot_state["speed"] - np.matmul(rotation_matrix, speed_command)
        speed_update = MNRC.robot_dynamic * speed_difference * delta_t
        robot_state["speed"] = robot_state["speed"] + speed_update

        # Compute new speed command
        speed_command = MNRC.update(reference, robot_state, delta_t)
