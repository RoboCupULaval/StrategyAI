
MAX_LINEAR_SPEED = 2000  # mm/s
MAX_LINEAR_ACCELERATION = 2000  # mm/s^2
MAX_ANGULAR_SPEED = 1  # rad/s
MAX_ANGULAR_ACCELERATION = 1  # rad/s^2
MIN_LINEAR_SPEED = 200  # mm/s Speed near zero, but still move the robot


class Robot:

    __slots__ = ('_robot_id', 'position_regulator', 'velocity_regulator',
                 'pose', 'velocity', 'path', 'engine_cmd')

    def __init__(self, robot_id):
        self._robot_id = robot_id
        self.position_regulator = None
        self.velocity_regulator = None
        self.pose = None
        self.velocity = None
        self.path = None
        self.engine_cmd = None

    @property
    def robot_id(self):
        return self._robot_id

    @property
    def target_orientation(self):
        if self.engine_cmd:
            return self.engine_cmd.target_orientation

    @property
    def cruise_speed(self):
        if self.engine_cmd:
            return self.engine_cmd.cruise_speed

    @property
    def raw_path(self):
        if self.engine_cmd:
            return self.engine_cmd.path

