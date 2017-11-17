import logging
from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_IP, IP_ADD_MEMBERSHIP, inet_aton, INADDR_ANY, timeout
from queue import Full
from ipaddress import ip_address
from struct import pack
from multiprocessing import Process, Event, Queue
from protobuf_to_dict import protobuf_to_dict
from google.protobuf.message import DecodeError

from RULEngine.Communication.protobuf.messages_robocup_ssl_wrapper_pb2 import SSL_WrapperPacket


class VisionReceiver(Process):
    def __init__(self, host: str, port: int, detection_queue: Queue, stop_event: Event):
        super(VisionReceiver, self).__init__()
        self.logger = logging.getLogger("VisionReceiver")

        self.host = host
        self.port = port
        self.detection_frame_queue = detection_queue
        self.stop_event = stop_event

        self.socket = None

        self.logger.debug("initialized to {} {}".format(self.host, self.port))

    def initialize(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

        if ip_address(self.host).is_multicast:
            self.socket.setsockopt(IPPROTO_IP,
                                   IP_ADD_MEMBERSHIP,
                                   pack("=4sl", inet_aton(self.host), INADDR_ANY))
        self.socket.settimeout(0.2)
        self.logger.debug("Socket initialized")

    def run(self):
        self.logger.info('Starting process.')
        self.initialize()

        try:
            self.receive_packet()
        except KeyboardInterrupt:
            pass

        self.finalize()

    def receive_packet(self):
        packet = SSL_WrapperPacket()
        while not self.stop_event.is_set():
            try:
                data, _ = self.socket.recvfrom(2048)
                packet.ParseFromString(data)
                self.detection_frame_queue.put(protobuf_to_dict(packet))
            except Full as e:
                self.logger.debug("{}".format(e))
            except DecodeError:
                self.logger.error("Vision receiver had trouble decoding a packet! Are you listening "
                                  "to the correct port")
            except timeout:
                self.logger.error("Socket timed out after {}, Are you listening to the correct port?".format(0.2))

    def finalize(self):
        self.logger.debug("has exited gracefully")
        # exit(0)
