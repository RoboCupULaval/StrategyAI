from Util import Pose
from Util.path import Path

MAX_LINEAR_SPEED = 400000  # mm/s
MAX_LINEAR_ACCELERATION = 400000  # mm/s^2
MAX_ANGULAR_SPEED = 1  # rad/s
MAX_ANGULAR_ACCELERATION = 1  # rad/s^2

class Robot:

    __slots__ = ('_robot_id', 'controller', 'target_orientation', 'pose', 'velocity',
                 'kick_type', 'kick_force', 'dribbler_active', 'input_command',
                 'cruise_speed', 'max_linear_speed', 'max_linear_acceleration',
                 'max_angular_speed', 'max_angular_acceleration', 'path', 'raw_path')

    def __init__(self, robot_id, controller):
        self._robot_id = robot_id
        self.controller = controller
        self.pose = None
        self.velocity = None
        self.kick_type = None
        self.kick_force = 0
        self.dribbler_active = False
        self.input_command = None
        self.max_linear_speed = MAX_LINEAR_SPEED
        self.max_linear_acceleration = MAX_LINEAR_ACCELERATION
        self.max_angular_speed = MAX_ANGULAR_SPEED
        self.max_angular_acceleration = MAX_ANGULAR_ACCELERATION
        self.cruise_speed = 2000
        self.path = None
        self.raw_path = None
        self.target_orientation = 0

    @property
    def robot_id(self):
        return self._robot_id