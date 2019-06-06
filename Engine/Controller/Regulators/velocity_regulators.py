from math import sqrt

from Engine.Controller.Regulators.PID import PID
from Engine.Controller.Regulators.regulator_base_class import RegulatorBaseClass
from Engine.Controller.robot import Robot, MAX_LINEAR_ACCELERATION, MAX_ANGULAR_SPEED
from Util import Pose
from Util.geometry import clamp, normalize
from Util.pose import Position

from config.config import Config
config = Config()

settings = {
    'orientation_pid_settings': {'kp': 2, 'ki': 1, 'kd': 0.3},
    'v_d': 1000,  # lower = bigger path correction
    'emergency_brake_constant': 0, # Higher = higher correction of trajectory
    'brake_offset': 1,  # Offset to brake before because of the delay
    'max_acceleration': MAX_LINEAR_ACCELERATION,
    'derivative_deadzone': 0,
    'acceleration_deadzone': 0,  # mm, if the robot is at X mm of the objective it can not accelerate
}

if Config()['COACH']['type'] == 'sim':
    settings['orientation_pid_settings'] = {'kp': 2, 'ki': 0.3, 'kd': 0}
    settings['v_d'] = 15
    settings['brake_offset'] = 1


class VelocityRegulator(RegulatorBaseClass):

    def __init__(self):
        self.orientation_controller = PID(**settings['orientation_pid_settings'],
                                          signed_error=True,
                                          deadzone=settings['derivative_deadzone'])
        self.dt = 0.0
        self.last_commanded_velocity = Position()

    def execute(self, robot: Robot, dt):
        self.dt = dt
        speed_norm = self.get_next_speed(robot)

        path_correction = self.following_path_vector(robot) * 0

        velocity = (normalize(robot.position_error) + path_correction / settings['v_d']) * speed_norm
        if velocity.norm > speed_norm: velocity = normalize(velocity) * speed_norm

        cmd_orientation = self.orientation_controller.execute(robot.orientation_error)
        cmd_orientation = clamp(cmd_orientation, -MAX_ANGULAR_SPEED, MAX_ANGULAR_SPEED)

        self.last_commanded_velocity = velocity
        return Pose(velocity, cmd_orientation)

    def following_path_vector(self, robot):

        direction_error = self.last_commanded_velocity - robot.velocity.position
        if direction_error.norm > 0:
            return normalize(direction_error)
        else:
            return direction_error

    def get_next_speed(self, robot, acc=settings['max_acceleration']):
        
        dt = self.dt

        #  /------\
        # /        \
        # A   B    C
        if robot.target_speed > robot.current_speed:  # Only for non-zero current_speed
            next_speed = robot.current_speed + acc * dt
        else:
            if self.is_distance_for_brake(robot, acc, offset=1) and robot.position_error.norm > settings['acceleration_deadzone']:
                # A and B, for B the clamp prevent a speed higher than cruise speed
                next_speed = robot.current_speed + acc * dt
            else:  # C
                next_speed = robot.current_speed - acc * dt
        # print(robot.position_error.norm, next_speed)
        return clamp(next_speed, 0, robot.cruise_speed)

    @staticmethod
    def is_distance_for_brake(robot, acc, offset=1) -> bool:
        distance = 0.5 * abs(robot.current_speed ** 2 - robot.target_speed ** 2) / acc
        return robot.position_error.norm > (distance * offset)

    def reset(self):
        self.orientation_controller.reset()
        self.last_commanded_velocity = Position()
        self.dt = 0.0


def is_time_to_brake(robot, destination, cruise_speed, acceleration, target_speed):
    # v_f ** 2 = v_i ** 2 - 2 * acc * distance
    dist_to_target = (destination - robot.pose.position).norm
    return dist_to_target < (abs(cruise_speed ** 2 - target_speed**2) / (2 * acceleration)) * settings['brake_offset']


def optimal_speed(robot, destination, cruise_speed, acceleration, target_speed):
    # v_f ** 2 = v_i ** 2 - 2 * acc * distance
    dist_to_target = (destination - robot.pose.position).norm

    return max(cruise_speed, sqrt(abs(2 * acceleration * dist_to_target - target_speed**2)))
