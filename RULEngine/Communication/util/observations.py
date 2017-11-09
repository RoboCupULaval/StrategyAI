
from collections import namedtuple
from typing import Optional

_detection_frame_fields = 'frame_number, t_capture, t_sent, camera_id, balls, robots_blue, robots_yellow'
_robot_observation_fields = 'confidence, robot_id, x, y, orientation, pixel_x, pixel_y, height'
_ball_observation_fields = 'confidence, area, x, y, z, pixel_x, pixel_y'


class RobotObservation(namedtuple('RobotObservation', _robot_observation_fields)):

    __slots__ = ()

    # Add default argument to optional value
    def __new__(cls,
                robot_id: Optional[int]=None,
                orientation: Optional[float]=None,
                height: Optional[float]=None,
                **kwargs):

        return super().__new__(cls, robot_id=robot_id, orientation=orientation, height=height, **kwargs)


class BallObservation(namedtuple('BallObservation', _ball_observation_fields)):

    __slots__ = ()

    # Add default argument to optional value
    def __new__(cls,
                area: Optional[float]=None,
                z: Optional[float]=None,
                **kwargs):

        return super().__new__(cls, area=area, z=z, **kwargs)


class DetectionFrame(namedtuple('DetectionFrame', _detection_frame_fields)):

    __slots__ = ()

    # Add default argument to optional value
    def __new__(cls,
                balls: Optional[BallObservation]=None,
                robots_blue: Optional[RobotObservation]=None,
                robots_yellow: Optional[RobotObservation]=None,
                **kwargs):

        return super().__new__(cls, balls=balls, robots_blue=robots_blue, robots_yellow=robots_yellow, **kwargs)
