
from Util import Pose
from Util.path import Path

MAX_LINEAR_SPEED = 2000  # mm/s
MAX_LINEAR_ACCELERATION = 2000  # mm/s^2
MAX_ANGULAR_SPEED = 1  # rad/s
MAX_ANGULAR_ACCELERATION = 1  # rad/s^2
MIN_LINEAR_SPEED = 200  # mm/s Speed near zero, but still move the robot


class Robot:

    __slots__ = ('_robot_id', 'position_controller', 'velocity_controller',
                 'pose', 'velocity', 'path', 'engine_command',
                 'max_linear_speed', 'min_linear_speed', 'max_linear_acceleration',
                 'max_angular_speed', 'max_angular_acceleration')

    def __init__(self, robot_id):
        self._robot_id = robot_id
        self.position_controller = None
        self.velocity_controller = None
        self.pose = None
        self.velocity = None
        self.path = None
        self.engine_command = None

    @property
    def robot_id(self):
        return self._robot_id

    @property
    def target_orientation(self):
        if self.engine_command:
            return self.engine_command.target_orientation

    @property
    def cruise_speed(self):
        if self.engine_command:
            return self.engine_command.cruise_speed

    @property
    def raw_path(self):
        if self.engine_command:
            return self.engine_command.path

