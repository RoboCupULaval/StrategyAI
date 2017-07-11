import time
from copy import deepcopy
from typing import Dict, List, Type

import RULEngine.Communication.protobuf.messages_robocup_ssl_detection_pb2 as ssl_detection
import RULEngine.Communication.protobuf.messages_robocup_ssl_wrapper_pb2 as ssl_wrapper
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.image_transformer.image_transformer import ImageTransformer
from config.config_service import ConfigService


class KalmanImageTransformer(ImageTransformer):
    def __init__(self):
        super().__init__()
        nb_cameras = int(ConfigService().config_dict["IMAGE"]["number_of_camera"])
        self.last_new_packet = None
        self.new_image_flag = False
        self.time = time.time()
        self.cameras = [CameraPacket(cam_nb) for cam_nb in range(nb_cameras)]
        self.last_camera_frame = self._create_kalman_image()

    def update(self, packets: List=None):
        self.new_image_flag = False
        self._update_camera_kalman(packets)
        self._create_kalman_image()
        return self.last_camera_frame

    def _update_camera_kalman(self, packets: List[ssl_wrapper.SSL_WrapperPacket]) -> None:
        if not packets:
            return

        self.last_new_packet = packets

        for packet in packets:
            if packet.HasField("detection"):
                self.cameras[packet.detection.camera_id].update(packet)

    def _create_kalman_image(self):
        self.last_camera_frame = {"ball": [camera.ball for camera in self.cameras],
                                  "blues": list(zip(*(camera.robots_blue for camera in self.cameras))),
                                  "yellows": list(zip(*(camera.robots_yellow for camera in self.cameras)))}


class CameraPacket:
    def __init__(self, id: int):
        assert 0 <= id <= int(ConfigService().config_dict["IMAGE"]["number_of_camera"]), "Creating CameraPacket " \
                                                                                         "class with wrong id!"
        self.camera_id = id
        self.timestamp = 0
        self.t_capture = 0
        self.frame_number = 0
        self.ball = None
        self.robots_blue = [None for _ in range(PLAYER_PER_TEAM)]
        self.robots_blue_set = set()
        self.robots_yellow = [None for _ in range(PLAYER_PER_TEAM)]
        self.robots_yellow_set = set()
        self.packet = None

    def update(self, camera_packet: ssl_detection._SSL_DETECTIONFRAME) -> None:
        # sanity check to remove eventually
        if camera_packet.detection.camera_id != self.camera_id:
            raise ValueError("Wrong camera to packet assignation in", self.__class__.__name__)

        # skip updating if we have already a more recent packet
        if camera_packet.detection.frame_number <= self.frame_number:
            return

        # remember the last packet received
        self.packet = camera_packet

        # reset the set of the robots currently viewed in our packet
        self.robots_blue_set.update([i for i in range(PLAYER_PER_TEAM)])
        self.robots_yellow_set.update([i for i in range(PLAYER_PER_TEAM)])

        self._update_entities()
        self._remove_missing_entities()

    def _update_entities(self) -> None:
        # should there be a sanity check for multiple balls/players on the field viewed by the same camera?
        for ball in self.packet.detection.balls:
            self.ball = Position(ball.x, ball.y)

        # maybe a sanity check on the id of the robots. always 0 to 11 ? Possible key error on the set operations
        for blue in self.packet.detection.robots_blue:
            self.robots_blue[blue.robot_id] = Pose(blue.x, blue.y, blue.orientation)
            self.robots_blue_set.remove(blue.robot_id)

        for yellow in self.packet.detection.robots_yellow:
            self.robots_yellow[yellow.robot_id] = Pose(yellow.x, yellow.y, yellow.orientation)
            self.robots_yellow_set.remove(yellow.robot_id)

    def _remove_missing_entities(self) -> None:
        while self.robots_blue_set:
            self.robots_blue[self.robots_blue_set.pop()] = None

        while self.robots_yellow_set:
            self.robots_yellow[self.robots_yellow_set.pop()] = None

    def get_robots_blue(self)-> List:
        return self.robots_blue

    def get_robots_yellow(self)->List:
        return self.robots_yellow

    def get_ball(self)->Position:
        return self.ball
