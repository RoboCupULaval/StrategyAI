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
        self.ball_position = ()
        self.camera_packet = {}
        self.frame_number = 0

    def update(self, packets):
        
        blue_team = packets.detection.robots_blue
        yellow_team = packets.detection.robots_yellow
        new_image = VisionFrame()

        new_vision_packet = self.create_default_ssl_packet()
        self.add_ball_info_to_packet(packets, new_vision_packet)

        # player in blue team position corrected
        for player in blue_team:
            if player.robot_id in self.blue_position.keys():
                last_position = self.blue_position[player.robot_id][1]
                current_position = Position(player.x, player.y)
                self.blue_position[player.robot_id][1] = \
                    self.point_milieu(last_position, current_position)
                self.blue_position[player.robot_id][0] = 2
            else:
                self.blue_position[player.robot_id] = [None] * 2
                self.blue_position[player.robot_id][1] = \
                    Position(player.x, player.y)
                self.blue_position[player.robot_id][0] = 2

        # player in yellow team position corrected
        for player in yellow_team:
            if player.robot_id in self.yellow_position.keys():
                last_position = self.yellow_position[player.robot_id][1]
                current_position = Position(player.x, player.y)
                self.yellow_position[player.robot_id][1] = \
                    self.point_milieu(last_position, current_position)
                self.yellow_position[player.robot_id][0] = 2
            else:
                self.yellow_position[player.robot_id] = [None] * 2
                self.yellow_position[player.robot_id][1] = \
                    Position(player.x, player.y)
                self.yellow_position[player.robot_id][0] = 2

        for key, player in self.blue_position.items():
            if player[0] > 0:
                packet_robot = new_vision_packet.detection.robots_blue.add()
                packet_robot.confidence = 0.999
                packet_robot.robot_id = key
                packet_robot.x = player[1].x
                packet_robot.y = player[1].y
                packet_robot.pixel_x = 0.
                packet_robot.pixel_y = 0.

        for key, player in self.yellow_position.items():
            if player[0] > 0:
                packet_robot = new_vision_packet.detection.robots_yellow.add()
                packet_robot.confidence = 0.999
                packet_robot.robot_id = key
                packet_robot.x = player[1].x
                packet_robot.y = player[1].y
                packet_robot.pixel_x = 0.
                packet_robot.pixel_y = 0.

        return new_vision_packet

    def create_default_ssl_packet(self):
        pb_sslwrapper = ssl_wrapper.SSL_WrapperPacket()

        # making sure we increment the internal frame number
        self.frame_number += 1
        # those fields are obligatory for the detection part of the packet
        pb_sslwrapper.detection.frame_number = self.frame_number
        pb_sslwrapper.detection.camera_id = 0
        pb_sslwrapper.detection.t_capture = 0
        pb_sslwrapper.detection.t_sent = 0

        return pb_sslwrapper

    def add_ball_info_to_packet(self, packets_info, packet_to_add):
        pass

    def update_camera_packets(self, packets):
        for packet in packets:
            pass

    @staticmethod
    def point_milieu(position1, position2):
        x = (position1.x + position2.x)/2
        y = (position1.y + position2.y)/2
        return Position(x, y)
