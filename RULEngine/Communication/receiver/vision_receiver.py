
import socket
import queue
import threading
import logging
from ipaddress import ip_address

import struct

from RULEngine.Communication.trackbots.tracker.field import Field
from RULEngine.Communication.trackbots.tracker.observations import DetectionFrame, BallObservation, RobotObservation
from RULEngine.Communication.trackbots.tracker.proto.messages_robocup_ssl_wrapper_pb2 import SSL_WrapperPacket
from RULEngine.Communication.util.protobuf_packet_receiver import ProtobufPacketReceiver


class VisionReceiver(ProtobufPacketReceiver):

    def __init__(self, server_address):
        self.server_address = server_address
        super().__init__(server_address[0], server_address[1], SSL_WrapperPacket)

        self.logger = logging.getLogger('VisionReceiver')

        self.field = Field()
        self._detection_frame_queue = queue.Queue()

        self._thread = threading.Thread(target=self.receive_packet, daemon=True)

    def get(self):
        return self._detection_frame_queue.get(block=True)

    def start(self):
        self.logger.info('Starting vision receiver thread.')
        self._wait_for_geometry()
        self._thread.start()

    def receive_packet(self):
        while True:
            packet = self.get_latest_frame()
            if packet.HasField('detection'):
                self.create_detection_frame(packet)
            if packet.HasField('geometry'):
                self.field.update(packet.geometry)

    def _wait_for_geometry(self):
        self.logger.info('Waiting for geometry from {}:{}'.format(*self.server_address))
        while self.field.geometry is None:
            packet = self.get_latest_frame()
            if packet is None:
                continue
            if packet.HasField('geometry'):
                self.logger.info('Geometry packet received.')
                self.field.update(packet.geometry)

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

        self._detection_frame_queue.put(DetectionFrame(**frame_fields))

    @staticmethod
    def parse_proto(proto_packet):
        return dict(map(lambda f: (f[0].name, f[1]), proto_packet.ListFields()))
