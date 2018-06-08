from typing import Optional

from Util import Pose, Position, Path
from Util.geometry import wrap_to_pi


MAX_LINEAR_SPEED = 4000  # mm/s
MAX_LINEAR_ACCELERATION = 3000  # mm/s^2
MAX_ANGULAR_COMMAND = 100  # rad
MAX_ANGULAR_COMMAND_VARIATION = 3  # rad/s
MIN_LINEAR_SPEED = 200  # mm/s Speed near zero, but still move the robot


class Robot:

    __slots__ = ('_id', 'is_on_field', 'velocity_regulator', 'position_regulator', 'pose', 'velocity', 'path', 'engine_cmd', 'target_speed')

    def __init__(self, _id: int):
        self._id = _id
        self.velocity_regulator = None
        self.position_regulator = None
        self.pose = None
        self.velocity = None
        self.path = None
        self.engine_cmd = None
        self.target_speed = None
        self.is_on_field = False

    @property
    def id(self) -> int:
        return self._id

    @property
    def is_active(self):
        return self.is_on_field and self.raw_path is not None

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
        if self.engine_cmd is not None and self.engine_cmd.path is not None:
            self.engine_cmd.path.start = self.position
            return self.engine_cmd.path

    @property
    def distance_to_path_end(self) ->Optional[float]:
        if self.path:
            return (self.position - self.path.target).norm

