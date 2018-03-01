
from math import sqrt

from RULEngine.controllers.PID import PID
from RULEngine.controllers.controller_base_class import ControllerBaseClass
from RULEngine.robot import Robot
from Util import Pose, Position
from Util.geometry import wrap_to_pi, rotate


class RealVelocityController(ControllerBaseClass):

    def __init__(self, control_setting):
        self.orientation_controller = PID(**control_setting['rotation'], wrap_error=True)

    def execute(self, robot: Robot):

        target_orientation = \
            robot.target_orientation if robot.target_orientation is not None else robot.pose.orientation
        target = Pose(robot.path.points[1], target_orientation)

        error = Pose()
        error.position = target.position - robot.pose.position
        error.orientation = wrap_to_pi(target.orientation - robot.pose.orientation)

        speed_norm = robot.cruise_speed
        if is_time_to_break(robot.pose, robot.path.points[-1], robot.cruise_speed, robot.max_linear_acceleration):
            speed_norm = robot.min_linear_speed

        # TODO: test this IRL
        # speed_norm = optimal_speed(robot.pose, path.points[-1], robot.cruise_speed, robot.max_linear_acceleration)

        vel = speed_norm * error.position / error.norm

        cmd_pos = rotate(vel, -robot.pose.orientation)
        cmd_orientation = self.orientation_controller.execute(error.orientation)

        return Pose(cmd_pos, cmd_orientation)

    def reset(self):
        pass


class GrSimVelocityController(RealVelocityController):
    pass


def is_time_to_break(robots_pose, destination, cruise_speed, acceleration):
    # TODO: we assume that the end speed is zero, which is not always the case
    dist_to_target = (destination - robots_pose.position).norm
    return dist_to_target < cruise_speed ** 2 / acceleration


def optimal_speed(robots_pose, destination, cruise_speed, acceleration):
    # TODO: we assume that the end speed is zero, which is not always the case
    dist_to_target = (destination - robots_pose.position).norm

    return max(cruise_speed, sqrt(acceleration * dist_to_target))
