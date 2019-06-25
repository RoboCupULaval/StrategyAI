from math import sqrt

from Engine.Controller.Regulators.PID import PID
from Engine.Controller.Regulators.regulator_base_class import RegulatorBaseClass
from Engine.Controller.robot import Robot, MAX_LINEAR_ACCELERATION, MAX_ANGULAR_SPEED
from Util import Pose
from Util.geometry import clamp, normalize, rotate
from Util.pose import Position

from config.config import Config
config = Config()

settings = {
    'orientation_pid_settings': {'kp': 10, 'ki': 1, 'kd': 0.0},
    'derivative_deadzone': 0.5
}


class PivotRegulator(RegulatorBaseClass):

    def __init__(self):
        self.orientation_controller = PID(**settings['orientation_pid_settings'],
                                          signed_error=True,
                                          deadzone=settings['derivative_deadzone'])
        self.dt = 0.0

    def reset(self):
        self.orientation_controller.reset()
        self.last_commanded_velocity = Position()
        self.dt = 0.0

    def execute(self, robot: Robot, dt):
        self.dt = dt

        # Velocity in robot's frame
        rotation_speed = robot.cruise_speed / 1000  # rad/s
        radius = robot.position_error.norm
        target_radius = robot.engine_cmd.target_radius
        # To control the radius, we tell the robot to go towards or away from the target
        # I only used a pid with P=1 for this correction, it's dumb, but it works
        corr_x = radius - target_radius
        velocity = Position(corr_x, rotation_speed * radius)

        target_orientation = robot.position_error.angle
        # Correct the orientation
        orientation_error = target_orientation - robot.orientation
        cmd_orientation = self.orientation_controller.execute(orientation_error)
        cmd_orientation = clamp(cmd_orientation, -MAX_ANGULAR_SPEED, MAX_ANGULAR_SPEED)

        world_velocity = rotate(velocity, target_orientation)
        return Pose(world_velocity, -rotation_speed + cmd_orientation)