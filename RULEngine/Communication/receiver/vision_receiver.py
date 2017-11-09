import logging
from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_IP, IP_ADD_MEMBERSHIP, inet_aton, INADDR_ANY
from queue import Queue
from ipaddress import ip_address
from struct import pack
from threading import Thread, Event
from protobuf_to_dict import protobuf_to_dict

from RULEngine.Communication.protobuf.messages_robocup_ssl_wrapper_pb2 import SSL_WrapperPacket
from RULEngine.Communication.util.observations import BallObservation, RobotObservation, DetectionFrame


class VisionReceiver(Thread):
    def __init__(self, host: str, port: int, detection_queue: Queue, stop_event: Event):
        super(VisionReceiver, self).__init__()
        self.logger = logging.getLogger("VisionReceiver")

        self.host = host
        self.port = port
        self.detection_frame_queue = detection_queue
        self.stop_event = stop_event

        self.socket = None

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
        while not self.stop_event.is_set():
            try:
                data, _ = self.socket.recvfrom(2048)
            except Exception as e:
                self.logger.debug(e)
                exit(0)
            packet.ParseFromString(data)
            self.detection_frame_queue.put(protobuf_to_dict(packet))
