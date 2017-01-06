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
        self.blue_last_position = {}
        self.yellow_last_position = {}
        self.frame_number = 1

    def update(self, packet):
        
        blue_team = packet.detection.robots_blue
        yellow_team = packet.detection.robots_yellow
        new_image = VisionFrame()
        new_vision_packet = self.create_ssl_packet(packet)

        # pass a frame by changing the
        for robot in self.blue_last_position.values():
            if robot[0] > 0:
                robot[0] -= 1

        for robot in self.yellow_last_position.values():
            if robot[0] > 0:
                robot[0] -= 1

        # player in blue team position corrected
        for player in blue_team:
            if player.robot_id in self.blue_last_position.keys():
                last_position = self.blue_last_position[player.robot_id][1]
                current_position = Position(player.x, player.y)
                self.blue_last_position[player.robot_id][1] = \
                    self.point_milieu(last_position, current_position)
                self.blue_last_position[player.robot_id][0] = 2
            else:
                self.blue_last_position[player.robot_id] = [None] * 2
                self.blue_last_position[player.robot_id][1] = \
                    Position(player.x, player.y)
                self.blue_last_position[player.robot_id][0] = 2

        # player in yellow team position corrected
        for player in yellow_team:
            if player.robot_id in self.yellow_last_position.keys():
                last_position = self.yellow_last_position[player.robot_id][1]
                current_position = Position(player.x, player.y)
                self.yellow_last_position[player.robot_id][1] = \
                    self.point_milieu(last_position, current_position)
                self.yellow_last_position[player.robot_id][0] = 2
            else:
                self.yellow_last_position[player.robot_id] = [None] * 2
                self.yellow_last_position[player.robot_id][1] = \
                    Position(player.x, player.y)
                self.yellow_last_position[player.robot_id][0] = 2

        for key, player in self.blue_last_position.items():
            if player[0] > 0:
                packet_robot = new_vision_packet.detection.robots_blue.add()
                packet_robot.confidence = 0.999
                packet_robot.robot_id = key
                packet_robot.x = player[1].x
                packet_robot.y = player[1].y
                packet_robot.pixel_x = 0.
                packet_robot.pixel_y = 0.

        for key, player in self.yellow_last_position.items():
            if player[0] > 0:
                packet_robot = new_vision_packet.detection.robots_yellow.add()
                packet_robot.confidence = 0.999
                packet_robot.robot_id = key
                packet_robot.x = player[1].x
                packet_robot.y = player[1].y
                packet_robot.pixel_x = 0.
                packet_robot.pixel_y = 0.

        return new_vision_packet

    def create_ssl_packet(self, packet):
        pb_sslwrapper = ssl_wrapper.SSL_WrapperPacket()
        # not sure if the frame_number is useful here
        pb_sslwrapper.detection.frame_number = self.frame_number
        self.frame_number += 1
        # those fields are obligatory for the vision packet
        pb_sslwrapper.detection.camera_id = 0
        pb_sslwrapper.detection.t_capture = 0
        pb_sslwrapper.detection.t_sent = 0

        ball = pb_sslwrapper.detection.balls.add()
        ball.x = 0     # packet.detection.balls[0].x
        ball.y = 15  # packet.detection.balls[0].y
        # i think we can ignore those values, but they are mandatory.
        ball.confidence = 0.999
        ball.pixel_x = 0
        ball.pixel_y = 0

        return pb_sslwrapper

    @staticmethod
    def point_milieu(position1, position2):
        x = (position1.x + position2.x)/2
        y = (position1.y + position2.y)/2
        return Position(x, y)
