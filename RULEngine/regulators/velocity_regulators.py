
from math import sqrt

from RULEngine.regulators.PID import PID
from RULEngine.regulators.regulator_base_class import RegulatorBaseClass
from RULEngine.robot import Robot, MIN_LINEAR_SPEED, MAX_LINEAR_ACCELERATION
from Util import Pose
from Util.geometry import wrap_to_pi, rotate


class RealVelocityController(RegulatorBaseClass):

    settings = {
        'translation': {'kp': .01, 'ki': 0.0, 'kd': 0},
        'rotation': {'kp': 0.5, 'ki': 0.02, 'kd': 0.0}
    }

    def __init__(self):
        self.orientation_controller = PID(**self.settings['rotation'], wrap_error=True)

    def execute(self, robot: Robot):

        target_orientation = \
            robot.target_orientation if robot.target_orientation is not None else robot.pose.orientation
        target = Pose(robot.path.points[1], target_orientation)
        target_speed = robot.path.speeds[1]
        error = Pose()
        error.position = target.position - robot.pose.position
        error.orientation = wrap_to_pi(target.orientation - robot.pose.orientation)

        speed_norm = robot.cruise_speed
        if is_time_to_break(robot.pose, robot.path.points[-1], robot.cruise_speed, MAX_LINEAR_ACCELERATION, target_speed):
            speed_norm = MIN_LINEAR_SPEED

        # TODO: test this IRL
        # fonctionne pas du tout, le robot break pas pentoute
        # speed_norm = optimal_speed(robot.pose, robot.path.points[-1], robot.cruise_speed, MAX_LINEAR_ACCELERATION, target_speed)

        vel = speed_norm * error.position / error.norm

        cmd_pos = rotate(vel, -robot.pose.orientation)
        cmd_orientation = self.orientation_controller.execute(error.orientation)

        return Pose(cmd_pos, cmd_orientation)

    def reset(self):
        pass


class GrSimVelocityController(RealVelocityController):

    settings = {
       'rotation': {'kp': .75, 'ki': 0.05, 'kd': 0}
    }


def is_time_to_break(robots_pose, destination, cruise_speed, acceleration, target_speed):
    # formule physique: v_finale ** 2 = v_init ** 2 - 2 * acceleration * distance_deplacement
    offset = 1  # petite marge pour break avant le point vue qu'il y a du délais
    dist_to_target = (destination - robots_pose.position).norm
    return dist_to_target < (abs(cruise_speed ** 2 - target_speed**2) / (2 * acceleration)) * offset


def optimal_speed(robots_pose, destination, cruise_speed, acceleration, target_speed):
    # formule physique: v_finale ** 2 = v_init ** 2 - 2 * acceleration * distance_deplacement
    dist_to_target = (destination - robots_pose.position).norm

    return max(cruise_speed, sqrt(abs(2 * acceleration * dist_to_target - target_speed**2)))
