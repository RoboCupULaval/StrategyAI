import time
from copy import deepcopy

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.image_transformer.image_transformer import ImageTransformer
from config.config_service import ConfigService


class KalmanImageTransformer(ImageTransformer):
    def __init__(self):
        super().__init__()
        nb_cameras = int(ConfigService().config_dict["IMAGE"]["number_of_camera"])
        self.last_camera_frame = [empty_camera for _ in range(nb_cameras)]
        self.kalman_arranged_frame = {"balls": [None for _ in range(nb_cameras)],
                                      "blues": {i: [None for i in range(nb_cameras)] for i in range(PLAYER_PER_TEAM)},
                                      "yellows": {i: [None for i in range(nb_cameras)] for i in range(PLAYER_PER_TEAM)}}

    def update(self, packets):
        self._update_camera_kalman(packets)

        return self.kalman_arranged_frame

    def _update_camera_kalman(self, packets):
        self.new_image_flag = False
        if not packets:
            return
        # change the packets of a camera if frame_number of camera is higher
        # than what we have
        for packet in packets:
            if packet.HasField("detection"):

                c_id = packet.detection.camera_id
                f_nb = packet.detection.frame_number

                if f_nb > self.last_camera_frame[c_id]["frame_number"]:
                    new_camera = deepcopy(empty_camera)
                    new_camera["camera_id"] = c_id
                    new_camera["frame_number"] = f_nb
                    new_camera["t_capture"] = packet.detection.t_capture
                    new_camera["timestamp"] = time.time()

                    for ball in packet.detection.balls:
                        new_camera["ball"] = Position(ball.x, ball.y)
                        self.kalman_arranged_frame["balls"][c_id] = Position(ball.x, ball.y)

                    for blue in packet.detection.robots_blue:
                        new_camera["blues"][blue.robot_id] = Pose(Position(blue.x, blue.y),
                                                                  blue.orientation)
                        self.kalman_arranged_frame["blues"][blue.robot_id][c_id] = Pose(Position(blue.x, blue.y),
                                                                                        blue.orientation)
                    for yellow in packet.detection.robots_yellow:
                        new_camera["yellows"][yellow.robot_id] = Pose(Position(yellow.x, yellow.y),
                                                                      yellow.orientation)
                        self.kalman_arranged_frame["yellows"][yellow.robot_id][c_id] = \
                            Pose(Position(yellow.x, yellow.y),yellow.orientation)


                    self.last_camera_frame[c_id] = new_camera
                    self.new_image_flag = True

# TODO check the max numbers of bots
empty_camera = {"frame_number": 0,
                "t_capture": None,
                "camera_id": None,
                "timestamp": 0,
                "ball": None,
                "blues": [None for _ in range(0, 11)],
                "yellows": [None for __ in range(0, 11)]
                }
