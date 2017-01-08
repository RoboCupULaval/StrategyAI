from RULEngine.Util.Position import Position
from RULEngine.Util.vision_frame import VisionFrame
from RULEngine.Communication.protobuf import \
    messages_robocup_ssl_wrapper_pb2 as ssl_wrapper
from RULEngine.Communication.protobuf import \
    messages_robocup_ssl_detection_pb2 as ssl_detection


class ImageTransformer(object):

    def __init__(self):
        # dict keys=robot_id, values=array of size 2 with at pos 0 an int <=2
        # and at pos 1 the position to
        self.blue_position = {}
        self.yellow_position = {}
        self.ball_position = None
        self.camera_packet = {}
        self.frame_number = 0
        self.new_image_flag = False
        self.last_packet = None

    def update(self, packets):

        self._update_camera_packets(packets)

        if not self.new_image_flag:
            return self.last_packet

        new_vision_packet = self._create_default_ssl_packet()
        self.add_ball_info_to_packet(new_vision_packet)
        self._adjust_best_robot_position()
        self._create_robot_packet(new_vision_packet)
        self.last_packet = new_vision_packet
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
        self.frame_number += 1
        # those fields are obligatory for the detection part of the packet
        pb_sslwrapper.detection.frame_number = self.frame_number
        pb_sslwrapper.detection.camera_id = 0
        pb_sslwrapper.detection.t_capture = 0
        pb_sslwrapper.detection.t_sent = 0

        return pb_sslwrapper

    def _update_camera_packets(self, packets):
        self.new_image_flag = False

        if not packets:
            return self.last_packet

        # change the packets of a camera if frame_number of camera is higher
        # than what we have
        for packet in packets:
            if packet.HasField("detection"):
                c_id = packet.detection.camera_id
                f_nb = packet.detection.frame_number

                if not self.camera_packet.get(c_id, 0):
                    self.camera_packet[c_id] = packet
                    self.new_image_flag = True
                elif f_nb > self.camera_packet[c_id].detection.frame_number:
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
                        best_ball_pos = (Position(ball.x, ball.y),
                                         ball.confidence)
        self.ball_position = best_ball_pos

        # creating the packet here
        pck_ball = packet_to_add.detection.balls.add()
        pck_ball.x = self.ball_position[0].x
        pck_ball.y = self.ball_position[0].y
        # required for the packet no use for us at this stage
        pck_ball.confidence = 0.999
        pck_ball.pixel_x = 0.
        pck_ball.pixel_y = 0.

    @staticmethod
    def point_milieu(position1, position2):
        x = (position1.x + position2.x)/2
        y = (position1.y + position2.y)/2
        return Position(x, y)
