
from math import sqrt

from Engine.regulators.PID import PID
from Engine.regulators.regulator_base_class import RegulatorBaseClass
from Engine.robot import Robot, MAX_LINEAR_ACCELERATION, MAX_ANGULAR_COMMAND
from Util import Pose
from Util.geometry import clamp
from config.config import Config
config = Config()


class RealVelocityController(RegulatorBaseClass):

    settings = {'kp': 10, 'ki': 0, 'kd': 1}
    offset = 1

    def __init__(self):
        self.orientation_controller = PID(**self.settings, signed_error=True, deadzone=0)

    @property
    def dt(self):
        return 1 / config['ENGINE']['fps']

    def execute(self, robot: Robot):
        speed_norm = self.get_next_speed(robot)

        velocity = robot.position_error * speed_norm / robot.position_error.norm

        cmd_orientation = self.orientation_controller.execute(robot.orientation_error)
        cmd_orientation /= max(1, abs(cmd_orientation) / MAX_ANGULAR_COMMAND)

        return Pose(velocity, cmd_orientation)

    def get_next_speed(self, robot, acc=MAX_LINEAR_ACCELERATION):
        if robot.target_speed > robot.current_speed:
            next_speed = robot.current_speed + acc * self.dt * 1.5
        else:
            if self.distance_for_break(robot, acc, offset=self.offset):
                next_speed = robot.current_speed + acc * self.dt * 1.5
            else:
                distance = 0.5 * abs(robot.current_speed ** 2 - robot.target_speed ** 2) / acc
                if robot.position_error.norm < (distance / 0.5):
                    next_speed = robot.current_speed - acc * self.dt * 30
                else:
                    next_speed = robot.current_speed - acc * self.dt

        return clamp(next_speed, -1 * robot.cruise_speed, robot.cruise_speed)

    @staticmethod
    def distance_for_break(robot, acc, offset=2) -> bool:
        distance = 0.5 * abs(robot.current_speed ** 2 - robot.target_speed ** 2) / acc
        return robot.position_error.norm > (distance * offset)

    def reset(self):
        self.orientation_controller.reset()


class GrSimVelocityController(RealVelocityController):

    settings = {'kp': 2, 'ki': 0.3, 'kd': 0}
    offset = 1


def is_time_to_break(robot, destination, cruise_speed, acceleration, target_speed):
    # formule physique: v_finale ** 2 = v_init ** 2 - 2 * acceleration * distance_deplacement
    offset = 1.2  # petite marge pour break avant le point vue qu'il y a du délais
    dist_to_target = (destination - robot.pose.position).norm
    return dist_to_target < (abs(cruise_speed ** 2 - target_speed**2) / (2 * acceleration)) * offset


def optimal_speed(robot, destination, cruise_speed, acceleration, target_speed):
    # formule physique: v_finale ** 2 = v_init ** 2 - 2 * acceleration * distance_deplacement
    dist_to_target = (destination - robot.pose.position).norm

    return max(cruise_speed, sqrt(abs(2 * acceleration * dist_to_target - target_speed**2)))
