from math import sqrt

from Engine.regulators.PID import PID
from Engine.regulators.regulator_base_class import RegulatorBaseClass
from Engine.robot import Robot, MAX_LINEAR_ACCELERATION, MAX_ANGULAR_SPEED
from Util import Pose
from Util.geometry import clamp, normalize
from Util.pose import Position
from config.config import Config
config = Config()


class RealVelocityController(RegulatorBaseClass):

    settings = {'kp': 10, 'ki': 0, 'kd': 1}
    v_d = 2
    emergency_break_constant = 0.4
    emergency_break_safety_factor = 0.5

    def __init__(self):
        self.orientation_controller = PID(**self.settings, signed_error=True, deadzone=0.05)
        self.dt = 0
        self.last_commanded_velocity = Position()

    def execute(self, robot: Robot, dt):
        self.dt = dt
        speed_norm = self.get_next_speed(robot)

        path_correction = self.following_path_vector(robot)

        velocity = robot.position_error * speed_norm / robot.position_error.norm + path_correction * speed_norm / self.v_d
        velocity /= max(1.0, abs(velocity.norm) / speed_norm)
        cmd_orientation = self.orientation_controller.execute(robot.orientation_error)
        cmd_orientation /= max(1.0, abs(cmd_orientation) / MAX_ANGULAR_SPEED)

        self.last_commanded_velocity = velocity

        return Pose(velocity, cmd_orientation)

    def following_path_vector(self, robot):

        direction_error = self.last_commanded_velocity - robot.velocity.position
        if direction_error.norm > 0:
            return normalize(direction_error)
        else:
            return direction_error

    def get_next_speed(self, robot, acc=MAX_LINEAR_ACCELERATION):
        acceleration_offset = 1.5  # on veut que le robot soit plus aggressif en début de trajet
        emergency_break_offset = self.emergency_break_constant / self.dt * (robot.current_speed / 1000)  # on veut que le robot break le plus qu'il peut si on s'approche trop vite de la target
        emergency_break_offset = max(1.0, emergency_break_offset)

        if robot.target_speed > robot.current_speed:
            next_speed = robot.current_speed + acc * self.dt * acceleration_offset
        else:
            if self.is_distance_for_break(robot, acc, offset=1):
                next_speed = robot.current_speed + acc * self.dt * acceleration_offset
            else:
                distance = 0.5 * abs(robot.current_speed ** 2 - robot.target_speed ** 2) / acc
                if robot.position_error.norm < (distance/self.emergency_break_safety_factor):
                    next_speed = robot.current_speed - acc * self.dt * emergency_break_offset
                else:
                    next_speed = robot.current_speed - acc * self.dt

        return clamp(next_speed, -1 * robot.cruise_speed, robot.cruise_speed)

    @staticmethod
    def is_distance_for_break(robot, acc, offset=1) -> bool:
        distance = 0.5 * abs(robot.current_speed ** 2 - robot.target_speed ** 2) / acc
        return robot.position_error.norm > (distance * offset)

    def reset(self):
        self.orientation_controller.reset()


class GrSimVelocityController(RealVelocityController):

    settings = {'kp': 2, 'ki': 0.3, 'kd': 0}
    v_d = 15
    emergency_break_constant = 0
    emergency_break_safety_factor = 1


def is_time_to_break(robot, destination, cruise_speed, acceleration, target_speed):
    # formule physique: v_finale ** 2 = v_init ** 2 - 2 * acceleration * distance_deplacement
    offset = 1.2  # petite marge pour break avant le point vue qu'il y a du délais
    dist_to_target = (destination - robot.pose.position).norm
    return dist_to_target < (abs(cruise_speed ** 2 - target_speed**2) / (2 * acceleration)) * offset


def optimal_speed(robot, destination, cruise_speed, acceleration, target_speed):
    # formule physique: v_finale ** 2 = v_init ** 2 - 2 * acceleration * distance_deplacement
    dist_to_target = (destination - robot.pose.position).norm

    return max(cruise_speed, sqrt(abs(2 * acceleration * dist_to_target - target_speed**2)))
