
from math import sqrt

from Engine.regulators.PID import PID
from Engine.regulators.regulator_base_class import RegulatorBaseClass
from Engine.robot import Robot, MAX_LINEAR_ACCELERATION, MAX_ANGULAR_SPEED
from Util import Pose
from Util.geometry import clamp
from config.config import Config
config = Config()

class RealVelocityController(RegulatorBaseClass):

    settings = {'kp': 2, 'ki': 0.4, 'kd': 0.0}
    offset = 1

    def __init__(self):
        self.orientation_controller = PID(**self.settings, wrap_error=True)

    @property
    def dt(self):
        return 1 / config['ENGINE']['fps']

    def execute(self, robot: Robot):
        speed_norm = self.get_next_speed(robot, offset=self.offset)

        velocity = robot.position_error * speed_norm / robot.position_error.norm

        cmd_orientation = self.orientation_controller.execute(robot.orientation_error)
        cmd_orientation /= max(1, abs(cmd_orientation) / MAX_ANGULAR_SPEED)

        return Pose(velocity, cmd_orientation)

    def get_next_speed(self, robot, acc=MAX_LINEAR_ACCELERATION, offset=20):
        if robot.target_speed > robot.current_speed:
            next_speed = robot.current_speed + acc * self.dt * offset
        else:
            if not self.reach_acceleration_dist(robot, acc, offset=self.offset):
                next_speed = robot.current_speed + acc * self.dt * offset
            else:
                next_speed = robot.current_speed - acc * self.dt * offset

        return clamp(next_speed, 0, robot.cruise_speed)

    @staticmethod
    def reach_acceleration_dist(robot, acc, offset=2) -> bool:
        distance = 0.5 * abs(min(robot.current_speed ** 2, robot.cruise_speed ** 2) - robot.target_speed ** 2) / acc
        return robot.position_error.norm < distance * offset * 2

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
