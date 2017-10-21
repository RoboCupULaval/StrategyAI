# Under MIT License, see LICENSE.txt
from multiprocessing import Process, Queue, Event

from RULEngine.Communication.protobuf import referee_pb2 as ssl_referee
from RULEngine.Communication.util.protobuf_packet_receiver import ProtobufPacketReceiver
from config.config_service import ConfigService


class RefereeReceiver(Process):

    def __init__(self, referee_queue: Queue, stop_event: Event):
        super().__init__()
        cfg = ConfigService()
        self.host = cfg.config_dict["COMMUNICATION"]["referee_udp_address"]
        self.port = int(cfg.config_dict["COMMUNICATION"]["referee_port"])
        self.server = None
        self.stop_event = stop_event

    def loop(self):
        while not self.stop_event.is_set():
            self.server.get_latest_packet()

    def start(self):
        self.server = ProtobufPacketReceiver(self.host, self.port, ssl_referee.SSL_Referee)
