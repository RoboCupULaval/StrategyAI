from multiprocessing import Process, Event, Queue
from time import sleep

from config.config_service import ConfigService
from RULEngine.Communication.protobuf import referee_pb2 as ssl_referee
from RULEngine.Communication.util.protobuf_packet_receiver import ProtobufPacketReceiver


class RefereeCommunicationManager(Process):
    def __init__(self, referee_queue: Queue, stop_event: Event):
        super().__init__()
        cfg = ConfigService()
        self.host = cfg.config_dict["COMMUNICATION"]["referee_udp_address"]
        self.port = int(cfg.config_dict["COMMUNICATION"]["referee_port"])
        self.server = None
        self.queue = referee_queue
        self.stop_event = stop_event

    def initialize(self):
        self.server = ProtobufPacketReceiver(self.host, self.port, ssl_referee.SSL_Referee)
        self.loop()

    def loop(self):
        while not self.stop_event.is_set():
            packet = self.server.get_latest_frame()
            if packet is not None:
                self.queue.put(packet, False)
            sleep(0)

    def run(self):
        self.initialize()
