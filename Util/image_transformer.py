from RULEngine.Util.Position import Position
from RULEngine.Util.vision_frame import VisionFrame
from RULEngine.Communication.protobuf import \
    messages_robocup_ssl_wrapper_pb2 as ssl_wrapper
from RULEngine.Communication.protobuf import \
    messages_robocup_ssl_detection_pb2 as ssl_detection


class ImageTransformer(object):

    def __init__(self):
        self.blue_last_position = {}
        self.yellow_last_position = {}
        self.new_image = None
        self.new_protobuf_sslwrapper = None

    def update(self, packet_list):
        blue_team = packet_list.detection.robots_blue
        yellow_team = packet_list.detection.robots_yellow
        self.new_image = VisionFrame()

        for player in blue_team:
            if player.robot_id in self.blue_last_position.keys():
                last_position = self.blue_last_position[player.robot_id]
                current_position = Position(player.x, player.y)
                self.blue_last_position[player.robot_id] = \
                    self.point_milieu(last_position, current_position)
            else:
                self.blue_last_position[player.robot_id] = \
                    Position(player.x, player.y)

        for player in yellow_team:
            if player.robot_id in self.yellow_last_position.keys():
                last_position = self.yellow_last_position[player.robot_id]
                current_position = Position(player.x, player.y)
                self.yellow_last_position[player.robot_id] = \
                    self.point_milieu(last_position, current_position)
            else:
                self.yellow_last_position[player.robot_id] = \
                    Position(player.x, player.y)

    def create_ssl_packet(self):
        self.new_protobuf_sslwrapper = ssl_wrapper.SSL_WrapperPacket()
        ssl_detection_packets = ssl_detection.SSL_DetectionFrame()
        ball = ssl_detection.SSL_DetectionBall()
        



    @staticmethod
    def point_milieu(position1, position2):
        x = (position1.x + position2.x)/2
        y = (position1.y + position2.y)/2
        return Position(x, y)
