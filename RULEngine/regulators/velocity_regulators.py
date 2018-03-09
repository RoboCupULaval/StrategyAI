
from math import sqrt

from RULEngine.regulators.PID import PID
from RULEngine.regulators.regulator_base_class import RegulatorBaseClass
from RULEngine.robot import Robot, MAX_ANGULAR_SPEED, MAX_LINEAR_ACCELERATION
from RULEngine.trapezoidal_speed_profile import get_next_velocity
from Util import Pose
from Util.geometry import wrap_to_pi, rotate


class RealVelocityController(RegulatorBaseClass):

    settings = {'kp': 0.5, 'ki': 0.4, 'kd': 0.0}

    def __init__(self):
        self.orientation_controller = PID(**self.settings, wrap_error=True)

    @property
    def dt(self):
        return self.orientation_controller.dt

    def execute(self, robot: Robot):
        target_orientation = \
            robot.target_orientation if robot.target_orientation is not None else robot.pose.orientation
        target = Pose(robot.path.points[1], target_orientation)

        error = Pose(target.position - robot.pose.position)
        error.orientation = wrap_to_pi(target.orientation - robot.pose.orientation)

        speed_norm = get_next_velocity(robot, self.dt)

        vel = error.position * speed_norm / error.norm

        cmd_pos = rotate(vel, -robot.pose.orientation)
        cmd_orientation = self.orientation_controller.execute(error.orientation)
        cmd_orientation /= max(1, abs(cmd_orientation) / MAX_ANGULAR_SPEED)

        return Pose(cmd_pos, cmd_orientation)

    def reset(self):
        pass


class GrSimVelocityController(RealVelocityController):

    settings = {'kp': .75, 'ki': 0.05, 'kd': 0}


def is_time_to_break(robot, destination, cruise_speed, acceleration, target_speed):
    # formule physique: v_finale ** 2 = v_init ** 2 - 2 * acceleration * distance_deplacement
    offset = 1.2  # petite marge pour break avant le point vue qu'il y a du délais
    dist_to_target = (destination - robot.pose.position).norm
    return dist_to_target < (abs(cruise_speed ** 2 - target_speed**2) / (2 * acceleration)) * offset


def optimal_speed(robot, destination, cruise_speed, acceleration, target_speed):
    # formule physique: v_finale ** 2 = v_init ** 2 - 2 * acceleration * distance_deplacement
    dist_to_target = (destination - robot.pose.position).norm

    return max(cruise_speed, sqrt(abs(2 * acceleration * dist_to_target - target_speed**2)))
