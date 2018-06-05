from typing import Optional

from Util import Pose, Position, Path
from Util.geometry import wrap_to_pi


MAX_LINEAR_SPEED = 3000  # mm/s
MAX_LINEAR_ACCELERATION = 3000  # mm/s^2
MAX_ANGULAR_SPEED = 5  # rad/s
MAX_ANGULAR_ACCELERATION = 2  # rad/s^2
MIN_LINEAR_SPEED = 200  # mm/s Speed near zero, but still move the robot


class Robot:

    __slots__ = ('_robot_id', 'position_regulator', 'velocity_regulator',
                 'pose', 'velocity', 'path', 'engine_cmd', 'target_speed', 'is_active')

    def __init__(self, robot_id: int):
        self._robot_id = robot_id
        self.position_regulator = None
        self.velocity_regulator = None
        self.is_active = False
        self.pose = None
        self.velocity = None
        self.path = None
        self.engine_cmd = None
        self.target_speed = None

    @property
    def robot_id(self) -> int:
        return self._robot_id

    @property
    def target_pose(self) -> Pose:
        if self.target_orientation is not None:
            orientation = self.target_orientation
        else:
            orientation = self.orientation

        if self.target_position is not None:
            position = self.target_position
        else:
            position = self.position

        return Pose(position, orientation)

    @property
    def pose_error(self) -> Pose:
        return Pose(self.position_error, self.orientation_error)

    @property
    def position(self) -> Optional[Position]:
        if self.pose is not None:
            return self.pose.position

    @property
    def position_error(self) -> Optional[Position]:
        return self.target_position - self.position

    @property
    def target_position(self) -> Optional[Position]:
        if self.path is not None:
            return self.path.next_position

    @property
    def orientation(self) -> Optional[float]:
        if self.pose is not None:
            return self.pose.orientation

    @property
    def target_orientation(self) -> Optional[float]:
        if self.engine_cmd is not None:
            return self.engine_cmd.target_orientation

    @property
    def orientation_error(self) -> Optional[float]:
        if self.target_orientation is not None and self.orientation is not None:
            return wrap_to_pi(self.target_orientation - self.orientation)

    @property
    def end_speed(self) -> Optional[float]:
        if self.engine_cmd is not None:
            return self.engine_cmd.end_speed

    @property
    def cruise_speed(self) -> Optional[float]:
        if self.engine_cmd is not None:
            return self.engine_cmd.cruise_speed

    @property
    def current_speed(self) -> Optional[float]:
        if self.velocity is not None:
            return self.velocity.position.norm

    @property
    def raw_path(self) -> Optional[Path]:
        if self.engine_cmd is not None:
            return self.engine_cmd.path

