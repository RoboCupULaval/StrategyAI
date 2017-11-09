import logging
from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_IP, IP_ADD_MEMBERSHIP, inet_aton, INADDR_ANY
from queue import Queue
from ipaddress import ip_address
from struct import pack
from threading import Thread

from RULEngine.Communication.protobuf.messages_robocup_ssl_wrapper_pb2 import SSL_WrapperPacket
from RULEngine.Communication.util.observations import BallObservation, RobotObservation, DetectionFrame


class VisionReceiver(Thread):
    def __init__(self, host: str, port: int, detection_queue: Queue):
        super(VisionReceiver, self).__init__()
        self.logger = logging.getLogger("VisionReceiver")

        self.host = host
        self.port = port

        self.socket = None
        self._detection_frame_queue = detection_queue

        self.logger.debug("Vision receiver initialized to {} {}".format(self.host, self.port))

    def initialize_server(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

        if ip_address(self.host).is_multicast:
            self.socket.setsockopt(IPPROTO_IP,
                                   IP_ADD_MEMBERSHIP,
                                   pack("=4sl", inet_aton(self.host), INADDR_ANY))

    def run(self):

        self.logger.info('Starting vision receiver thread.')
        self.initialize_server()
        self.receive_packet()

    def receive_packet(self):
        packet = SSL_WrapperPacket()
        while True:
            data, _ = self.socket.recvfrom(2048)
            packet.ParseFromString(data)
            if packet.HasField('detection'):
                self.create_detection_frame(packet)
            if packet.HasField('geometry'):
                self._detection_frame_queue.put("thing")

    def create_detection_frame(self, packet):
        balls = []
        for ball in packet.detection.balls:
            ball_fields = VisionReceiver.parse_proto(ball)
            balls.append(BallObservation(**ball_fields))

        robots_blue = []
        for robot in packet.detection.robots_blue:
            robot_fields = VisionReceiver.parse_proto(robot)
            robots_blue.append(RobotObservation(**robot_fields))

        robots_yellow = []
        for robot in packet.detection.robots_yellow:
            robot_fields = VisionReceiver.parse_proto(robot)
            robots_yellow.append(RobotObservation(**robot_fields))

        frame_fields = VisionReceiver.parse_proto(packet.detection)
        frame_fields['balls'] = balls
        frame_fields['robots_blue'] = robots_blue
        frame_fields['robots_yellow'] = robots_yellow

        self._detection_frame_queue.put("THINGD")

    @staticmethod
    def parse_proto(proto_packet):
        return dict(map(lambda f: (f[0].name, f[1]), proto_packet.ListFields()))
