import time
from copy import deepcopy

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Communication.protobuf import \
    messages_robocup_ssl_wrapper_pb2 as ssl_wrapper


class ImageTransformer(object):

    def __init__(self, kalman=False):
        # dict keys=robot_id, values=array of size 2 with at pos 0 an int <=2
        # and at pos 1 the position to
        if not kalman:
            self.blue_position = {}
            self.yellow_position = {}
            self.ball_position = None
            self.camera_packet = {}
            self.last_t_capture = 0
            self.new_image_flag = False
            self.last_new_packet = None
            self.frame_number = 1
        else:
            self.last_camera_frame = [empty_camera for _ in range(0, 4)]
            self.last_new_packet = None
        self.time = time.time()



    def update(self, packets):

        self._update_camera_packets(packets)

        if not self.new_image_flag:
            return self.last_new_packet

        new_vision_packet = self._create_default_ssl_packet()
        self.add_ball_info_to_packet(new_vision_packet)
        self._adjust_best_robot_position()
        self._create_robot_packet(new_vision_packet)
        self._add_final_fields(new_vision_packet)
        self.last_new_packet = new_vision_packet

        return new_vision_packet

    def has_new_image(self):
        return self.new_image_flag

    def _adjust_best_robot_position(self):
        self.blue_position.clear()
        self.yellow_position.clear()

        for c in self.camera_packet.values():
            if len(c.detection.robots_blue) > 0:
                for rb in c.detection.robots_blue:
                    if not self.blue_position.get(rb.robot_id, 0):
                        new_entry = (Position(rb.x, rb.y), rb.confidence)
                        self.blue_position[rb.robot_id] = new_entry

                    elif self.blue_position[rb.robot_id][1] < rb.confidence:
                        new_entry = (Position(rb.x, rb.y), rb.confidence)
                        self.blue_position[rb.robot_id] = new_entry

        for c in self.camera_packet.values():
            if len(c.detection.robots_yellow) > 0:
                for rb in c.detection.robots_yellow:
                    if not self.yellow_position.get(rb.robot_id, 0):
                        new_entry = (Position(rb.x, rb.y), rb.confidence)
                        self.yellow_position[rb.robot_id] = new_entry
                    elif self.yellow_position[rb.robot_id][1] < rb.confidence:
                        new_entry = (Position(rb.x, rb.y), rb.confidence)
                        self.yellow_position[rb.robot_id] = new_entry

    def _create_robot_packet(self, packet_to_add):
        for key, player in self.blue_position.items():
            if player[1] > 0:
                packet_robot = packet_to_add.detection.robots_blue.add()
                packet_robot.confidence = 0.999
                packet_robot.robot_id = key
                packet_robot.x = player[0].x
                packet_robot.y = player[0].y
                packet_robot.pixel_x = 0.
                packet_robot.pixel_y = 0.

        for key, player in self.yellow_position.items():
            if player[1] > 0:
                packet_robot = packet_to_add.detection.robots_yellow.add()
                packet_robot.confidence = 0.999
                packet_robot.robot_id = key
                packet_robot.x = player[0].x
                packet_robot.y = player[0].y
                packet_robot.pixel_x = 0.
                packet_robot.pixel_y = 0.

    def _create_default_ssl_packet(self):
        pb_sslwrapper = ssl_wrapper.SSL_WrapperPacket()

        # making sure we increment the internal frame number

        # those fields are obligatory for the detection part of the packet
        pb_sslwrapper.detection.camera_id = 0
        pb_sslwrapper.detection.t_sent = 0

        return pb_sslwrapper

    def _add_final_fields(self, packet_to_add):
        self.frame_number += 1
        packet_to_add.detection.t_capture = self.last_t_capture
        packet_to_add.detection.frame_number = self.frame_number

    def _update_camera_packets(self, packets):
        self.new_image_flag = False
        if not packets:
            return self.last_new_packet

        # change the packets of a camera if frame_number of camera is higher
        # than what we have
        for packet in packets:
            if packet.HasField("detection"):
                c_id = packet.detection.camera_id
                f_nb = packet.detection.frame_number
                t_cp = packet.detection.t_capture

                if not self.camera_packet.get(c_id, 0):
                    if t_cp > self.last_t_capture:
                        self.last_t_capture = t_cp
                    self.camera_packet[c_id] = packet
                    self.new_image_flag = True
                elif f_nb > self.camera_packet[c_id].detection.frame_number:
                    if t_cp > self.last_t_capture:
                        self.last_t_capture = t_cp
                    self.camera_packet[c_id] = packet
                    self.new_image_flag = True

    def add_ball_info_to_packet(self, packet_to_add):

        # This is logic to take a middle point from all the camera packet but
        # it isn't tested yet
        """
        all_ball_pst = []
        for packet in self.camera_packet.values():
            if packet.detection.HasField("balls"):
                for ball in packet.detection.balls:
                    ball_pst = Position(ball.x, ball.y)
                    all_ball_pst.append(ball_pst)

        ball_x = 0
        ball_y = 0
        for ball_pst in all_ball_pst:
            ball_x += ball_pst.x
            ball_y += ball_pst.y

        ball_x /= len(all_ball_pst)
        ball_y /= len(all_ball_pst)
        self.ball_position = Position(ball_x, ball_y)
        """

        # tuple with the position of the best ball and the confidence
        # of that position
        best_ball_pos = (Position(), 0)
        # get the ball with the best confidence among all subjects
        for packet in self.camera_packet.values():
            if len(packet.detection.balls) > 0:
                for ball in packet.detection.balls:
                    if best_ball_pos[1] < ball.confidence:
                        best_ball_pos = (Position(ball.x, ball.y, ball.z),
                                         ball.confidence)
        self.ball_position = best_ball_pos

        # creating the packet here
        pck_ball = packet_to_add.detection.balls.add()
        pck_ball.x = self.ball_position[0].x
        pck_ball.y = self.ball_position[0].y
        pck_ball.z = self.ball_position[0].z
        # required for the packet no use for us at this stage
        pck_ball.confidence = 0.999
        pck_ball.pixel_x = self.ball_position[0].x
        pck_ball.pixel_y = self.ball_position[0].y

    def kalman_update(self, packets):
        self._update_camera_kalman(packets)
        #if (time.time() - self.time > 2):
            #for cam in self.last_camera_frame:
            #    print(cam)
            #self.time = time.time()
        #print(time.time())
        return self.last_camera_frame

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

                    for blue in packet.detection.robots_blue:
                        new_camera["blues"][blue.robot_id] = Pose(Position(blue.x, blue.y),
                                                                  blue.orientation)
                    for yellow in packet.detection.robots_yellow:
                        new_camera["yellows"][yellow.robot_id] = Pose(Position(yellow.x, yellow.y),
                                                                      yellow.orientation)

                    self.last_camera_frame[c_id] = new_camera
                    self.new_image_flag = True

    @staticmethod
    def point_milieu(position1, position2):
        x = (position1.x + position2.x)/2
        y = (position1.y + position2.y)/2
        return Position(x, y)

# TODO check the max numbers of bots
empty_camera = {"frame_number": 0,
                "t_capture": None,
                "camera_id": None,
                "timestamp": 0,
                "ball": None,
                "blues": [None for _ in range(0, 11)],
                "yellows": [None for __ in range(0, 11)]
                }
